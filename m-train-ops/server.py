from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551457/run/v2"
ODCLOUD_BASE = "https://api.odcloud.kr/api"

mcp = FastMCP("KORAIL 열차운행정보")

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


def _get(key: str, loader):
    if key not in _cache:
        _cache[key] = loader()
    return _cache[key]


def fetch_train(endpoint: str, cond: dict = {}) -> list:
    params = {
        "serviceKey": API_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
    }
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    response = httpx.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
    body = response.json().get("response", {}).get("body", {})
    items = (body.get("items") or {}).get("item", [])
    return items if isinstance(items, list) else [items]


@mcp.tool()
def get_train_codes(code_type: str = "", code: str = "", value: str = "") -> str:
    """열차운행 코드정보 조회. 최소 하나 이상의 파라미터 필요.
    code_type=코드유형(예:stn_cd,mrnt_cd), code=코드값(정확일치), value=코드명(부분일치)
    주요 code_type: stn_cd(역코드), mrnt_cd(주운행선코드)"""
    cond = {}
    if code_type: cond["type::EQ"] = code_type
    if code: cond["code::EQ"] = code
    if value: cond["value::LIKE"] = value
    items = fetch_train("codes2", cond)
    if not items:
        return "조회된 코드가 없습니다."
    return json.dumps(items, ensure_ascii=False, indent=2)


@mcp.tool()
def get_train_run_plan(
    run_ymd_gte: str = "",
    run_ymd_lte: str = "",
    run_ymd: str = "",
    dptre_stn_nm: str = "",
    arvl_stn_nm: str = "",
) -> str:
    """여객열차 운행계획 조회 (열차번호·출발/도착역·계획출발/도착시각).
    run_ymd=특정일자(YYYYMMDD), run_ymd_gte/lte=기간 범위,
    dptre_stn_nm=출발역명(예:서울), arvl_stn_nm=도착역명(예:부산)"""
    cond = {}
    if run_ymd:
        cond["run_ymd::GTE"] = run_ymd
        cond["run_ymd::LTE"] = run_ymd
    else:
        if run_ymd_gte: cond["run_ymd::GTE"] = run_ymd_gte
        if run_ymd_lte: cond["run_ymd::LTE"] = run_ymd_lte
    if dptre_stn_nm: cond["dptre_stn_nm::EQ"] = dptre_stn_nm
    if arvl_stn_nm: cond["arvl_stn_nm::EQ"] = arvl_stn_nm
    items = fetch_train("travelerTrainRunPlan2", cond)
    if not items:
        return "조회된 운행계획이 없습니다."
    result = [
        {
            "운행일자": i.get("run_ymd"),
            "열차번호": i.get("trn_no"),
            "출발역코드": i.get("dptre_stn_cd"),
            "출발역명": i.get("dptre_stn_nm"),
            "도착역코드": i.get("arvl_stn_cd"),
            "도착역명": i.get("arvl_stn_nm"),
            "계획출발일시": i.get("trn_plan_dptre_dt"),
            "계획도착일시": i.get("trn_plan_arvl_dt"),
        }
        for i in items
    ]
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_train_run_info(
    run_ymd_gte: str = "",
    run_ymd_lte: str = "",
    run_ymd: str = "",
    stn_nm: str = "",
    mrnt_nm: str = "",
) -> str:
    """여객열차 실제 운행정보 조회 (운행일자·역별 실제 출발/도착시각·정차구분).
    run_ymd=특정일자(YYYYMMDD), run_ymd_gte/lte=기간 범위,
    stn_nm=역명(예:서울), mrnt_nm=주운행선명(예:경부선)"""
    cond = {}
    if run_ymd:
        cond["run_ymd::GTE"] = run_ymd
        cond["run_ymd::LTE"] = run_ymd
    else:
        if run_ymd_gte: cond["run_ymd::GTE"] = run_ymd_gte
        if run_ymd_lte: cond["run_ymd::LTE"] = run_ymd_lte
    if stn_nm: cond["stn_nm::EQ"] = stn_nm
    if mrnt_nm: cond["mrnt_nm::EQ"] = mrnt_nm
    items = fetch_train("travelerTrainRunInfo2", cond)
    if not items:
        return "조회된 운행정보가 없습니다."
    result = [
        {
            "운행일자": i.get("run_ymd"),
            "열차번호": i.get("trn_no"),
            "열차운행순번": i.get("trn_run_sn"),
            "역코드": i.get("stn_cd"),
            "역명": i.get("stn_nm"),
            "주운행선코드": i.get("mrnt_cd"),
            "주운행선명": i.get("mrnt_nm"),
            "상하행구분": i.get("uppln_dn_se_cd"),
            "정차구분코드": i.get("stop_se_cd"),
            "정차구분명": i.get("stop_se_nm"),
            "실제출발일시": i.get("trn_dptre_dt"),
            "실제도착일시": i.get("trn_arvl_dt"),
        }
        for i in items
    ]
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_train_run_history(
    run_dt: str = "",
    trn_no: str = "",
    stn_nm: str = "",
    stn_cd: str = "",
    dedupe: bool = False,
) -> str:
    """차세대예약발매 열차 운행내역 조회 (2024-01-01 단일 일자 100건 스냅샷).

    ※ 데이터 한계 (반드시 참고):
    - 이 데이터는 2024-01-01 하루치만 존재. 다른 날짜 필터 시 0건 반환.
    - 실제 하루 운행 열차는 수백 편이나, 이 스냅샷은 일부 열차·역 포함.
    - 동일 (열차번호, 역)이 2건씩 중복 등장하는 경우 있음 (경유 처리 방식).
    - 정차 순번 필드 없음 → 정확한 정차 순서는 get_train_run_info 또는
      get_train_run_plan으로 교차 확인 필요.
    - 역코드 상세 정보(영문명·지역본부 등)는 korail-codebook의
      decode_station_code 도구로 조회 가능.

    파라미터:
    - run_dt: 운행일자 (YYYY-MM-DD, 예: '2024-01-01')
    - trn_no: 열차번호 (예: '6' 또는 '00006', 숫자 자동 변환)
    - stn_nm: 한글역명 부분일치 (예: '서울', '부산')
    - stn_cd: 역코드 정확일치 (예: '3900023')
    - dedupe: True 시 동일 (열차번호+역코드) 중복 레코드 제거 (기본 False)

    반환 필드: 운행일자(RUN_DT), 열차번호(TRN_NO), 역코드(STN_CD), 한글역명(KOR_STN_NM)"""
    PATH = "/15138153/v1/uddi:95e7cf38-fea1-40d7-bab1-b63b5155b1f1"
    rows = _get("train_run_history", lambda: _odcloud_load_all(PATH))

    result = rows
    if run_dt:
        result = [r for r in result if r.get("운행일자(RUN_DT)", "") == run_dt]
    if trn_no:
        try:
            no_int = int(trn_no)
            result = [r for r in result if int(r.get("열차번호(TRN_NO)", -1)) == no_int]
        except ValueError:
            pass
    if stn_nm:
        result = [r for r in result if stn_nm in str(r.get("한글역명(KOR_STN_NM)", ""))]
    if stn_cd:
        try:
            cd_int = int(stn_cd)
            result = [r for r in result if int(r.get("역코드(STN_CD)", -1)) == cd_int]
        except ValueError:
            pass

    if dedupe:
        seen = set()
        deduped = []
        for r in result:
            key = (r.get("열차번호(TRN_NO)"), r.get("역코드(STN_CD)"))
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        result = deduped

    if not result:
        return "조회된 운행내역이 없습니다."
    return _wrap(result, "한국철도공사_차세대예약발매_열차운행내역", "2024.01.01")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8003)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
