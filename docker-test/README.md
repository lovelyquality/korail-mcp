# KORAIL MCP 클린 설치 검증

이 폴더는 **새로 clone한 사용자 환경에서 모든 서버가 설치·기동되는지 검증**하는 자산을 담고 있습니다.

## 왜 필요한가

최근까지 이 저장소는 **새 사용자 전원 설치 실패**하는 심각한 문제가 있었습니다.

### 사건 경위
- `m-*/requirements.txt`에 `mcp[cli]>=1.0.0`처럼 버전 상한 없이 적혀 있었음
- 새로 설치하면 최신 `mcp==2.0.0`이 깔림
- MCP 2.0에서 모듈명이 `mcp.server.fastmcp` → `mcp.server.mcpserver`로 개명됨
- 11개 서버 모두 import 실패

### 교훈
개발자 PC에는 구버전(mcp 1.27.1)이 남아 있어서 이 사고를 몰랐습니다. **자동화된 클린 환경 검증이 없으면 이런 사고를 놓치기 쉽습니다.**

이후 `mcp>=2.0.0,<3` 으로 상한을 고정했고, **의존성 선언을 `gateway/requirements.txt` 한 곳으로 모았습니다**(예전에는 `m-*/requirements.txt` 11곳을 동기화해야 했고 그게 사고의 원인이었습니다). 그래도 **푸시 전에 반드시 이 검증을 실행해야 합니다.**

## 빠른 실행 (로컬 Windows)

```bash
E:\AI\MCP\venv\Scripts\python.exe E:\AI\MCP\docker-test\smoke_test.py
```

가상환경이 없으면 `uv` 로 바로 실행할 수도 있습니다:
```bash
uv run docker-test/smoke_test.py
```

## 완전한 클린 환경 (Docker)

리눅스 컨테이너에서 완전히 깨끗한 환경으로 검증할 수 있습니다.

빌드:
```bash
docker build -f docker-test/Dockerfile -t korail-mcp-test .
```

실행:
```bash
docker run --rm korail-mcp-test
```

## 검증 항목

스크립트는 다음 3가지를 확인합니다:

1. **Import / 도구 등록**: 11개 서버 모두 import 성공, 도구 수 정확히 98개
2. **반환 타입 선언 검증**: 선언과 실제 반환값이 어긋난 도구 탐지. SDK 는 반환 타입 선언으로
   출력 스키마를 만들어 검증하므로, 어긋나면 **MCP 경유 호출에서만 실패**하고 파이썬 직접
   호출로는 통과해버린다(2026-08-13 에 m-network 4개 도구가 이 상태로 방치돼 있었음)
3. **실제 API 호출**: 프록시 경유 3개 샘플 호출 (인터넷 필요)
4. **Exit code**: 성공=0, 실패=1

## 규칙

- **`gateway/requirements.txt` 를 수정했거나, 도구를 추가·수정했거나, 의존성에 영향 있는 변경을 푸시하기 전에는 반드시 이 검증을 실행한다**
- 스크립트가 exit code 0으로 종료되어야 성공
- API 호출 실패는 네트워크 이슈일 수 있으므로 경고로만 처리 (import/도구수 불일치는 반드시 실패)
