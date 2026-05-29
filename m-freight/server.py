"""korail-freight MCP server.

7 datasets from data.go.kr (KORAIL freight/logistics).
- 4 odcloud REST APIs: container spec, work line, loading time master, loading time adjustment
- 3 local files: freight codes (XLSX), consignment changes (2 CSV), logistics facility (3 CSV)

Memory cache strategy:
- Small datasets (<10K rows): cached at startup
- Large datasets (container 166K, adjustment 36K): per-request page fetch
"""

import os
import csv
import openpyxl
import httpx
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(encoding='utf-8-sig')
API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"
DATA_DIR = Path(__file__).parent / "data"

CONTAINER_PATH = "/15153898/v1/uddi:7430d02d-b78a-4395-9bf5-b1ab000e1be2"
WORK_LINE_PATH = "/15153559/v1/uddi:a369ea3f-6493-441a-9a5d-b4da591cbeb3"
LOAD_TIME_PATH = "/15153575/v1/uddi:106d1522-6c05-4f5a-b95d-9fe4c9453361"
ADJUSTMENT_PATH = "/15153818/v1/uddi:02a37f71-0988-43ca-9dc3-fe4b1bb88a7a"

mcp = FastMCP("korail-freight")

_cache: dict[str, list[dict[str, Any]]] = {}


def _odcloud_get(path: str, page: int = 1, per_page: int = 1000) -> dict:
    r = httpx.get(
        f"{ODCLOUD_BASE}{path}",
        params={"serviceKey": API_KEY, "page": page, "perPage": per_page},
        timeout=20,
    )
    return r.json()


def _odcloud_load_all(path: str) -> list[dict[str, Any]]:
    """Fetch all pages from an odcloud endpoint (for small datasets)."""
    all_data: list[dict[str, Any]] = []
    page = 1
    while True:
        body = _odcloud_get(path, page=page, per_page=1000)
        data = body.get("data", [])
        all_data.extend(data)
        total = body.get("totalCount", 0)
        if len(all_data) >= total or not data:
            break
        page += 1
    return all_data


def _load_xlsx(filename: str) -> list[dict[str, Any]]:
    wb = openpyxl.load_workbook(DATA_DIR / filename, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header = [h for h in next(rows) if h is not None]
    data = []
    for r in rows:
        row = {header[i]: r[i] for i in range(len(header)) if i < len(r)}
        if any(v not in (None, "") for v in row.values()):
            data.append(row)
    wb.close()
    return data


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
    """출처·기준일 메타 딕셔너리 생성."""
    return {
        "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
        "데이터셋": dataset,
        "데이터기준일": ref_date,
    }


@mcp.tool()
def search_freight_code(query: str = "", limit: int = 50) -> dict:
    """내적화물코드 검색 (총 961건).

    분류코드(예: 7404), 한글명, 영문명에 대한 부분일치 검색.
    빈 query시 limit만큼 앞에서부터 반환.
    """
    rows = _get("freight_codes", lambda: _load_xlsx("freight_codes.xlsx"))
    if query:
        q = query.strip()
        rows = [
            r for r in rows
            if _contains(r.get("내적화물분류코드"), q)
            or _contains(r.get("내적화물한글명"), q)
            or _contains(r.get("내적화물영문명"), q)
            or _contains(r.get("메모내용"), q)
        ]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_철도운영정보_화물_내적화물코드 정보", "2023.01.01"),
    }


@mcp.tool()
def decode_freight_code(code: str) -> dict:
    """내적화물분류코드 → 한글명/영문명 단건 디코딩."""
    rows = _get("freight_codes", lambda: _load_xlsx("freight_codes.xlsx"))
    code = code.strip()
    _meta = _make_meta("한국철도공사_철도운영정보_화물_내적화물코드 정보", "2023.01.01")
    for r in rows:
        if str(r.get("내적화물분류코드", "")).strip() == code:
            return {
                "분류코드": r.get("내적화물분류코드"),
                "한글명": r.get("내적화물한글명"),
                "영문명": r.get("내적화물영문명"),
                "메모내용": r.get("메모내용"),
                "_meta": _meta,
            }
    return {"error": f"코드 {code} 에 해당하는 화물코드 없음", "_meta": _meta}


@mcp.tool()
def search_container_record(
    page: int = 1,
    per_page: int = 100,
    container_number: str = "",
    wagon_number: str = "",
    receipt_date: str = "",
    item_name: str = "",
) -> dict:
    """컨테이너 적재 이력 페이지 조회 (총 166,275건, odcloud).

    대용량이라 매 호출 시 odcloud에 페이지 단위로 요청.
    필터(컨테이너번호/화차차량번호/화물수탁일자/품목명)가 주어지면 받은 페이지 내에서 부분일치로 후필터링.
    per_page 최대 1000.
    """
    body = _odcloud_get(CONTAINER_PATH, page=page, per_page=min(per_page, 1000))
    rows = body.get("data", [])
    filters = {
        "컨테이너번호": container_number,
        "화차차량번호": wagon_number,
        "화물수탁일자": receipt_date,
        "품목명": item_name,
    }
    for k, v in filters.items():
        if v:
            rows = [r for r in rows if _contains(r.get(k), v.strip())]
    return {
        "page": body.get("page"),
        "perPage": body.get("perPage"),
        "totalCount": body.get("totalCount"),
        "matched_in_page": len(rows),
        "data": rows,
        "_meta": _make_meta("한국철도공사_철도운영정보_컨테이너규격", "2025.09.16"),
    }


@mcp.tool()
def list_freight_work_lines(station_name: str = "", limit: int = 100) -> dict:
    """화물적하작업 - 전용 작업선 정보 (총 424건, odcloud, 전체 캐시).

    역명 부분일치 필터 가능. 작업선 길이·작업거리·운임계산거리·할인할증 등 포함.
    """
    rows = _get("work_lines", lambda: _odcloud_load_all(WORK_LINE_PATH))
    if station_name:
        rows = [r for r in rows if _contains(r.get("역명"), station_name.strip())]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_철도운영정보_화물적하작업", "2025.11.07"),
    }


@mcp.tool()
def list_standard_loading_time() -> dict:
    """표준 적하시간 마스터 (총 11건, odcloud, 전체 반환).

    ⚠️ 명칭 주의: data.go.kr 등록명은 '적하시간'이지만 실제 데이터는 화물 유형별
    표준 작업시간 마스터(일반 보통품·화약류·컨테이너 등 11건). 조정 이력은
    search_loading_time_adjustment 사용.
    """
    rows = _get("load_time_master", lambda: _odcloud_load_all(LOAD_TIME_PATH))
    return {
        "total": len(rows),
        "data": rows,
        "_meta": _make_meta("한국철도공사_철도운영정보_적하시간", "2025.11.07"),
    }


@mcp.tool()
def search_loading_time_adjustment(
    page: int = 1,
    per_page: int = 100,
    station: str = "",
    reason: str = "",
    region: str = "",
) -> dict:
    """적하시간 조정 이력 페이지 조회 (총 35,967건, odcloud).

    ⚠️ 명칭 주의: data.go.kr 등록명은 '표준적하시간'이지만 실제 데이터는 표준 대비
    조정된 이력. 마스터는 list_standard_loading_time 사용.

    필터: 조정역(station), 조정사유(reason, 예: '천재지변등 악조건', '작업능력초과'),
    조정지역본부(region). 받은 페이지 내 부분일치 필터링.
    per_page 최대 1000.
    """
    body = _odcloud_get(ADJUSTMENT_PATH, page=page, per_page=min(per_page, 1000))
    rows = body.get("data", [])
    filters = {
        "조정역": station,
        "화물적하시간조정사유구분": reason,
        "조정지역본부": region,
    }
    for k, v in filters.items():
        if v:
            rows = [r for r in rows if _contains(r.get(k), v.strip())]
    return {
        "page": body.get("page"),
        "perPage": body.get("perPage"),
        "totalCount": body.get("totalCount"),
        "matched_in_page": len(rows),
        "data": rows,
        "_meta": _make_meta("한국철도공사_철도운영정보_표준적하시간", "2025.09.15"),
    }


@mcp.tool()
def search_consignment_change(
    station: str = "",
    waybill_no: str = "",
    change_type: str = "",
    limit: int = 100,
) -> dict:
    """수탁변경요금 검색 (총 4,015건, 로컬 CSV).

    화물 운송장 접수 후 발생한 착역 변경·화물 지시 변경 등 수탁 조건 변경 건별 요금 이력.
    필터: 제요금입력역명(station), 운송장번호(waybill_no), 화물지시종류(change_type).
    """
    rows = _get("consignment_fee", lambda: _load_csv("consignment_fee.csv"))
    if station:
        rows = [r for r in rows if _contains(r.get("제요금입력역명"), station.strip())]
    if waybill_no:
        rows = [r for r in rows if _contains(r.get("운송장번호"), waybill_no.strip())]
    if change_type:
        rows = [r for r in rows if _contains(r.get("화물지시종류"), change_type.strip())]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_철도운영정보_화물정보_수탁 정보", "2025.11.07"),
    }


@mcp.tool()
def search_consignment_change_per_wagon(
    wagon_number: str = "",
    waybill_no: str = "",
    limit: int = 100,
) -> dict:
    """수탁변경요금 화차별 (총 6,681건, 로컬 CSV).

    개별 화차 단위 지시번호·운송장번호·화통번호 매핑 및 화차요금 산출 근거.
    필터: 화차차량번호(wagon_number), 운송장번호(waybill_no).
    """
    rows = _get(
        "consignment_per_wagon",
        lambda: _load_csv("consignment_fee_per_wagon.csv"),
    )
    if wagon_number:
        rows = [r for r in rows if _contains(r.get("화차차량번호"), wagon_number.strip())]
    if waybill_no:
        rows = [r for r in rows if _contains(r.get("운송장번호"), waybill_no.strip())]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_철도운영정보_화물정보_수탁 정보", "2025.11.07"),
    }


@mcp.tool()
def get_logistics_facility(station_name: str = "", region: str = "", limit: int = 50) -> dict:
    """물류시설 정보 통합 조회 (기본 210건 + 규모 71건 + 사진 457건).

    역명 또는 지역본부명 부분일치 필터. 기본정보(시설 면적·요금·수입 등),
    규모(싸이로 용량·수), 사진(첨부파일명·설명)을 역명 기준으로 결합 반환.
    """
    basic = _get("facility_basic", lambda: _load_csv("facility_basic.csv"))
    scale = _get("facility_scale", lambda: _load_csv("facility_scale.csv"))
    photo = _get("facility_photo", lambda: _load_csv("facility_photo.csv"))

    if station_name:
        s = station_name.strip()
        basic = [r for r in basic if _contains(r.get("역명"), s)]
    if region:
        r_ = region.strip()
        basic = [r for r in basic if _contains(r.get("지역본부명"), r_)]

    basic = basic[:limit]
    target_stations = {r.get("역명") for r in basic}

    scale_matched = [r for r in scale if r.get("역명") in target_stations]
    photo_matched = [r for r in photo if r.get("역명") in target_stations]

    return {
        "basic_total": len(basic),
        "basic": basic,
        "scale": scale_matched,
        "photo": photo_matched,
        "_meta": _make_meta("한국철도공사_철도운영정보_화물정보_물류시설 정보", "2024.02.26"),
    }


@mcp.tool()
def get_freight_items(query: str = "", limit: int = 50) -> dict:
    """화물 품목정보 조회 (총 861건, 로컬 CSV).

    품목코드·품목명·품목약어명·최저톤수율 정보. 계층형 코드 구조
    (상위 0000, 중위 00, 하위 01~99). 빈 query시 상위 항목부터 limit 반환.
    """
    rows = _get("freight_items", lambda: _load_csv("freight_items.csv"))
    if query:
        q = query.strip()
        rows = [
            r for r in rows
            if _contains(r.get("품목코드(ITM_CD)"), q)
            or _contains(r.get("품목명(ITM_NM)"), q)
            or _contains(r.get("품목약어명(ITM_AVVR_NM)"), q)
        ]
    return {
        "total": len(rows),
        "data": rows[:limit],
        "_meta": _make_meta("한국철도공사_철도운영정보_품목정보", "2024.08.01"),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8006)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
