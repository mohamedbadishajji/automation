import enum
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, Float, DateTime, Enum, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tender import Tender


class AssetType(str, enum.Enum):
    CV = "CV"
    PAST_PROJECT = "PAST_PROJECT"
    TOOL_STACK = "TOOL_STACK"


class InternalAsset(Base):
    __tablename__ = "internal_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Reference to vector stored in Qdrant DB
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)  # e.g. {"skills": ["Python", "FastAPI"]}
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    matches: Mapped[List["TenderAssetMatch"]] = relationship("TenderAssetMatch", back_populates="asset")


class TenderAssetMatch(Base):
    __tablename__ = "tender_asset_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("internal_assets.id"), nullable=False)

    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 0.89 vector similarity score
    match_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # RAG explanation
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    tender: Mapped["Tender"] = relationship("Tender", back_populates="asset_matches")
    asset: Mapped["InternalAsset"] = relationship("InternalAsset", back_populates="matches")