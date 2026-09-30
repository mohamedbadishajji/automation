from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tender import Tender


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Structured JSON for slide sections (editable by Human-in-the-Loop feature)
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    rag_matches: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Requirements coverage matrix (Bonus feature: scores technical coverage against RFP)
    coverage_score_matrix: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # File export paths
    file_path_pptx: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=datetime.utcnow)

    tender: Mapped["Tender"] = relationship("Tender", back_populates="proposals")