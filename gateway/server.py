# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mcp>=2.0.0,<3",
#     "httpx>=0.25.0,<1",
#     "python-dotenv>=1.0.0,<2",
#     "openpyxl>=3.1.0,<4",
#     "uvicorn>=0.30.0,<1",
#     "starlette>=0.40.0,<1",
# ]
# ///
"""
KORAIL MCP Gateway
11개 MCP 서버(98개 도구)를 단일 서버로 통합. 로컬(stdio)·원격(Streamable HTTP) 둘 다 지원.

로컬 실행 (Claude Desktop 등 stdio 클라이언트, 기본값):
  python gateway/server.py
  일반 사용자는 `uv tool install` 로 설치한 korail-mcp 실행파일을 등록한다(루트 README 참고).

원격 실행 (Streamable HTTP) — 저장소 루트에서 -m 으로 실행할 것:
  python -m gateway.server --transport http --port 8080
  또는
  uvicorn gateway.server:app --host 0.0.0.0 --port 8080
  ⚠️ `python gateway/server.py --transport http` 처럼 파일 경로로 직접 실행하면
     uvicorn이 "gateway.server" 모듈을 다시 import하지 못해 ModuleNotFoundError 발생.
     (stdio 모드는 이 문제 없음 — 파일 경로로 직접 실행 가능)

클라이언트 연결 (원격):
  { "type": "streamableHttp", "url": "https://<host>/mcp" }
  헤더: Authorization: Bearer <MCP_API_KEY>

환경변수:
  KORAIL_PROXY_URL   Cloudflare 프록시 URL (기본값 내장)
  KORAIL_PROXY_TOKEN 프록시 인증 토큰 (proxy-worker에 PROXY_AUTH_TOKEN secret 설정 시 필수,
                      미설정 시 인증 없음 — 하위 11개 서버가 공용으로 사용)
  MCP_API_KEY        Bearer Token, 원격 모드 전용 (미설정 시 인증 없음 — 개발용)
  PORT               원격 모드 수신 포트 (기본 8080)
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── 환경변수 로드 ──────────────────────────────────────────────────
# gateway/.env → 상위 .env 순으로 탐색
load_dotenv(Path(__file__).parent / ".env", encoding="utf-8-sig")
load_dotenv(Path(__file__).parent.parent / ".env", encoding="utf-8-sig")

# ── m-* 서버 위치 판별 ─────────────────────────────────────────────
# 두 가지 배치를 모두 지원한다.
#   1) 저장소에서 직접 실행: gateway/ 의 상위(저장소 루트)에 m-* 가 있음
#   2) uvx/pip 로 패키지 설치: 휠에 번들된 gateway/_bundled/m-* 를 사용
_HERE = Path(__file__).parent
if (_HERE / "_bundled" / "m-codebook").is_dir():
    ROOT = _HERE / "_bundled"
else:
    ROOT = _HERE.parent

# ── Gateway MCPServer 인스턴스 ─────────────────────────────────────
# version 을 명시하지 않으면 serverInfo.version 이 빈 문자열로 나간다
# (mcp 1.x 는 SDK 버전을 자동으로 채웠으나 2.0 은 채우지 않음).
gateway = MCPServer("KORAIL MCP", version="1.0.0")
# mcp 2.0: settings.stateless_http 가 제거되어 streamable_http_app() 인자로 전달한다.

# ── 11개 서버 동적 로드 후 도구 통합 ──────────────────────────────
SERVERS = [
    "m-codebook",
    "m-convenience",
    "m-freight",
    "m-internal-svc",
    "m-network",
    "m-procurement",
    "m-rolling-stock",
    "m-stats",
    "m-train-ops",
    "m-urban-rail",
    "m-voc-cs",
]

_loaded: dict[str, int] = {}

for _srv in SERVERS:
    _srv_path = ROOT / _srv / "server.py"
    _spec = importlib.util.spec_from_file_location(
        _srv.replace("-", "_") + "_srv", str(_srv_path)
    )
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
    _count = 0
    for _name, _tool in _mod.mcp._tool_manager._tools.items():
        gateway.add_tool(_tool.fn, name=_name, description=_tool.description)
        _count += 1
    _loaded[_srv] = _count

_total = sum(_loaded.values())


# ── Bearer Token 미들웨어 ──────────────────────────────────────────
class BearerAuthMiddleware(BaseHTTPMiddleware):
    """MCP_API_KEY 환경변수가 설정된 경우 Bearer Token 검증."""

    async def dispatch(self, request: Request, call_next):
        # 헬스체크는 인증 제외
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        api_key = os.getenv("MCP_API_KEY", "")
        if not api_key:
            # 키 미설정 = 개발 모드, 통과
            return await call_next(request)

        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {api_key}":
            return Response(
                '{"error":"Unauthorized"}',
                status_code=401,
                media_type="application/json",
            )
        return await call_next(request)


# ── 헬스체크 엔드포인트 (custom_route로 /mcp 앱 내부에 등록) ───
import json as _json


@gateway.custom_route("/health", methods=["GET"])
async def health(request: Request) -> Response:
    return Response(
        _json.dumps(
            {
                "status": "ok",
                "service": "korail-mcp-gateway",
                "tools": _total,
                "servers": _loaded,
            },
            ensure_ascii=False,
        ),
        media_type="application/json",
    )


# ── ASGI 앱 조립 ──────────────────────────────────────────────────
# streamable_http_app()이 반환하는 Starlette 앱 자체에 미들웨어 추가.
# Mount() 감싸기를 피해 307 리다이렉트 문제를 방지.
# stateless_http=True: 세션 불필요(도구 호출만) — 원격 배포 시 인스턴스가
# 바뀌어도 세션 유실 문제가 없다.
app = gateway.streamable_http_app(stateless_http=True, host="0.0.0.0")
app.add_middleware(BearerAuthMiddleware)


# ── 진입점 ────────────────────────────────────────────────────────
def main() -> None:
    """콘솔 스크립트 진입점. uvx/pip 설치 시 `korail-mcp` 명령으로 호출된다."""
    import argparse

    parser = argparse.ArgumentParser(prog="korail-mcp")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    args = parser.parse_args()

    if args.transport == "stdio":
        gateway.run(transport="stdio")
    else:
        import uvicorn

        # 패키지로 설치된 경우 "gateway.server:app" 문자열 import 가 가능하지만,
        # 파일 경로로 직접 실행하면 실패하므로 app 객체를 그대로 넘긴다.
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
