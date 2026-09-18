from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    return """
    <!doctype html>
    <html lang="ko">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>ncp-lab</title>
      <style>
        * { box-sizing: border-box; }
        body {
          margin: 0;
          padding: 48px 20px;
          background: #f6f7f9;
          color: #202124;
          font-family: Arial, "Noto Sans KR", sans-serif;
          line-height: 1.6;
        }
        main {
          width: min(760px, 100%);
          margin: 0 auto;
          padding: 40px;
          border: 1px solid #dfe3e8;
          border-radius: 8px;
          background: #ffffff;
        }
        h1 {
          margin: 0 0 8px;
          font-size: 32px;
        }
        header p {
          margin: 0 0 32px;
          color: #5f6368;
        }
        .versions {
          border-top: 1px solid #dfe3e8;
        }
        article {
          padding: 24px 0;
          border-bottom: 1px solid #dfe3e8;
        }
        .version {
          color: #1967d2;
          font-size: 14px;
          font-weight: 700;
        }
        h2 {
          margin: 5px 0;
          font-size: 19px;
        }
        article p {
          margin: 0;
          color: #5f6368;
          font-size: 14px;
        }
        @media (max-width: 650px) {
          body { padding: 16px; }
          main { padding: 28px 22px; }
        }
      </style>
    </head>
    <body>
      <main>
        <header>
          <h1>ncp-lab</h1>
        </header>

        <section class="versions" aria-label="프로젝트 버전별 구현 내용">
          <article>
            <span class="version">v1</span>
            <h2>CI/CD 자동 배포</h2>
            <p>GitHub Actions와 NCP SourceDeploy를 연동해 테스트부터 서버 배포까지 자동화했습니다.</p>
          </article>
          <article>
            <span class="version">v2</span>
            <h2>Blue-Green 무중단 배포</h2>
            <p>Nginx가 정상 상태를 확인한 새 컨테이너로 트래픽을 전환하도록 구성했습니다.</p>
          </article>
          <article>
            <span class="version">v3</span>
            <h2>추적 가능한 이미지 배포</h2>
            <p>Git 커밋 SHA 이미지 태그와 배포 결과 검증을 적용해 배포 이력을 추적할 수 있습니다.</p>
          </article>
          <article>
            <span class="version">v4</span>
            <h2>운영 모니터링 및 알림</h2>
            <p>Cloud Insight로 서버 자원을 감시하고 임계값을 초과하면 이메일 알림을 발송합니다.</p>
          </article>
        </section>
      </main>
    </body>
    </html>
    """


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
