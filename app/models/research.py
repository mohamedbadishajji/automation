from datetime import datetime, timezone
from typing import Optional, List, Any, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tender import Tender


class ProspectResearch(Base):
    __tablename__ = "prospect_research"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), unique=True, nullable=False)

    # Research findings
    sector: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    estimated_revenue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    key_partners: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)  # e.g. ["AWS", "Microsoft"]
    domain_requirements: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)  # e.g. ["ISO 27001", "GDPR"]

    # Bonus points features support
    competitor_insights: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    estimated_budget_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    raw_research_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    tender: Mapped["Tender"] = relationship("Tender", back_populates="research")