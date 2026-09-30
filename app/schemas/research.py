from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator

class ProspectResearchBase(BaseModel):
    sector: Optional[str] = None
    estimated_revenue: Optional[str] = None
    key_partners: Optional[List[str]] = []
    domain_requirements: Optional[List[str]] = []
    competitor_insights: Optional[Dict[str, Any]] = None
    estimated_budget_range: Optional[str] = None
    raw_research_notes: Optional[str] = None

    @field_validator("key_partners", "domain_requirements", mode="before")
    @classmethod
    def parse_string_to_list(cls, value: Any) -> List[str]:
        """Auto-converts comma-separated strings from n8n into clean Python lists."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value or []

class ProspectResearchCreate(ProspectResearchBase):
    pass

class ProspectResearchResponse(ProspectResearchBase):
    id: int
    tender_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)