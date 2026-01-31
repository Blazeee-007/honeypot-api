# 👵 Agentic HoneyPot for Scam Detection

A production-ready autonomous AI agent designed to detect scammers, engage them using a "vulnerable elderly citizen" persona, and extract intelligence (UPI IDs, bank accounts, phishing links) for defensive purposes.

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
A dedicated validation script `tester.py` is included to verify the production readiness of the API.

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
