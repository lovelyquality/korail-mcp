"""korail-rail-infra MCP server.

철도 건설·개발·안전 종합정보 (국가철도공단 KRIC, data.go.kr).
KORAIL 간선·도시철도 운영 데이터와 구분되는 '철도 인프라/사업/안전' 기능 영역.

데이터 소스: data.go.kr (기존 DATA_GO_KR_API_KEY, 파일데이터는 키 불필요)

⚠️ 구현 상태: 데이터 구조(기능별 도구 인터페이스) 완성.
   각 데이터셋의 실제 소스(odcloud UUID 또는 로컬 CSV 파일명)는
   MD/CSV 제공 시 _ENDPOINTS에 채울 것. 미설정 시 안내 메시지 반환.

기능 그룹:
  안전     : 철도 안전사고 정보, 사고현황 연보
  국가계획 : 제4차 국가철도망 구축계획, 고속철도 현황·사업계획
  개발     : 역세권·복합역사 개발 현황, 철도부지 행복주택
  자산     : 국유재산 정보
  건설     : 철도건설현황, 건설현장정보
"""

import os
import csv
import json
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(encoding="utf-8-sig")
API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"
DATA_DIR = Path(__file__).parent / "data"

mcp = FastMCP("korail-rail-infra")

_cache: dict[str, list] = {}


# ── 엔드포인트 매핑 ──────────────────────────────────────────────────────────
# source: "odcloud" → {id, uddi}, "local" → {csv, encoding}
# MD/CSV 제공 시 채울 것. 미설정(빈 값)이면 안내 메시지 반환.

_ENDPOINTS = {
    "safety_incident":   {"name": "철도 안전 사고 정보",            "id": "15067611", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "safety_yearbook":   {"name": "철도 통계 자료(사고현황 연보)",  "id": "15067627", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "national_plan":     {"name": "제4차 국가철도망 구축계획",       "id": "15105939", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "hsr_status":        {"name": "고속철도 현황",                  "id": "15139391", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "hsr_plan":          {"name": "고속철도 사업계획",              "id": "15118143", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "station_dev":       {"name": "역세권 및 복합역사 개발 현황",    "id": "15118160", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "happy_housing":     {"name": "철도부지 활용 행복주택 건설 현황","id": "15118159", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "national_property": {"name": "국유재산 정보",                  "id": "15024987", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "construction":      {"name": "철도건설현황",                  "id": "15037490", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
    "construction_site": {"name": "철도건설현장정보",              "id": "15012855", "uddi": "", "csv": "", "encoding": "utf-8-sig"},
}


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────

def _wrap(data: list, dataset: str) -> str:
    return json.dumps(
        {
            "data": data,
            "_meta": {
                "출처": "국가철도공단(KRIC) 공공데이터포털 (data.go.kr)",
                "데이터셋": dataset,
                "건수": len(data),
            },
        },
        ensure_ascii=False, indent=2,
    )


def _odcloud_load_all(uddi_path: str) -> list:
    all_data, page = [], 1
    while True:
        r = httpx.get(
            f"{ODCLOUD_BASE}{uddi_path}",
            params={"serviceKey": API_KEY, "page": page, "perPage": 1000},
            timeout=20,
        )
        body = r.json()
        data = body.get("data", [])
        all_data.extend(data)
        if len(all_data) >= body.get("totalCount", 0) or not data:
            break
        page += 1
    return all_data


def _load(key: str) -> tuple[list, str | None]:
    """엔드포인트 로드. 로컬 CSV 우선, 없으면 odcloud, 둘 다 미설정 시 안내."""
    entry = _ENDPOINTS[key]
    if key in _cache:
        return _cache[key], None

    # 1) 로컬 CSV
    if entry.get("csv"):
        path = DATA_DIR / entry["csv"]
        if path.exists():
            with open(path, encoding=entry.get("encoding", "utf-8-sig"), newline="") as f:
                _cache[key] = list(csv.DictReader(f))
            return _cache[key], None

    # 2) odcloud
    if entry.get("uddi"):
        _cache[key] = _odcloud_load_all(f"/{entry['id']}/v1/uddi:{entry['uddi']}")
        return _cache[key], None

    # 3) 미설정
    return [], (
        f"'{entry['name']}'(data.go.kr {entry['id']}) 데이터가 아직 연결되지 않았습니다. "
        f"MD/CSV를 제공해 주시면 연결됩니다."
    )


def _simple_query(key: str, query: str) -> str:
    rows, msg = _load(key)
    if msg:
        return msg
    if query:
        rows = [r for r in rows if any(query in str(v) for v in r.values())]
    return _wrap(rows, _ENDPOINTS[key]["name"])


# ── 도구: 안전 ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_rail_safety_incidents(query: str = "") -> str:
    """철도 안전사고 정보 조회.
    query: 사고유형·노선·연도 등 부분일치. 미입력 시 전체."""
    return _simple_query("safety_incident", query)


@mcp.tool()
def get_rail_safety_yearbook(query: str = "") -> str:
    """철도 사고현황 연보(통계) 조회.
    query: 연도·구분 등 부분일치. 미입력 시 전체."""
    return _simple_query("safety_yearbook", query)


# ── 도구: 국가계획 ──────────────────────────────────────────────────────────

@mcp.tool()
def get_national_rail_plan(query: str = "") -> str:
    """제4차 국가철도망 구축계획 조회.
    query: 노선·권역·사업명 등 부분일치. 미입력 시 전체."""
    return _simple_query("national_plan", query)


@mcp.tool()
def get_hsr_status(query: str = "", include_plan: bool = False) -> str:
    """고속철도 현황 조회 (include_plan=True 시 사업계획 포함).
    query: 노선·구간 등 부분일치. 미입력 시 전체."""
    status = _simple_query("hsr_status", query)
    if not include_plan:
        return status
    plan = _simple_query("hsr_plan", query)
    return json.dumps(
        {"현황": json.loads(status) if status.startswith("{") else status,
         "사업계획": json.loads(plan) if plan.startswith("{") else plan},
        ensure_ascii=False, indent=2,
    )


# ── 도구: 개발 ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_station_area_development(query: str = "") -> str:
    """역세권 및 복합역사 개발 현황 조회.
    query: 역명·지역·사업명 등 부분일치. 미입력 시 전체."""
    return _simple_query("station_dev", query)


@mcp.tool()
def get_happy_housing(query: str = "") -> str:
    """철도부지 활용 행복주택 건설 현황 조회.
    query: 지역·역명·사업명 등 부분일치. 미입력 시 전체."""
    return _simple_query("happy_housing", query)


# ── 도구: 자산·건설 ─────────────────────────────────────────────────────────

@mcp.tool()
def get_national_property(query: str = "") -> str:
    """철도 국유재산 정보 조회.
    query: 지역·재산구분 등 부분일치. 미입력 시 전체."""
    return _simple_query("national_property", query)


@mcp.tool()
def get_construction_status(query: str = "", include_site: bool = False) -> str:
    """철도건설현황 조회 (include_site=True 시 건설현장정보 포함).
    query: 노선·사업명·지역 등 부분일치. 미입력 시 전체."""
    status = _simple_query("construction", query)
    if not include_site:
        return status
    site = _simple_query("construction_site", query)
    return json.dumps(
        {"건설현황": json.loads(status) if status.startswith("{") else status,
         "현장정보": json.loads(site) if site.startswith("{") else site},
        ensure_ascii=False, indent=2,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8014)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
