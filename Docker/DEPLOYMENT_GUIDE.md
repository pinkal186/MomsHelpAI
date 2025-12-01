# 🚀 MomsHelperAI - Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying MomsHelperAI to various platforms. The application can be deployed locally, on Google Cloud Platform (Cloud Run or Vertex AI), or on other cloud providers.

---

## 🎯 Project Architecture Summary

**MomsHelperAI** is a multi-agent AI system built with:
- **Framework**: Google Agent Development Kit (ADK)
- **LLM**: Gemini 2.0 Flash / Gemini 2.5 Flash Lite
- **Backend**: Python 3.10+ with Flask REST API
- **Storage**: SQLite (local) or Firestore (cloud)
- **Vector Store**: ChromaDB (optional, for preferences)

**Agent Flow**:
```
User Request → Orchestrator Agent
  ↓
├─→ Meal Planner Agent (uses Google Search)
├─→ Week Planner Agent (schedules meals + activities)
└─→ Grocery Planner Agent (creates shopping list)
  ↓
Combined Response to User
```

---

## 📦 Prerequisites

### Required
- Python 3.10 or higher
- Google API Key (for Gemini)
- Git

### Optional (for cloud deployment)
- Google Cloud Platform account
- Docker Desktop
- gcloud CLI

---

## 🏠 Local Deployment (Development)

### Step 1: Clone Repository

```bash
git clone https://github.com/pinkal186/MomsHelpAI.git
cd MomsHelperAI
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
GOOGLE_API_KEY=your_gemini_api_key_here
PROJECT_ID=momshelper-ai
REGION=us-central1
DEBUG=True

# Optional: Firestore configuration (if using cloud storage)
# FIRESTORE_DATABASE=(default)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Optional: ChromaDB configuration
# CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

**Get Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env` file

### Step 5: Initialize Database

The SQLite database will be created automatically on first run, but you can initialize it manually:

```bash
python -c "from storage.sqlite_storage import SQLiteStorage; SQLiteStorage().initialize()"
```

### Step 6: Run the Application

**Option A: CLI Application (Interactive)**
```bash
python main.py
```

**Option B: REST API Server (Flask)**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Step 7: Test the Application

**CLI Test:**
```
You: Plan meals for this week
```

**API Test:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan meals for this week",
    "family_id": "sharma_001"
  }'
```

---

## 🐳 Docker Deployment

### Step 1: Create Dockerfile

A `Dockerfile` has been created in the project root (see below).

### Step 2: Create .dockerignore

A `.dockerignore` file has been created to exclude unnecessary files.

### Step 3: Build Docker Image

```bash
docker build -t momshelper-ai:latest .
```

### Step 4: Run Docker Container

**For CLI Mode:**
```bash
docker run -it --rm \
  -e GOOGLE_API_KEY=your_api_key_here \
  momshelper-ai:latest python main.py
```

**For API Server:**
```bash
docker run -d -p 5000:5000 \
  -e GOOGLE_API_KEY=your_api_key_here \
  --name momshelper-api \
  momshelper-ai:latest
```

Access at `http://localhost:5000`

### Step 5: Stop and Remove Container

```bash
docker stop momshelper-api
docker rm momshelper-api
```

---

## ☁️ Google Cloud Run Deployment

### Prerequisites

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 1: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Create Secret for API Key

```bash
# Create secret
echo -n "your_gemini_api_key_here" | \
  gcloud secrets create gemini-api-key --data-file=-

# Verify
gcloud secrets versions access latest --secret=gemini-api-key
```

### Step 3: Build and Deploy to Cloud Run

**Option A: Using gcloud (Recommended)**

```bash
# Build and deploy in one command
gcloud run deploy momshelper-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=GOOGLE_API_KEY=gemini-api-key:latest \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

**Option B: Using Docker + gcloud**

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/momshelper-ai

# 2. Deploy to Cloud Run
gcloud run deploy momshelper-ai \
  --image gcr.io/YOUR_PROJECT_ID/momshelper-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets=GOOGLE_API_KEY=gemini-api-key:latest \
  --memory 512Mi \
  --cpu 1
```

### Step 4: Get Service URL

```bash
gcloud run services describe momshelper-ai \
  --platform managed \
  --region us-central1 \
  --format='value(status.url)'
```

### Step 5: Test Deployed API

```bash
CLOUD_RUN_URL=$(gcloud run services describe momshelper-ai --region us-central1 --format='value(status.url)')

curl -X POST $CLOUD_RUN_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Plan meals for this week",
    "family_id": "sharma_001"
  }'
```

---

## 🤖 Vertex AI Agent Engine Deployment

### Prerequisites

```bash
gcloud services enable aiplatform.googleapis.com
```

### Step 1: Create Agent Configuration

Create `agent_config.yaml`:

```yaml
agents:
  - name: momshelper-orchestrator
    display_name: "MomsHelper Orchestrator"
    model: gemini-2.0-flash-exp
    description: "Orchestrates meal planning, scheduling, and grocery list generation"
    tools:
      - name: meal_planner
        type: function
      - name: week_planner
        type: function
      - name: grocery_planner
        type: function
```

### Step 2: Deploy Agent

```bash
# Using ADK CLI (if available)
adk deploy agent_config.yaml \
  --project=YOUR_PROJECT_ID \
  --region=us-central1

# Or using gcloud
gcloud ai-platform agents create momshelper-orchestrator \
  --region=us-central1 \
  --config=agent_config.yaml
```

### Step 3: Test Agent

```bash
gcloud ai-platform agents query momshelper-orchestrator \
  --region=us-central1 \
  --query="Plan meals for this week"
```

---

## 🌐 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | `AIzaSy...` |
| `PROJECT_ID` | GCP project ID | `momshelper-ai` |
| `REGION` | GCP region | `us-central1` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `FIRESTORE_DATABASE` | Firestore database name | `(default)` |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | `./data/chroma_db` |
| `PORT` | Server port | `5000` |

---

## 🔒 Security Considerations

### 1. API Key Protection

**❌ Don't:**
- Commit `.env` file to Git
- Hardcode API keys in code
- Share API keys publicly

**✅ Do:**
- Use environment variables
- Use Google Secret Manager for production
- Add `.env` to `.gitignore`

### 2. Production Deployment

```bash
# Use service account instead of API key
gcloud run deploy momshelper-ai \
  --service-account=momshelper-sa@PROJECT_ID.iam.gserviceaccount.com \
  --no-allow-unauthenticated
```

### 3. Rate Limiting

Add to `app.py`:
```python
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per hour"])
```

---

## 📊 Monitoring & Logging

### Cloud Run Logs

```bash
# View logs
gcloud run services logs read momshelper-ai \
  --region=us-central1 \
  --limit=50

# Stream logs
gcloud run services logs tail momshelper-ai \
  --region=us-central1
```

### Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime-checks create momshelper-health \
  --resource-type=uptime-url \
  --host=YOUR_CLOUD_RUN_URL \
  --path=/health
```

---

## 💰 Cost Estimation

### Local Development
- **Cost**: $0 (free)
- **API Usage**: Pay per Gemini API call (~$0.001/request)

### Cloud Run (Production)
| Resource | Usage | Monthly Cost |
|----------|-------|--------------|
| CPU | 1 vCPU @ 1% avg | $0.50 |
| Memory | 512 MB | $0.25 |
| Requests | 10K/month | $0.00 |
| Gemini API | 10K requests | $20-40 |
| **Total** | | **~$21-41/month** |

### Vertex AI Agent Engine
| Resource | Usage | Monthly Cost |
|----------|-------|--------------|
| Agent Engine | 10K requests | $15-30 |
| Gemini API | 10K requests | $20-40 |
| **Total** | | **~$35-70/month** |

---

## 🛠️ Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "API key not found"

**Solution:**
```bash
# Check .env file exists
cat .env

# Verify API key is loaded
python -c "from utils.config import Config; print(Config.GOOGLE_API_KEY[:10])"
```

### Issue: Database not initialized

**Solution:**
```bash
python -c "from storage.sqlite_storage import SQLiteStorage; SQLiteStorage().initialize()"
```

### Issue: Docker container won't start

**Solution:**
```bash
# Check logs
docker logs momshelper-api

# Run interactively to debug
docker run -it --rm momshelper-ai:latest /bin/bash
```

### Issue: Cloud Run deployment fails

**Solution:**
```bash
# Check Cloud Build logs
gcloud builds list --limit=1

# View build details
gcloud builds describe BUILD_ID
```

---

## 🔄 Update & Redeploy

### Local Development

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python app.py
```

### Cloud Run

```bash
# Option 1: Automatic build from source
gcloud run deploy momshelper-ai --source .

# Option 2: Build new image and deploy
docker build -t gcr.io/PROJECT_ID/momshelper-ai:v2 .
docker push gcr.io/PROJECT_ID/momshelper-ai:v2
gcloud run deploy momshelper-ai --image gcr.io/PROJECT_ID/momshelper-ai:v2
```

---

## 📝 API Endpoints Reference

### Health Check
```bash
GET /health
```

### Chat (Main Endpoint)
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Plan meals for this week",
  "family_id": "sharma_001",
  "session_id": "optional-session-id"
}
```

### List Families
```bash
GET /api/families
```

### Plan Meals
```bash
POST /api/meal-plan
Content-Type: application/json

{
  "family_id": "sharma_001",
  "start_date": "2025-12-02",
  "days": 7,
  "preferences": "quick meals"
}
```

### Create Shopping List
```bash
POST /api/shopping-list
Content-Type: application/json

{
  "family_id": "sharma_001",
  "recipes": ["Poha", "Dal Tadka"]
}
```

### Plan Schedule
```bash
POST /api/schedule
Content-Type: application/json

{
  "family_id": "sharma_001",
  "start_date": "2025-12-02",
  "special_events": ["Birthday on Wednesday"]
}
```

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] API key configured in `.env`
- [ ] Dependencies installed (`requirements.txt`)
- [ ] Database initialized (SQLite/Firestore)
- [ ] All tests passing
- [ ] `.env` added to `.gitignore`

### Local Deployment
- [ ] Virtual environment activated
- [ ] Application runs without errors
- [ ] API endpoints respond correctly
- [ ] Sample data loads successfully

### Docker Deployment
- [ ] Dockerfile created
- [ ] `.dockerignore` configured
- [ ] Docker image builds successfully
- [ ] Container runs and responds to requests

### Cloud Run Deployment
- [ ] GCP project created
- [ ] APIs enabled (Cloud Run, Cloud Build, Secret Manager)
- [ ] API key stored in Secret Manager
- [ ] Service deployed successfully
- [ ] Health check passes
- [ ] API endpoints accessible publicly

### Production Readiness
- [ ] Environment variables secured
- [ ] Logging enabled
- [ ] Monitoring configured
- [ ] Error handling implemented
- [ ] Rate limiting enabled
- [ ] Documentation updated

---

## 🆘 Support & Resources

### Documentation
- [MomsHelperAI README](README.md)
- [Technical Architecture](TECHNICAL_ARCHITECTURE.md)
- [Google ADK Docs](https://google.github.io/adk-docs/)

### API Keys
- [Get Gemini API Key](https://makersuite.google.com/app/apikey)
- [Google Cloud Console](https://console.cloud.google.com)

### Community
- GitHub Issues: [Report bugs](https://github.com/pinkal186/MomsHelpAI/issues)
- Contact: pinkal186@gmail.com

---

## 📄 License

This project is built for the Kaggle Google AI Agents Capstone competition.

---

**Document Version:** 1.0  
**Last Updated:** December 1, 2025  
**Author:** Pinkal  
**Status:** ✅ Production Ready
