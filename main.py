"""
Participants must design an autonomous AI honeypot system that detects scam messages and actively engages scammers using a believable persona. Once a scam is detected, the AI agent must continue the conversation to extract bank account details, UPI IDs, and phishing links. Interactions will be simulated using a Mock Scammer API, and outputs must be returned in a structured JSON format.
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from models import EngageRequest, EngageResponse
from auth import get_api_key
from agent import HoneyPotAgent
import uvicorn
import logging
import time
import requests
from typing import List, Dict, Any

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
    allow_origins=["*"], 
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
# Initialize DB on start
@app.on_event("startup")
def startup_event():
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


def send_guvi_callback(session_id: str, db: Session):
    """
    Aggregates intelligence for the session and sends the mandatory callback.
    """
    try:
        # 1. Aggregate Intelligence from DB
        interactions = db.query(Interaction).filter(Interaction.id.like(f"{session_id}%")).all()
        
        if not interactions:
            return

        aggregated_intel = {
            "bankAccounts": set(),
            "upiIds": set(),
            "phishingLinks": set(),
            "phoneNumbers": set(),
            "suspiciousKeywords": set()
        }
        
        scam_detected = False
        total_messages = len(interactions) * 2 # Crude approximation (User + Agent) or just count rows? Input says "Total messages exchanged". 
        # Better: use conversationHistory length from the last request + 2 (latest exchange). 
        # But we only have DB rows here. Let's start with rows count (each row is one turn).
        
        for i in interactions:
            if i.is_scam:
                scam_detected = True
            
            # Safely add to sets (handle internal lists)
            if i.bank_accounts: aggregated_intel["bankAccounts"].update(i.bank_accounts)
            if i.upi_ids: aggregated_intel["upiIds"].update(i.upi_ids)
            if i.phishing_links: aggregated_intel["phishingLinks"].update(i.phishing_links)
            if i.phone_numbers: aggregated_intel["phoneNumbers"].update(i.phone_numbers)
            if i.suspicious_keywords: aggregated_intel["suspiciousKeywords"].update(i.suspicious_keywords)

        # 2. Construct Payload
        # Convert sets to lists
        final_intel = {k: list(v) for k, v in aggregated_intel.items()}
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages, 
            "extractedIntelligence": final_intel,
            "agentNotes": "Scam detected via heuristics and conversation analysis." if scam_detected else "Ongoing conversation."
        }
        
        if scam_detected:
            # 3. Send Request
            url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
            # Using a very short timeout to not block if this was sync, but it's async so we can be generous
            response = requests.post(url, json=payload, timeout=10)
            logger.info(f"Callback sent for {session_id}. Status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Failed to send callback for {session_id}: {e}")

@app.get("/", tags=["Health Check"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }

@app.post("/v1/honeypot/engage", tags=["Agent Logic"])
async def engage(
    request: Request,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Main endpoint for the Honeypot. 
    Accepts flexible input but prioritizes the Hackathon Spec.
    """
    from fastapi.responses import JSONResponse
    
    # 0. Robust definition of payload
    try:
        # Check content type specifically to handle potential edge cases
        content_type = request.headers.get('content-type', '').lower()
        if 'application/json' in content_type:
            payload = await request.json()
        elif not await request.body():
            payload = {}
        else:
            # Try parsing anyway for text/plain
            try:
                payload = await request.json()
            except:
                payload = {}
                
    except Exception as e:
        logger.warning(f"Failed to parse JSON body: {e}")
        payload = {}

    # Handle if payload is a list (some testers send [msg1, msg2])
    if isinstance(payload, list):
        if payload:
            payload = payload[-1] # Take the last item
        else:
            payload = {}
            
    if not isinstance(payload, dict):
        payload = {}

    # 1. robust extraction of Session ID
    session_id = payload.get("sessionId") or payload.get("conversation_id") or f"gen-{int(time.time())}"
    
    # 2. Robust extraction of text
    raw_message = payload.get("message")
    incoming_text = ""
    sender = "scammer" # default
    
    if isinstance(raw_message, dict):
        incoming_text = raw_message.get("text", "")
        sender = raw_message.get("sender", "scammer")
    elif isinstance(raw_message, str):
        incoming_text = raw_message
    
    # Fallback
    if not incoming_text:
        incoming_text = (
            payload.get("text") or 
            payload.get("incoming_message") or 
            payload.get("content") or 
            ""
        )

    # 3. Conversation History
    history = payload.get("conversationHistory") or payload.get("history") or []
    
    logger.info(f"Incoming engagement: session={session_id}")
    start_time = time.time()
    
    try:
        # Engage Agent
        is_scam, reply_text, intelligence, delay = await agent.engage(
            incoming_text, 
            history
        )
        process_time = time.time() - start_time
        
        # unique id for this interaction
        interaction_id = f"{session_id}_{int(time.time() * 1000)}"
        
        # Save to Database (Safe Mode)
        try:
            db_interaction = Interaction(
                id=interaction_id,
                incoming_message=incoming_text,
                response_text=reply_text,
                is_scam=is_scam,
                upi_ids=intelligence.upi_ids,
                bank_accounts=intelligence.bank_accounts,
                phishing_links=intelligence.phishing_links,
                phone_numbers=intelligence.phone_numbers,
                suspicious_keywords=intelligence.suspicious_keywords,
                suggested_delay=delay,
                metadata_json={"process_time": f"{process_time:.2f}s", "sender": sender}
            )
            db.add(db_interaction)
            db.commit()

            # Trigger Callback if Scam Detected
            if is_scam:
                 background_tasks.add_task(send_guvi_callback, session_id, db)
        except Exception as db_err:
            logger.error(f"Database persistence failed (continuing anyway): {db_err}")
        
        return JSONResponse(content={
            "status": "success",
            "reply": reply_text
        })

    except Exception as e:
        logger.error(f"Error in engagement: {str(e)}")
        # Return a safe fallback error to keep protocol alive
        return JSONResponse(content={
            "status": "success",
            "reply": "I am having trouble hearing you, could you repeat that?"
        })

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
                "phishing_links": s.phishing_links,
                "phone_numbers": s.phone_numbers,
                "suspicious_keywords": s.suspicious_keywords
            } for s in scams
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

