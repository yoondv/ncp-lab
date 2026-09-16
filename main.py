from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    return """
    v1 : GitHub Actions와 NCP SourceDeploy를 통한 자동 배포<br>
    v2 : Nginx Blue-Green 무중단 배포
    """


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
