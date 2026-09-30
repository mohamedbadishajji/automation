import os
import httpx
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db
from app.models.tender import Tender, TenderStatus
from app.models.proposal import Proposal
from app.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalResponse

router = APIRouter()

def _call_n8n_webhook(url: str, payload: dict):
    try:
        httpx.post(url, json=payload, timeout=5.0)
    except Exception as e:
        # Don't crash if n8n is offline in dev mode
        print(f"Warning: Could not contact n8n webhook: {e}")

@router.post("/tenders/{tender_id}/trigger-proposal", status_code=status.HTTP_202_ACCEPTED)
def trigger_n8n_proposal(
    tender_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger the n8n agent workflow to start autonomous proposal generation.
    """
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")

    tender.status = TenderStatus.GENERATING_PROPOSAL
    db.commit()

    # Async background HTTP call to n8n Webhook
    payload = {
        "tender_id": tender.id,
        "title": tender.title,
        "organization_name": tender.organization_name,
        "raw_description": tender.raw_description
    }
    background_tasks.add_task(
        _call_n8n_webhook,
        url=settings.N8N_PROPOSAL_WEBHOOK_URL,
        payload=payload
    )

    return {"message": "Proposal generation triggered successfully", "status": tender.status}


@router.post("/tenders/{tender_id}/generate-proposal", response_model=ProposalResponse,
             status_code=status.HTTP_201_CREATED)
def create_proposal(
        tender_id: int,
        proposal_in: ProposalCreate,
        db: Session = Depends(get_db)
):
    """
    Save a new generated commercial proposal draft (from n8n workflow or LLM generator).
    Updates tender status to 'PROPOSAL_READY'.
    """
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender with ID {tender_id} not found."
        )

    # Increment version number automatically if a proposal already exists
    latest_proposal = db.scalar(
        select(Proposal)
        .where(Proposal.tender_id == tender_id)
        .order_by(desc(Proposal.version))
    )
    new_version = (latest_proposal.version + 1) if latest_proposal else 1

    db_proposal = Proposal(
        tender_id=tender_id,
        version=new_version,
        content_json=proposal_in.content_json,
        coverage_score_matrix=proposal_in.coverage_score_matrix,
        rag_matches=proposal_in.rag_matches.model_dump() if proposal_in.rag_matches else None,
        file_path_pptx=proposal_in.file_path_pptx,
        file_path_pdf=proposal_in.file_path_pdf
    )
    db.add(db_proposal)

    # Update tender status
    tender.status = TenderStatus.PROPOSAL_READY
    db.add(tender)

    db.commit()
    db.refresh(db_proposal)
    return db_proposal


@router.get("/tenders/{tender_id}/proposals", response_model=List[ProposalResponse])
def list_proposals_for_tender(
        tender_id: int,
        db: Session = Depends(get_db)
):
    """
    Get all proposal versions associated with a specific tender.
    """
    stmt = select(Proposal).where(Proposal.tender_id == tender_id).order_by(desc(Proposal.version))
    return db.scalars(stmt).all()


@router.patch("/proposals/{proposal_id}", response_model=ProposalResponse)
def update_proposal_human_in_the_loop(
        proposal_id: int,
        proposal_in: ProposalUpdate,
        db: Session = Depends(get_db)
):
    """
    Human-in-the-Loop Refinement Feature:
    Allows sales team to refine and edit proposal slides/content in real-time from the dashboard.
    """
    db_proposal = db.get(Proposal, proposal_id)
    if not db_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found."
        )

    update_data = proposal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_proposal, field, value)

    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


@router.get("/proposals/{proposal_id}/download")
def download_proposal_file(
        proposal_id: int,
        file_type: str = Query("pptx", regex="^(pptx|pdf)$"),
        db: Session = Depends(get_db)
):
    """
    Download the generated presentation file (.pptx or .pdf).
    """
    db_proposal = db.get(Proposal, proposal_id)
    if not db_proposal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found."
        )

    file_path = db_proposal.file_path_pptx if file_type == "pptx" else db_proposal.file_path_pdf

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requested {file_type.upper()} file is not generated or found on the server."
        )

    media_type = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        if file_type == "pptx"
        else "application/pdf"
    )

    filename = os.path.basename(file_path)
    return FileResponse(path=file_path, media_type=media_type, filename=filename)