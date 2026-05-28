# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")

# ── B551457 REST API (임대매장정보) ──────────────────────────────────────
LEASE_BASE = "https://apis.data.go.kr/B551457/lease"

# ── odcloud 파일 변환 API ────────────────────────────────────────────────
ODCLOUD_BASE = "https://api.odcloud.kr/api"

ENDPOINTS = {
    "leased_assets":          "/15048398/v1/uddi:daa8f21e-a08d-4b57-8d8f-ac9710467fab",
    "dorm_longterm_codes":    "/15148497/v1/uddi:e6fbbd6a-0252-4a07-968e-ef9b3ca7f9de",
    "social_funds":           "/15138442/v1/uddi:01b17f28-7f8d-4b21-9c19-ee35557ee13a",
    "social_vol_fields":      "/15138441/v1/uddi:d1505fd5-90fb-4342-ac19-9711ed5028cf",
    "social_donations":       "/15153958/v1/uddi:c6e5876a-ea23-4dbe-b7e4-a92095681096",
    "social_vol_matching":    "/15153923/v1/uddi:e7467fbe-9dc2-4396-802a-daf4bfbb1468",
    "social_org":             "/15153791/v1/uddi:cbe55055-2504-4d8b-8af9-b2f43d87ceb8",
    "support_facilities":     "/15153971/v1/uddi:394df6e4-92f7-4440-b100-93735ab6a5be",
    "support_departments":    "/15153967/v1/uddi:45f3a2bc-628d-4ce8-a8ca-e8789af3a0fd",
    "office_meeting_rooms":   "/15138437/v1/uddi:cdb563dd-d72f-4759-bf41-faae9b125fc3",
    "job_grades":             "/15154169/v1/uddi:cbfb94b1-fa4a-4dab-aa62-e764caa4dbc3",
    "cafeteria_menu_stats":   "/15154168/v1/uddi:cd6218c1-2bb9-4f0d-bdf9-9a4e5fde9558",
}

_DATASETS = {
    "leased_assets":       ("한국철도공사_임대자산 현황",              "2025.08.30"),
    "dorm_longterm_codes": ("한국철도공사_직원숙사_장기예약코드",        "2025.09.09"),
    "social_funds":        ("한국철도공사_사회공헌_펀드종류",           "2024.09.01"),
    "social_vol_fields":   ("한국철도공사_사회공헌_봉사분야",           "2024.09.01"),
    "social_donations":    ("한국철도공사_사회공헌_사랑의성금사용",      "2025.10.25"),
    "social_vol_matching": ("한국철도공사_사회공헌_봉사활동 매칭사용",   "2025.09.10"),
    "social_org":          ("한국철도공사_사회공헌 조직정보",           "2025.10.31"),
    "support_facilities":  ("한국철도공사_업무지원_부대시설",           "2025.08.20"),
    "support_departments": ("한국철도공사_업무지원_부서정보",           "2025.09.12"),
    "office_meeting_rooms":("한국철도공사_사옥_회의실",                "2024.09.01"),
    "job_grades":          ("한국철도공사_ 직급 정보",                 "2025.10.31"),
    "cafeteria_menu_stats":("한국철도공사_구내식당 메뉴 건수 현황",     "2025.04.01"),
}

mcp = FastMCP("KORAIL 내부서비스")

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
            timeout=30,
        )
        body = r.json()
        data = body.get("data", [])
        all_data.extend(data)
        if len(all_data) >= body.get("totalCount", 0) or not data:
            break
        page += 1
    _cache[key] = all_data
    return all_data


def _wrap(data: list, key: str, extra_note: str = "") -> str:
    dataset, ref_date = _DATASETS[key]
    meta = {
        "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
        "데이터셋": dataset,
        "데이터기준일": ref_date,
        "건수": len(data),
    }
    if extra_note:
        meta["주의"] = extra_note
    return json.dumps({"data": data, "_meta": meta}, ensure_ascii=False, indent=2)


def _fetch_lease(endpoint: str, cond: dict = {}) -> list:
    """B551457 임대매장정보 REST API 호출."""
    params = {"serviceKey": API_KEY, "pageNo": 1, "numOfRows": 1000}
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    r = httpx.get(f"{LEASE_BASE}/{endpoint}", params=params, timeout=15)
    body = r.json().get("response", {}).get("body", {})
    items = (body.get("items") or {}).get("item", [])
    return items if isinstance(items, list) else [items]


def _wrap_lease(data: list, dataset: str) -> str:
    return json.dumps(
        {
            "data": data,
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋": dataset,
                "데이터기준일": "실시간 API",
                "건수": len(data),
            },
        },
        ensure_ascii=False,
        indent=2,
    )


# ════════════════════════════════════════════════════════════════════════════
# B551457 REST API 도구 (2개)
# ════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_lease_stores(
    store_name: str = "",
    station_code: str = "",
    station_name: str = "",
) -> str:
    """역사 내 임대매장 운영정보 조회 (실시간 REST API).

    역사 내 임대매장의 매장명, 매장위치, 역명, 본부, 개업일자,
    계약기간, 승인면적, 평일·휴일 영업시간 등을 제공한다.

    store_name:   매장명 부분일치 필터 (예: "파리바게뜨", "GS25")
    station_code: 역코드 정확일치 필터 (예: "0001")
    station_name: 역명 정확일치 필터 (예: "서울역", "부산역")
    """
    cond = {}
    if store_name:
        cond["stor_nm::LIKE"] = store_name
    if station_code:
        cond["stn_cd::EQ"] = station_code
    if station_name:
        cond["stn_nm::EQ"] = station_name

    items = _fetch_lease("stores", cond)
    return _wrap_lease(items, "한국철도공사_임대매장정보_stores")


@mcp.tool()
def get_lease_codes(
    code_type: str = "",
    code: str = "",
    value: str = "",
) -> str:
    """임대 시스템 코드 조회 (실시간 REST API).

    임대 관련 분류 코드표를 제공한다.
    코드타입(type), 코드값(code), 코드설명(value)으로 구성된다.

    code_type: 코드타입 정확일치 필터
    code:      코드 정확일치 필터
    value:     코드설명 부분일치 필터
    """
    cond = {}
    if code_type:
        cond["type::EQ"] = code_type
    if code:
        cond["code::EQ"] = code
    if value:
        cond["value::LIKE"] = value

    items = _fetch_lease("codes", cond)

    if not items:
        return json.dumps({
            "data": [],
            "_meta": {
                "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
                "데이터셋": "한국철도공사_임대매장정보_codes",
                "데이터기준일": "실시간 API",
                "건수": 0,
                "주의": (
                    "/codes 엔드포인트가 현재 빈 응답을 반환합니다. "
                    "업종 분류 확인이 필요하면 get_lease_stores()를 호출한 뒤 "
                    "biz_se_nm(업종 대분류)·biz_dtl_se_nm(업종 세분류) 필드를 참고하세요."
                ),
            },
        }, ensure_ascii=False, indent=2)

    return _wrap_lease(items, "한국철도공사_임대매장정보_codes")


# ════════════════════════════════════════════════════════════════════════════
# odcloud 도구 (14개)
# ════════════════════════════════════════════════════════════════════════════

# ── 임대자산 현황 ──────────────────────────────────────────────────────────

@mcp.tool()
def get_leased_assets(
    location: str = "",
    facility_name: str = "",
) -> str:
    """한국철도공사 임대자산 현황 조회 (1,773건).

    철도공사가 관리 중인 임대 자산의 소재지, 시설명, 계약기간,
    임대면적(㎡), 연간임대료(부가세 별도)를 제공한다.
    역사 내 상업공간·건물·유휴부지 등 실제 임대 중인 부동산 자산 정보.
    B551457 /stores(매장 운영정보)와 다름 — 이 도구는 자산/재무 관점.

    location:      자산소재지 부분일치 필터 (예: "서울", "대전", "경기")
    facility_name: 시설명 부분일치 필터 (예: "서울역", "용산역")
    """
    rows = _load("leased_assets")

    if location:
        rows = [r for r in rows if location in str(r.get("자산소재지", ""))]
    if facility_name:
        rows = [r for r in rows if facility_name in str(r.get("시설명", ""))]

    return _wrap(rows, "leased_assets")


# ── 직원숙사 ───────────────────────────────────────────────────────────────


@mcp.tool()
def get_dormitory_longterm_codes(group: str = "") -> str:
    """직원숙사 장기예약 사유 코드 조회 (15건).

    장기숙박 예약 시 사용되는 사유코드(그룹·값·명칭)를 제공한다.
    '장기'(교육생·출장자·비연고지 발령 등)와 '기타'(2급이상·야간근무 등) 구분.

    group: 코드그룹 필터 (예: "장기", "기타")
    """
    rows = _load("dorm_longterm_codes")

    if group:
        rows = [r for r in rows if group in str(r.get("장기숙박코드그룹", ""))]

    return _wrap(rows, "dorm_longterm_codes")


# ── 사회공헌 ───────────────────────────────────────────────────────────────

@mcp.tool()
def get_social_funds() -> str:
    """사회공헌 펀드 종류 조회 (6건).

    사회공헌 재원 펀드 유형(종류명, 기본값여부, 분류순서)을 제공한다.
    '사랑의 성금', '매칭그랜트', '자체성금', '러브포인트' 등 구분.
    """
    rows = _load("social_funds")
    return _wrap(rows, "social_funds")


@mcp.tool()
def get_social_volunteer_fields(keyword: str = "") -> str:
    """사회공헌 봉사 분야 코드 조회 (7건).

    봉사분야 구분코드, 분야명, 분야설명을 제공한다.
    내일하우스·해피트레인·복지단체·환경봉사·헌혈 등.

    keyword: 분야명 부분일치 필터 (예: "헌혈", "환경", "해피")
    """
    rows = _load("social_vol_fields")

    if keyword:
        rows = [r for r in rows if keyword in str(r.get("봉사분야명(SERVICETYPENAME)", ""))
                or keyword in str(r.get("분야설명(DESCRIPTION)", ""))]

    return _wrap(rows, "social_vol_fields")


@mcp.tool()
def get_social_donations(
    date_from: str = "",
    date_to: str = "",
    keyword: str = "",
) -> str:
    """사회공헌 '사랑의 성금' 사용 내역 조회 (1,053건).

    성금 지출 관리번호, 순번, 지출일자, 금액(원), 사용내역을 제공한다.
    온누리상품권 구매, 해피트레인 여행상품비, 후원물품 구입 등.

    date_from: 지출일자 시작 (예: "2025-01-01")
    date_to:   지출일자 종료
    keyword:   내역 부분일치 필터 (예: "온누리", "해피트레인", "헌혈")
    """
    rows = _load("social_donations")

    if date_from:
        rows = [r for r in rows if str(r.get("지출일자", "")) >= date_from]
    if date_to:
        rows = [r for r in rows if str(r.get("지출일자", "")) <= date_to]
    if keyword:
        rows = [r for r in rows if keyword in str(r.get("내역", ""))]

    return _wrap(rows, "social_donations")


@mcp.tool()
def get_social_volunteer_matching(
    date_from: str = "",
    date_to: str = "",
    keyword: str = "",
) -> str:
    """사회공헌 봉사활동 매칭 지출 내역 조회 (877건).

    봉사활동 매칭 관련 지출의 관리번호, 순번, 지출일자,
    사용금액(원), 사용내역을 제공한다.
    매칭그랜트·온누리상품권·봉사요원 간식비 등.

    date_from: 지출일자 시작
    date_to:   지출일자 종료
    keyword:   사용내역 부분일치 필터 (예: "매칭그랜트", "봉사자", "온누리")
    """
    rows = _load("social_vol_matching")

    if date_from:
        rows = [r for r in rows if str(r.get("지출일자", "")) >= date_from]
    if date_to:
        rows = [r for r in rows if str(r.get("지출일자", "")) <= date_to]
    if keyword:
        rows = [r for r in rows if keyword in str(r.get("사용내역", ""))]

    return _wrap(rows, "social_vol_matching")


@mcp.tool()
def get_social_org(
    org_name: str = "",
    headquarter: str = "",
) -> str:
    """사회공헌 포털 조직정보 조회 (6,306건).

    한국철도공사 전체 조직 현황(본부·역·사업소·팀 등)을 제공한다.
    조직명은 'KORAIL/강원본부/강릉역' 형식의 계층 경로.
    메모1·메모2·메모3에 본부명·소속 정보 포함.

    ※ 전체 조회 시 최대 200건 반환. org_name 또는 headquarter 필터 권장.

    org_name:    조직명 부분일치 필터 (예: "강릉역", "차량사업소", "AI전략본부")
    headquarter: 본부명 부분일치 필터 (예: "강원본부", "서울본부", "대전")
    """
    rows = _load("social_org")

    if org_name:
        rows = [r for r in rows if org_name in str(r.get("조직명", ""))]
    if headquarter:
        rows = [r for r in rows if headquarter in str(r.get("메모1", ""))
                or headquarter in str(r.get("조직명", ""))]
    if not org_name and not headquarter:
        rows = rows[:200]

    return _wrap(rows, "social_org")


# ── 업무지원 ───────────────────────────────────────────────────────────────

@mcp.tool()
def get_support_facilities() -> str:
    """사옥 내 부대시설 목록 조회 (29건).

    본사 사옥 내 부대시설(카페·어린이집·회의실·스포츠센터·편의점 등)의
    시설명, 생성일시, 수정일시, 비고를 제공한다.

    ※ 최신성 주의: 2025.08.20 기준 데이터로 현재와 다를 수 있음.
    """
    rows = _load("support_facilities")
    return _wrap(
        rows, "support_facilities",
        extra_note="2025.08.20 기준 스냅샷. 실제 운영 현황과 다를 수 있음."
    )


@mcp.tool()
def get_support_departments(
    dept_name: str = "",
    position: str = "",
    grade: str = "",
) -> str:
    """업무지원 부서별 직위·직급 인원 현황 조회 (10,015건).

    부서명, 직위명, 직급명, 인원수를 제공한다.
    조직 내 인력 배분 및 직무 구조 파악에 활용.

    ※ 전체 조회 시 최대 200건 반환. 필터 사용 권장.

    dept_name: 부서명 부분일치 필터 (예: "서울역", "AI전략본부", "차량사업소")
    position:  직위명 부분일치 필터 (예: "역장", "팀장", "기술원")
    grade:     직급명 부분일치 필터 (예: "사무영업3급", "운전4급", "토목5급")
    """
    rows = _load("support_departments")

    if dept_name:
        rows = [r for r in rows if dept_name in str(r.get("부서명", ""))]
    if position:
        rows = [r for r in rows if position in str(r.get("직위명", ""))]
    if grade:
        rows = [r for r in rows if grade in str(r.get("직급명", ""))]

    if not dept_name and not position and not grade:
        rows = rows[:200]

    return _wrap(rows, "support_departments")


# ── 사옥 ───────────────────────────────────────────────────────────────────

@mcp.tool()
def get_office_meeting_rooms(min_capacity: int = 0) -> str:
    """본사 사옥 회의실 목록 조회 (11건).

    회의실코드, 수용인원, 회의실사양(명칭·좌석수)을 제공한다.
    대회의실(160석)부터 소회의실(18석), 영상회의실, 디지털허브 랩 포함.

    ※ 2024년 이후 최신화 이력 없음. 현재 운영 현황과 다를 수 있음.

    min_capacity: 최소 수용인원 필터 (예: 30 → 30인 이상 회의실만)
    """
    rows = _load("office_meeting_rooms")

    if min_capacity > 0:
        rows = [r for r in rows if (r.get("수용인원(ACEPTNC_NMPR)") or 0) >= min_capacity]

    return _wrap(
        rows, "office_meeting_rooms",
        extra_note="2024.09.01 기준 스냅샷. 현재 운영 현황과 다를 수 있음."
    )


# ── 인사 ───────────────────────────────────────────────────────────────────

@mcp.tool()
def get_job_grades(
    grade_level: int = 0,
    keyword: str = "",
) -> str:
    """직급 코드 정보 조회 (109건).

    직급등급(1~10급), 직급명, 직급코드를 제공한다.
    사무·기술·차량·운전·전기통신·토목·건축·특수·열차승무·물류영업 등 직종별 구분.

    grade_level: 직급등급 정확일치 필터 (예: 3 → 3급 전체)
    keyword:     직급명 부분일치 필터 (예: "운전", "차량", "사무영업")
    """
    rows = _load("job_grades")

    if grade_level > 0:
        rows = [r for r in rows if r.get("직급등급") == grade_level]
    if keyword:
        rows = [r for r in rows if keyword in str(r.get("직급명", ""))]

    return _wrap(rows, "job_grades")


# ── 구내식당 ───────────────────────────────────────────────────────────────

@mcp.tool()
def get_cafeteria_menu_stats(location: str = "") -> str:
    """구내식당 메뉴 건수 현황 조회 (33건).

    각 구내식당의 조식·중식·석식 식단 라인 수(등록된 식단 항목 건수)를 제공한다.
    용산역·서울역·대전충남본부·부산역·인재개발원 등 전국 식당 포함.

    ※ '메뉴 건수'는 실제 요리 가짓수가 아닌 식단 제공 라인 수임에 유의.
       (예: 중식 2라인 = A코스·B코스 2종 제공)

    location: 식단지역명 부분일치 필터 (예: "서울역", "부산", "대전", "본사")
    """
    rows = _load("cafeteria_menu_stats")

    if location:
        rows = [r for r in rows if location in str(r.get("식단지역명", ""))]

    return _wrap(rows, "cafeteria_menu_stats")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
