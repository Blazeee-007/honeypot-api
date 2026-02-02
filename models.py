from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Any

class Intelligence(BaseModel):
    upi_ids: List[str] = Field(default_factory=list)
    bank_accounts: List[str] = Field(default_factory=list)
    phishing_links: List[str] = Field(default_factory=list)

class EngageRequest(BaseModel):
    conversation_id: Optional[str] = Field(default="unknown")
    incoming_message: Optional[str] = None
    
    # Flexible input fields to handle different tester formats
    text: Optional[str] = None
    message: Optional[str] = None
    content: Optional[str] = None
    
    history: Optional[List[Any]] = Field(default_factory=list)

    @model_validator(mode='after')
    def consolidate_message(self):
        # If incoming_message is missing, try to find it in other common fields
        if not self.incoming_message:
            self.incoming_message = self.text or self.message or self.content
            
        if not self.incoming_message:
            # Fallback for strict validation
            raise ValueError("Request must contain a message field ('incoming_message', 'message', 'text', or 'content')")
        return self

class EngageResponse(BaseModel):
    status: str
    is_scam: bool
    response_text: str
    intelligence: Intelligence
    suggested_delay_seconds: float
