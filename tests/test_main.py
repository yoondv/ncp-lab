from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "v1 : GitHub Actions와 NCP SourceDeploy를 통한 자동 배포" in response.text
    assert "v2 : Nginx Blue-Green 무중단 배포" in response.text


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
