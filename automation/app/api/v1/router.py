from fastapi import APIRouter
from app.api.v1.endpoints import tenders, research, assets, proposals

api_router = APIRouter()

api_router.include_router(tenders.router, prefix="/tenders", tags=["Tenders / RFPs"])
api_router.include_router(research.router, tags=["Agentic Prospect Research"])
api_router.include_router(assets.router, tags=["Internal Assets & RAG Matching"])
api_router.include_router(proposals.router, tags=["Commercial Proposals & Deck Generation"])