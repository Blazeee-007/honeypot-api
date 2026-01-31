from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Intelligence(BaseModel):
    upi_ids: List[str] = Field(default_factory=list)
    bank_accounts: List[str] = Field(default_factory=list)
    phishing_links: List[str] = Field(default_factory=list)

class EngageRequest(BaseModel):
    conversation_id: str
    incoming_message: str
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class EngageResponse(BaseModel):
    status: str
    is_scam: bool
    response_text: str
    intelligence: Intelligence
