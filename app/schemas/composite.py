from typing import Optional, List
from app.schemas.tender import TenderResponse
from app.schemas.research import ProspectResearchResponse
from app.schemas.asset import TenderAssetMatchResponse
from app.schemas.proposal import ProposalResponse

class TenderDetailResponse(TenderResponse):
    research: Optional[ProspectResearchResponse] = None
    asset_matches: List[TenderAssetMatchResponse] = []
    proposals: List[ProposalResponse] = []