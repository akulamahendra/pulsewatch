from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from .models import Alert, AlertRule, AlertRuleCreate, MetricSample, Service, ServiceCreate
from .store import store

app = FastAPI(title="PulseWatch", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    return {"status": "ready", "services": len(store.services)}


@app.post("/api/v1/services", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceCreate) -> Service:
    if any(s.name == body.name for s in store.services.values()):
        raise HTTPException(409, "service name already exists")
    return store.add_service(Service(**body.model_dump()))


@app.get("/api/v1/services", response_model=list[Service])
def list_services() -> list[Service]:
    return list(store.services.values())


@app.get("/api/v1/services/{sid}", response_model=Service)
def get_service(sid: UUID) -> Service:
    svc = store.services.get(sid)
    if not svc:
        raise HTTPException(404, "service not found")
    return svc


@app.delete("/api/v1/services/{sid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(sid: UUID) -> None:
    if not store.remove_service(sid):
        raise HTTPException(404, "service not found")


@app.post("/api/v1/metrics", status_code=status.HTTP_202_ACCEPTED)
def ingest_metric(sample: MetricSample) -> dict:
    if sample.service_id not in store.services:
        raise HTTPException(404, "service not found")
    fired = store.add_metric(sample)
    return {"accepted": True, "alerts_fired": len(fired)}


@app.get("/api/v1/metrics/{sid}", response_model=list[MetricSample])
def query_metrics(sid: UUID, name: str | None = None, limit: int = 100) -> list[MetricSample]:
    if sid not in store.services:
        raise HTTPException(404, "service not found")
    samples = [m for m in store.metrics[sid] if name is None or m.name == name]
    return samples[-limit:]


@app.post("/api/v1/alerts/rules", response_model=AlertRule, status_code=status.HTTP_201_CREATED)
def create_rule(body: AlertRuleCreate) -> AlertRule:
    if body.service_id not in store.services:
        raise HTTPException(404, "service not found")
    rule = AlertRule(**body.model_dump())
    store.rules[rule.id] = rule
    return rule


@app.get("/api/v1/alerts", response_model=list[Alert])
def list_alerts() -> list[Alert]:
    return store.alerts
