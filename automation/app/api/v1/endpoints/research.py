from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.tender import Tender, TenderStatus
from app.models.research import ProspectResearch
from app.schemas.research import ProspectResearchCreate, ProspectResearchResponse

router = APIRouter()


@router.post("/tenders/{tender_id}/research", response_model=ProspectResearchResponse, status_code=status.HTTP_201_CREATED)
def upsert_prospect_research(
    tender_id: int,
    research_in: ProspectResearchCreate,
    db: Session = Depends(get_db)
):
    """
    Webhook target for n8n agent workflow to save/update prospect research findings for a given tender.
    Automatically advances the tender status to 'RESEARCHED'.
    """
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender with ID {tender_id} not found."
        )

    # Check if research already exists (Upsert logic)
    existing_research = db.scalar(
        select(ProspectResearch).where(ProspectResearch.tender_id == tender_id)
    )

    if existing_research:
        # Update existing record
        for field, value in research_in.model_dump(exclude_unset=True).items():
            setattr(existing_research, field, value)
        db_research = existing_research
    else:
        # Create new record
        db_research = ProspectResearch(
            tender_id=tender_id,
            **research_in.model_dump()
        )
        db.add(db_research)

    # Advance status
    tender.status = TenderStatus.RESEARCHED
    db.add(tender)

    db.commit()
    db.refresh(db_research)
    return db_research


@router.get("/tenders/{tender_id}/research", response_model=ProspectResearchResponse)
def get_prospect_research(
    tender_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve prospect research for a specific tender.
    """
    research = db.scalar(
        select(ProspectResearch).where(ProspectResearch.tender_id == tender_id)
    )
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prospect research found for tender ID {tender_id}."
        )
    return research