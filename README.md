# 🏥 MedAssist RAG
![App Screenshot](https://github.com/Saikat-SS24/NLP_Flask_AI_ChatBot/blob/main/chat1.png)
AI-powered clinical decision support system using Retrieval-Augmented Generation (RAG) to help healthcare professionals access medical information through natural language queries.

![MedAssist RAG](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

## ✨ Features

### 🔍 Medical Chat Interface
- Natural language medical queries
- Evidence-based answers with citations
- Source document references with links to PubMed/DOI
- Streaming responses for real-time feedback

### 💊 Drug Interaction Checker
- Check interactions between multiple medications
- Severity classification (mild/moderate/severe/contraindicated)
- Management recommendations
- Alternative drug suggestions

### 📋 Medical Code Lookup
- ICD-10 code search and lookup
- SNOMED-CT concept search
- Copy codes to clipboard
- Category and exclusion information

### 🌐 Medical Translation
- Japanese ↔ English medical term translation
- Related ICD-10 codes
- Patient-friendly explanations
- Medical context information

### 🔒 Security & Compliance
- Role-based access control (Doctor/Nurse/Pharmacist/Admin)
- Audit logging for all queries
- Session timeout for security
- HIPAA-ready architecture

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI (Python 3.11+), Pydantic |
| **LLM** | OpenAI GPT-4o |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Vector DB** | ChromaDB (local) / Pinecone (production) |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Deployment** | Docker, Docker Compose |

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd medassist-rag
```

### 2. Configure Environment

Create `.env` file in the root directory:

```env
# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Pinecone (optional, for production)
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=medassist

# Application
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

### 3. Run with Docker Compose

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Seed the Vector Database

```bash
# With Docker
docker-compose exec backend python scripts/seed_vector_db.py

# Or locally
cd backend
python scripts/seed_vector_db.py
```

## 💻 Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📁 Project Structure

```
medassist-rag/
├── frontend/                    # Next.js application
│   ├── app/                     # App router pages
│   │   ├── (auth)/              # Authentication pages
│   │   ├── (dashboard)/         # Main app pages
│   │   └── page.tsx             # Landing page
│   ├── components/              # React components
│   │   ├── ui/                  # shadcn/ui components
│   │   └── layout/              # Layout components
│   ├── lib/                     # Utilities and API client
│   └── types/                   # TypeScript types
│
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/rag/            # RAG pipeline
│   │   ├── models/              # Pydantic & SQLAlchemy models
│   │   ├── services/            # Business logic
│   │   └── db/                  # Database configuration
│   └── data/                    # Data ingestion scripts
│
├── scripts/                     # Utility scripts
│   ├── init.sql                 # Database initialization
│   └── seed_vector_db.py        # Vector DB seeding
│
└── docker-compose.yml           # Docker orchestration
```

## 🔌 API Endpoints

### Chat / RAG
- `POST /api/v1/chat` - Send a medical query
- `POST /api/v1/chat/stream` - Stream response (SSE)
- `GET /api/v1/chat/suggestions` - Get suggested queries

### Drug Interactions
- `POST /api/v1/drugs/check-interactions` - Check drug interactions
- `GET /api/v1/drugs/search` - Search drugs
- `GET /api/v1/drugs/{drug_name}` - Get drug details

### Medical Codes
- `GET /api/v1/codes/icd10/search` - Search ICD-10 codes
- `GET /api/v1/codes/snomed/search` - Search SNOMED-CT
- `GET /api/v1/codes/translate` - Translate medical terms

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

## 🎨 Screenshots

### Chat Interface
The main chat interface provides a clean, modern UI for medical queries with inline source citations.

### Drug Interaction Checker
Visual severity indicators and detailed interaction information help clinicians make informed decisions.

### Medical Code Lookup
Quickly search and copy ICD-10 and SNOMED-CT codes with full descriptions.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Optional |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://...` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `SECRET_KEY` | JWT secret key | Required |
| `ENVIRONMENT` | `development` or `production` | `development` |

### Vector Database Options

**ChromaDB (Local Development)**
- Runs locally in Docker
- No API key required
- Good for development and testing

**Pinecone (Production)**
- Managed vector database
- Better scaling and performance
- Requires API key

## 📊 Demo Data

The application includes demo data for:
- Medical literature (hypertension, diabetes, pneumonia guidelines)
- Drug interactions (10+ common interaction pairs)
- ICD-10 codes (cardiovascular, endocrine, respiratory)
- SNOMED-CT concepts

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure Pinecone for vector storage
- [ ] Set up PostgreSQL with proper credentials
- [ ] Configure Redis for session management
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Review CORS settings

## ⚠️ Disclaimer

**MedAssist RAG is a clinical decision support tool, not a replacement for professional medical judgment.**

- Information provided is for educational and decision support purposes only
- Always verify critical information through authoritative sources
- Final medical decisions should be made by qualified healthcare professionals
- Not intended for emergency or life-threatening situations

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📧 Support

For questions or support, please open an issue on GitHub.

---

Built with ❤️ for healthcare professionals

