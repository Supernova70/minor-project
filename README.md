# Phishing Guard V2

Email phishing detection system with ML-based text analysis, URL scanning, and attachment analysis.

## Quick Start

```bash
# 1. Download datasets from Kaggle
# Download CEAS_08.csv and phishing_email.csv from Kaggle
# Place them in: data/archive/

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start with Docker
docker-compose up --build

# 4. Check health
curl http://localhost:8000/health

# 5. View API docs
# Open http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `POST` | `/emails/fetch?limit=20` | Fetch emails from IMAP inbox |
| `GET` | `/emails` | List all fetched emails |
| `GET` | `/emails/{id}` | Get email details |
| `POST` | `/scans/{email_id}` | Trigger scan on an email |
| `GET` | `/scans` | List all scans |
| `GET` | `/scans/{id}` | Get scan details + verdict |

## Architecture

```
app/
├── api/          # Route handlers (thin controllers)
├── engines/      # Analysis engines (ML, URL, attachment)
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic request/response schemas
└── services/     # Business logic orchestration
```

## Tech Stack

- **FastAPI** — API framework
- **PostgreSQL** — Database
- **SQLAlchemy 2.0** — ORM
- **Alembic** — Migrations
- **scikit-learn** — ML model
- **Docker** — Containerization
