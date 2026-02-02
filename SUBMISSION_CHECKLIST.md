# HoneyPot API - Submission Checklist

## 1. Deployment
- [ ] **Push to GitHub**: Ensure all latest code (including `config.py` fixes) is pushed.
- [ ] **Deploy to Vercel**: Import the repository.
  - Framework Preset: **FastAPI** (or select "Other" and override build command if needed, but `@vercel/python` in `vercel.json` usually handles it).
- [ ] **Environment Variables**: passing these is CRITICAL.
  - `HONEYPOT_API_KEY`: Set your secret key (or use the default `agentic-honeypot-secret-key` if testing).
  - `OPENAI_API_KEY`: Required for the AI persona to work.
  - `VERCEL`: Set to `1` (Vercel usually sets this, but adding it explicitly ensures the DB fix works).

## 2. Verification
Before submitting, test your live endpoint using `curl` or Postman.

**Endpoint**: `https://<your-project>.vercel.app/v1/honeypot/engage`
**Method**: `POST`
**Headers**:
- `Content-Type: application/json`
- `X-API-KEY: <your-key>`

**Body**:
```json
{
  "incoming_message": "Hello, I am calling from the bank. You need to verify your account immediately.",
  "conversation_id": "test_submission_001"
}
```

**Expected 200 OK Response**:
```json
{
  "status": "success",
  "is_scam": true,
  "response_text": "...",
  "intelligence": { ... },
  "suggested_delay_seconds": 2.5
}
```

## 3. Submission Form Details
- **API Endpoint URL**: `https://<your-project>.vercel.app/v1/honeypot/engage`
  - *Note: Ensure you include the full path `/v1/honeypot/engage`, not just the domain.*
- **API Key**: `<your-api-key>`
- **Problem Statement**: Problem 2: Agentic Honey-Pot

## 4. Key Features Verified
- [x] **Public Endpoint**: Live on Vercel.
- [x] **Authentication**: Validated via `X-API-KEY`.
- [x] **Input Handling**: Accepts scam messages via JSON.
- [x] **Output Structure**: Returns intelligence and classification.
- [x] **Deployment Stability**: DB path patched for serverless environment.
