# PulseWatch

Cloud-native monitoring platform. FastAPI backend that registers services, ingests metrics, evaluates alert rules, and exposes health endpoints.

## Quick start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -q
```

Or with Docker:

```bash
docker compose up --build
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness |
| GET | /ready | Readiness |
| POST | /api/v1/services | Register a monitored service |
| GET | /api/v1/services | List services |
| GET | /api/v1/services/{id} | Get service |
| DELETE | /api/v1/services/{id} | Remove service |
| POST | /api/v1/metrics | Ingest a metric sample |
| GET | /api/v1/metrics/{service_id} | Query samples |
| POST | /api/v1/alerts/rules | Create alert rule |
| GET | /api/v1/alerts | List fired alerts |

Tracking: Linear project "PulseWatch Monitoring Platform". Docs: Notion page "PulseWatch Documentation".
