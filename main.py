from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "배포 테스트 v2"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
