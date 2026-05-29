from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os
import json

load_dotenv(encoding='utf-8-sig')

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
ODCLOUD_BASE = "https://api.odcloud.kr/api"

mcp = FastMCP("KORAIL 차량·장비 정보")

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


# ── 도구 1: 동력차 형별제원 ──────────────────────────────────────────────────

@mcp.tool()
def get_train_type_specs(train_type: str = "") -> str:
    """동력차 형별제원 조회 (2024.12.31 기준, 47개 차종).
    KTX·KTX-산천·KTX-이음·디젤기관차·전기기관차·디젤동차·전기동차·ITX 등
    각 차종의 마력(HP)·보유대수·자중(톤)·내용연수 포함.
    train_type: 형별명 부분일치 (예: 'KTX', '디젤기관차', '전기기관차', 'ITX').
    미입력 시 전체 47개 반환."""
    PATH = "/15053623/v1/uddi:d69a42a9-11e9-4f89-add5-ac1a7621ea52"
    rows = _get("train_type_specs", lambda: _odcloud_load_all(PATH))
    result = rows
    if train_type:
        result = [r for r in result if train_type in str(r.get("형별", ""))]
    if not result:
        return f"'{train_type}'에 해당하는 차종을 찾을 수 없습니다."
    return _wrap(result, "한국철도공사_ 동력차 형별제원", "2024.12.31")


# ── 도구 2: 연도별 차량보유현황 ──────────────────────────────────────────────

@mcp.tool()
def get_rolling_stock_by_year(year: str = "") -> str:
    """연도별 차량보유현황 조회 (2024.12.31 기준, 2016~2024년 9개 연도).
    KTX·SRT·KTX-이음·디젤기관차·전기기관차·디젤동차·전기동차·간선형전기동차·
    ITX-청춘·객차·발전차·화차·기중기 차종별 연도별 보유 대수 포함.
    year: 조회 연도 (예: '2024', '2020'). 미입력 시 전체 9개 연도 반환.
    ※ SRT는 SR(수서고속철도) 소속으로 KORAIL 보유 수치에 포함된 것으로 표기됨."""
    PATH = "/15053619/v1/uddi:c5b78411-7cd8-4de5-90ea-ab4ca3d3211a"
    rows = _get("rolling_stock_by_year", lambda: _odcloud_load_all(PATH))
    result = rows
    if year:
        result = [r for r in result if str(r.get("시점", "")) == year]
    if not result:
        return f"'{year}'년도 데이터를 찾을 수 없습니다. (제공 범위: 2016~2024)"
    return _wrap(result, "한국철도공사_연도별 차량보유현황", "2024.12.31")


# ── 도구 3: 화차자중별 보유현황 ──────────────────────────────────────────────

@mcp.tool()
def get_wagon_by_weight_class(
    wagon_type: str = "",
    min_weight: str = "",
    max_weight: str = "",
) -> str:
    """화차 자중별 보유현황 조회 (2024.12.31 기준, 70개 자중 구간).
    자중(톤) 구간별 유개차·유조차·무개차·평판차·소화물·차장차·침식차 보유 대수.
    wagon_type: 차종 필터 (예: '유개차', '유조차', '무개차', '평판차').
                해당 차종 보유량 > 0 인 행만 반환.
    min_weight: 최소 자중(톤, 예: '20').
    max_weight: 최대 자중(톤, 예: '25').
    미입력 시 전체 70개 행 반환."""
    PATH = "/15053622/v1/uddi:4376e97d-20da-4150-8e2b-f42cb339a96c"
    rows = _get("wagon_by_weight_class", lambda: _odcloud_load_all(PATH))
    result = rows
    if min_weight:
        try:
            mn = float(min_weight)
            result = [r for r in result if float(str(r.get("자중(톤)", 0) or 0)) >= mn]
        except ValueError:
            pass
    if max_weight:
        try:
            mx = float(max_weight)
            result = [r for r in result if float(str(r.get("자중(톤)", 0) or 0)) <= mx]
        except ValueError:
            pass
    if wagon_type:
        result = [r for r in result if int(r.get(wagon_type, 0) or 0) > 0]
    if not result:
        return "조회된 화차 보유현황이 없습니다."
    return _wrap(result, "한국철도공사_화차자중별 보유현황", "2024.12.31")


# ── 도구 4: 화차하중별 보유현황 ──────────────────────────────────────────────

@mcp.tool()
def get_wagon_by_load_capacity(
    wagon_type: str = "",
    min_load: str = "",
    max_load: str = "",
) -> str:
    """화차 적재하중별 보유현황 조회 (2024.12.31 기준, 27개 하중 등급).
    적재하중(화물 최대 적재 중량) 등급별 유개차·무개차·평판차·소화물·유조차·차장차·침식차 보유 대수.
    필드명 주의: '유 개 차', '무 개 차', '평 판 차' 등 띄어쓰기 포함.
    wagon_type: 차종 (예: '유 개 차', '무 개 차', '평 판 차', '유 조 차').
                해당 차종 보유량 > 0 인 행만 반환.
    min_load: 최소 적재하중 (예: '40').
    max_load: 최대 적재하중 (예: '60').
    미입력 시 전체 27개 행 반환."""
    PATH = "/15053621/v1/uddi:6a51e6d0-d135-4f49-951c-aecd4f960783"
    rows = _get("wagon_by_load_capacity", lambda: _odcloud_load_all(PATH))
    result = rows
    if min_load:
        try:
            mn = float(min_load)
            result = [r for r in result if float(str(r.get("적재하중", 0) or 0)) >= mn]
        except ValueError:
            pass
    if max_load:
        try:
            mx = float(max_load)
            result = [r for r in result if float(str(r.get("적재하중", 0) or 0)) <= mx]
        except ValueError:
            pass
    if wagon_type:
        result = [r for r in result if int(r.get(wagon_type, 0) or 0) > 0]
    if not result:
        return "조회된 화차 보유현황이 없습니다."
    return _wrap(result, "한국철도공사_화차 하중별 보유현황", "2024.12.31")


# ── 도구 5: 기계 보유현황 ────────────────────────────────────────────────────

@mcp.tool()
def get_maintenance_equipment(region: str = "") -> str:
    """철도차량 검수용 기계 보유현황 조회 (2024.12.31 기준, 16개 지역).
    지역(정비단·지역본부)별 공작기계·원동기계·시험기계·유체기계·양물기계·
    공기기계·토목기계·계중기계·차량이동기계·전기기계·로기계·잡기계·고속시험기계 수량.
    region: 지역 부분일치 (예: '수도권', '부산', '대전', '강원').
             '정비단' 또는 '지역본부'로 구분 가능.
    미입력 시 전체 16개 지역 반환."""
    PATH = "/15053620/v1/uddi:4be7be93-b948-46e3-b20b-f03c0a54ddc6"
    rows = _get("maintenance_equipment", lambda: _odcloud_load_all(PATH))
    result = rows
    if region:
        result = [r for r in result if region in str(r.get("지역", ""))]
    if not result:
        return f"'{region}'에 해당하는 지역을 찾을 수 없습니다."
    return _wrap(result, "한국철도공사_기계 보유현황", "2024.12.31")


@mcp.tool()
def get_train_operation_by_type(year: int = 0, train_type: str = "") -> str:
    """차종별 연간 운행실적 조회 (로컬 CSV, 2025.08.31 기준, 2019~2025년).

    디젤기관차·전기기관차·전동차(수도권) 등 KORAIL 보유 차종별 연간 운행 횟수.
    2025년은 8월까지의 통계.

    - year: 특정 연도 (예: 2024). 0이면 전체(2019~2025).
    - train_type: 차종명 부분일치 필터 (예: 'KTX', 'ITX', '디젤기관차', '전기기관차').
                  미입력 시 전체 차종 컬럼 반환.

    주요 차종: 디젤기관차(4400·7300·7400·7500호대), 전기기관차(8200·8500호대),
              KTX, ITX-새마을, ITX-청춘, 누리로, 수도권전동차 각 계열
    """
    from pathlib import Path as _Path
    import csv as _csv

    def _load_op_type():
        with open(_Path(__file__).parent / "data" / "train_operation_by_type.csv",
                  encoding="cp949", newline="") as f:
            return list(_csv.DictReader(f))

    rows = _get("train_op_type", _load_op_type)

    if year:
        rows = [r for r in rows if str(r.get("년도", "")).strip() == str(year)]

    if not rows:
        return f"연도 '{year}'에 해당하는 데이터가 없습니다. (범위: 2019~2025)"

    if train_type:
        # 해당 차종 컬럼만 추출
        result = []
        for r in rows:
            filtered = {"년도": r.get("년도", "")}
            for col, val in r.items():
                if train_type in col:
                    filtered[col] = val
            if len(filtered) > 1:
                result.append(filtered)
        if not result:
            all_cols = [c for c in rows[0].keys() if c != "년도" and c != "차종별 운행 결과 합계"]
            return json.dumps({
                "error": f"'{train_type}'에 해당하는 차종 없음",
                "사용가능한_차종": all_cols,
            }, ensure_ascii=False, indent=2)
        return _wrap(result, "한국철도공사_차종별운행", "2025.08.31")

    return _wrap(rows, "한국철도공사_차종별운행", "2025.08.31")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8008)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
