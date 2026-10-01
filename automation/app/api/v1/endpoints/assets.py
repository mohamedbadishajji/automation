from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.tender import Tender
from app.models.asset import InternalAsset, TenderAssetMatch
from app.schemas.asset import (
    InternalAssetCreate,
    InternalAssetResponse,
    TenderAssetMatchCreate,
    TenderAssetMatchResponse
)

router = APIRouter()


# --- Internal Assets CRUD ---

@router.post("/assets/", response_model=InternalAssetResponse, status_code=status.HTTP_201_CREATED)
def create_internal_asset(
        asset_in: InternalAssetCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new internal asset (CV, Past Project, Tool Stack) and link its Qdrant point ID.
    """
    db_asset = InternalAsset(**asset_in.model_dump())
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.get("/assets/", response_model=List[InternalAssetResponse])
def list_internal_assets(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """
    List all registered internal knowledge assets.
    """
    stmt = select(InternalAsset).offset(skip).limit(limit)
    return db.scalars(stmt).all()


# --- RAG Matches Webhook ---

@router.post("/tenders/{tender_id}/matches", response_model=List[TenderAssetMatchResponse],
             status_code=status.HTTP_201_CREATED)
def record_rag_matches(
        tender_id: int,
        matches_in: List[TenderAssetMatchCreate],
        db: Session = Depends(get_db)
):
    """
    Bulk submit top RAG matches extracted from Qdrant vector search for a tender.
    """
    tender = db.get(Tender, tender_id)
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tender with ID {tender_id} not found."
        )

    created_matches = []
    for match_item in matches_in:
        asset = db.get(InternalAsset, match_item.asset_id)
        if not asset:
            continue  # Skip invalid asset references

        db_match = TenderAssetMatch(
            tender_id=tender_id,
            asset_id=match_item.asset_id,
            relevance_score=match_item.relevance_score,
            match_reason=match_item.match_reason
        )
        db.add(db_match)
        created_matches.append(db_match)

    db.commit()
    for match in created_matches:
        db.refresh(match)

    return created_matches