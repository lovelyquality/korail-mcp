"""
KORAIL MCP Gateway
11개 FastMCP 서버(98개 도구)를 단일 서버로 통합. 로컬(stdio)·원격(Streamable HTTP) 둘 다 지원.

로컬 실행 (Claude Desktop 등 stdio 클라이언트, 기본값):
  python gateway/server.py
  mcp-config.json 에서 11개 서버 대신 이 파일 하나만 등록하면 됨

원격 실행 (Streamable HTTP) — 저장소 루트(E:\AI\MCP)에서 -m 으로 실행할 것:
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
  KORAIL_PROXY_URL  Cloudflare 프록시 URL (기본값 내장)
  MCP_API_KEY       Bearer Token, 원격 모드 전용 (미설정 시 인증 없음 — 개발용)
  PORT              원격 모드 수신 포트 (기본 8080)
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── 환경변수 로드 ──────────────────────────────────────────────────
# gateway/.env → 상위 .env 순으로 탐색
load_dotenv(Path(__file__).parent / ".env", encoding="utf-8-sig")
load_dotenv(Path(__file__).parent.parent / ".env", encoding="utf-8-sig")

ROOT = Path(__file__).parent.parent  # E:\AI\MCP

# ── Gateway FastMCP 인스턴스 ───────────────────────────────────────
gateway = FastMCP("KORAIL MCP")
gateway.settings.stateless_http = True   # 세션 불필요 (도구 호출만)

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


# ── 헬스체크 엔드포인트 (FastMCP custom_route로 /mcp 앱 내부에 등록) ───
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
app = gateway.streamable_http_app()
app.add_middleware(BearerAuthMiddleware)


# ── 직접 실행 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "http"])
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")))
    args = parser.parse_args()

    if args.transport == "stdio":
        gateway.run(transport="stdio")
    else:
        import uvicorn

        uvicorn.run(
            "gateway.server:app",
            host="0.0.0.0",
            port=args.port,
            log_level="info",
        )
