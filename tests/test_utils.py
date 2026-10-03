import pytest
import requests

from app_common_library.utils import obtener_status_red


def test_obtener_status_red_returns_status_code(monkeypatch):
    class FakeResponse:
        status_code = 200

    monkeypatch.setattr(requests, "get", lambda url, timeout: FakeResponse())
    assert obtener_status_red() == 200


def test_obtener_status_red_propagates_errors(monkeypatch):
    def boom(url, timeout):
        raise requests.exceptions.ConnectionError("network down")

    monkeypatch.setattr(requests, "get", boom)
    with pytest.raises(requests.exceptions.ConnectionError):
        obtener_status_red()
