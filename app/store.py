"""In-memory store. Replaced by PostgreSQL in milestone M3 (see docs/database.md)."""
from threading import Lock
from uuid import UUID

from .models import Alert, AlertRule, MetricSample, Service


class Store:
    def __init__(self) -> None:
        self._lock = Lock()
        self.services: dict[UUID, Service] = {}
        self.metrics: dict[UUID, list[MetricSample]] = {}
        self.rules: dict[UUID, AlertRule] = {}
        self.alerts: list[Alert] = []

    def add_service(self, svc: Service) -> Service:
        with self._lock:
            self.services[svc.id] = svc
            self.metrics[svc.id] = []
        return svc

    def remove_service(self, sid: UUID) -> bool:
        with self._lock:
            if sid not in self.services:
                return False
            del self.services[sid]
            self.metrics.pop(sid, None)
            self.rules = {k: r for k, r in self.rules.items() if r.service_id != sid}
            return True

    def add_metric(self, sample: MetricSample) -> list[Alert]:
        with self._lock:
            self.metrics[sample.service_id].append(sample)
            fired = []
            for rule in self.rules.values():
                if rule.service_id != sample.service_id or rule.metric != sample.name:
                    continue
                hit = sample.value > rule.threshold if rule.comparator == "gt" else sample.value < rule.threshold
                if hit:
                    alert = Alert(rule_id=rule.id, service_id=rule.service_id, metric=rule.metric, value=sample.value)
                    self.alerts.append(alert)
                    fired.append(alert)
            return fired


store = Store()
