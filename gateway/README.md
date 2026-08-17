# 🚪 통합 게이트웨이

11개 MCP 서버(98개 도구)를 단일 서버로 통합. 로컬(stdio)·원격(Streamable HTTP) 둘 다 지원.

> 📌 설치는 [루트 README](../README.md) 참고. 개별 서버 11개를 각각 등록하는 대신, 이 파일 하나만 등록하면 동일한 98개 도구를 전부 쓸 수 있습니다.

## 로컬 실행 (기본값)

```
python gateway/server.py
```

Claude Desktop 등 stdio 클라이언트가 이 방식으로 연결합니다. API 키·인증 설정이 필요 없습니다.

일반 사용자는 [루트 README](../README.md)의 `uv tool install` 안내를 따르면 되고, 아래는 **저장소를 직접 받아 개발할 때** 쓰는 방법입니다.

## 원격 실행 (대국민 공개 등)

저장소 루트(`E:\AI\MCP`)에서 **반드시 `-m`으로 실행**하세요(파일 경로로 직접 실행하면 `ModuleNotFoundError` 발생 — stdio 모드는 이 문제 없음).

```
python -m gateway.server --transport http --port 8080
```

또는:

```
uvicorn gateway.server:app --host 0.0.0.0 --port 8080
```

클라이언트 연결:
```json
{ "type": "streamableHttp", "url": "https://<host>/mcp", "headers": { "Authorization": "Bearer <MCP_API_KEY>" } }
```

`MCP_API_KEY` 환경변수 미설정 시 인증 없이 열림(개발용). `.env.example` 참고.

## 컨테이너 배포 (Cloud Run 등)

저장소 루트의 [`Dockerfile`](../Dockerfile)이 이 게이트웨이를 HTTP 모드로 띄운다. 빌드 컨텍스트는 13MB(`.dockerignore`가 venv·발표자산·개인설정 제외).

로컬 확인:
```bash
docker build -t korail-mcp-gateway .
docker run --rm -p 8080:8080 korail-mcp-gateway
curl http://localhost:8080/health
```

Cloud Run 배포(`PORT`는 플랫폼이 주입하며 코드가 자동으로 읽음):
```bash
gcloud run deploy korail-mcp --source . --region asia-northeast3 --allow-unauthenticated --memory 512Mi
```

기동 실측: 모듈 로드 **2.5~2.9초**(98개 도구). Cloud Run은 컨테이너 기동에 기본 240초를 허용하므로 여유가 크다. 데이터 캐시는 기동 시점이 아니라 **도구가 처음 호출될 때** 채워지므로, 냉시동 자체가 공공데이터 API 호출량을 소모하지 않는다.

`stateless_http=True`로 동작하므로 인스턴스가 교체돼도 세션이 끊기지 않는다.

> ⚠️ **공개 배포 전 반드시 읽을 것** — 공공데이터포털 **개발계정은 1일 1,000회** 제한이다. Workers의 요청 제한은 최소 주기가 60초여서, **분당 1회로 묶어도 1,440회/일**이 되어 한도를 넘는다. 즉 개발계정 상태에서는 어떤 요청 제한으로도 공개 운영이 성립하지 않는다. 공개는 **운영계정(1일 100,000회) 전환 이후**에만 가능하다.
>
> 그 전 단계로는 `--no-allow-unauthenticated`(본인만 접근) 또는 `MCP_API_KEY` 설정 상태로 배포해 동작을 확인하는 것까지가 적절하다.

## 장단점 (11개 개별 서버 방식과 비교)

| | 개별 서버 11개 | 게이트웨이 1개 |
|---|---|---|
| 설정 줄 수 | 11줄 | 1줄 |
| 상주 메모리(실측) | 약 600MB | 약 66MB |
| 장애 영향 범위 | 서버 하나 죽어도 나머지 살아있음 | 하나가 죽으면 98개 도구 전부 중단 |
| 원격 배포 | 불가 | 가능 |

두 방식 모두 계속 유지됩니다 — 상황에 맞는 쪽을 선택하세요.
