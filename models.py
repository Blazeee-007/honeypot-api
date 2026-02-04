from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union

# --- Internal Intelligence Model ---
class Intelligence(BaseModel):
    upi_ids: List[str] = Field(default_factory=list)
    bank_accounts: List[str] = Field(default_factory=list)
    phishing_links: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    suspicious_keywords: List[str] = Field(default_factory=list)

# --- Incoming Request Models ---

class MessageContent(BaseModel):
    sender: str
    text: str
    timestamp: Optional[int] = None

class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None

class EngageRequest(BaseModel):
    sessionId: str
    message: MessageContent
    conversationHistory: List[Union[Dict[str, Any], MessageContent]] = Field(default_factory=list)
    metadata: Optional[Metadata] = None

# --- Outgoing Response Models ---

class EngageResponse(BaseModel):
    status: str = "success"
    reply: str

