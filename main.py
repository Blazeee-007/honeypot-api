from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from models import EngageRequest, EngageResponse
from typing import Dict, Any
from auth import get_api_key
from agent import HoneyPotAgent
import uvicorn
import logging
import time

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="An autonomous AI agent for scam detection and scambaiting.",
    version="1.0.0"
)

# Enable CORS (Critical for frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In strict production, replace with your dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = HoneyPotAgent()

from database import init_db, get_db, Interaction
from sqlalchemy.orm import Session
from config import settings

# Initialize DB on start
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized.")

@app.get("/", tags=["Health Check"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

@app.post("/v1/honeypot/engage", response_model=EngageResponse, tags=["Agent Logic"])
async def engage(
    payload: Dict[str, Any] = Body(...),
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Engages with a potential scammer, classifies the intent, 
    and extracts intelligence. Saves interaction to DB.
    Accepts generic JSON to support various tester formats.
    """
    # Flexible Extraction Logic
    incoming_message = (
        payload.get("incoming_message") or 
        payload.get("text") or 
        payload.get("message") or 
        payload.get("content") or 
        payload.get("input") or
        payload.get("prompt")
    )
    
    conversation_id = payload.get("conversation_id", "unknown")
    history = payload.get("history", [])

    if not incoming_message:
        # If we still can't find it, dump the keys to help user debug (in logs)
        print(f"DEBUG: Failed to find message in payload keys: {list(payload.keys())}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not find a valid message field in request. Tried: incoming_message, text, message, content, input"
        )

    logger.info(f"Incoming engagement: conv_id={conversation_id}")
    start_time = time.time()
    
    try:
        is_scam, response_text, intelligence, delay = await agent.engage(
            incoming_message, 
            history
        )
        process_time = time.time() - start_time
        
        # Save to Database for persistence (The "Production" way)
        db_interaction = Interaction(
            id=f"{conversation_id}_{int(time.time())}",
            incoming_message=incoming_message,
            response_text=response_text,
            is_scam=is_scam,
            upi_ids=intelligence.upi_ids,
            bank_accounts=intelligence.bank_accounts,
            phishing_links=intelligence.phishing_links,
            suggested_delay=delay,
            metadata_json={"process_time": f"{process_time:.2f}s"}
        )
        db.add(db_interaction)
        db.commit()

        logger.info(f"Engagement processed: is_scam={is_scam}, duration={process_time:.2f}s")
        
        return EngageResponse(
            status="success",
            is_scam=is_scam,
            response_text=response_text,
            intelligence=intelligence,
            suggested_delay_seconds=delay
        )
    except Exception as e:
        logger.error(f"Error in engagement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred."
        )

@app.get("/v1/honeypot/engage", tags=["Help"])
async def engage_browser_check():
    """
    Helper endpoint for browser-based validation.
    """
    return {
        "status": "ready",
        "message": "The Honeypot API is live! Send a POST request to this endpoint to engage the agent.",
        "usage_example": {
            "method": "POST",
            "headers": {"X-API-KEY": "your-key", "Content-Type": "application/json"},
            "body": {"incoming_message": "Hello"}
        }
    }

@app.get("/v1/honeypot/intelligence", tags=["Intelligence"])
async def get_intelligence(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Retrieve all extracted intelligence from suspected scammers.
    """
    scams = db.query(Interaction).filter(Interaction.is_scam == True).all()
    return {
        "total_scams_detected": len(scams),
        "reports": [
            {
                "id": s.id,
                "timestamp": s.timestamp,
                "upi_ids": s.upi_ids,
                "bank_accounts": s.bank_accounts,
                "phishing_links": s.phishing_links
            } for s in scams
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
