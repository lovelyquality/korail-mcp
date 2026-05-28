from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551457/convenience"
ODCLOUD_BASE = "https://api.odcloud.kr/api"

mcp = FastMCP("KORAIL 편의시설·역 정보")

_cache: dict[str, list] = {}


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────

def _wrap(data: list, dataset: str, ref_date: str) -> str:
    """데이터 + 메타(출처·기준일·건수) 통합 반환. 모든 도구의 표준 반환 형식."""
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


# ── B551457 REST 헬퍼 ────────────────────────────────────────────────────────

def _fetch_all(endpoint: str) -> list:
    response = httpx.get(
        f"{BASE_URL}/{endpoint}",
        params={"serviceKey": API_KEY, "pageNo": 1, "numOfRows": 1000},
        timeout=15,
    )
    body = response.json().get("response", {}).get("body", {})
    items = body.get("items", {}).get("item", [])
    return items if isinstance(items, list) else [items]


# ── odcloud 헬퍼 ──────────────────────────────────────────────────────────────

def _odcloud_get(path: str, page: int = 1, per_page: int = 1000) -> dict:
    r = httpx.get(
        f"{ODCLOUD_BASE}{path}",
        params={"serviceKey": API_KEY, "page": page, "perPage": per_page},
        timeout=20,
    )
    return r.json()


def _odcloud_load_all(path: str) -> list:
    all_data, page = [], 1
    while True:
        body = _odcloud_get(path, page=page, per_page=1000)
        data = body.get("data", [])
        all_data.extend(data)
        if len(all_data) >= body.get("totalCount", 0) or not data:
            break
        page += 1
    return all_data


def _get(key: str, loader) -> list:
    if key not in _cache:
        _cache[key] = loader()
    return _cache[key]


# ── 도구 1~3: B551457 REST (기존, 메타 추가) ─────────────────────────────────

@mcp.tool()
def get_station_facilities(station_name: str) -> str:
    """역 이름으로 편의시설 정보 조회 (B551457 실시간 API).
    엘리베이터·에스컬레이터·화장실·수유실·종합안내센터 유무.
    station_name: 역 이름 부분일치 (예: '서울', '부산')
    ※ 데이터기준일: 실시간 API (날짜 미포함). 현장 변경이 즉시 반영되지 않을 수 있음."""
    items = _fetch_all("stationFacilities")
    matches = [i for i in items if station_name in i.get("stn_nm", "")]
    if not matches:
        return f"'{station_name}'에 해당하는 역을 찾을 수 없습니다."
    data = [
        {
            "역명": i.get("stn_nm"),
            "역코드": i.get("stn_cd"),
            "엘리베이터": f"{i.get('elevt_cnt')}개",
            "에스컬레이터": f"{i.get('esclt_cnt')}개",
            "일반화장실": "있음" if i.get("gen_tolt_estnc") == "Y" else "없음",
            "수유실": "있음" if i.get("nrsrm_estnc") == "Y" else "없음",
            "종합안내센터": "있음" if i.get("altm_lead_cntr_estnc") == "Y" else "없음",
        }
        for i in matches
    ]
    return _wrap(data, "한국철도공사_편의시설정보", "실시간 API")


@mcp.tool()
def get_accessible_facilities(station_name: str) -> str:
    """역 이름으로 교통약자(장애인) 편의시설 조회 (B551457 실시간 API).
    휠체어리프트·장애인경사로·장애인화장실 유무.
    station_name: 역 이름 부분일치 (예: '서울', '부산')
    ※ 데이터기준일: 실시간 API. 현장 변경이 즉시 반영되지 않을 수 있음."""
    items = _fetch_all("weekPersonFacilities")
    matches = [i for i in items if station_name in i.get("stn_nm", "")]
    if not matches:
        return f"'{station_name}'에 해당하는 역을 찾을 수 없습니다."
    data = [
        {
            "역명": i.get("stn_nm"),
            "역코드": i.get("stn_cd"),
            "휠체어리프트": f"{i.get('whlch_liftt_cnt')}개",
            "장애인경사로": "있음" if i.get("pwdbs_slwy_estnc") == "Y" else "없음",
            "장애인화장실": "있음" if i.get("pwdbs_tolt_estnc") == "Y" else "없음",
        }
        for i in matches
    ]
    return _wrap(data, "한국철도공사_편의시설정보", "실시간 API")


@mcp.tool()
def list_stations_with_elevator() -> str:
    """엘리베이터가 설치된 역 목록 전체 조회 (B551457 실시간 API).
    ※ 데이터기준일: 실시간 API. 현장 변경이 즉시 반영되지 않을 수 있음."""
    items = _fetch_all("stationFacilities")
    matches = [i for i in items if int(i.get("elevt_cnt", 0) or 0) > 0]
    data = [{"역명": i.get("stn_nm"), "엘리베이터 수": i.get("elevt_cnt")} for i in matches]
    return _wrap(data, "한국철도공사_편의시설정보", "실시간 API")


# ── 도구 4~6: odcloud 정적 데이터 (신규) ─────────────────────────────────────

@mcp.tool()
def get_station_facilities_detail(station_name: str = "") -> str:
    """역사 내외부 시설현황 조회 (odcloud, 2024.12.31 기준, 288개 역).
    엘리베이터·에스컬레이터·휠체어리프트·장애인경사로·장애인화장실·일반화장실·
    모유수유실·종합안내소·환승주차장(면수) 수량 포함.
    station_name: 역명 부분일치 (예: '서울', '광명'). 미입력 시 전체 반환.
    ※ B551457 편의시설 API 대비 수량 정보 더 풍부하나 데이터 기준일 고정(2024.12.31)."""
    PATH = "/15090379/v1/uddi:6a8ae00e-4d06-4bdd-af70-c360b9fbbbc6"
    rows = _get("station_facilities_detail", lambda: _odcloud_load_all(PATH))
    result = rows
    if station_name:
        result = [r for r in result if station_name in str(r.get("역명", ""))]
    if not result:
        return f"'{station_name}'에 해당하는 역을 찾을 수 없습니다."
    return _wrap(result, "한국철도공사_역사내외부 시설현황", "2024.12.31")


@mcp.tool()
def get_station_transfer_info(station_name: str = "", line_name: str = "") -> str:
    """역별 타 교통수단과 환승현황 조회 (odcloud, 2024.12.31 기준, 93개 역).
    노선별·역별 KTX·광역철도·도시철도 역수 및 환승주차장 면수 포함.
    station_name: 역명 부분일치 (예: '서울', '동대구').
    line_name: 노선명 부분일치 (예: '경부고속', '호남선').
    미입력 시 전체 반환."""
    PATH = "/15090378/v1/uddi:57b94475-833c-4242-9a42-cd7d3bfef4d8"
    rows = _get("station_transfer_info", lambda: _odcloud_load_all(PATH))
    result = rows
    if station_name:
        result = [r for r in result if station_name in str(r.get("역별", ""))]
    if line_name:
        result = [r for r in result if line_name in str(r.get("노선별", ""))]
    if not result:
        return "조회된 환승현황이 없습니다."
    return _wrap(result, "한국철도공사_역별 타 교통수단과 환승현황", "2024.12.31")


@mcp.tool()
def get_station_location(station_name: str = "", region: str = "") -> str:
    """역 위치 정보 조회 (odcloud, 2024.04.01 기준, 202개 간선 철도역).
    지역본부·역명·위도·경도·출입구 개수 포함.
    station_name: 역명 부분일치 (예: '서울', '부산').
    region: 지역본부 부분일치 (예: '서울본부', '대전충청', '강원본부').
    미입력 시 전체 반환."""
    PATH = "/15127532/v1/uddi:c1d09745-9e5c-48e4-b26c-c1833592509c"
    rows = _get("station_location", lambda: _odcloud_load_all(PATH))
    result = rows
    if station_name:
        result = [r for r in result if station_name in str(r.get("역명", ""))]
    if region:
        result = [r for r in result if region in str(r.get("지역본부", ""))]
    if not result:
        return "조회된 역 위치 정보가 없습니다."
    return _wrap(result, "한국철도공사_역 위치 정보", "2024.04.01")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
