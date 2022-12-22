import pytest


@pytest.fixture(autouse=True)
def configure_doctss(monkeypatch):
    monkeypatch.setenv("PLOOMBER_VERSION_CHECK_DISABLED", "true")
