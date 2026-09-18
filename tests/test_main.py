from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "CI/CD 자동 배포" in response.text
    assert "Blue-Green 무중단 배포" in response.text
    assert "추적 가능한 이미지 배포" in response.text
    assert "운영 모니터링 및 알림" in response.text


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
