"""korail-procurement MCP server.

Local CSV files from data.go.kr (KORAIL procurement/material data).
- material_group.csv  : 자재그룹코드 (999건)
- g2b_item.csv        : G2B 분류번호·품명 (13,400건)
- material_attr.csv   : 자재속성정보 (34,630건)
- material_equipment.csv : 자재대상장비 (24,258건)
"""

import csv
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(__file__).parent / "data"

mcp = FastMCP("korail-procurement")

_cache: dict[str, list[dict[str, Any]]] = {}


def _load_csv(filename: str) -> list[dict[str, Any]]:
    with open(DATA_DIR / filename, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _get(key: str, loader) -> list[dict[str, Any]]:
    if key not in _cache:
        _cache[key] = loader()
    return _cache[key]


def _contains(value: Any, q: str) -> bool:
    return q in str(value) if value is not None else False


def _make_meta(dataset: str, ref_date: str) -> dict:
    return {
        "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
        "데이터셋": dataset,
        "데이터기준일": ref_date,
    }


@mcp.tool()
def search_material_group(query: str = "", active_only: bool = True, limit: int = 100) -> dict:
    """자재그룹코드 검색 (총 999건, 로컬 CSV).

    그룹코드(예: BB1300) 또는 그룹명칭(예: EMU용품)으로 부분일치 검색.
    active_only=True 시 사용 중(Y)인 코드만 반환.
    """
    rows = _get("material_group", lambda: _load_csv("material_group.csv"))
    if active_only:
        rows = [r for r in rows if r.get("그룹코드사용여부(GRP_CODEUSE)") == "Y"]
    if query:
        q = query.strip()
        rows = [
            r for r in rows
            if _contains(r.get("그룹코드(GRP_CODE)"), q)
            or _contains(r.get("그룹명칭(GRP_TEXT)"), q)
        ]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_물품_자재그룹코드", "2024.09.01"),
    }


@mcp.tool()
def search_g2b_item(query: str = "", active_only: bool = True, limit: int = 50) -> dict:
    """G2B(나라장터) 분류번호·품명 검색 (총 13,400건, 로컬 CSV).

    G2B분류번호(8자리) 또는 G2B품명(한글·영문)으로 부분일치 검색.
    품명해설 포함. active_only=True 시 사용 코드만 반환.
    """
    rows = _get("g2b_item", lambda: _load_csv("g2b_item.csv"))
    if active_only:
        rows = [r for r in rows if r.get("G2B코드사용여부") == "Y"]
    if query:
        q = query.strip()
        rows = [
            r for r in rows
            if _contains(r.get("G2B분류번호"), q)
            or _contains(r.get("G2B품명"), q)
            or _contains(r.get("G2B영문품명"), q)
        ]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_물품정보_자재속성_G2B분류번호", "2024.09.01"),
    }


@mcp.tool()
def search_material_attr(
    material_no: str = "",
    g2b_code: str = "",
    attr_code: str = "",
    limit: int = 100,
) -> dict:
    """자재속성정보 조회 (총 34,630건, 로컬 CSV).

    자재번호·G2B분류번호·속성코드로 조회. 자재별 속성값(규격·재질·치수 등) 확인.
    최소 1개 필터 권장 (미지정 시 앞에서 limit건 반환).
    """
    rows = _get("material_attr", lambda: _load_csv("material_attr.csv"))
    if material_no:
        rows = [r for r in rows if r.get("자재번호") == material_no.strip()]
    if g2b_code:
        rows = [r for r in rows if _contains(r.get("G2B분류번호"), g2b_code.strip())]
    if attr_code:
        rows = [r for r in rows if r.get("속성코드") == attr_code.strip()]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_물품정보_자재속성정보", "2024.09.01"),
    }


@mcp.tool()
def search_material_equipment(
    material_no: str = "",
    equipment: str = "",
    limit: int = 100,
) -> dict:
    """자재대상장비 조회 (총 24,258건, 로컬 CSV).

    특정 자재번호가 사용되는 장비 코드 조회, 또는 장비코드로 해당 자재 역검색.
    """
    rows = _get("material_equipment", lambda: _load_csv("material_equipment.csv"))
    if material_no:
        rows = [r for r in rows if r.get("자재번호") == material_no.strip()]
    if equipment:
        rows = [r for r in rows if _contains(r.get("대상장비"), equipment.strip())]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_물품정보_자재대상장비", "2024.09.01"),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8011)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
