<h1 align="center">NCP CI/CD Lab</h1>

<p align="center">
  GitHub Actions, Docker, GHCR, NCP SourceDeploy를 연동한 FastAPI 웹 API 자동 배포 프로젝트
</p>

## ncp-lab v2

**배포 주소**: [http://211.233.214.70](http://211.233.214.70) (현재 운영 중)<br>
**개발 기간**: 2026.09 ~ 진행 중<br>
**배포 환경**: NCP Server (Ubuntu 24.04.1 LTS)

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [CI/CD 아키텍처 및 배포 흐름](#cicd-아키텍처-및-배포-흐름)
4. [설계 선택과 이유](#설계-선택과-이유)
5. [보안 및 권한 관리](#보안-및-권한-관리)

## 프로젝트 개요

#### CI/CD의 전체 흐름을 이해하고 직접 구축하기 위해 시작했습니다.

프로젝트의 핵심 기능은 다음과 같습니다.

1. **API 자동 테스트**: push와 pull request마다 pytest로 `/`와 `/health`의 상태 코드와 응답 내용을 검사합니다.

2. **이미지 빌드 및 저장**: 테스트를 통과한 `main` 브랜치의 Docker 이미지를 빌드해 GHCR에 게시합니다.
3. **배포 요청 자동화**: GitHub Actions가 `deploy.sh`를 Object Storage에 업로드하고 서명된 NCP API 요청으로 SourceDeploy 시나리오를 실행합니다.
4. **Blue-Green 무중단 배포**: SourceDeploy Agent가 비활성 컨테이너에 최신 이미지를 실행한 뒤 Nginx의 요청 대상을 전환합니다.
5. **헬스 체크 및 롤백**: 새 컨테이너와 Nginx 전환 후의 HTTP 응답을 검사합니다. 모두 성공하면 새 컨테이너로 배포를 완료하고, 실패하면 기존 컨테이너로 요청을 되돌립니다.

## 기술 스택

### Development

![Python](https://img.shields.io/badge/Python-3.14.7-555555?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-Application-555555?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=009688)
![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI_Server-555555?style=for-the-badge&logo=uvicorn&logoColor=white&labelColor=4051B5)
![pytest](https://img.shields.io/badge/pytest-Automated_Testing-555555?style=for-the-badge&logo=pytest&logoColor=white&labelColor=0A9EDC)

### Deployment

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-555555?style=for-the-badge&logo=githubactions&logoColor=white&labelColor=2088FF)
![Docker](https://img.shields.io/badge/Docker-Container-555555?style=for-the-badge&logo=docker&logoColor=white&labelColor=2496ED)
![GHCR](https://img.shields.io/badge/GHCR-Container_Registry-555555?style=for-the-badge&logo=github&logoColor=white&labelColor=181717)

### Infrastructure

![NCP](https://img.shields.io/badge/NCP-Server-555555?style=for-the-badge&logo=naver&logoColor=white&labelColor=03C75A)
![SourceDeploy](https://img.shields.io/badge/NCP-SourceDeploy-555555?style=for-the-badge&logo=naver&logoColor=white&labelColor=03C75A)
![Object Storage](https://img.shields.io/badge/NCP-Object_Storage-555555?style=for-the-badge&logo=naver&logoColor=white&labelColor=03C75A)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04.1_LTS-555555?style=for-the-badge&logo=ubuntu&logoColor=white&labelColor=E95420)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-555555?style=for-the-badge&logo=nginx&logoColor=white&labelColor=009639)


## CI/CD 아키텍처 및 배포 흐름

```mermaid
flowchart TB
    DEV[Developer] -->|1. push 또는 pull request| REPO[GitHub Repository]

    subgraph GHA[GitHub Actions]
        direction LR
        CHECK["check<br/>2. pytest API 테스트"]
        PUBLISH["publish<br/>3. Docker 이미지 빌드 및 게시"]
        DEPLOY["deploy<br/>4. deploy.sh 업로드 및 배포 요청"]
        CHECK --> PUBLISH --> DEPLOY
    end

    REPO --> CHECK
    PUBLISH -->|image push| GHCR[(GHCR<br/>Private)]
    DEPLOY -->|deploy.sh.zip| STORAGE[(Object Storage<br/>Private)]
    DEPLOY -->|서명된 API 요청| SD[SourceDeploy]

    subgraph NCP[NCP Server]
        direction TB
        AGENT[SourceDeploy Agent] -->|5. 스크립트 실행| SCRIPT[deploy.sh]
        SCRIPT -->|6. 비활성 환경에 실행| BLUE["Blue<br/>127.0.0.1:8001 → 8000"]
        SCRIPT -->|6. 비활성 환경에 실행| GREEN["Green<br/>127.0.0.1:8002 → 8000"]
        BLUE --> HEALTH{7. Container Health Check}
        GREEN --> HEALTH
        HEALTH -->|성공| SWITCH[8. Nginx upstream 전환]
        HEALTH -->|실패| KEEP[기존 환경 유지]
        SWITCH --> NGINX[Nginx :80]
        NGINX --> FINAL{9. Service Health Check}
        FINAL -->|성공| COMPLETE["배포 완료"]
        FINAL -->|실패| ROLLBACK[기존 환경으로 롤백]
    end

    STORAGE -. 배포 파일 .-> AGENT
    SD -->|배포 작업 전달| AGENT
    GHCR -->|docker pull| SCRIPT
    USER[User] -->|HTTP :80| NGINX

    classDef github fill:#24292f,color:#ffffff,stroke:#57606a;
    classDef registry fill:#0969da,color:#ffffff,stroke:#0550ae;
    classDef ncp fill:#03c75a,color:#ffffff,stroke:#009f47;
    classDef success fill:#dafbe1,color:#116329,stroke:#2da44e;
    classDef failure fill:#ffebe9,color:#cf222e,stroke:#cf222e;

    class REPO,CHECK,PUBLISH,DEPLOY github;
    class GHCR registry;
    class SD,STORAGE,AGENT,SCRIPT,BLUE,GREEN,SWITCH,NGINX ncp;
    class COMPLETE success;
    class KEEP,ROLLBACK failure;
```

#### `check`

- push와 pull request가 발생하면 Python 3.14.7 및 테스트에 필요한 패키지를 설치합니다.
- pytest로 `/` 페이지의 상태와 표시 내용, `/health`의 상태 코드와 응답값을 검사합니다.

#### `publish`

- `check` 성공 후 `main` 브랜치 push에서만 실행합니다.
- `GITHUB_TOKEN`으로 GHCR에 로그인합니다.
- 저장소의 Dockerfile로 이미지를 빌드하고 `ghcr.io/yoondv/ncp-lab:latest`로 게시합니다.

#### `deploy`

- `publish` 성공 후 `main` 브랜치 push에서만 실행합니다.
- `deploy.sh`를 압축해 NCP Object Storage의 배포 파일로 업로드합니다.
- GitHub Secrets에 저장된 NCP 인증 키로 HMAC-SHA256 방식의 API 요청 서명을 생성합니다.
- SourceDeploy의 프로젝트, 스테이지, 시나리오 ID를 조회한 뒤 배포 API를 호출합니다.

#### `deploy.sh`

- 현재 Nginx upstream 설정을 확인해 Blue와 Green 중 비활성 환경을 선택합니다.
- GHCR의 최신 이미지를 pull하고 대기 컨테이너를 제거한 뒤, 최신 이미지로 새 컨테이너를 생성합니다.
- 이후 검사에 성공하면 새 환경으로 배포를 완료하고 기존 컨테이너는 다음 배포 또는 롤백을 위한 대기 상태로 유지합니다.

## 설계 선택과 이유

### GHCR 기반 이미지 배포

소스 코드와 빌드된 Docker 이미지를 GitHub 생태계 안에서 함께 관리하기 위해 Docker Hub와 같은 별도 Registry 대신 GitHub에서 제공하는 GHCR을 선택했습니다. GitHub Actions는 기본으로 제공되는 `GITHUB_TOKEN`으로 이미지를 게시하고, NCP 서버는 GitHub PAT로 Private 이미지를 pull하도록 역할을 분리했습니다.

### SSH 대신 SourceDeploy 사용

SSH 배포를 적용하면 서버의 22번 포트에 대한 접근 범위를 넓혀야 할 수도 있습니다. 이를 피하기 위해 GitHub Actions가 NCP API로 배포를 요청하고 서버 내부의 SourceDeploy Agent가 명령을 실행하는 방식을 선택했습니다.

### 이중 헬스체크

첫 번째 헬스체크는 새 컨테이너 내부의 `/health`를 호출해 FastAPI 서버가 정상적으로 시작됐는지 확인합니다.<br>
두 번째 헬스체크는 Nginx 전환 후 실제 서비스 경로를 호출합니다. 이를 통해 컨테이너뿐만 아니라 Nginx 설정과 upstream 연결까지 정상인지 확인합니다.

## 보안 및 권한 관리

### 인증 및 접근 구조

```mermaid
flowchart TB
    REPO["GitHub Repository<br/>Public"] --> ACTIONS[GitHub Actions]

    TOKEN["GITHUB_TOKEN"] -.->|GHCR push 인증| ACTIONS
    SECRETS["NCP Access Key · Secret Key"] -.->|NCP API · Object Storage 인증| ACTIONS

    ACTIONS -->|Image push| GHCR["GHCR<br/>Private"]
    ACTIONS -->|deploy.sh.zip 업로드| STORAGE["Object Storage<br/>Private"]
    ACTIONS -->|HMAC-SHA256 서명 요청| SD["NCP SourceDeploy"]

    AUTH["NCP_AUTH_KEY"] -.->|Agent 인증| AGENT[SourceDeploy Agent]
    SD --> AGENT
    STORAGE -->|deploy.sh.zip| AGENT

    AGENT --> SCRIPT[deploy.sh 실행]
    PAT["GitHub PAT"] -->|서버에 저장| DOCKER_AUTH["Docker 인증정보"]
    DOCKER_AUTH -.->|GHCR pull 인증| SCRIPT
    SCRIPT -->|Image pull| GHCR
    SCRIPT --> BLUE["Blue Container<br/>127.0.0.1:8001"]
    SCRIPT --> GREEN["Green Container<br/>127.0.0.1:8002"]

    USER[외부 사용자] -->|HTTP 80 · Public| NGINX[Nginx]
    NGINX -->|Internal| BLUE
    NGINX -->|Internal| GREEN
```

### 계정 분리

<p align="center">
  <img src="docs/images/sub-account-separation.png" width="600" alt="NCP Sub Account 분리 화면"><br>
  <sub>GitHub Actions용 Sub Account와 SourceDeploy Agent용 Sub Account를 분리해 하나의 인증 키가 다른 배포 구성에 미치는 영향을 줄였습니다.</sub>
</p>

### 최소 권한 정책

<p align="center">
  <img src="docs/images/custom-policy.png" width="600" alt="SourceDeploy 사용자 정의 정책 화면"><br>
  <sub>Actions용 계정에는 지정된 SourceDeploy 프로젝트의 배포 실행 권한과 Object Storage 파일 업로드 권한만 사용자 정의 정책으로 부여했습니다.<br>
  NCP 서버에서 이미지를 pull하기 위한 GitHub PAT에는 <code>read:packages</code> 권한만 부여해 토큰의 작업 범위를 이미지 읽기로 제한했습니다.</sub>
</p>

### 인증 정보 관리

<p align="center">
  <img src="docs/images/github-secrets.png" width="600" alt="GitHub Actions Secrets 화면"><br>
  <sub>NCP Access Key와 Secret Key는 하드코딩하지 않고 GitHub Actions Secrets에 저장했습니다.<br>
  NCP 서버에 저장된 인증 정보는 root 계정만 접근할 수 있도록 파일 권한을 제한했습니다.</sub>
</p>

### 네트워크 접근 제한

<p align="center">
  <img src="docs/images/acg-rules.png" width="600" alt="NCP ACG 접근 제어 설정 화면"><br>
  <sub>웹 서비스용 80번 포트는 Nginx를 통해 외부 접속을 허용하고, SSH 22번 포트는 관리자 공인 IP에서만 접근할 수 있도록 NCP ACG를 설정했습니다.<br>
  Blue와 Green의 8001·8002번 포트는 127.0.0.1에만 바인딩해 서버 외부에서 컨테이너로 직접 접근할 수 없도록 구성했습니다.</sub>
</p>

<p align="center">
  <strong>감사합니다.</strong>
</p>
