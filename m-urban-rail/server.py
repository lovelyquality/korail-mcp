"""korail-urban-rail MCP server.

전국 도시철도(수도권1~9호선, 부산·대구·대전·광주·인천, 경전철 등) 역사 종합정보.
국가철도공단(KRIC) data.go.kr 오픈API 26건 → 기능 그룹별 9개 도구로 통합.

데이터 소스: data.go.kr 오픈API (기존 DATA_GO_KR_API_KEY 사용, 활용신청 필요)
  - 삭제된 m-kric(openapi.kric.go.kr 직접 API, 구버전)와 다름.
  - 이쪽은 data.go.kr 표준 odcloud 자동변환 API.

⚠️ 구현 상태: 데이터 구조(기능 그룹 매핑 + 도구 인터페이스) 완성.
   각 API의 odcloud UUID는 활용신청 후 MD로 확인하여 _ENDPOINTS의 'uddi'에 채울 것.
   UUID가 빈 값이면 도구는 안내 메시지를 반환한다(크래시 없음).

기능 그룹:
  접근성(C2): 엘리베이터·에스컬레이터·휠체어리프트·안전발판·승강장이격거리·점자·장애인화장실
  편의      : 화장실·수유실·물품보관함·ATM·유실물센터
  안전(C3)  : 제세동기·소화설비·비상콜폰·공기호흡기·스크린도어
  안내      : 역사정보·출구정보·환승정보·운행시각표·전체노선정보·열차시각표
"""

import os
import json
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(encoding="utf-8-sig")
API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"

mcp = FastMCP("korail-urban-rail")

_cache: dict[str, list] = {}


# ── 엔드포인트 매핑 (data.go.kr 데이터 번호 기준) ────────────────────────────
# uddi: 활용신청 후 Swagger(https://infuser.odcloud.kr/oas/docs?namespace={id}/v1)에서
#       확인하여 채울 것. MD 제공 시 일괄 입력.

_ACCESSIBILITY_MAP = {
    "elevator":          {"id": "15041682", "uddi": "", "name": "역사별 엘리베이터 현황"},
    "elevator_route":    {"id": "15041689", "uddi": "", "name": "역사별 엘리베이터 이동동선"},
    "escalator":         {"id": "15041683", "uddi": "", "name": "역사별 에스컬레이터 현황"},
    "wheelchair_lift":   {"id": "15041686", "uddi": "", "name": "역사별 휠체어리프트 위치"},
    "wheelchair_route":  {"id": "15041690", "uddi": "", "name": "역사별 휠체어리프트 이동동선"},
    "safety_step":       {"id": "15041688", "uddi": "", "name": "역사별 안전발판 설치유무"},
    "platform_gap":      {"id": "15041687", "uddi": "", "name": "역사별 승강장 이격거리"},
    "braille":           {"id": "15041685", "uddi": "", "name": "역사별 점자표시유무"},
    "disabled_toilet":   {"id": "15041692", "uddi": "", "name": "역사별 장애인 화장실 위치"},
    "adjacent_elevator": {"id": "15041691", "uddi": "", "name": "역사별 인접 승강기 차량번호"},
}

_AMENITY_MAP = {
    "toilet":       {"id": "15041679", "uddi": "", "name": "역사별 화장실 현황"},
    "nursing_room": {"id": "15041681", "uddi": "", "name": "역사별 수유실 현황"},
    "locker":       {"id": "15041678", "uddi": "", "name": "역사별 물품보관함 현황"},
    "atm":          {"id": "15041680", "uddi": "", "name": "역사별 ATM 기기위치"},
    "lost_found":   {"id": "15041684", "uddi": "", "name": "역사별 유실물센터 정보"},
}

_SAFETY_MAP = {
    "defibrillator":   {"id": "15041671", "uddi": "", "name": "역사별 제세동기 현황"},
    "fire_extinguish": {"id": "15057421", "uddi": "", "name": "역사별 소화설비 현황"},
    "emergency_phone": {"id": "15041667", "uddi": "", "name": "역사별 비상콜폰 현황"},
    "air_respirator":  {"id": "15056590", "uddi": "", "name": "역사별 공기호흡기 현황"},
    "screen_door":     {"id": "15041672", "uddi": "", "name": "역사별 스크린도어 현황"},
}

_INFO_MAP = {
    "station":        {"id": "15041676", "uddi": "", "name": "역사별 정보"},
    "exit":           {"id": "15041677", "uddi": "", "name": "역사별 출구정보"},
    "transfer":       {"id": "15041673", "uddi": "", "name": "역사별 환승정보"},
    "timetable":      {"id": "15041674", "uddi": "", "name": "역사별 운행시각표"},
    "lines":          {"id": "15041666", "uddi": "", "name": "도시철도 전체노선정보"},
    "train_timetable":{"id": "15041665", "uddi": "", "name": "열차별운행시각표"},
}


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────

def _wrap(data: list, dataset: str, extra_meta: dict | None = None) -> str:
    """데이터 + 메타(출처·데이터셋·건수) 표준 반환 형식."""
    meta = {
        "출처": "국가철도공단(KRIC) 공공데이터포털 (data.go.kr)",
        "데이터셋": dataset,
        "건수": len(data),
    }
    if extra_meta:
        meta.update(extra_meta)
    return json.dumps({"data": data, "_meta": meta}, ensure_ascii=False, indent=2)


def _odcloud_load_all(uddi_path: str) -> list[dict[str, Any]]:
    """odcloud 엔드포인트 전체 페이지 로드."""
    all_data: list = []
    page = 1
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


def _get(cache_key: str, entry: dict) -> tuple[list, str | None]:
    """엔드포인트 entry({id,uddi,name})로 데이터 로드.
    uddi 미설정 시 (빈 리스트, 안내메시지) 반환."""
    if not entry.get("uddi"):
        return [], (
            f"'{entry['name']}'(data.go.kr {entry['id']}) API의 UUID가 아직 설정되지 않았습니다. "
            f"활용신청 후 MD를 제공해 주시면 연결됩니다."
        )
    if cache_key not in _cache:
        path = f"/{entry['id']}/v1/uddi:{entry['uddi']}"
        _cache[cache_key] = _odcloud_load_all(path)
    return _cache[cache_key], None


def _query_group(group_map: dict, sub_type: str, station_name: str,
                 station_field_candidates: tuple = ("역사명", "역명", "정거장명", "STATION_NM")) -> str:
    """기능 그룹(접근성/편의/안전) 공통 조회 로직.
    sub_type='all'이면 그룹 내 전체 종류 순회."""
    if sub_type != "all" and sub_type not in group_map:
        return json.dumps(
            {"error": f"'{sub_type}' 미지원. 사용가능: {list(group_map.keys()) + ['all']}"},
            ensure_ascii=False, indent=2,
        )

    targets = list(group_map.keys()) if sub_type == "all" else [sub_type]
    result: dict[str, Any] = {}
    pending: list[str] = []

    for key in targets:
        entry = group_map[key]
        rows, msg = _get(key, entry)
        if msg:
            pending.append(msg)
            continue
        if station_name:
            rows = [
                r for r in rows
                if any(station_name in str(r.get(f, "")) for f in station_field_candidates)
            ]
        result[key] = {"종류": entry["name"], "건수": len(rows), "data": rows}

    return json.dumps(
        {
            "data": result,
            "_meta": {
                "출처": "국가철도공단(KRIC) 공공데이터포털 (data.go.kr)",
                "조회종류": targets,
                "미연결API": pending,
            },
        },
        ensure_ascii=False, indent=2,
    )


# ── 도구: 접근성 (C2 접근성 Agent) ──────────────────────────────────────────

@mcp.tool()
def get_urban_accessibility(facility_type: str = "all", station_name: str = "") -> str:
    """전국 도시철도 역사 접근성 시설 조회 (교통약자).

    facility_type:
      "elevator"          엘리베이터 현황
      "elevator_route"    엘리베이터 이동동선
      "escalator"         에스컬레이터 현황
      "wheelchair_lift"   휠체어리프트 위치
      "wheelchair_route"  휠체어리프트 이동동선
      "safety_step"       승강장 안전발판 설치유무
      "platform_gap"      승강장-차량 이격거리
      "braille"           점자표시 유무
      "disabled_toilet"   장애인 화장실 위치
      "adjacent_elevator" 인접 승강기 차량번호
      "all"               위 전체 (기본값, 응답이 큼)
    station_name: 역명 부분일치 (예: '서울', '강남'). 미입력 시 전체.
    """
    return _query_group(_ACCESSIBILITY_MAP, facility_type, station_name)


# ── 도구: 편의시설 ──────────────────────────────────────────────────────────

@mcp.tool()
def get_urban_amenity(amenity_type: str = "all", station_name: str = "") -> str:
    """전국 도시철도 역사 편의시설 조회.

    amenity_type:
      "toilet"       화장실 현황
      "nursing_room" 수유실 현황
      "locker"       물품보관함 현황
      "atm"          ATM 기기위치
      "lost_found"   유실물센터 정보
      "all"          위 전체 (기본값)
    station_name: 역명 부분일치. 미입력 시 전체.
    """
    return _query_group(_AMENITY_MAP, amenity_type, station_name)


# ── 도구: 안전시설 (C3 고객응대 Agent) ──────────────────────────────────────

@mcp.tool()
def get_urban_safety(safety_type: str = "all", station_name: str = "") -> str:
    """전국 도시철도 역사 안전시설 조회.

    safety_type:
      "defibrillator"   제세동기(AED) 현황
      "fire_extinguish" 소화설비 현황
      "emergency_phone" 비상콜폰 현황
      "air_respirator"  공기호흡기 현황
      "screen_door"     스크린도어 현황
      "all"             위 전체 (기본값)
    station_name: 역명 부분일치. 미입력 시 전체.
    """
    return _query_group(_SAFETY_MAP, safety_type, station_name)


# ── 도구: 역사 안내정보 ─────────────────────────────────────────────────────

@mcp.tool()
def get_urban_station_info(station_name: str = "") -> str:
    """전국 도시철도 역사 기본정보 조회 (역사별 정보).
    station_name: 역명 부분일치. 미입력 시 전체."""
    entry = _INFO_MAP["station"]
    rows, msg = _get("info_station", entry)
    if msg:
        return msg
    if station_name:
        rows = [r for r in rows if any(station_name in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


@mcp.tool()
def get_urban_exit_info(station_name: str = "") -> str:
    """전국 도시철도 역사 출구정보 조회.
    station_name: 역명 부분일치. 미입력 시 전체."""
    entry = _INFO_MAP["exit"]
    rows, msg = _get("info_exit", entry)
    if msg:
        return msg
    if station_name:
        rows = [r for r in rows if any(station_name in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


@mcp.tool()
def get_urban_transfer_info(station_name: str = "") -> str:
    """전국 도시철도 역사 환승정보 조회.
    station_name: 역명 부분일치. 미입력 시 전체."""
    entry = _INFO_MAP["transfer"]
    rows, msg = _get("info_transfer", entry)
    if msg:
        return msg
    if station_name:
        rows = [r for r in rows if any(station_name in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


@mcp.tool()
def get_urban_timetable(station_name: str = "") -> str:
    """전국 도시철도 역사별 운행시각표 조회.
    station_name: 역명 부분일치. 미입력 시 전체(응답 큼)."""
    entry = _INFO_MAP["timetable"]
    rows, msg = _get("info_timetable", entry)
    if msg:
        return msg
    if station_name:
        rows = [r for r in rows if any(station_name in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


@mcp.tool()
def get_urban_lines(line_name: str = "") -> str:
    """전국 도시철도 전체 노선정보 조회.
    line_name: 노선명 부분일치 (예: '2호선', '신분당'). 미입력 시 전체."""
    entry = _INFO_MAP["lines"]
    rows, msg = _get("info_lines", entry)
    if msg:
        return msg
    if line_name:
        rows = [r for r in rows if any(line_name in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


@mcp.tool()
def get_urban_train_timetable(query: str = "") -> str:
    """전국 도시철도 열차별 운행시각표 조회.
    query: 열차번호/노선 등 부분일치. 미입력 시 전체(응답 큼)."""
    entry = _INFO_MAP["train_timetable"]
    rows, msg = _get("info_train_timetable", entry)
    if msg:
        return msg
    if query:
        rows = [r for r in rows if any(query in str(v) for v in r.values())]
    return _wrap(rows, entry["name"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8013)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
