from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json
import re
import openpyxl
from pathlib import Path

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551457/issueStatistics"
DATA_DIR = Path(__file__).parent / "data"

mcp = FastMCP("KORAIL 발권·이동유형 통계")

_ktx_cache: dict = {}


def fetch_stats(endpoint: str, cond: dict = {}) -> list:
    params = {
        "serviceKey": API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "type": "json",
    }
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    response = httpx.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
    body = response.json().get("response", {}).get("body", {})
    items = (body.get("items") or {}).get("item", [])
    return items if isinstance(items, list) else [items]


@mcp.tool()
def get_mainline_station_per(opr_ymd: str = "", opr_ymd_gte: str = "", opr_ymd_lte: str = "", stn_nm: str = "") -> str:
    """간선열차 역별 승하차 통계 (갱신: 매일 D-2~D-1). opr_ymd=특정일자(YYYYMMDD), opr_ymd_gte/lte=기간, stn_nm=역명"""
    cond = {}
    if opr_ymd: cond["opr_ymd::EQ"] = opr_ymd
    if opr_ymd_gte: cond["opr_ymd::GTE"] = opr_ymd_gte
    if opr_ymd_lte: cond["opr_ymd::LTE"] = opr_ymd_lte
    if stn_nm: cond["stn_nm::LIKE"] = stn_nm
    items = fetch_stats("mainLineStationPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행일자": i.get("opr_ymd"), "역코드": i.get("stn_cd"), "역명": i.get("stn_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_route_per(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 노선별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLineRoutePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "이용인원": i.get("utztn_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_wide_rail_station_per(run_ym: str = "", stn_nm: str = "") -> str:
    """광역철도 역별 승하차 통계 (갱신: 매월 26일, M-1). run_ym=운행연월(YYYYMM), stn_nm=역명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if stn_nm: cond["stn_nm::LIKE"] = stn_nm
    items = fetch_stats("wideRailloadStationPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "역코드": i.get("stn_cd"), "역명": i.get("stn_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_wide_rail_route_per(run_ym: str = "", sbwy_ln_nm: str = "") -> str:
    """광역철도 노선별 이용인원 통계 (갱신: 매월 26일, M-1). run_ym=운행연월(YYYYMM), sbwy_ln_nm=전철선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if sbwy_ln_nm: cond["sbwy_ln_nm::LIKE"] = sbwy_ln_nm
    items = fetch_stats("wideRailloadRoutePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "전철선코드": i.get("sbwy_ln_cd"), "전철선명": i.get("sbwy_ln_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_distance_per(run_ym: str = "") -> str:
    """간선열차 거리별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM)"""
    cond = {"run_ym::EQ": run_ym} if run_ym else {}
    items = fetch_stats("mainLineDistancePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "거리구분코드": i.get("dst_se_cd"), "거리구분명": i.get("dst_se_nm"), "이용인원": i.get("utztn_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_model_per(run_ym: str = "", carmdl: str = "") -> str:
    """간선열차 차량별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), carmdl=차종명(예:KTX)"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if carmdl: cond["carmdl::LIKE"] = carmdl
    items = fetch_stats("mainLineModelPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "이용인원": i.get("utztn_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_day_of_week_per(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 요일별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLineDayOfWeekPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "요일": i.get("dow"), "이용인원": i.get("utztn_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_grade_per(run_ym: str = "", carmdl: str = "") -> str:
    """간선열차 객실별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), carmdl=차종명(예:KTX)"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if carmdl: cond["carmdl::LIKE"] = carmdl
    items = fetch_stats("mainLineGradePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "객실등급코드": i.get("gsrm_grd_cd"), "객실등급명": i.get("gsrm_grd_nm"), "이용인원": i.get("utztn_nope")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_ticketing_stat(ntsl_ym: str = "", ise_type: str = "") -> str:
    """간선열차 발권유형 통계 (갱신: 매월 1일, M-1). ntsl_ym=판매연월(YYYYMM), ise_type=발권유형명"""
    cond = {}
    if ntsl_ym: cond["ntsl_ym::EQ"] = ntsl_ym
    if ise_type: cond["ise_type::LIKE"] = ise_type
    items = fetch_stats("mainLineTicketingStat", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"판매연월": i.get("ntsl_ym"), "발권유형코드": i.get("ise_type_cd"), "발권유형": i.get("ise_type"), "판매비율(%)": i.get("ntsl_rt")} for i in items], ensure_ascii=False, indent=2)


@mcp.tool()
def get_mainline_person_distance(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 노선별 인거리 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLinePersonDistance", cond)
    if not items: return "조회된 데이터가 없습니다."
    return json.dumps([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "인거리": i.get("pd")} for i in items], ensure_ascii=False, indent=2)


def _parse_ktx_stats() -> dict:
    """KTX 구간별 통계 XLSX(2004~2023) 파싱 → 4개 섹션 dict.

    XLSX 구조 (행 인덱스, 0-based):
      Row 3 : 주중 운행횟수 헤더 (구분, 2004, …, 2023)
      Row 4-5: 경부선·호남선 주중 운행횟수 (단위: 회)
      Row 9 : 주말 운행횟수 헤더
      Row 10-11: 경부선·호남선 주말 운행횟수 (단위: 회)
      Row 16: 운임 헤더 (구분, 2004년, …, 2023년)
      Row 17-18: 경부선(서울-부산)·호남선(용산-목포) 운임 (단위: 원)
      Row 23: 이용객 헤더 (구분, 2004년4월~, 2005년, …, 2023년)
      Row 24-25: 경부선(서울-부산)·호남선(서울/용산-목포) 이용객 (단위: 천명/월)
    """
    wb = openpyxl.load_workbook(DATA_DIR / "ktx_segment_stats.xlsx", read_only=True, data_only=True)
    ws = wb.active
    rows = [list(row) for row in ws.iter_rows(values_only=True)]
    wb.close()

    def _years(header_row: list) -> list[str]:
        return [
            re.match(r"(\d{4})", str(v)).group(1)
            for v in header_row[1:]
            if v is not None and re.match(r"\d{4}", str(v))
        ]

    def _section(header_idx: int, data_idxs: list[int]) -> dict:
        years = _years(rows[header_idx])
        sec = {}
        for ridx in data_idxs:
            r = rows[ridx]
            if not r or r[0] is None:
                continue
            route = str(r[0]).strip()
            sec[route] = {
                years[i]: r[i + 1]
                for i in range(len(years))
                if i + 1 < len(r) and r[i + 1] is not None
            }
        return sec

    return {
        "운행횟수_주중": _section(3, [4, 5]),
        "운행횟수_주말": _section(9, [10, 11]),
        "운임_원":       _section(16, [17, 18]),
        "이용객_천명월": _section(23, [24, 25]),
    }


@mcp.tool()
def get_ktx_long_term_stats(
    category: str = "",
    route: str = "",
    year_from: int = 0,
    year_to: int = 0,
) -> str:
    """KTX 장기 통계 조회 (2004~2023년, 로컬 XLSX).

    경부선(서울-부산)·호남선(용산-목포) 2개 노선의 20년 역사 데이터.

    category 선택:
      "운행횟수_주중" — 화요일 기준 편도 운행 횟수 (단위: 회)
      "운행횟수_주말" — 토요일 기준 편도 운행 횟수 (단위: 회)
      "운임_원"       — 해당 연도 운임 (단위: 원, 서울-부산·용산-목포 기준)
      "이용객_천명월" — 월평균 이용객 수 (단위: 천명/월)
      빈값           — 위 4개 카테고리 전체 반환

    route: "경부선" | "호남선" 부분일치 필터 (빈값=전체)
    year_from / year_to: 연도 범위 필터 (예: year_from=2010, year_to=2019)
    """
    if "ktx_stats" not in _ktx_cache:
        _ktx_cache["ktx_stats"] = _parse_ktx_stats()

    raw = _ktx_cache["ktx_stats"]
    valid_cats = list(raw.keys())

    # category 필터
    if category:
        if category not in raw:
            return json.dumps(
                {"error": f"category '{category}' 없음. 사용 가능: {valid_cats}"},
                ensure_ascii=False,
            )
        data = {category: raw[category]}
    else:
        data = raw

    # route·year 범위 필터
    filtered = {}
    for cat_name, cat_data in data.items():
        cat_filtered = {}
        for route_name, year_dict in cat_data.items():
            if route and route not in route_name:
                continue
            if year_from or year_to:
                year_dict = {
                    y: v for y, v in year_dict.items()
                    if (not year_from or int(y) >= year_from)
                    and (not year_to or int(y) <= year_to)
                }
            if year_dict:
                cat_filtered[route_name] = year_dict
        if cat_filtered:
            filtered[cat_name] = cat_filtered

    if not filtered:
        return json.dumps({"error": "조건에 맞는 데이터 없음."}, ensure_ascii=False)

    return json.dumps(
        {
            "data": filtered,
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋": "한국철도공사_KTX 구간별 통계 데이터",
                "데이터기준일": "2024.01.01",
                "범위": "경부선(서울-부산)·호남선(용산-목포), 2004~2023년",
                "단위": {
                    "운행횟수_주중": "회 (화요일 기준)",
                    "운행횟수_주말": "회 (토요일 기준)",
                    "운임_원": "원",
                    "이용객_천명월": "천명/월",
                },
            },
        },
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
