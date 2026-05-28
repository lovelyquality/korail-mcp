# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551457/carriageStatistics"

mcp = FastMCP("KORAIL 열차수송통계")


def fetch_carriage(endpoint: str, cond: dict = {}) -> list:
    """carriageStatistics 엔드포인트에서 데이터를 가져옵니다 (최대 1000건)."""
    params = {"serviceKey": API_KEY, "pageNo": 1, "numOfRows": 1000}
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    response = httpx.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
    body = response.json().get("response", {}).get("body", {})
    items = (body.get("items") or {}).get("item", [])
    return items if isinstance(items, list) else [items]


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
    return json.dumps(items, ensure_ascii=False, indent=2)


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
    return json.dumps(items, ensure_ascii=False, indent=2)


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
    return json.dumps(items, ensure_ascii=False, indent=2)


@mcp.tool()
def get_carriage_codes(code_type: str = "", code: str = "", value: str = "") -> str:
    """
    열차수송통계 코드정보 조회. 간선·광역·화물 수송실적에서 사용되는 코드를 조회합니다.
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
    return json.dumps(items, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8005)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
