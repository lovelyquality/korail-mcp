# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"

ENDPOINTS = {
    "satisfaction":          "/15153929/v1/uddi:8996eb87-a404-4acb-80fe-b267fb5325fd",
    "consult_type":          "/15131262/v1/uddi:cf4a745d-e7e0-4daa-9433-f5377f952f7d",
    "consult_dept":          "/15153586/v1/uddi:9b4fbb34-a309-42bf-a838-cf843ddeedb3",
    "advance_disclosure":    "/15131416/v1/uddi:3c8f75b7-85f2-43e4-a93c-e9d899a17331",
    "advance_detail":        "/15131421/v1/uddi:9777bebc-9212-46a7-aa73-cb5ec86a123c",
    "advance_files":         "/15135862/v1/uddi:6ac7394e-58a2-4163-a031-90618c85f035",
    "info_dept":             "/15136386/v1/uddi:5540fd8e-af5a-455f-9c39-949eeacd2293",
    "info_codes":            "/15136381/v1/uddi:a192f49b-bd3d-4fc0-bf94-8f6e1bc0d5d7",
    "homepage_dept":         "/15133642/v1/uddi:39614479-48ee-44a3-a99b-93f4e2d84a36",
    "homepage_position":     "/15135865/v1/uddi:c946542d-d513-44d2-a95d-f0ff8ab01dd6",
}

_DATASETS = {
    "satisfaction":       ("한국철도공사_고객의소리_만족도_일별_통계",              "2025.09.11"),
    "consult_type":       ("한국철도공사_철도고객센터DB의 상담유형 테이블",          "2024.08.01"),
    "consult_dept":       ("한국철도공사_철도고객센터DB의 부서정보 데이터",          "2025.11.07"),
    "advance_disclosure": ("한국철도공사_홈페이지_사전정보공표 데이터",              "2024.08.01"),
    "advance_detail":     ("한국철도공사_홈페이지_사전정보공표 데이터_세부사항",     "2024.08.01"),
    "advance_files":      ("한국철도공사_홈페이지_사전정보공표 데이터_첨부파일 데이터", "2024.08.01"),
    "info_dept":          ("한국철도공사_정보공개_부서",                            "2024.09.01"),
    "info_codes":         ("한국철도공사_정보공개_공통코드",                        "2024.09.01"),
    "homepage_dept":      ("한국철도공사_홈페이지_부서 정보",                       "2024.08.01"),
    "homepage_position":  ("한국철도공사_홈페이지_직책 정보",                       "2024.08.01"),
}

mcp = FastMCP("KORAIL 고객서비스·정보공개")

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


def _wrap(data: list, key: str) -> str:
    dataset, ref_date = _DATASETS[key]
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


# ── 도구 1: 고객의소리 만족도 일별 통계 ─────────────────────────────

@mcp.tool()
def get_customer_satisfaction_stats(
    date_from: str = "",
    date_to: str = "",
    day_of_week: str = "",
) -> str:
    """고객의소리 만족도 일별 통계 조회.

    철도 고객센터 만족도 조사 결과를 일별로 제공한다.
    참여수와 평균 점수(100점 만점)를 확인할 수 있다.

    date_from / date_to: 조사일자 범위 (예: "2025-01-01", "2025-03-31")
    day_of_week: 요일 필터 (예: "월요일", "토요일")
    """
    rows = _load("satisfaction")

    if date_from:
        rows = [r for r in rows if r.get("조사일자", "") >= date_from]
    if date_to:
        rows = [r for r in rows if r.get("조사일자", "") <= date_to]
    if day_of_week:
        rows = [r for r in rows if day_of_week in r.get("요일", "")]

    return _wrap(rows, "satisfaction")


# ── 도구 2: 상담유형 테이블 ───────────────────────────────────────────

@mcp.tool()
def get_consultation_types(keyword: str = "") -> str:
    """철도 고객센터 상담유형 코드 조회.

    상담 대분류(MAJOR_COUNSEL), 중분류(MINOR_COUNSEL), 그룹명,
    상담코드(COUNSEL_CODE), 유형명을 제공한다.

    keyword: 그룹명 또는 유형명 부분일치 필터 (예: "운임", "예매", "분실")
    """
    rows = _load("consult_type")

    if keyword:
        rows = [
            r for r in rows
            if keyword in r.get("그룹명(COUNSEL_GROUP_NAME)", "")
            or keyword in r.get("유형명(COUNSEL_NAME)", "")
        ]

    return _wrap(rows, "consult_type")


# ── 도구 3: 철도고객센터 부서정보 ─────────────────────────────────────

@mcp.tool()
def get_consultation_departments(headquarter: str = "") -> str:
    """철도 고객센터 담당 부서(역) 목록 조회.

    본부명, 담당센터명(역명), 표기명을 제공한다.

    headquarter: 본부명 부분일치 필터 (예: "강원", "대구", "서울")
    """
    rows = _load("consult_dept")

    if headquarter:
        rows = [r for r in rows if headquarter in r.get("본부명", "")]

    return _wrap(rows, "consult_dept")


# ── 도구 4: 사전정보공표 데이터 ──────────────────────────────────────

@mcp.tool()
def get_advance_disclosure(keyword: str = "") -> str:
    """홈페이지 사전정보공표 목록 조회.

    공표대상, 공표시기, 담당부서 코드를 제공한다.
    경영 투명성 확인 또는 특정 공표 항목 탐색에 활용.

    keyword: 공표대상 부분일치 필터
    """
    rows = _load("advance_disclosure")

    if keyword:
        rows = [r for r in rows if keyword in r.get("공표대상(INFO_REL_TARGET)", "")]

    return _wrap(rows, "advance_disclosure")


# ── 도구 5: 사전정보공표 세부사항 ─────────────────────────────────────

@mcp.tool()
def get_advance_disclosure_detail(keyword: str = "", dept_code: str = "") -> str:
    """홈페이지 사전정보공표 세부 내역 조회.

    공표대상 제목, 담당부서코드, 조회수를 제공한다.

    keyword: 제목 부분일치 필터
    dept_code: 담당부서 코드 일치 필터
    """
    rows = _load("advance_detail")

    if keyword:
        rows = [r for r in rows if keyword in r.get("공표대상(INFO_REL_DETAIL_TITLE)", "")]
    if dept_code:
        rows = [r for r in rows if r.get("담당부서(DEPT_CODE)", "") == dept_code]

    return _wrap(rows, "advance_detail")


# ── 도구 6: 사전정보공표 첨부파일 ─────────────────────────────────────

@mcp.tool()
def get_advance_disclosure_files(keyword: str = "") -> str:
    """홈페이지 사전정보공표 첨부파일 목록 조회.

    첨부파일명, 파일 확장자, 연결된 공표대상 번호를 제공한다.

    keyword: 파일명 부분일치 필터
    """
    rows = _load("advance_files")

    if keyword:
        rows = [r for r in rows if keyword in r.get("첨부파일명(FILE_NM)", "")]

    return _wrap(rows, "advance_files")


# ── 도구 7: 정보공개 부서 ─────────────────────────────────────────────

@mcp.tool()
def get_info_disclosure_dept(keyword: str = "") -> str:
    """정보공개 담당 부서 목록 조회.

    부서코드, 부서명, 상위부서명(영문)을 제공한다.

    keyword: 부서명 부분일치 필터
    """
    rows = _load("info_dept")

    if keyword:
        rows = [r for r in rows if keyword in r.get("부서명(DEPT_NM)", "")]

    return _wrap(rows, "info_dept")


# ── 도구 9: 정보공개 공통코드 ─────────────────────────────────────────

@mcp.tool()
def get_info_disclosure_codes(code_type: str = "") -> str:
    """정보공개 시스템 공통코드 조회.

    분류코드(CODETYPE), 분류코드명(CODENAME), 사용여부를 제공한다.

    code_type: CODETYPE 일치 필터 (빈값=전체)
    """
    rows = _load("info_codes")

    if code_type:
        rows = [r for r in rows if r.get("분류코드(CODETYPE)", "") == code_type]

    return _wrap(rows, "info_codes")


# ── 도구 10: 홈페이지 부서 정보 ───────────────────────────────────────

@mcp.tool()
def get_homepage_dept(keyword: str = "") -> str:
    """KORAIL 홈페이지 부서 정보 조회 (전체 약 500건).

    부서명(DEPT_NM), 부서코드(DEPT_CODE), 상위부서코드(UPPER_DEPT_CODE)를 제공한다.

    keyword: 부서명 부분일치 필터 (예: "본부", "처", "단", "TF")
             ※ 전체 데이터가 크므로 keyword 없이 호출하면 처음 200건만 반환됨.
                전체 조회가 필요하면 keyword를 여러 번 나눠 호출할 것.
    """
    rows = _load("homepage_dept")

    if keyword:
        rows = [r for r in rows if keyword in r.get("부서명(DEPT_NM)", "")]
    else:
        rows = rows[:200]

    return _wrap(rows, "homepage_dept")


# ── 도구 11: 홈페이지 직책 정보 ───────────────────────────────────────

@mcp.tool()
def get_homepage_position(keyword: str = "") -> str:
    """KORAIL 홈페이지 직책 코드 조회.

    직책 ID, 직책명, 직책코드를 제공한다.

    keyword: 직책명 부분일치 필터
    """
    rows = _load("homepage_position")

    if keyword:
        rows = [r for r in rows if keyword in r.get("직책명(POS_NAME)", "")]

    return _wrap(rows, "homepage_position")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8009)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
