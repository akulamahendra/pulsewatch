from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    environment: str = Field(default="production", pattern="^(production|staging|development)$")


class Service(ServiceCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricSample(BaseModel):
    service_id: UUID
    name: str = Field(min_length=1, max_length=64)
    value: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Comparator(str, Enum):
    gt = "gt"
    lt = "lt"


class AlertRuleCreate(BaseModel):
    service_id: UUID
    metric: str
    comparator: Comparator
    threshold: float


class AlertRule(AlertRuleCreate):
    id: UUID = Field(default_factory=uuid4)


class Alert(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    rule_id: UUID
    service_id: UUID
    metric: str
    value: float
    fired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
