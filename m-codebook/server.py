# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"

# odcloud 엔드포인트 정의
ENDPOINTS = {
    "ktx_station":   "/15138145/v1/uddi:bced7ecb-1c3a-44fa-b0a2-e0579433ab6a",  # 차세대예약발매_역코드 (75행)
    "route":         "/15137990/v1/uddi:1f3d12f8-0cfb-46b0-915e-d0920bc63e7d",  # 차세대예약발매_노선코드 (100행)
    "ops_station":   "/15138467/v1/uddi:dcd1dc8d-1fe1-4625-9ec5-fc7eb2542fe4",  # 철도운영정보_역코드 (1255행)
    "common_code":   "/15137989/v1/uddi:0e875993-8248-49f1-b694-89a406bf18c0",  # 차세대예약발매_공통코드 (6행)
    "station_region":"/15154148/v1/uddi:a360f730-9fd5-4a1b-90a5-fd1b571b232b",  # 역별코드+지역본부 (1161행)
}

mcp = FastMCP("KORAIL 코드북")

# ── 데이터셋 기준일 ────────────────────────────────────
_DATASETS = {
    "ktx_station":    ("한국철도공사_차세대예약발매_역코드",       "2024.09.01"),
    "route":          ("한국철도공사_차세대예약발매_노선코드",      "2024.09.01"),
    "ops_station":    ("한국철도공사_철도운영정보_역코드",          "2024.09.01"),
    "station_region": ("한국철도공사_역별 코드 및 지역본부 목록",   "2025.10.31"),
}

# ── 캐시 ───────────────────────────────────────────────
_cache: dict = {}

def _load(key: str) -> list:
    """최초 호출 시 전체 데이터를 가져와 메모리에 캐시."""
    if key in _cache:
        return _cache[key]
    path = ENDPOINTS[key]
    all_data = []
    page = 1
    while True:
        r = httpx.get(
            f"{ODCLOUD_BASE}{path}",
            params={"serviceKey": API_KEY, "page": page, "perPage": 1000},
            timeout=20,
        )
        body = r.json()
        data = body.get("data", [])
        all_data.extend(data)
        if len(all_data) >= body.get("totalCount", 0) or not data:
            break
        page += 1
    _cache[key] = all_data
    return all_data

# ── 헬퍼 ───────────────────────────────────────────────

def _wrap(data: list, dataset: str, ref_date: str) -> str:
    """단일 데이터셋 표준 반환 형식."""
    return json.dumps(
        {
            "data": data,
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋": dataset,
                "데이터기준일": ref_date,
                "건수": len(data),
            },
        },
        ensure_ascii=False,
        indent=2,
    )

# ── 도구 ───────────────────────────────────────────────

@mcp.tool()
def search_station(name: str) -> str:
    """역명(부분일치)으로 역코드·영문명·지역본부를 통합 조회.
    차세대예약발매 역코드(75역, 영문명 포함)와 철도운영정보 역코드(1255역) 두 시스템을 함께 검색.
    예: name='서울', name='수서', name='광명'"""
    name = name.strip()

    # 1) 차세대예약발매_역코드 (영문명 있음)
    ktx = [
        {
            "출처": "차세대예약발매",
            "역코드": str(i.get("역코드(STN_CD)", "")),
            "역명": i.get("한글역명(KOR_STN_NM)", ""),
            "약어명": i.get("역약어명(STN_AVVR_NM)", ""),
            "영문명": i.get("영문역명(STN_ENGM_NM)", ""),
        }
        for i in _load("ktx_station")
        if name in str(i.get("한글역명(KOR_STN_NM)", ""))
    ]

    # 2) 철도운영정보_역코드 (전체 1255역)
    ops = [
        {
            "출처": "철도운영정보",
            "역코드": str(i.get("역코드(STN_CD)", "")),
            "역명": i.get("역명(STN_NM)", ""),
            "약어명": i.get("역약어명(STN_AVVR_NM)", ""),
        }
        for i in _load("ops_station")
        if name in str(i.get("역명(STN_NM)", ""))
    ]

    # 3) 역별코드+지역본부 (지역본부 정보)
    region_map = {
        str(i.get("역코드", "")): i.get("지역본부", "")
        for i in _load("station_region")
    }

    # ops 결과에 지역본부 추가
    for r in ops:
        r["지역본부"] = region_map.get(r["역코드"], "")

    if not ktx and not ops:
        return f"'{name}'에 해당하는 역을 찾을 수 없습니다."
    result = {
        "차세대예약발매_역": ktx,
        "철도운영정보_역": ops,
        "_meta": {
            "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
            "데이터셋별_기준일": {
                "한국철도공사_차세대예약발매_역코드":    "2024.09.01",
                "한국철도공사_철도운영정보_역코드":      "2024.09.01",
                "한국철도공사_역별 코드 및 지역본부 목록": "2025.10.31",
            },
            "건수": {"차세대예약발매_역": len(ktx), "철도운영정보_역": len(ops)},
        },
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def decode_station_code(code: str) -> str:
    """역코드(숫자)로 역명을 조회. 다른 MCP 응답에서 코드가 나왔을 때 사용.
    차세대예약발매(75역)와 철도운영정보(1255역) 두 시스템 동시 검색.
    예: code='3900023'(서울), code='390'(부분매칭 가능)"""
    code = code.strip()
    results = []

    for item in _load("ktx_station"):
        if code in str(item.get("역코드(STN_CD)", "")):
            results.append({
                "출처": "차세대예약발매",
                "역코드": str(item.get("역코드(STN_CD)", "")),
                "역명": item.get("한글역명(KOR_STN_NM)", ""),
                "영문명": item.get("영문역명(STN_ENGM_NM)", ""),
            })

    region_map = {str(i.get("역코드", "")): i.get("지역본부", "") for i in _load("station_region")}

    for item in _load("ops_station"):
        if code in str(item.get("역코드(STN_CD)", "")):
            c = str(item.get("역코드(STN_CD)", ""))
            results.append({
                "출처": "철도운영정보",
                "역코드": c,
                "역명": item.get("역명(STN_NM)", ""),
                "지역본부": region_map.get(c, ""),
            })

    if not results:
        return f"역코드 '{code}'에 해당하는 역을 찾을 수 없습니다."
    return json.dumps(
        {
            "data": results,
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋별_기준일": {
                    "차세대예약발매_역코드_20240901": "2024.09.01",
                    "철도운영정보_역코드_20240901":   "2024.09.01",
                    "역별코드_및_지역본부_20251031":  "2025.10.31",
                },
                "건수": len(results),
            },
        },
        ensure_ascii=False,
        indent=2,
    )


@mcp.tool()
def search_route(name: str = "") -> str:
    """노선명(부분일치)으로 노선코드를 조회. name 미입력 시 전체 노선 목록 반환.
    예: name='경부', name='호남', name='KTX'"""
    data = _load("route")
    if name:
        data = [i for i in data if name in str(i.get("노선명(ROUT_NM)", ""))]
    if not data:
        return f"'{name}'에 해당하는 노선을 찾을 수 없습니다."
    result = [
        {
            "노선코드": i.get("노선코드(ROUT_CD)", ""),
            "노선명": i.get("노선명(ROUT_NM)", ""),
            "우회여부": i.get("우회여부(DTUR_FLG)", ""),
        }
        for i in data
    ]
    return _wrap(result, "한국철도공사_차세대예약발매_노선코드", "2024.09.01")


@mcp.tool()
def list_stations_by_region(region: str) -> str:
    """지역본부명(부분일치)으로 관할 역 목록 조회.
    주요 지역본부: 서울본부, 수도권동부본부, 충청본부, 전라본부, 대구본부, 부산경남본부, 강원본부
    예: region='서울', region='부산경남'"""
    data = [
        {
            "역코드": str(i.get("역코드", "")),
            "역명": i.get("역코드명", ""),
            "지역본부": i.get("지역본부", ""),
        }
        for i in _load("station_region")
        if region in str(i.get("지역본부", ""))
    ]
    if not data:
        return f"'{region}' 지역본부에 해당하는 역을 찾을 수 없습니다."
    return _wrap(data, "한국철도공사_역별 코드 및 지역본부 목록", "2025.10.31")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8004)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
