# 🚪 통합 게이트웨이

11개 MCP 서버(98개 도구)를 단일 서버로 통합. 로컬(stdio)·원격(Streamable HTTP) 둘 다 지원.

> 📌 설치는 [루트 README](../README.md) 참고. 개별 서버 11개를 각각 등록하는 대신, 이 파일 하나만 등록하면 동일한 98개 도구를 전부 쓸 수 있습니다.

## 로컬 실행 (기본값)

```
python gateway/server.py
```

`mcp-config.json`에서 11개 서버 블록 대신 이 파일 하나만 등록하면 됩니다. Claude Desktop 등 stdio 클라이언트 전용이며, API 키·인증 설정이 필요 없습니다.

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

## 장단점 (11개 개별 서버 방식과 비교)

| | 개별 서버 11개 | 게이트웨이 1개 |
|---|---|---|
| 설정 줄 수 | 11줄 | 1줄 |
| 상주 메모리(실측) | 약 600MB | 약 66MB |
| 장애 영향 범위 | 서버 하나 죽어도 나머지 살아있음 | 하나가 죽으면 98개 도구 전부 중단 |
| 원격 배포 | 불가 | 가능 |

두 방식 모두 계속 유지됩니다 — 상황에 맞는 쪽을 선택하세요.
