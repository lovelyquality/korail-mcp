"""korail-urban-rail MCP server.

전국 도시철도(수도권 1~9호선·신분당·공항철도 등, 부산·대구·대전·광주·인천,
경전철·GTX 등) 역사 종합정보. 국가철도공단(KRIC) 오픈API 27건을 기능 그룹별
도구로 통합한다.

데이터 소스: 국가철도공단 KRIC 오픈API (openapi.kric.go.kr)
  - Cloudflare 프록시(KORAIL_PROXY_URL)/proxy/kric/ 를 경유해 서비스키 없이 호출.
  - 프록시가 서비스키(공통키 + 승강장정보 stPlf 전용키)를 대신 부착한다.

호출 구조: GET {PROXY}/proxy/kric/{서비스ID}/{오퍼레이션ID}
           ?format=json&railOprIsttCd=&lnCd=&stinCd=...
응답 구조: {"header": {"resultCode","resultMsg","resultCnt"}, "body": [ ... ]}
           resultCode "00" 이 정상.

KRIC API는 운영기관코드(railOprIsttCd)+선코드(lnCd)+역코드(stinCd)가 필수라
역명만으로는 조회할 수 없다. 따라서 data/stations.json(전국 1,108개 역 코드표)을
번들해 역명→코드 변환을 내장한다. 환승역 등 동일 역명은 operator 인자로 좁힌다.
"""

import os
import json
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(encoding="utf-8-sig")

PROXY_URL = os.getenv(
    "KORAIL_PROXY_URL", "https://korail-mcp-proxy.lovelymong.workers.dev"
).rstrip("/")
KRIC_BASE = f"{PROXY_URL}/proxy/kric"

mcp = FastMCP("korail-urban-rail")

# ── 역 코드표 로드 (역명 검색용) ─────────────────────────────────────────────
_DATA_DIR = Path(__file__).parent / "data"
try:
    with open(_DATA_DIR / "stations.json", encoding="utf-8") as _f:
        STATIONS: list[dict[str, str]] = json.load(_f)
except FileNotFoundError:
    STATIONS = []


# ── 기능 그룹 ↔ KRIC (서비스ID, 오퍼레이션ID, 라벨) 매핑 ──────────────────────

_ACCESS = {
    "elevator":          ("convenientInfo",     "stationElevator",                "엘리베이터 현황"),
    "elevator_route":    ("vulnerableUserInfo", "stationElevatorMovement",        "엘리베이터 이동동선"),
    "elevator_route_detail":("trafficWeekInfo", "stinElevatorMovement",           "엘리베이터 상세 이동동선(경로 텍스트)"),
    "escalator":         ("convenientInfo",     "stationEscalator",               "에스컬레이터 현황"),
    "wheelchair_route":  ("vulnerableUserInfo", "stationWheelchairLiftMovement",  "휠체어리프트 이동동선"),
    "wheelchair_lift_loc":("vulnerableUserInfo","stationWheelchairLiftLocation",  "휠체어리프트 설치 위치"),
    "safety_step":       ("vulnerableUserInfo", "stationSafetyPlatform",          "승강장 안전발판 설치유무"),
    "platform_gap":      ("vulnerableUserInfo", "stationPlatformTrainDistance",   "승강장-차량 이격거리"),
    "braille":           ("vulnerableUserInfo", "stationBrailleDisplays",         "점자표시 유무"),
    "disabled_toilet":   ("vulnerableUserInfo", "stationDisabledToilet",          "장애인화장실 위치"),
    "adjacent_elevator": ("vulnerableUserInfo", "stationElevatorCarNumber",       "인접 승강기 차량번호"),
    "stair_car":         ("vulnerableUserInfo", "stationStairCarNumber",          "인접 계단 차량번호(휠체어 하차위치)"),
}

_AMENITY = {
    "toilet":       ("convenientInfo", "stationToilet",             "화장실 현황"),
    "nursing_room": ("convenientInfo", "stationDairyRoom",          "수유실 현황"),
    "locker":       ("convenientInfo", "stationLocker",             "물품보관함 현황"),
    "atm":          ("convenientInfo", "stationATM",                "ATM 기기위치"),
    "lost_found":   ("convenientInfo", "stationLostPropertyOffice", "유실물센터 정보"),
    "wifi":         ("convenientInfo", "stationWIFI",               "무선인터넷(WiFi) 위치"),
}

_SAFETY = {
    "defibrillator":   ("safetyInfo", "stationDefibrillator",       "제세동기(AED) 현황"),
    "fire_extinguish": ("safetyInfo", "stationFireExtinguishing",   "소화설비 현황"),
    "emergency_phone": ("safetyInfo", "stationEmergencyCallPhone",  "비상콜폰 현황"),
    "air_respirator":  ("safetyInfo", "stationAirRespirator",       "공기호흡기 현황"),
    "screen_door":     ("safetyInfo", "stationScreenDoor",          "스크린도어 현황"),
    "safety_fence":    ("safetyInfo", "stationSafetyFence",         "승강장 안전펜스(설치역 한정)"),
}

# 역 주변 시설 그룹 (역단위, opr+ln+stin)
_SURROUND = {
    "public_transport": ("convenientInfo", "stationEnvironsPublicTransport", "역 주변 대중교통(버스 등)"),
    "parking":          ("convenientInfo", "stationEnvironsParkingLot",      "역 주변 주차장"),
    "bike_parking":     ("convenientInfo", "stationBikeParkingLot",          "자전거 주차시설"),
    "bike_rental":      ("convenientInfo", "stationBikeRental",              "자전거 대여시설"),
}

# 역사 환경측정 그룹 (역단위, opr+ln+stin). 측정기 설치역에만 데이터 존재.
_ENV = {
    "air_quality":  ("convenientInfo", "stationAirQuality",  "공기질(미세먼지·CO2 등)"),
    "temperature":  ("convenientInfo", "stationTemperature", "온도"),
    "humidity":     ("convenientInfo", "stationHumidity",    "습도"),
    "noise":        ("convenientInfo", "stationNoiseLevel",  "소음도(설치역 드묾)"),
}

# 차량별 시설 그룹 (역 무관, railOprIsttCd+scarSqno+cpsTpCd).
# cpsTpCd(편성유형코드)·호차는 get_urban_train_composition으로 먼저 확인한다.
# 운영기관마다 보유 항목이 달라 일부는 빈 결과일 수 있다.
# (subwayFacilitiesInfo는 호차당 수백 행 중복 반환 + 아래 전용 9종과 개념 중복이라 제외)
_TRAIN_FACIL = {
    "fire_extinguisher": ("safetyInfo",         "trainFireExtinguisher",        "소화기"),
    "emergency_phone":   ("safetyInfo",         "trainEmergencyCallPhone",      "비상콜폰"),
    "crush_hammer":      ("safetyInfo",         "trainCrushHammer",             "비상탈출망치"),
    "door_manual":       ("safetyInfo",         "trainDoorManualSetting",       "출입문 수동설정"),
    "defibrillator":     ("safetyInfo",         "trainDefibrillator",           "제세동기(AED)"),
    "pregnant_seat":     ("vulnerableUserInfo", "trainSeatPregnantWoman",       "임산부 배려석"),
    "priority_seat":     ("vulnerableUserInfo", "trainPrioritySeat",            "노약자석"),
    "wheelchair_board":  ("vulnerableUserInfo", "trainWheelchairBoardPossible", "휠체어 승차가능 차량"),
    "wheelchair_belt":   ("vulnerableUserInfo", "trainWheelchairSeatBelt",      "휠체어 안전벨트"),
}

# 권역코드(mreaWideCd) — 전체노선정보
_REGION_MAP = {
    "수도권": "01", "서울": "01", "경기": "01", "인천": "01",
    "부산": "02", "대구": "03", "광주": "04", "대전": "05",
}

# 요일코드(dayCd) — 운행시각표
_DAY_MAP = {
    "전요일": "0", "전체": "0", "일": "1", "일요일": "1", "월": "2", "월요일": "2",
    "화": "3", "화요일": "3", "수": "4", "수요일": "4", "목": "5", "목요일": "5",
    "금": "6", "금요일": "6", "토": "7", "토요일": "7", "평일": "8", "휴일": "9",
}
# 환경측정구분(envrMsmtDvCd) — 열차/공기질
_ENVR_MAP = {
    "1": "미세먼지(PM10)", "2": "이산화탄소(CO2)", "3": "폼알데하이드(HCHO)",
    "4": "일산화탄소(CO)", "5": "이산화질소(NO2)", "6": "라돈(Rn)",
    "7": "휘발성유기화합물(TVOC)", "8": "석면", "9": "오존(O3)", "10": "초미세먼지(PM2.5)",
    "21": "온도", "22": "습도", "23": "소음도", "24": "진동",
}

SOURCE = "국가철도공단(KRIC) 공공데이터 (openapi.kric.go.kr)"
_MAX_STATIONS = 10  # 한 번에 조회할 역 후보 상한

# 데이터셋(오퍼레이션)별 KRIC 레일포털 최종 수정일 (data.kric.go.kr 고시, 2026-06 확인).
# KRIC API 응답에는 갱신일자 필드가 없어, 포털 고시 수정일을 데이터 기준 시점으로 노출한다.
# 대부분 2019~2020년 구축 후 갱신이 드물며, 공기질·승강장 등 일부만 최근 갱신됨.
_DATASET_DATE = {
    "stationInfo": "2020.02.13", "stationGateInfo": "2020.02.13",
    "stationTransferInfo": "2020.02.13", "stationTimetable": "2020.02.13",
    "stationElevator": "2020.05.12", "stationEscalator": "2020.02.13",
    "stationToilet": "2020.02.13", "stationDairyRoom": "2020.02.13",
    "stationLocker": "2020.02.13", "stationATM": "2020.02.13",
    "stationLostPropertyOffice": "2020.02.13", "stationAirQuality": "2025.12.08",
    "stPlf": "2026.05.11",
    "stationDefibrillator": "2020.02.13", "stationFireExtinguishing": "2020.02.13",
    "stationEmergencyCallPhone": "2020.02.13", "stationAirRespirator": "2020.05.13",
    "stationScreenDoor": "2020.02.13",
    "subwayTimetableExp": "2026.03.09", "subwayEnvironmental": "2025.12.08",
    "stationElevatorMovement": "2020.02.13", "stationWheelchairLiftMovement": "2020.02.13",
    "stationSafetyPlatform": "2020.02.13", "stationPlatformTrainDistance": "2020.02.13",
    "stationBrailleDisplays": "2020.02.13", "stationDisabledToilet": "2019.05.13",
    "stationElevatorCarNumber": "2020.02.13",
    # 2026-06-02 추가분 (KRIC OpenAPI 카탈로그 data.kric.go.kr/rips/M_01_02 고시 수정일)
    "stationStairCarNumber": "2020.02.13", "stationWheelchairLiftLocation": "2020.02.13",
    "stationWIFI": "2020.02.13", "stationSafetyFence": "2020.02.13",
    "stationEnvironsPublicTransport": "2020.02.13", "stationEnvironsParkingLot": "2020.02.13",
    "stationBikeParkingLot": "2020.02.13", "stationBikeRental": "2020.02.13",
    "stationNoiseLevel": "2020.02.13", "stationHumidity": "2020.02.13",
    "stationTemperature": "2020.02.13",
    "stationMovement": "2020.05.13", "stinElevatorMovement": "2020.05.13",
    "subwayRouteInfo": "2020.05.13", "subwayComposed": "2020.02.13",
    "trainFireExtinguisher": "2020.02.13", "trainEmergencyCallPhone": "2020.02.13",
    "trainCrushHammer": "2020.02.13", "trainDoorManualSetting": "2020.02.13",
    "trainDefibrillator": "2020.02.13", "trainSeatPregnantWoman": "2020.02.13",
    "trainPrioritySeat": "2020.02.13", "trainWheelchairBoardPossible": "2020.02.13",
    "trainWheelchairSeatBelt": "2020.02.13",
}


def _modified(op: str) -> str | None:
    """오퍼레이션의 KRIC 레일포털 최종 수정일 문자열."""
    d = _DATASET_DATE.get(op)
    return f"{d} (KRIC 레일포털 최종수정)" if d else None


# ── 공통 헬퍼 ────────────────────────────────────────────────────────────────

def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def _err(msg: str) -> str:
    return _json({"error": msg})


# KRIC 응답행에서 측정일시 필드를 찾기 위한 키 힌트 (소문자 부분일치)
_DATE_HINTS = ("dttm", "ymd")


def _measure_period(rows: list) -> list[str]:
    """응답행에서 측정일시(msmtDttm 등) 값을 모은다. 공기질 등 측정성 데이터용."""
    vals: set[str] = set()
    for r in rows:
        if not isinstance(r, dict):
            continue
        for k, v in r.items():
            if v in (None, ""):
                continue
            if any(h in str(k).lower() for h in _DATE_HINTS):
                s = str(v).strip()
                if s:
                    vals.add(s)
    return sorted(vals)[:8]


def _wrap(data: list, dataset: str, extra: dict | None = None) -> str:
    meta = {"출처": SOURCE, "데이터셋": dataset, "건수": len(data)}
    period = _measure_period(data) if data else []
    if period:
        meta["측정시점"] = period
    if extra:
        meta.update(extra)
    return _json({"data": data, "_meta": meta})


def _resolve(station_name: str, operator: str = "", line: str = "") -> list[dict]:
    """역명 → 코드 후보 목록. 정확 일치 우선, 없으면 부분 일치.
    operator: 운영기관 코드(S1) 또는 명('서울교통공사') 부분일치로 좁힘.
    line: 선코드(3) 또는 선명('3호선') 부분일치로 좁힘."""
    name = (station_name or "").strip()
    if not name:
        return []
    exact = [s for s in STATIONS if s["stinNm"] == name]
    cands = exact if exact else [s for s in STATIONS if name in s["stinNm"]]
    if operator:
        op = operator.strip()
        cands = [s for s in cands if op == s["opr"] or op in s["oprNm"]]
    if line:
        ln = line.strip()
        cands = [s for s in cands if ln == s["ln"] or ln in s["lnNm"]]
    return cands


def _label(s: dict) -> str:
    return f'{s["oprNm"]} {s["lnNm"]} {s["stinNm"]}'


def _resolve_opr(operator: str) -> str:
    """운영기관 코드(S1) 또는 명('서울교통공사') → 코드. 못 찾으면 입력 그대로."""
    op = (operator or "").strip()
    if not op or any(s["opr"] == op for s in STATIONS):
        return op
    return next((s["opr"] for s in STATIONS if op in s["oprNm"]), op)


def _opr_name(opr: str) -> str:
    """운영기관 코드 → 명. 없으면 코드 그대로."""
    return next((s["oprNm"] for s in STATIONS if s["opr"] == opr), opr)


def _too_many(cands: list[dict], name: str) -> str:
    brief = [{"운영기관": c["oprNm"], "노선": c["lnNm"], "역명": c["stinNm"],
              "operator": c["opr"]} for c in cands[:30]]
    return _json({
        "error": f"'{name}'에 해당하는 역이 {len(cands)}개로 너무 많습니다. "
                 f"operator(운영기관 코드/명)로 좁히거나 정확한 역명을 입력하세요.",
        "후보": brief,
    })


def _kric_get(svc: str, op: str, params: dict) -> tuple[list, str | None]:
    """KRIC API 1건 호출. (body 리스트, 에러메시지) 반환.

    일부 API(stationInfo, 이동동선 등)는 stinCd를 넘겨도 노선 전체를 반환하므로,
    요청 stinCd가 있으면 응답행의 stinCd로 후처리 필터링한다(해당 역만 남김)."""
    url = f"{KRIC_BASE}/{svc}/{op}"
    q = {"format": "json", **params}
    try:
        r = httpx.get(url, params=q, timeout=30)
    except Exception as e:  # noqa: BLE001
        return [], f"요청 실패: {type(e).__name__}: {e}"
    if r.status_code != 200:
        return [], f"HTTP {r.status_code}"
    try:
        body = r.json()
    except Exception:  # noqa: BLE001
        return [], f"JSON 파싱 실패: {r.text[:200]}"
    hdr = body.get("header", {}) if isinstance(body, dict) else {}
    if hdr.get("resultCode") not in ("00", None):
        return [], hdr.get("resultMsg", f"오류(resultCode={hdr.get('resultCode')})")
    rows = body.get("body", []) if isinstance(body, dict) else []
    rows = rows or []
    stin = params.get("stinCd")
    if stin is not None:
        # stinCd 필드를 가진 행만 요청 역으로 한정. 필드가 없으면 그대로 통과.
        filtered = [r for r in rows if str(r.get("stinCd", stin)) == str(stin)]
        rows = filtered
    return rows, None


def _query_single(svc: str, op: str, dataset: str, station_name: str,
                  operator: str = "", line: str = "", extra: dict | None = None) -> str:
    """단일 종류 API를 역 후보들에 대해 호출하고 합쳐 반환."""
    cands = _resolve(station_name, operator, line)
    if not cands:
        return _err(f"'{station_name}' 역을 찾을 수 없습니다. "
                    f"search_urban_station으로 역명·운영기관을 먼저 확인하세요.")
    if len(cands) > _MAX_STATIONS:
        return _too_many(cands, station_name)

    rows: list = []
    errors: list = []
    for s in cands:
        p = {"railOprIsttCd": s["opr"], "lnCd": s["ln"], "stinCd": s["stin"]}
        if extra:
            p.update(extra)
        data, msg = _kric_get(svc, op, p)
        if msg:
            errors.append(f'{_label(s)}: {msg}')
            continue
        for d in data:
            d["_역사"] = _label(s)
        rows.extend(data)
    extra_meta = {"조회역수": len(cands)}
    md = _modified(op)
    if md:
        extra_meta["데이터수정일"] = md
    if errors:
        extra_meta["비고"] = errors
    return _wrap(rows, dataset, extra_meta)


def _query_group(group: dict, sub_type: str, station_name: str,
                 operator: str = "", line: str = "") -> str:
    """기능 그룹(접근성/편의/안전) 공통 조회. sub_type='all'이면 그룹 내 전체."""
    if sub_type != "all" and sub_type not in group:
        return _err(f"'{sub_type}' 미지원. 사용 가능: {list(group.keys()) + ['all']}")

    cands = _resolve(station_name, operator, line)
    if not cands:
        return _err(f"'{station_name}' 역을 찾을 수 없습니다. "
                    f"search_urban_station으로 역명·운영기관을 먼저 확인하세요.")
    if len(cands) > _MAX_STATIONS:
        return _too_many(cands, station_name)
    if sub_type == "all" and len(cands) > 3:
        return _too_many(cands, station_name)  # 전체 종류 × 다수 역은 과도 → 좁히게

    types = list(group) if sub_type == "all" else [sub_type]
    result: dict[str, Any] = {}
    errors: list = []
    all_rows: list = []
    for t in types:
        svc, op, label = group[t]
        bucket: list = []
        for s in cands:
            data, msg = _kric_get(svc, op,
                                  {"railOprIsttCd": s["opr"], "lnCd": s["ln"], "stinCd": s["stin"]})
            if msg:
                errors.append(f'{label}/{_label(s)}: {msg}')
                continue
            for d in data:
                d["_역사"] = _label(s)
            bucket.extend(data)
        result[t] = {"종류": label, "수정일": _DATASET_DATE.get(op, "미상"),
                     "건수": len(bucket), "data": bucket}
        all_rows.extend(bucket)

    meta = {"출처": SOURCE, "조회종류": types, "조회역수": len(cands),
            "데이터수정일": {t: _DATASET_DATE.get(group[t][1], "미상") for t in types}}
    period = _measure_period(all_rows)
    if period:
        meta["측정시점"] = period
    if errors:
        meta["비고"] = errors
    return _json({"data": result, "_meta": meta})


# ══ 도구 ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def search_urban_station(station_name: str = "", operator: str = "") -> str:
    """전국 도시철도 역명으로 운영기관·선·역코드를 검색한다 (다른 조회의 선행 단계).

    KRIC API는 운영기관·선·역코드가 필요하므로, 먼저 이 도구로 역을 특정하면
    환승역 등 동일 역명의 운영기관 구분을 확인할 수 있다.
    station_name: 역명 부분일치 (예: '서울역', '강남'). 미입력 시 operator 기준 전체.
    operator: 운영기관 코드(예: 'S1') 또는 명(예: '서울교통공사') 부분일치로 좁힘.
    """
    name = (station_name or "").strip()
    if not name and not operator:
        # 운영기관 목록 안내
        oprs = {}
        for s in STATIONS:
            oprs.setdefault(s["opr"], s["oprNm"])
        return _json({
            "안내": "station_name 또는 operator를 입력하세요.",
            "운영기관목록": [{"operator": k, "명": v} for k, v in oprs.items()],
            "전체역수": len(STATIONS),
        })
    cands = _resolve(name, operator)
    if not cands:
        return _err(f"'{station_name}'(operator='{operator}') 역을 찾을 수 없습니다.")
    out = [{"운영기관": c["oprNm"], "operator": c["opr"], "노선": c["lnNm"],
            "lnCd": c["ln"], "역명": c["stinNm"], "stinCd": c["stin"]} for c in cands]
    return _wrap(out, "역 코드 검색", {"검색어": station_name})


@mcp.tool()
def get_urban_station_info(station_name: str, operator: str = "") -> str:
    """도시철도 역사 기본정보 조회 (주소·좌표·다국어 역명).
    station_name: 역명. operator: 환승역 구분용 운영기관 코드/명(선택)."""
    return _query_single("convenientInfo", "stationInfo", "역사별 정보",
                         station_name, operator)


@mcp.tool()
def get_urban_accessibility(station_name: str, facility_type: str = "all",
                            operator: str = "") -> str:
    """도시철도 역사 접근성 시설 조회 (교통약자).

    facility_type:
      elevator             엘리베이터 현황
      elevator_route       엘리베이터 이동동선
      elevator_route_detail 엘리베이터 상세 이동동선(경로 텍스트)
      escalator            에스컬레이터 현황
      wheelchair_route     휠체어리프트 이동동선
      wheelchair_lift_loc  휠체어리프트 설치 위치(치수·한계중량)
      safety_step          승강장 안전발판 설치유무
      platform_gap         승강장-차량 이격거리
      braille              점자표시 유무
      disabled_toilet      장애인화장실 위치
      adjacent_elevator    인접 승강기 차량번호
      stair_car            인접 계단 차량번호(휠체어 하차위치)
      all                  위 전체 (역이 1~3개로 특정될 때만)
    station_name: 역명. operator: 운영기관 코드/명(선택).
    """
    return _query_group(_ACCESS, facility_type, station_name, operator)


@mcp.tool()
def get_urban_amenity(station_name: str, amenity_type: str = "all",
                      operator: str = "") -> str:
    """도시철도 역사 편의시설 조회.

    amenity_type: toilet(화장실) / nursing_room(수유실) / locker(물품보관함) /
                  atm(ATM) / lost_found(유실물센터) / wifi(무선인터넷) / all(전체)
    station_name: 역명. operator: 운영기관 코드/명(선택).
    """
    return _query_group(_AMENITY, amenity_type, station_name, operator)


@mcp.tool()
def get_urban_safety(station_name: str, safety_type: str = "all",
                     operator: str = "") -> str:
    """도시철도 역사 안전시설 조회.

    safety_type: defibrillator(제세동기) / fire_extinguish(소화설비) /
                 emergency_phone(비상콜폰) / air_respirator(공기호흡기) /
                 screen_door(스크린도어) / safety_fence(승강장 안전펜스) / all(전체)
    station_name: 역명. operator: 운영기관 코드/명(선택).
    """
    return _query_group(_SAFETY, safety_type, station_name, operator)


@mcp.tool()
def get_urban_exit_info(station_name: str, operator: str = "") -> str:
    """도시철도 역사 출구정보 조회 (출구번호·주변시설·거리).
    station_name: 역명. operator: 운영기관 코드/명(선택)."""
    return _query_single("convenientInfo", "stationGateInfo", "역사별 출구정보",
                         station_name, operator)


@mcp.tool()
def get_urban_transfer_info(station_name: str, operator: str = "") -> str:
    """도시철도 역사 환승정보 조회 (환승노선·환승거리·동선).
    station_name: 역명. operator: 운영기관 코드/명(선택)."""
    return _query_single("convenientInfo", "stationTransferInfo", "역사별 환승정보",
                         station_name, operator)


@mcp.tool()
def get_urban_platform(station_name: str, operator: str = "") -> str:
    """도시철도 역사 승강장 정보 조회 (승강장 유형·복합여부·안전발판 등).
    station_name: 역명. operator: 운영기관 코드/명(선택)."""
    return _query_single("convenientInfo", "stPlf", "역사별 승강장 정보",
                         station_name, operator)


@mcp.tool()
def get_urban_environment(station_name: str, measure: str = "all",
                          operator: str = "") -> str:
    """도시철도 역사 환경측정 정보 조회 (공기질·온도·습도·소음).

    measure: air_quality(공기질·미세먼지·CO2) / temperature(온도) /
             humidity(습도) / noise(소음도) / all(전체)
    station_name: 역명. operator: 운영기관 코드/명(선택).
    주의: 환경측정기는 일부 운영기관·역에만 설치되어 데이터가 없을 수 있다
          (특히 소음도). 측정값에는 측정일시(msmtDttm)가 함께 온다.
    """
    return _query_group(_ENV, measure, station_name, operator)


@mcp.tool()
def get_urban_timetable(station_name: str, day: str = "평일",
                        express: bool = False, operator: str = "") -> str:
    """도시철도 역사별 운행시각표(열차 도착·출발시각) 조회.

    station_name: 역명. operator: 운영기관 코드/명(선택).
    day: 요일 — 평일/휴일/토/일/월~금 또는 전요일. (기본 평일)
    express: True면 급행 시각표(운영기관에 따라 미제공일 수 있음).
    """
    day_cd = _DAY_MAP.get(day.strip(), day.strip())
    if express:
        return _query_single("trainUseInfo", "subwayTimetableExp",
                             f"역사별 운행시각표(급행, {day})", station_name, operator,
                             extra={"dayCd": day_cd})
    return _query_single("convenientInfo", "stationTimetable",
                         f"역사별 운행시각표({day})", station_name, operator,
                         extra={"dayCd": day_cd})


@mcp.tool()
def get_urban_train_environment(operator: str, train_no: str = "",
                                measure: str = "") -> str:
    """도시철도 열차 차내 환경정보 조회 (CO2·미세먼지·온도·습도·소음 등, 역 무관).

    operator: 운영기관 코드(예 'S1') 또는 명(예 '서울교통공사').
    train_no: 열차번호(선택). 미입력 시 해당 운영기관 전체 측정 데이터를 반환한다
              (사용자가 열차번호를 모를 때가 많으므로 보통 생략).
    measure: 환경측정 항목코드(envrMsmtDvCd) — 1 미세먼지(PM10), 2 CO2, 21 온도,
             22 습도, 23 소음 등. 미입력 시 전체 항목.
    참고: 차내 환경 데이터는 서울교통공사(S1)·부산(BS)·대구(DG) 등 일부 기관만 제공.
          한국철도공사(KR)·공항철도(AR) 등은 미제공.
    """
    opr_code = _resolve_opr(operator)
    params = {"railOprIsttCd": opr_code}
    if train_no.strip():
        params["trnNo"] = train_no.strip()
    if measure.strip():
        params["envrMsmtDvCd"] = measure.strip()
    data, msg = _kric_get("trainUseInfo", "subwayEnvironmental", params)
    if msg:
        return _err(msg)
    extra = {"운영기관": f"{_opr_name(opr_code)}({opr_code})",
             "열차번호": train_no or "(전체)",
             "측정항목": _ENVR_MAP.get(measure.strip(), measure or "전체")}
    md = _modified("subwayEnvironmental")
    if md:
        extra["데이터수정일"] = md
    return _wrap(data, "도시철도 열차별 환경정보", extra)


@mcp.tool()
def get_urban_surroundings(station_name: str, kind: str = "all",
                           operator: str = "") -> str:
    """도시철도 역 주변 시설 조회 (대중교통·주차장·자전거).

    kind: public_transport(주변 버스 등 대중교통) / parking(주변 주차장) /
          bike_parking(자전거 주차시설) / bike_rental(자전거 대여) / all(전체)
    station_name: 역명. operator: 운영기관 코드/명(선택).
    """
    return _query_group(_SURROUND, kind, station_name, operator)


@mcp.tool()
def get_urban_movement(station_name: str, next_station: str = "",
                       operator: str = "", line: str = "") -> str:
    """도시철도 교통약자 출입구→승강장 이동경로(동선) 조회.

    엘리베이터 등 무장애 경로를 출입구부터 승강장까지 단계별 텍스트(mvContDtl)와
    안내 이미지(imgPath)로 제공한다.
    station_name: 역명. operator: 운영기관 코드/명(선택). line: 노선(선택).
    next_station: 열차 진행방면의 '다음 역명'(승강장 방향 특정에 사용). 같은
                  노선의 다음 역명을 넣는다. 미입력 시 방면 구분 없이 조회.
    참고: 역 내 엘리베이터 상세 동선은 get_urban_accessibility(elevator_route_detail)도 있다.
    """
    cands = _resolve(station_name, operator, line)
    if not cands:
        return _err(f"'{station_name}' 역을 찾을 수 없습니다. "
                    f"search_urban_station으로 먼저 확인하세요.")
    if len(cands) > _MAX_STATIONS:
        return _too_many(cands, station_name)

    rows: list = []
    errors: list = []
    for s in cands:
        p = {"railOprIsttCd": s["opr"], "lnCd": s["ln"], "stinCd": s["stin"]}
        nxt = (next_station or "").strip()
        if nxt:
            # 같은 운영기관·노선 안에서 다음 역코드를 찾는다.
            nx = next((c["stin"] for c in STATIONS
                       if c["opr"] == s["opr"] and c["ln"] == s["ln"]
                       and c["stinNm"] == nxt), None)
            if nx:
                p["nextStinCd"] = nx
        data, msg = _kric_get("vulnerableUserInfo", "stationMovement", p)
        if msg:
            errors.append(f'{_label(s)}: {msg}')
            continue
        for d in data:
            d["_역사"] = _label(s)
        rows.extend(data)
    extra = {"조회역수": len(cands), "데이터수정일": _modified("stationMovement")}
    if next_station:
        extra["방면"] = next_station
    if errors:
        extra["비고"] = errors
    return _wrap(rows, "교통약자 출입구→승강장 이동경로", extra)


@mcp.tool()
def get_urban_route(line: str = "", region: str = "") -> str:
    """도시철도 노선 전체 역 구성(상행~하행 순서) 조회. 역 무관, 노선 단위.

    line: 선코드(예 '1','A1','I1') 또는 노선명 일부(예 '1호선','경의중앙').
    region: 권역 — 수도권/부산/대구/광주/대전 (또는 코드 01~05).
            수도권 노선은 region을 함께 주면 정확하다.
    """
    ln = (line or "").strip()
    ln_cd = ln
    if ln and not any(s["ln"] == ln for s in STATIONS):
        # 노선명 부분일치 → 선코드
        m = next((s["ln"] for s in STATIONS if ln in s["lnNm"]), None)
        if m:
            ln_cd = m
    reg = (region or "").strip()
    reg_cd = _REGION_MAP.get(reg, reg)

    params: dict = {}
    if ln_cd:
        params["lnCd"] = ln_cd
    if reg_cd:
        params["mreaWideCd"] = reg_cd
    if not params:
        return _err("line(선코드/노선명) 또는 region(권역) 중 하나는 입력하세요.")

    data, msg = _kric_get("trainUseInfo", "subwayRouteInfo", params)
    if msg:
        return _err(msg)
    # 역구성순서(stinConsOrdr)로 정렬해 상행~하행 순서를 명확히 한다.
    try:
        data = sorted(data, key=lambda r: int(r.get("stinConsOrdr") or 0))
    except Exception:  # noqa: BLE001
        pass
    extra = {
        "선": line or "(전체)", "권역": region or "(전체)", "역수": len(data),
        "데이터수정일": _modified("subwayRouteInfo"),
        "주의": ("이 데이터는 분기·지선이나 종착역 구조를 구분하지 않는 평면 역 목록이다. "
                "반환된 역 목록만 근거로 답하고, 데이터에 없는 지선·종착역·구간별 역수는 "
                "추정하지 말 것(예: 반환되지 않은 역명을 종착역으로 단정 금지)."),
    }
    return _wrap(data, "도시철도 전체노선 역 구성", extra)


@mcp.tool()
def get_urban_train_composition(operator: str) -> str:
    """도시철도 운영기관별 열차 편성종류 조회 (역 무관).

    편성유형코드(cpsTpCd)·편성명·호차별 좌석/출입문수/교통약자석 등을 준다.
    이 도구로 얻은 cpsTpCd와 호차(scarNo)를 get_urban_train_facility의
    composition_type·scar_seq 인자로 넘겨 차량별 시설을 조회한다.
    operator: 운영기관 코드(예 'BS') 또는 명(예 '부산교통공사').
    참고: 서울교통공사(S1)·한국철도공사(KR)·공항철도(AR)는 편성데이터 미제공.
          부산(BS)·대구(DG)·인천(IC)·대전(DJ)·광주(GJ) 등은 제공.
    """
    opr = _resolve_opr(operator)
    data, msg = _kric_get("trainUseInfo", "subwayComposed", {"railOprIsttCd": opr})
    if msg:
        return _err(f"{_opr_name(opr)}({opr}) 편성종류 조회 실패: {msg}")
    # cpsTpCd별 요약(중복 제거)으로 후속 조회 편의 제공
    types: dict[str, dict] = {}
    for r in data:
        c = str(r.get("cpsTpCd", ""))
        t = types.setdefault(c, {"cpsTpCd": c, "cpsTpNm": r.get("cpsTpNm"),
                                 "trnClsfCd": r.get("trnClsfCd"), "호차목록": []})
        sn = r.get("scarNo")
        if sn is not None and sn not in t["호차목록"]:
            t["호차목록"].append(sn)
    extra = {"운영기관": f"{_opr_name(opr)}({opr})",
             "편성유형요약": list(types.values()),
             "데이터수정일": _modified("subwayComposed")}
    return _wrap(data, "도시철도 노선별 열차 편성종류", extra)


@mcp.tool()
def get_urban_train_facility(operator: str, scar_seq: str, composition_type: str,
                             facility_type: str = "all") -> str:
    """도시철도 차량(호차)별 시설 조회 (역 무관).

    facility_type:
      fire_extinguisher(소화기) / emergency_phone(비상콜폰) /
      crush_hammer(비상탈출망치) / door_manual(출입문 수동설정) / defibrillator(제세동기) /
      pregnant_seat(임산부 배려석) / priority_seat(노약자석) /
      wheelchair_board(휠체어 승차가능) / wheelchair_belt(휠체어 안전벨트) / all(전체)
    operator: 운영기관 코드/명. scar_seq: 호차일련번호(scarSqno, 예 '1').
    composition_type: 편성유형코드(cpsTpCd). get_urban_train_composition으로 먼저 확인한다.
    주의: 운영기관마다 보유 항목이 달라 일부 종류는 빈 결과일 수 있다.
    """
    if facility_type != "all" and facility_type not in _TRAIN_FACIL:
        return _err(f"'{facility_type}' 미지원. 사용 가능: {list(_TRAIN_FACIL) + ['all']}")
    opr = _resolve_opr(operator)
    base = {"railOprIsttCd": opr, "scarSqno": str(scar_seq).strip(),
            "cpsTpCd": str(composition_type).strip()}
    types = list(_TRAIN_FACIL) if facility_type == "all" else [facility_type]
    result: dict[str, Any] = {}
    errors: list = []
    for t in types:
        svc, op, label = _TRAIN_FACIL[t]
        data, msg = _kric_get(svc, op, dict(base))
        if msg:
            errors.append(f"{label}: {msg}")
            result[t] = {"종류": label, "건수": 0, "data": []}
            continue
        # subwayFacilitiesInfo 등 일부는 scarSqno를 무시하고 전체를 반환 →
        # 응답행에 scarSqno가 있으면 요청 호차로 한정(필드 없으면 통과).
        sq = base["scarSqno"]
        data = [r for r in data if str(r.get("scarSqno", sq)) == str(sq)]
        result[t] = {"종류": label, "건수": len(data), "data": data}
    meta = {"출처": SOURCE, "운영기관": f"{_opr_name(opr)}({opr})",
            "호차일련번호": base["scarSqno"], "편성유형코드": base["cpsTpCd"],
            "조회종류": types,
            "데이터수정일": {t: _DATASET_DATE.get(_TRAIN_FACIL[t][1], "미상") for t in types}}
    if errors:
        meta["비고"] = errors
    return _json({"data": result, "_meta": meta})


# 모든 도구 설명에 '데이터 시점 고지' 지침을 일괄 부착.
# 사용자가 기준일을 묻지 않아도 모델이 데이터 시점을 안내하되, 수정일 최신도에 따라
# 톤을 달리해 과한 반복·경고를 피하도록 유도한다.
_ANSWER_FOOTER = (
    "\n\n[답변 지침] _meta의 '데이터수정일'(KRIC 데이터 최종수정 시점, 측정성 데이터는 '측정시점')을 "
    "근거로 데이터 시점을 알리되, 수정일에 따라 톤을 달리하라.\n"
    "- 최근(약 2년 이내, 예 2025~2026): 답변 끝에 '데이터는 OOOO년 기준'을 간결히 한 줄만. "
    "경고 문구나 고객센터 전화번호를 따로 나열하지 마라.\n"
    "- 오래됨(2019~2021 등): 한 줄 고지에 더해 '최신 현황과 다를 수 있어 운영기관 확인 권장'을 "
    "딱 한 번만 덧붙여라. 전화번호는 사용자가 묻거나 응급·안전 관련일 때만.\n"
    "여러 데이터셋을 함께 보여줄 땐 가장 오래된 수정일 기준으로 한 번만 고지하면 된다. "
    "시점 고지·주의 문구를 답변 안에서 반복하지 마라. "
    "결과가 비어 있으면 지어내지 말고 '해당 데이터 없음'을 분명히 알려라."
)
try:
    _registered = getattr(mcp._tool_manager, "_tools", {})
    for _t in _registered.values():
        if getattr(_t, "description", None) and "[답변 지침]" not in _t.description:
            _t.description += _ANSWER_FOOTER
except Exception:  # noqa: BLE001
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8013)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = args.port
        mcp.settings.transport_security = None
    mcp.run(transport=args.transport)
