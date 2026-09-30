import enum
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, Enum, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.research import ProspectResearch
    from app.models.asset import TenderAssetMatch
    from app.models.proposal import Proposal


class TenderStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    RESEARCHING = "RESEARCHING"
    RESEARCHED = "RESEARCHED"
    GENERATING_PROPOSAL = "GENERATING_PROPOSAL"
    PROPOSAL_READY = "PROPOSAL_READY"
    FAILED = "FAILED"


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organization_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    nlp_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Metadata & Tracking
    status: Mapped[TenderStatus] = mapped_column(
        Enum(TenderStatus),
        default=TenderStatus.DETECTED,
        nullable=False
    )
    is_partial: Mapped[bool] = mapped_column(default=False)  # For handling incomplete RFP specs
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow)

    # Relationships
    research: Mapped[Optional["ProspectResearch"]] = relationship(
        "ProspectResearch", back_populates="tender", uselist=False, cascade="all, delete-orphan"
    )
    asset_matches: Mapped[List["TenderAssetMatch"]] = relationship(
        "TenderAssetMatch", back_populates="tender", cascade="all, delete-orphan"
    )
    proposals: Mapped[List["Proposal"]] = relationship(
        "Proposal", back_populates="tender", cascade="all, delete-orphan"
    )

