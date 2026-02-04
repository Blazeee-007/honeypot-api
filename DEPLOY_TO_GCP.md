# Deploying HoneyPot API to Google Cloud Run

**Cloud Run** is the best way to host this API on Google Cloud. It is serverless, auto-scales, and you only pay for what you use.

## Prerequisites

1.  **Google Cloud SDK**: Ensure you have the [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed.
2.  **GCP Project**: You need an active Google Cloud Project with billing enabled.

## Deployment Steps

Open your terminal in this folder (`c:\Users\saisa\Desktop\honeypot-api`) and run the following commands:

### 1. Login to Google Cloud
```powershell
gcloud auth login
```

### 2. Set your Project ID
Replace `YOUR_PROJECT_ID` with your actual GCP project ID:
```powershell
gcloud config set project YOUR_PROJECT_ID
```

### 3. Deploy to Cloud Run
Run this single command to build and deploy your container:

```powershell
gcloud run deploy honeypot-api --source .
```

You will be asked a few questions:
-   **Source code location**: Press Enter (current directory).
-   **Region**: Choose a region near you (e.g., `asia-south1` for Mumbai, or `us-central1`).
-   **Allow unauthenticated invocations?**: Type **`y`** (Yes). *This is crucial so the Hackathon platform can reach your API.*

### 4. Get your URL
Once finished, it will print a URL ending in `.run.app`.

Example: `https://honeypot-api-xyz123-uc.a.run.app`

### 5. Test your Deployment
Use that URL in the `tester.py` script or submit it to the hackathon portal.
(Remember to verify if you need to append `/v1/honeypot/engage` path depending on the submission form, but usually, they ask for the base URL or the specific endpoint).

## Troubleshooting
-   **Build fails?** Check the logs provided in the terminal link.
-   **503 Service Unavailable?** Wait a moment, or check the "Logs" tab in the Cloud Run console for Python errors.
