from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class MatchingProject(BaseModel):
    project_id: str
    title: str
    similarity: float
    sector: str
    technologies: List[str]

class MatchingCandidate(BaseModel):
    cv_id: str
    role: str
    skills: List[str]
    experience_years: int

class MatchingReference(BaseModel):
    project_id: str
    sector: str
    year: int

class RAGPayload(BaseModel):
    matching_projects: List[MatchingProject] = []
    matching_candidates: List[MatchingCandidate] = []
    matching_references: List[MatchingReference] = []

class ProposalCreate(BaseModel):
    content_json: Dict[str, Any]
    coverage_score_matrix: Optional[Dict[str, Any]] = None
    rag_matches: Optional[RAGPayload] = None
    file_path_pptx: Optional[str] = None
    file_path_pdf: Optional[str] = None

class ProposalUpdate(BaseModel):
    content_json: Optional[Dict[str, Any]] = None
    rag_matches: Optional[RAGPayload] = None
    file_path_pptx: Optional[str] = None
    file_path_pdf: Optional[str] = None

class ProposalResponse(BaseModel):
    id: int
    tender_id: int
    version: int
    content_json: Dict[str, Any]
    coverage_score_matrix: Optional[Dict[str, Any]] = None
    rag_matches: Optional[Dict[str, Any]] = None
    file_path_pptx: Optional[str] = None
    file_path_pdf: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)