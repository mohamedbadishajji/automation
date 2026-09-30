from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.asset import AssetType

# --- Internal Assets ---
class InternalAssetBase(BaseModel):
    title: str
    asset_type: AssetType
    description: str
    qdrant_point_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = {}
    file_url: Optional[str] = None

class InternalAssetCreate(InternalAssetBase):
    pass

class InternalAssetResponse(InternalAssetBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- RAG Asset Match ---
class TenderAssetMatchCreate(BaseModel):
    asset_id: int
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    match_reason: Optional[str] = None

class TenderAssetMatchResponse(BaseModel):
    id: int
    tender_id: int
    asset_id: int
    relevance_score: float
    match_reason: Optional[str]
    created_at: datetime
    asset: Optional[InternalAssetResponse] = None

    model_config = ConfigDict(from_attributes=True)