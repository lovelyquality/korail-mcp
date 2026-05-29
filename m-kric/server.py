"""korail-kric MCP server.

국가철도공단(KRIC) openapi.kric.go.kr 전국 도시철도 API
60개 엔드포인트를 15개 도구로 통합.

분류:
  열차이용정보 (3): 노선·편성, 시각표, 열차 시설·환경
  편의정보 (5): 역사정보, 시각표·혼잡도, 편의시설, 환경정보, 주변·환승
  교통약자정보 (4): 승강장 접근, 이동경로, 엘리베이터/리프트, 차량 접근성
  안전정보 (3): 역사 안전시설, 스크린도어, 차량 안전장비

공통 필터:
  rail_opr_istt_cd: 철도운영기관코드 (서울교통공사=11, 부산교통공사=21 등)
  ln_cd          : 노선코드
  stin_cd        : 역사코드
  stin_nm        : 역사명 (일부 API)
  train_no       : 열차번호 (차량 관련 API)

API 키: .env 파일의 KRIC_API_KEY
"""

import os
import httpx
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(encoding="utf-8-sig")
KRIC_API_KEY = os.getenv("KRIC_API_KEY")
KRIC_BASE = "https://openapi.kric.go.kr/openapi"

mcp = FastMCP("korail-kric")


# ── 공통 헬퍼 ─────────────────────────────────────────────

def _get(
    endpoint: str,
    extra: dict | None = None,
    num_rows: int = 100,
    page: int = 1,
) -> tuple[list[dict], dict]:
    """KRIC REST API 호출. (data_list, header) 반환."""
    params: dict[str, Any] = {
        "serviceKey": KRIC_API_KEY,
        "format": "json",
        "numOfRows": num_rows,
        "pageNo": page,
    }
    if extra:
        params.update({k: v for k, v in extra.items() if v not in (None, "")})
    try:
        r = httpx.get(f"{KRIC_BASE}/{endpoint}", params=params, timeout=20)
        data = r.json()
    except Exception as exc:
        return [], {"resultCode": "ERR", "resultMsg": str(exc)}

    header = data.get("header", {})
    if header.get("resultCode") not in ("00", "0000"):
        return [], header

    body = data.get("body", [])
    return (body if isinstance(body, list) else [body]), header


def _meta(*endpoints: str) -> dict:
    return {
        "출처": "국가철도공단(KRIC) 공공데이터 openapi.kric.go.kr",
        "참고API": list(endpoints),
    }


def _common(
    rail_opr_istt_cd: str,
    ln_cd: str,
    stin_cd: str,
    stin_nm: str,
    train_no: str = "",
) -> dict:
    """공통 필터 딕셔너리 생성."""
    d = {
        "railOprIsttCd": rail_opr_istt_cd,
        "lnCd": ln_cd,
        "stinCd": stin_cd,
        "stinNm": stin_nm,
    }
    if train_no:
        d["trainNo"] = train_no
    return d


# ═══════════════════════════════════════════════════════════
# 열차이용정보 (3개 도구)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_subway_routes(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """전국 도시철도 노선정보 및 열차 편성종류 조회.

    rail_opr_istt_cd(운영기관코드), ln_cd(노선코드) 필터 가능.
    노선 기본정보(노선명, 기점·종점, 총 길이 등)와
    편성종류(편성량수, 편성종류명)를 함께 반환.
    """
    extra = {"railOprIsttCd": rail_opr_istt_cd, "lnCd": ln_cd}
    routes, h1 = _get("trainUseInfo/subwayRouteInfo", extra, per_page, page)
    composed, h2 = _get("trainUseInfo/subwayComposed", extra, per_page, page)
    return {
        "route_info": {"count": len(routes), "data": routes},
        "composed_info": {"count": len(composed), "data": composed},
        "_meta": _meta(
            "trainUseInfo/subwayRouteInfo",
            "trainUseInfo/subwayComposed",
        ),
    }


@mcp.tool()
def get_subway_timetable(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    stin_cd: str = "",
    stin_nm: str = "",
    train_no: str = "",
    express: bool = False,
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 운행시각표 조회 (열차별).

    express=False → 일반 시각표, express=True → 급행 시각표.
    역사코드(stin_cd) 또는 역사명(stin_nm), 노선코드(ln_cd),
    운영기관코드(rail_opr_istt_cd), 열차번호(train_no) 필터 가능.
    """
    endpoint = (
        "trainUseInfo/subwayTimetableExp"
        if express
        else "trainUseInfo/subwayTimetable"
    )
    extra = _common(rail_opr_istt_cd, ln_cd, stin_cd, stin_nm, train_no)
    rows, header = _get(endpoint, extra, per_page, page)
    return {
        "type": "급행" if express else "일반",
        "count": len(rows),
        "data": rows,
        "_meta": _meta(endpoint),
    }


@mcp.tool()
def get_subway_train_details(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    train_no: str = "",
    info_type: str = "both",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 열차 시설정보 및 환경정보 조회.

    info_type: "facilities"(시설), "environment"(환경), "both"(기본, 둘 다).
    시설정보 - 객실 내 안내장치·CCTV·좌석 등.
    환경정보 - 온도·습도·CO2·미세먼지·소음 등.
    """
    extra = {"railOprIsttCd": rail_opr_istt_cd, "lnCd": ln_cd, "trainNo": train_no}
    result: dict[str, Any] = {"_meta": _meta(
        "trainUseInfo/subwayFacilitiesInfo",
        "trainUseInfo/subwayEnvironmental",
    )}

    if info_type in ("facilities", "both"):
        rows, _ = _get("trainUseInfo/subwayFacilitiesInfo", extra, per_page, page)
        result["facilities"] = {"count": len(rows), "data": rows}

    if info_type in ("environment", "both"):
        rows, _ = _get("trainUseInfo/subwayEnvironmental", extra, per_page, page)
        result["environment"] = {"count": len(rows), "data": rows}

    return result


# ═══════════════════════════════════════════════════════════
# 편의정보 (5개 도구)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_urban_station_info(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 기본정보 및 열차운영기관 정보 조회.

    역사명·주소·위도·경도·노선명 등 기본 정보와
    운영기관 목록(기관명, 노선 수 등)을 반환.
    """
    extra = _common(rail_opr_istt_cd, ln_cd, stin_cd, stin_nm)
    stations, _ = _get("convenientInfo/stationInfo", extra, per_page, page)
    operators, _ = _get("convenientInfo/trainOperationOrgan", {
        "railOprIsttCd": rail_opr_istt_cd,
    }, per_page, page)
    return {
        "station_info": {"count": len(stations), "data": stations},
        "operators": {"count": len(operators), "data": operators},
        "_meta": _meta(
            "convenientInfo/stationInfo",
            "convenientInfo/trainOperationOrgan",
        ),
    }


@mcp.tool()
def get_urban_station_schedule(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사별 운행시각표 및 혼잡도 조회.

    역사별 전체 운행시각표(도착·출발 시각, 방면 등)와
    혼잡도(서울교통공사 노선 위주, 시간대별 승하차 혼잡 지수)를 반환.
    """
    extra = _common(rail_opr_istt_cd, ln_cd, stin_cd, stin_nm)
    timetable, _ = _get("convenientInfo/stationTimetable", extra, per_page, page)
    congestion, _ = _get("convenientInfo/stationCongestion", {
        "railOprIsttCd": rail_opr_istt_cd,
        "stinCd": stin_cd,
    }, per_page, page)
    return {
        "timetable": {"count": len(timetable), "data": timetable},
        "congestion": {"count": len(congestion), "data": congestion},
        "_meta": _meta(
            "convenientInfo/stationTimetable",
            "convenientInfo/stationCongestion",
        ),
    }


# 편의시설 종류 → 엔드포인트 매핑
_FACILITY_MAP = {
    "elevator":    "convenientInfo/stationElevator",
    "escalator":   "convenientInfo/stationEscalator",
    "toilet":      "convenientInfo/stationToilet",
    "atm":         "convenientInfo/stationATM",
    "locker":      "convenientInfo/stationLocker",
    "dairy_room":  "convenientInfo/stationDairyRoom",
    "wifi":        "convenientInfo/stationWIFI",
    "lost_office": "convenientInfo/stationLostPropertyOffice",
}


@mcp.tool()
def get_urban_station_facilities(
    stin_cd: str = "",
    stin_nm: str = "",
    facility_type: str = "all",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 편의시설 현황 조회.

    facility_type 선택지:
      "elevator"   → 엘리베이터 현황
      "escalator"  → 에스컬레이터 현황
      "toilet"     → 화장실 현황
      "atm"        → ATM 기기 위치
      "locker"     → 물품보관함 현황
      "dairy_room" → 수유실 현황
      "wifi"       → 와이파이 위치
      "lost_office"→ 유실물센터 정보
      "all"        → 위 8종 모두 (기본값, 응답이 큼)
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    targets = (
        list(_FACILITY_MAP.keys())
        if facility_type == "all"
        else [facility_type]
        if facility_type in _FACILITY_MAP
        else list(_FACILITY_MAP.keys())
    )
    result: dict[str, Any] = {}
    for key in targets:
        rows, _ = _get(_FACILITY_MAP[key], extra, per_page, page)
        result[key] = {"count": len(rows), "data": rows}

    result["_meta"] = _meta(*(_FACILITY_MAP[k] for k in targets))
    return result


# 환경 종류 → 엔드포인트 매핑
_ENV_MAP = {
    "air_quality": "convenientInfo/stationAirQuality",
    "noise":       "convenientInfo/stationNoiseLevel",
    "humidity":    "convenientInfo/stationHumidity",
    "temperature": "convenientInfo/stationTemperature",
}


@mcp.tool()
def get_urban_station_environment(
    stin_cd: str = "",
    stin_nm: str = "",
    env_type: str = "all",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 환경정보 조회.

    env_type 선택지:
      "air_quality" → 공기질 측정 정보 (CO2, 미세먼지, VOC 등)
      "noise"       → 소음도 정보
      "humidity"    → 습도 정보
      "temperature" → 온도 정보
      "all"         → 4종 모두 (기본값)
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    targets = (
        list(_ENV_MAP.keys())
        if env_type == "all"
        else [env_type]
        if env_type in _ENV_MAP
        else list(_ENV_MAP.keys())
    )
    result: dict[str, Any] = {}
    for key in targets:
        rows, _ = _get(_ENV_MAP[key], extra, per_page, page)
        result[key] = {"count": len(rows), "data": rows}

    result["_meta"] = _meta(*(_ENV_MAP[k] for k in targets))
    return result


@mcp.tool()
def get_urban_station_access(
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 환승·출구·주변 교통 정보 통합 조회.

    환승정보(연결 노선·이동 방법), 출구정보(출구번호·방향·인근 시설),
    주변 주차장·대중교통·자전거 주차장·자전거 대여 정보를 반환.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    transfer, _ = _get("convenientInfo/stationTransferInfo", extra, per_page, page)
    gate, _ = _get("convenientInfo/stationGateInfo", extra, per_page, page)
    parking, _ = _get(
        "convenientInfo/stationEnvironsParkingLot", extra, per_page, page
    )
    public_trans, _ = _get(
        "convenientInfo/stationEnvironsPublicTransport", extra, per_page, page
    )
    bike_park, _ = _get(
        "convenientInfo/stationBikeParkingLot", extra, per_page, page
    )
    bike_rental, _ = _get(
        "convenientInfo/stationBikeRental", extra, per_page, page
    )
    return {
        "transfer_info":     {"count": len(transfer),      "data": transfer},
        "gate_info":         {"count": len(gate),           "data": gate},
        "parking":           {"count": len(parking),        "data": parking},
        "public_transport":  {"count": len(public_trans),   "data": public_trans},
        "bike_parking":      {"count": len(bike_park),      "data": bike_park},
        "bike_rental":       {"count": len(bike_rental),    "data": bike_rental},
        "_meta": _meta(
            "convenientInfo/stationTransferInfo",
            "convenientInfo/stationGateInfo",
            "convenientInfo/stationEnvironsParkingLot",
            "convenientInfo/stationEnvironsPublicTransport",
            "convenientInfo/stationBikeParkingLot",
            "convenientInfo/stationBikeRental",
        ),
    }


# ═══════════════════════════════════════════════════════════
# 교통약자정보 (4개 도구)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_accessible_platform(
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """교통약자 승강장 관련 정보 조회.

    승강장 기본정보(stPlf), 안전발판 설치유무,
    승강장·열차 간 이격거리를 통합 반환.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    platform, _ = _get("convenientInfo/stPlf", extra, per_page, page)
    safety_plf, _ = _get(
        "vulnerableUserInfo/stationSafetyPlatform", extra, per_page, page
    )
    distance, _ = _get(
        "vulnerableUserInfo/stationPlatformTrainDistance", extra, per_page, page
    )
    return {
        "platform_info":   {"count": len(platform),    "data": platform},
        "safety_platform": {"count": len(safety_plf),  "data": safety_plf},
        "train_distance":  {"count": len(distance),    "data": distance},
        "_meta": _meta(
            "convenientInfo/stPlf",
            "vulnerableUserInfo/stationSafetyPlatform",
            "vulnerableUserInfo/stationPlatformTrainDistance",
        ),
    }


@mcp.tool()
def get_accessible_routes(
    stin_cd: str = "",
    stin_nm: str = "",
    route_type: str = "both",
    standard: bool = False,
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """교통약자 역사 이동경로 조회.

    route_type: "station"(출입구→승강장), "transfer"(환승), "both"(기본).
    standard=True 시 표준(handicapped) 엔드포인트 사용.
    경로 단계별 이동 방법·거리·경유 시설 정보 포함.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    prefix = "handicapped" if standard else "vulnerableUserInfo"
    result: dict[str, Any] = {}

    if route_type in ("station", "both"):
        rows, _ = _get(f"{prefix}/stationMovement", extra, per_page, page)
        result["station_movement"] = {"count": len(rows), "data": rows}

    if route_type in ("transfer", "both"):
        rows, _ = _get(f"{prefix}/transferMovement", extra, per_page, page)
        result["transfer_movement"] = {"count": len(rows), "data": rows}

    endpoints = []
    if route_type in ("station", "both"):
        endpoints.append(f"{prefix}/stationMovement")
    if route_type in ("transfer", "both"):
        endpoints.append(f"{prefix}/transferMovement")
    result["_meta"] = _meta(*endpoints)
    return result


@mcp.tool()
def get_accessible_elevators(
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """교통약자 엘리베이터·휠체어리프트 정보 조회.

    엘리베이터 이동동선, 인접 차량번호,
    휠체어리프트 위치·이동동선을 통합 반환.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    elev_move, _ = _get(
        "vulnerableUserInfo/stationElevatorMovement", extra, per_page, page
    )
    elev_car, _ = _get(
        "vulnerableUserInfo/stationElevatorCarNumber", extra, per_page, page
    )
    lift_loc, _ = _get(
        "vulnerableUserInfo/stationWheelchairLiftLocation", extra, per_page, page
    )
    lift_move, _ = _get(
        "vulnerableUserInfo/stationWheelchairLiftMovement", extra, per_page, page
    )
    # 교통약자 역사 내 엘리베이터 이동동선 (별도 분류)
    elev_inner, _ = _get(
        "trafficWeekInfo/stinElevatorMovement", extra, per_page, page
    )
    return {
        "elevator_movement":   {"count": len(elev_move),  "data": elev_move},
        "elevator_car_number": {"count": len(elev_car),   "data": elev_car},
        "lift_location":       {"count": len(lift_loc),   "data": lift_loc},
        "lift_movement":       {"count": len(lift_move),  "data": lift_move},
        "elevator_inner_path": {"count": len(elev_inner), "data": elev_inner},
        "_meta": _meta(
            "vulnerableUserInfo/stationElevatorMovement",
            "vulnerableUserInfo/stationElevatorCarNumber",
            "vulnerableUserInfo/stationWheelchairLiftLocation",
            "vulnerableUserInfo/stationWheelchairLiftMovement",
            "trafficWeekInfo/stinElevatorMovement",
        ),
    }


@mcp.tool()
def get_accessible_train(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    stin_cd: str = "",
    stin_nm: str = "",
    train_no: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """교통약자 열차 접근성 및 역사 마커 정보 조회.

    차량별 우선좌석·임산부좌석·휠체어 승차가능·안전벨트 유무,
    역사별 점자블록 설치유무·장애인화장실 위치·계단 인접 차량번호를 반환.
    """
    extra_train = _common(rail_opr_istt_cd, ln_cd, stin_cd, stin_nm, train_no)
    extra_stin = {"stinCd": stin_cd, "stinNm": stin_nm}

    priority, _ = _get(
        "vulnerableUserInfo/trainPrioritySeat", extra_train, per_page, page
    )
    pregnant, _ = _get(
        "vulnerableUserInfo/trainSeatPregnantWoman", extra_train, per_page, page
    )
    wc_board, _ = _get(
        "vulnerableUserInfo/trainWheelchairBoardPossible", extra_train, per_page, page
    )
    wc_belt, _ = _get(
        "vulnerableUserInfo/trainWheelchairSeatBelt", extra_train, per_page, page
    )
    braille, _ = _get(
        "vulnerableUserInfo/stationBrailleDisplays", extra_stin, per_page, page
    )
    disabled_toilet, _ = _get(
        "vulnerableUserInfo/stationDisabledToilet", extra_stin, per_page, page
    )
    stair_car, _ = _get(
        "vulnerableUserInfo/stationStairCarNumber", extra_stin, per_page, page
    )
    return {
        "priority_seat":         {"count": len(priority),        "data": priority},
        "pregnant_seat":         {"count": len(pregnant),        "data": pregnant},
        "wheelchair_board":      {"count": len(wc_board),        "data": wc_board},
        "wheelchair_seatbelt":   {"count": len(wc_belt),         "data": wc_belt},
        "braille_display":       {"count": len(braille),         "data": braille},
        "disabled_toilet":       {"count": len(disabled_toilet), "data": disabled_toilet},
        "stair_car_number":      {"count": len(stair_car),       "data": stair_car},
        "_meta": _meta(
            "vulnerableUserInfo/trainPrioritySeat",
            "vulnerableUserInfo/trainSeatPregnantWoman",
            "vulnerableUserInfo/trainWheelchairBoardPossible",
            "vulnerableUserInfo/trainWheelchairSeatBelt",
            "vulnerableUserInfo/stationBrailleDisplays",
            "vulnerableUserInfo/stationDisabledToilet",
            "vulnerableUserInfo/stationStairCarNumber",
        ),
    }


# ═══════════════════════════════════════════════════════════
# 안전정보 (3개 도구)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_station_safety_equipment(
    stin_cd: str = "",
    stin_nm: str = "",
    safety_type: str = "all",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 안전시설 현황 조회.

    safety_type 선택지:
      "fire"        → 소화설비 현황
      "defibrillator" → 제세동기(AED) 현황
      "call_phone"  → 비상콜폰 현황
      "respirator"  → 공기호흡기 현황
      "safety_fence"→ 안전펜스 현황
      "all"         → 5종 모두 (기본값)
    """
    _safety_map = {
        "fire":          "safetyInfo/stationFireExtinguishing",
        "defibrillator": "safetyInfo/stationDefibrillator",
        "call_phone":    "safetyInfo/stationEmergencyCallPhone",
        "respirator":    "safetyInfo/stationAirRespirator",
        "safety_fence":  "safetyInfo/stationSafetyFence",
    }
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    targets = (
        list(_safety_map.keys())
        if safety_type == "all"
        else [safety_type]
        if safety_type in _safety_map
        else list(_safety_map.keys())
    )
    result: dict[str, Any] = {}
    for key in targets:
        rows, _ = _get(_safety_map[key], extra, per_page, page)
        result[key] = {"count": len(rows), "data": rows}

    result["_meta"] = _meta(*(_safety_map[k] for k in targets))
    return result


@mcp.tool()
def get_station_screen_door(
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 역사 스크린도어(PSD) 현황 조회.

    역사별 스크린도어 설치 현황, 유형, 제조사 등 정보 반환.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    rows, _ = _get("safetyInfo/stationScreenDoor", extra, per_page, page)
    return {
        "count": len(rows),
        "data": rows,
        "_meta": _meta("safetyInfo/stationScreenDoor"),
    }


@mcp.tool()
def get_train_safety_equipment(
    rail_opr_istt_cd: str = "",
    ln_cd: str = "",
    train_no: str = "",
    safety_type: str = "all",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """도시철도 차량 안전장비 현황 조회.

    safety_type 선택지:
      "fire_extinguisher" → 소화기 현황
      "crush_hammer"      → 비상탈출망치 현황
      "call_phone"        → 차량 비상콜폰 현황
      "defibrillator"     → 차량 제세동기(AED) 현황
      "door_manual"       → 출입문 수동 설정 현황
      "all"               → 5종 모두 (기본값)
    """
    _train_safety_map = {
        "fire_extinguisher": "safetyInfo/trainFireExtinguisher",
        "crush_hammer":      "safetyInfo/trainCrushHammer",
        "call_phone":        "safetyInfo/trainEmergencyCallPhone",
        "defibrillator":     "safetyInfo/trainDefibrillator",
        "door_manual":       "safetyInfo/trainDoorManualSetting",
    }
    extra = {
        "railOprIsttCd": rail_opr_istt_cd,
        "lnCd": ln_cd,
        "trainNo": train_no,
    }
    targets = (
        list(_train_safety_map.keys())
        if safety_type == "all"
        else [safety_type]
        if safety_type in _train_safety_map
        else list(_train_safety_map.keys())
    )
    result: dict[str, Any] = {}
    for key in targets:
        rows, _ = _get(_train_safety_map[key], extra, per_page, page)
        result[key] = {"count": len(rows), "data": rows}

    result["_meta"] = _meta(*(_train_safety_map[k] for k in targets))
    return result


# ═══════════════════════════════════════════════════════════
# 표준(handicapped) 편의시설 통합 도구 (별도 엔드포인트)
# ═══════════════════════════════════════════════════════════

@mcp.tool()
def get_handicapped_facilities(
    stin_cd: str = "",
    stin_nm: str = "",
    page: int = 1,
    per_page: int = 100,
) -> dict:
    """교통약자용 편의시설 표준 데이터 조회 (handicapped 엔드포인트).

    표준화된 편의시설 정보(stationCnvFacl)를 반환.
    get_urban_station_facilities 와 달리 표준 규격 데이터.
    """
    extra = {"stinCd": stin_cd, "stinNm": stin_nm}
    rows, _ = _get("handicapped/stationCnvFacl", extra, per_page, page)
    return {
        "count": len(rows),
        "data": rows,
        "_meta": _meta("handicapped/stationCnvFacl"),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8012)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
