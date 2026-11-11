import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import Store
import app.main as main_mod


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(main_mod, "store", Store())
    return TestClient(app)
