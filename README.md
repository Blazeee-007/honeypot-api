# 👵 Agentic HoneyPot for Scam Detection

Participants must design an autonomous AI honeypot system that detects scam messages and actively engages scammers using a believable persona. Once a scam is detected, the AI agent must continue the conversation to extract bank account details, UPI IDs, and phishing links. Interactions will be simulated using a Mock Scammer API, and outputs must be returned in a structured JSON format.

## 🚀 Features
- **Persona-Driven Engagement**: Uses a "Martha" persona (74 years old) with realistic typing flaws and human-like delays.
- **Scam Localization**: Automatically detects typical scam indicators (urgency, prize bait, kyc fraud).
- **Intelligence Extraction**: Uses advanced regex to pull payment details and malicious URLs from conversation text.
- **Persistence Layer**: All detected scams and extracted data are stored in a SQLite database.
- **Production Ready**: Includes CORS, structured logging, Pydantic-based configuration, and API Key security.

## 🛠 Tech Stack
- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy**: Database toolkit for persisting intel.
- **OpenAI/LangChain**: Powers the cognitive engine (Martha).
- **Pydantic Settings**: Industry-standard configuration management.

## 📂 API Endpoints
- `POST /v1/honeypot/engage`: Send messages to the agent; returns persona response and extracted intel.
- `GET /v1/honeypot/intelligence`: Dashboard endpoint to retrieve all collected scam intelligence.
- `GET /`: Health check.

## ⚙️ Configuration
Create a `.env` file from the following template:
```env
HONEYPOT_API_KEY=your-secret-key
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./honeypot.db
```

## 🧪 Validation Testing
This Honeypot API Endpoint Tester (`tester.py`) allows participants to validate whether their deployed honeypot service is reachable, secured, and responding correctly. The tester verifies authentication, endpoint availability, and response behavior using a simple request.

### What This Tests:
- **API Authentication** using headers (`X-API-KEY`).
- **Endpoint Availability** and connectivity.
- **Proper Request Handling** with Pydantic validation.
- **Response Structure** and status codes.
- **Basic Honeypot Behavior** validation (Scam detection & extraction).

> **Note:** This tester is for validation only. The final evaluation will involve automated security interaction scenarios.

### How to Run the Tester:
```bash
# Test Local
python tester.py http://localhost:8000 agentic-honeypot-secret-key

# Test Deployed (Render)
python tester.py https://honeypot-api-cg90.onrender.com agentic-honeypot-secret-key
```
