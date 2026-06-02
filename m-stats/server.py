from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json
import re
import openpyxl
from pathlib import Path

load_dotenv(encoding='utf-8-sig')

PROXY_BASE = os.getenv("KORAIL_PROXY_URL", "https://korail-mcp-proxy.lovelymong.workers.dev") + "/proxy"
BASE_URL = f"{PROXY_BASE}/apis/B551457/issueStatistics"
CARRIAGE_BASE = f"{PROXY_BASE}/apis/B551457/carriageStatistics"
DATA_DIR = Path(__file__).parent / "data"

mcp = FastMCP("KORAIL 여객·화물 수송통계")

_ktx_cache: dict = {}


def _wrap(data: list, dataset: str) -> str:
    """데이터 + 메타(출처·건수) 통합 반환. 모든 도구의 표준 반환 형식."""
    return json.dumps(
        {
            "data": data,
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋": dataset,
                "건수": len(data),
            },
        },
        ensure_ascii=False,
        indent=2,
    )


def fetch_stats(endpoint: str, cond: dict = {}) -> list:
    """issueStatistics 엔드포인트(발권·이용유형 통계)에서 데이터를 가져옵니다 (최대 1000건)."""
    params = {
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


def fetch_carriage(endpoint: str, cond: dict = {}) -> list:
    """carriageStatistics 엔드포인트(역별 수송실적)에서 데이터를 가져옵니다 (최대 1000건).
    issueStatistics와 달리 type 파라미터를 받지 않으므로 별도 헬퍼로 둔다."""
    params = {"pageNo": 1, "numOfRows": 1000}
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    response = httpx.get(f"{CARRIAGE_BASE}/{endpoint}", params=params, timeout=15)
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
    return _wrap([{"운행일자": i.get("opr_ymd"), "역코드": i.get("stn_cd"), "역명": i.get("stn_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], "issueStatistics/mainLineStationPer")


@mcp.tool()
def get_mainline_route_per(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 노선별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLineRoutePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "이용인원": i.get("utztn_nope")} for i in items], "issueStatistics/mainLineRoutePer")


@mcp.tool()
def get_wide_rail_station_per(run_ym: str = "", stn_nm: str = "") -> str:
    """광역철도 역별 승하차 통계 (갱신: 매월 26일, M-1). run_ym=운행연월(YYYYMM), stn_nm=역명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if stn_nm: cond["stn_nm::LIKE"] = stn_nm
    items = fetch_stats("wideRailloadStationPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "역코드": i.get("stn_cd"), "역명": i.get("stn_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], "issueStatistics/wideRailloadStationPer")


@mcp.tool()
def get_wide_rail_route_per(run_ym: str = "", sbwy_ln_nm: str = "") -> str:
    """광역철도 노선별 이용인원 통계 (갱신: 매월 26일, M-1). run_ym=운행연월(YYYYMM), sbwy_ln_nm=전철선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if sbwy_ln_nm: cond["sbwy_ln_nm::LIKE"] = sbwy_ln_nm
    items = fetch_stats("wideRailloadRoutePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "전철선코드": i.get("sbwy_ln_cd"), "전철선명": i.get("sbwy_ln_nm"), "승차인원": i.get("ride_nope"), "하차인원": i.get("goff_nope")} for i in items], "issueStatistics/wideRailloadRoutePer")


@mcp.tool()
def get_mainline_distance_per(run_ym: str = "") -> str:
    """간선열차 거리별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM)"""
    cond = {"run_ym::EQ": run_ym} if run_ym else {}
    items = fetch_stats("mainLineDistancePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "거리구분코드": i.get("dst_se_cd"), "거리구분명": i.get("dst_se_nm"), "이용인원": i.get("utztn_nope")} for i in items], "issueStatistics/mainLineDistancePer")


@mcp.tool()
def get_mainline_model_per(run_ym: str = "", carmdl: str = "") -> str:
    """간선열차 차량별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), carmdl=차종명(예:KTX)"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if carmdl: cond["carmdl::LIKE"] = carmdl
    items = fetch_stats("mainLineModelPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "이용인원": i.get("utztn_nope")} for i in items], "issueStatistics/mainLineModelPer")


@mcp.tool()
def get_mainline_day_of_week_per(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 요일별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLineDayOfWeekPer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "요일": i.get("dow"), "이용인원": i.get("utztn_nope")} for i in items], "issueStatistics/mainLineDayOfWeekPer")


@mcp.tool()
def get_mainline_grade_per(run_ym: str = "", carmdl: str = "") -> str:
    """간선열차 객실별 이용인원 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), carmdl=차종명(예:KTX)"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if carmdl: cond["carmdl::LIKE"] = carmdl
    items = fetch_stats("mainLineGradePer", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "차종코드": i.get("carmdl_cd"), "차종": i.get("carmdl"), "객실등급코드": i.get("gsrm_grd_cd"), "객실등급명": i.get("gsrm_grd_nm"), "이용인원": i.get("utztn_nope")} for i in items], "issueStatistics/mainLineGradePer")


@mcp.tool()
def get_mainline_ticketing_stat(ntsl_ym: str = "", ise_type: str = "") -> str:
    """간선열차 발권유형 통계 (갱신: 매월 1일, M-1). ntsl_ym=판매연월(YYYYMM), ise_type=발권유형명"""
    cond = {}
    if ntsl_ym: cond["ntsl_ym::EQ"] = ntsl_ym
    if ise_type: cond["ise_type::LIKE"] = ise_type
    items = fetch_stats("mainLineTicketingStat", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"판매연월": i.get("ntsl_ym"), "발권유형코드": i.get("ise_type_cd"), "발권유형": i.get("ise_type"), "판매비율(%)": i.get("ntsl_rt")} for i in items], "issueStatistics/mainLineTicketingStat")


@mcp.tool()
def get_mainline_person_distance(run_ym: str = "", rte_nm: str = "") -> str:
    """간선열차 노선별 인거리 통계 (갱신: 매월 1일, M-2). run_ym=운행연월(YYYYMM), rte_nm=노선명"""
    cond = {}
    if run_ym: cond["run_ym::EQ"] = run_ym
    if rte_nm: cond["rte_nm::LIKE"] = rte_nm
    items = fetch_stats("mainLinePersonDistance", cond)
    if not items: return "조회된 데이터가 없습니다."
    return _wrap([{"운행연월": i.get("run_ym"), "노선코드": i.get("rte_cd"), "노선명": i.get("rte_nm"), "인거리": i.get("pd")} for i in items], "issueStatistics/mainLinePersonDistance")


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


# ─── 수송실적 (구 m-carriage, carriageStatistics) ────────────────────────────

@mcp.tool()
def get_mainline_carriage(
    run_ymd: str = "",
    run_ymd_gte: str = "",
    run_ymd_lte: str = "",
    mrnt_cd: str = "",
    mrnt_nm: str = "",
    stn_cd: str = "",
    stn_nm: str = "",
) -> str:
    """
    간선 여객열차 수송실적 조회. 역별 승하차 인원수를 제공합니다.
    운행일자, 주운행선(경부선·호남선 등), 역 기준으로 필터링 가능.

    Args:
        run_ymd: 특정 운행일자 (YYYYMMDD). 입력 시 해당 날짜만 조회.
        run_ymd_gte: 운행일자 시작 (YYYYMMDD, 이후)
        run_ymd_lte: 운행일자 종료 (YYYYMMDD, 이전)
        mrnt_cd: 주운행선코드 (예: "01"=경부선)
        mrnt_nm: 주운행선명 (예: "경부선", "호남선")
        stn_cd: 역코드 (예: "3900023"=서울)
        stn_nm: 역명 (예: "서울", "부산")
    """
    cond = {}
    if run_ymd:
        cond["run_ymd::GTE"] = run_ymd
        cond["run_ymd::LTE"] = run_ymd
    else:
        if run_ymd_gte:
            cond["run_ymd::GTE"] = run_ymd_gte
        if run_ymd_lte:
            cond["run_ymd::LTE"] = run_ymd_lte
    if mrnt_cd:
        cond["mrnt_cd::EQ"] = mrnt_cd
    if mrnt_nm:
        cond["mrnt_nm::EQ"] = mrnt_nm
    if stn_cd:
        cond["stn_cd::EQ"] = stn_cd
    if stn_nm:
        cond["stn_nm::EQ"] = stn_nm

    items = fetch_carriage("mainLineTravelerTrain", cond)
    if not items:
        return "조회된 간선 여객열차 수송실적이 없습니다."
    return _wrap(items, "B551457/carriageStatistics/mainLineTravelerTrain")


@mcp.tool()
def get_wide_area_carriage(
    run_ymd: str = "",
    run_ymd_gte: str = "",
    run_ymd_lte: str = "",
    sbwy_ln_cd: str = "",
    sbwy_ln_nm: str = "",
    sbwy_stn_cd: str = "",
    sbwy_stn_nm: str = "",
    tmwd_se_cd: str = "",
) -> str:
    """
    광역 여객열차 수송실적 조회. 전철역별 시간대별 승하차 인원수를 제공합니다.
    광역철도(수도권 전철 등) 이용 통계 조회에 사용.

    Args:
        run_ymd: 특정 운행일자 (YYYYMMDD). 입력 시 해당 날짜만 조회.
        run_ymd_gte: 운행일자 시작 (YYYYMMDD, 이후)
        run_ymd_lte: 운행일자 종료 (YYYYMMDD, 이전)
        sbwy_ln_cd: 전철선코드 (예: "101")
        sbwy_ln_nm: 전철선명 (예: "경부선")
        sbwy_stn_cd: 전철역코드 (예: "010000")
        sbwy_stn_nm: 전철역명 (예: "서울")
        tmwd_se_cd: 시간대구분코드 (예: "01")
    """
    cond = {}
    if run_ymd:
        cond["run_ymd::GTE"] = run_ymd
        cond["run_ymd::LTE"] = run_ymd
    else:
        if run_ymd_gte:
            cond["run_ymd::GTE"] = run_ymd_gte
        if run_ymd_lte:
            cond["run_ymd::LTE"] = run_ymd_lte
    if sbwy_ln_cd:
        cond["sbwy_ln_cd::EQ"] = sbwy_ln_cd
    if sbwy_ln_nm:
        cond["sbwy_ln_nm::EQ"] = sbwy_ln_nm
    if sbwy_stn_cd:
        cond["sbwy_stn_cd::EQ"] = sbwy_stn_cd
    if sbwy_stn_nm:
        cond["sbwy_stn_nm::EQ"] = sbwy_stn_nm
    if tmwd_se_cd:
        cond["tmwd_se_cd::EQ"] = tmwd_se_cd

    items = fetch_carriage("wideAreaTravelerTrain", cond)
    if not items:
        return "조회된 광역 여객열차 수송실적이 없습니다."
    return _wrap(items, "B551457/carriageStatistics/wideAreaTravelerTrain")


@mcp.tool()
def get_freight_carriage(
    crtr_ymd: str = "",
    crtr_ymd_gte: str = "",
    crtr_ymd_lte: str = "",
    sndng_stn_cd: str = "",
    sndng_stn_nm: str = "",
    arvl_stn_cd: str = "",
    arvl_stn_nm: str = "",
    item_lclsf_cd: str = "",
    item_mclsf_cd: str = "",
    item_sclsf_cd: str = "",
) -> str:
    """
    화물열차 수송실적 조회. 발송역~도착역 구간별 화물 발송톤·운송연톤키로를 제공합니다.
    화물구분·품목(대/중/소분류)별 필터링 가능.

    Args:
        crtr_ymd: 특정 기준일자 (YYYYMMDD). 입력 시 해당 날짜만 조회.
        crtr_ymd_gte: 기준일자 시작 (YYYYMMDD, 이후)
        crtr_ymd_lte: 기준일자 종료 (YYYYMMDD, 이전)
        sndng_stn_cd: 발송역코드 (예: "3900090"=약목)
        sndng_stn_nm: 발송역명 (예: "약목")
        arvl_stn_cd: 도착역코드 (예: "3900113"=부산진)
        arvl_stn_nm: 도착역명 (예: "부산진")
        item_lclsf_cd: 품목대분류코드 (예: "110")
        item_mclsf_cd: 품목중분류코드 (예: "111")
        item_sclsf_cd: 품목소분류코드 (예: "1111")
    """
    cond = {}
    if crtr_ymd:
        cond["crtr_ymd::GTE"] = crtr_ymd
        cond["crtr_ymd::LTE"] = crtr_ymd
    else:
        if crtr_ymd_gte:
            cond["crtr_ymd::GTE"] = crtr_ymd_gte
        if crtr_ymd_lte:
            cond["crtr_ymd::LTE"] = crtr_ymd_lte
    if sndng_stn_cd:
        cond["sndng_stn_cd::EQ"] = sndng_stn_cd
    if sndng_stn_nm:
        cond["sndng_stn_nm::EQ"] = sndng_stn_nm
    if arvl_stn_cd:
        cond["arvl_stn_cd::EQ"] = arvl_stn_cd
    if arvl_stn_nm:
        cond["arvl_stn_nm::EQ"] = arvl_stn_nm
    if item_lclsf_cd:
        cond["item_lclsf_cd::EQ"] = item_lclsf_cd
    if item_mclsf_cd:
        cond["item_mclsf_cd::EQ"] = item_mclsf_cd
    if item_sclsf_cd:
        cond["item_sclsf_cd::EQ"] = item_sclsf_cd

    items = fetch_carriage("freightTrain", cond)
    if not items:
        return "조회된 화물열차 수송실적이 없습니다."
    return _wrap(items, "B551457/carriageStatistics/freightTrain")


@mcp.tool()
def get_transport_stat_codes(code_type: str = "", code: str = "", value: str = "") -> str:
    """
    수송실적 통계 코드정보 조회. 간선·광역·화물 수송실적에서 사용되는 코드를 조회합니다.
    (구 get_carriage_codes — carriageStatistics/codes)
    최소 하나 이상의 파라미터를 입력해야 결과가 반환됩니다.

    Args:
        code_type: 코드유형 (예: "stn_cd"=역코드, "mrnt_cd"=주운행선코드, "sbwy_ln_cd"=전철선코드)
        code: 코드값 정확일치 (예: "3900023")
        value: 코드명 부분일치 (예: "서울", "경부")

    주의: 파라미터 없이 호출하면 0건 반환될 수 있습니다. code_type 지정을 권장합니다.
    """
    cond = {}
    if code_type:
        cond["type::EQ"] = code_type
    if code:
        cond["code::EQ"] = code
    if value:
        cond["value::LIKE"] = value

    items = fetch_carriage("codes", cond)
    if not items:
        return "조회된 코드가 없습니다. code_type(예: stn_cd, mrnt_cd, sbwy_ln_cd)을 지정해주세요."
    return _wrap(items, "B551457/carriageStatistics/codes")


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
