# MedAssist RAG - Deployment Guide

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vercel        │────▶│   Railway/      │────▶│   Pinecone      │
│   (Frontend)    │     │   Render (API)  │     │   (Vectors)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                        ┌──────┴──────┐
                        │             │
                   ┌────▼────┐   ┌────▼────┐
                   │PostgreSQL│   │  Redis  │
                   └──────────┘   └─────────┘
```

## Quick Deploy Options

### Option 1: Vercel + Railway (Recommended)

**Frontend → Vercel** | **Backend → Railway**

### Option 2: Vercel + Render

**Frontend → Vercel** | **Backend → Render**

---

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - MedAssist RAG"

# Add remote (replace with your repo)
git remote add origin https://github.com/YOUR_USERNAME/medassist-rag.git

# Push
git push -u origin main
```

### 1.2 Required Environment Variables

Create these secrets in your deployment platforms:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `PINECONE_API_KEY` | Pinecone API key | ✅ |
| `PINECONE_INDEX_NAME` | Pinecone index name | ✅ |
| `SECRET_KEY` | 64+ char random string | ✅ |
| `DATABASE_URL` | PostgreSQL connection URL | ✅ |
| `REDIS_URL` | Redis connection URL | Optional |
| `ALLOWED_ORIGINS` | Frontend URL(s) | ✅ |

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import your `medassist-rag` repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)

### 2.2 Set Environment Variables

In Vercel Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL = https://your-backend-url.railway.app
```

### 2.3 Deploy

Click **Deploy**. Vercel will automatically:
- Install dependencies
- Build the Next.js app
- Deploy to their CDN

Your frontend will be live at: `https://your-project.vercel.app`

---

## Step 3: Deploy Backend

### Option A: Railway (Recommended)

#### 3A.1 Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your repository
4. Set **Root Directory**: `backend`

#### 3A.2 Add Services

In your Railway project, add:

1. **PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   
2. **Redis** (optional but recommended)
   - Click "New" → "Database" → "Redis"

#### 3A.3 Set Environment Variables

In Railway → Variables:

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<your-64-char-secret>
OPENAI_API_KEY=<your-openai-key>
PINECONE_API_KEY=<your-pinecone-key>
PINECONE_INDEX_NAME=medassist
ALLOWED_ORIGINS=https://your-project.vercel.app
ENABLE_AUDIT_LOG=true
ENABLE_DEMO_MODE=false

# These are auto-populated by Railway:
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

#### 3A.4 Deploy

Railway will automatically deploy. Your API will be at:
`https://medassist-backend-production.up.railway.app`

---

### Option B: Render

#### 3B.1 One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Or manually:

1. Go to [render.com](https://render.com) and sign in
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will use `render.yaml` to create all services

#### 3B.2 Set Secret Environment Variables

In Render Dashboard, set for each service:

```bash
OPENAI_API_KEY=<your-key>
PINECONE_API_KEY=<your-key>
ALLOWED_ORIGINS=https://your-project.vercel.app
```

---

## Step 4: Connect Frontend to Backend

### 4.1 Update Vercel Environment Variable

Once backend is deployed, update Vercel:

```
NEXT_PUBLIC_API_URL = https://your-backend-url.railway.app
```

### 4.2 Update Backend CORS

In your backend environment variables:

```
ALLOWED_ORIGINS=https://your-project.vercel.app,https://www.your-domain.com
```

### 4.3 Redeploy Both

Trigger a redeploy on both Vercel and Railway/Render.

---

## Step 5: Set Up Pinecone

### 5.1 Create Index

1. Go to [pinecone.io](https://pinecone.io) console
2. Create a new index:
   - **Name**: `medassist`
   - **Dimensions**: `1536` (for text-embedding-3-small)
   - **Metric**: `cosine`
   - **Cloud**: AWS
   - **Region**: us-east-1

### 5.2 Seed Data

After backend is deployed, seed the vector database:

```bash
# SSH into Railway or use Render Shell
cd backend
python scripts/seed_vector_db.py
```

Or run locally pointing to production:
```bash
export PINECONE_API_KEY=your-production-key
export OPENAI_API_KEY=your-key
export USE_CHROMA=false
python scripts/seed_vector_db.py
```

---

## Step 6: GitHub Actions (CI/CD)

### 6.1 Add GitHub Secrets

Go to GitHub → Repository → Settings → Secrets → Actions:

```
VERCEL_TOKEN        # From Vercel Account Settings
VERCEL_ORG_ID       # From Vercel Project Settings
VERCEL_PROJECT_ID   # From Vercel Project Settings
RAILWAY_TOKEN       # From Railway Account Settings (optional)
OPENAI_API_KEY      # For running tests
```

### 6.2 Get Vercel Tokens

```bash
# Install Vercel CLI
npm i -g vercel

# Login and link project
cd frontend
vercel link

# Get IDs from .vercel/project.json
cat .vercel/project.json
```

---

## Custom Domain Setup

### Vercel (Frontend)

1. Go to Vercel → Project → Settings → Domains
2. Add your domain: `app.yourdomain.com`
3. Update DNS with provided records

### Railway (Backend)

1. Go to Railway → Service → Settings → Networking
2. Add custom domain: `api.yourdomain.com`
3. Update DNS with provided records

---

## Monitoring & Logs

### Vercel
- Real-time logs: Vercel Dashboard → Deployments → Functions
- Analytics: Vercel Dashboard → Analytics

### Railway
- Logs: Railway Dashboard → Service → Logs
- Metrics: Railway Dashboard → Service → Metrics

### Application Logs
- Audit logs are stored in `logs/audit_YYYY-MM-DD.log`
- Configure external logging (e.g., Datadog, Logflare) for production

---

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `ALLOWED_ORIGINS` includes your frontend URL
   - Include both `https://` and `www.` versions

2. **Database Connection Failed**
   - Check `DATABASE_URL` is correctly set
   - Ensure database is in same region as backend

3. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is valid
   - Check API quota/billing

4. **Pinecone Connection Failed**
   - Verify `PINECONE_API_KEY` and `PINECONE_INDEX_NAME`
   - Ensure index has correct dimensions (1536)

### Health Checks

```bash
# Check backend health
curl https://your-api.railway.app/health

# Expected response:
# {"status":"healthy","services":{"api":"up","database":"up","vector_store":"up","cache":"up"}}
```

---

## Security Checklist

Before going live:

- [ ] `DEBUG=false` in production
- [ ] `ENABLE_DEMO_MODE=false` in production
- [ ] Strong `SECRET_KEY` (64+ characters)
- [ ] `ALLOWED_ORIGINS` properly configured
- [ ] SSL/HTTPS enabled (automatic on Vercel/Railway)
- [ ] Database credentials are secure
- [ ] API keys are in environment variables, not code
- [ ] Rate limiting is active
- [ ] Audit logging is enabled

---

## Cost Estimates

### Vercel (Frontend)
- **Hobby**: Free (good for testing)
- **Pro**: $20/month (production recommended)

### Railway (Backend)
- **Starter**: ~$5/month
- **Pro**: $20/month + usage

### Pinecone
- **Starter**: Free (10K vectors)
- **Standard**: $70/month (1M vectors)

### Total Estimated: $25-100/month for production

