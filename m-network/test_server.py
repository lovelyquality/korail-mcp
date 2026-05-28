"""M6 m-network 서버 스모크 테스트"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from server import (
    search_routes,
    get_station_distance,
    get_freight_minimum_fare,
    get_freight_rate,
    get_segment_info,
    get_operation_distance,
    get_ktx_stations,
)

PASS = "PASS"
FAIL = "FAIL"

def check(name, cond, detail=""):
    status = PASS if cond else FAIL
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    return cond

results = []

# ── 1. search_routes ─────────────────────────────────────────────────────────
print("\n=== search_routes ===")
try:
    all_routes = search_routes()
    results.append(check("전체 노선 수 ≥ 2000", len(all_routes) >= 2000, f"count={len(all_routes)}"))
    hs = search_routes(query="고속")
    results.append(check("고속 노선 검색", len(hs) > 0, f"count={len(hs)}"))
    electric = search_routes(electric_only=True)
    results.append(check("전기 노선 필터", len(electric) > 0 and all(r.get("전기동력차운행여부(ELC_LCM_RUN_FLG)") == "Y" for r in electric[:5]),
                          f"count={len(electric)}"))
except Exception as e:
    results.append(check("search_routes 예외", False, str(e)))

# ── 2. get_station_distance ───────────────────────────────────────────────────
print("\n=== get_station_distance ===")
try:
    rows = get_station_distance("서울", "부산")
    results.append(check("서울→부산 거리 존재", len(rows) > 0, f"count={len(rows)}"))
    if rows:
        dist = rows[0].get("여객최단운행거리") or rows[0].get("구간거리내용")
        results.append(check("여객최단운행거리 필드 존재", dist is not None, f"value={dist}"))
    all_from_seoul = get_station_distance("서울")
    results.append(check("서울 출발 전체 구간 ≥ 10", len(all_from_seoul) >= 10, f"count={len(all_from_seoul)}"))
except Exception as e:
    results.append(check("get_station_distance 예외", False, str(e)))

# ── 3. get_freight_minimum_fare ───────────────────────────────────────────────
print("\n=== get_freight_minimum_fare ===")
try:
    fares = get_freight_minimum_fare()
    results.append(check("화물 최저운임 데이터 존재", len(fares) > 0, f"count={len(fares)}"))
    if fares:
        results.append(check("운임요금유형 필드 존재", "운임요금유형" in fares[0], str(fares[0])))
except Exception as e:
    results.append(check("get_freight_minimum_fare 예외", False, str(e)))

# ── 4. get_freight_rate ───────────────────────────────────────────────────────
print("\n=== get_freight_rate ===")
try:
    rates = get_freight_rate()
    results.append(check("임율 데이터 ≥ 10건", len(rates) >= 10, f"count={len(rates)}"))
    container_rates = get_freight_rate(category="컨테이너")
    results.append(check("컨테이너 임율 필터", len(container_rates) > 0, f"count={len(container_rates)}"))
except Exception as e:
    results.append(check("get_freight_rate 예외", False, str(e)))

# ── 5. get_segment_info ───────────────────────────────────────────────────────
print("\n=== get_segment_info ===")
try:
    segs = get_segment_info()
    results.append(check("세그먼트 데이터 존재", segs["total_segments"] > 0, f"total={segs['total_segments']}"))
    by_code = get_segment_info(segment_code="100")
    results.append(check("코드 100 세그먼트 조회", by_code["total_segments"] >= 1, str(by_code.get("basic", [{}])[0] if by_code.get("basic") else "")))
    by_station = get_segment_info(station="서울")
    results.append(check("서울 경유 세그먼트 존재", by_station["total_segments"] > 0, f"total={by_station['total_segments']}"))
except Exception as e:
    results.append(check("get_segment_info 예외", False, str(e)))

# ── 6. get_operation_distance ─────────────────────────────────────────────────
print("\n=== get_operation_distance ===")
try:
    overview = get_operation_distance()
    results.append(check("노선 목록 ≥ 10개", len(overview.get("available_lines", [])) >= 10,
                          f"count={len(overview.get('available_lines', []))}"))
    gyeongbu = get_operation_distance(line_name="경부")
    results.append(check("경부선 조회", "error" not in gyeongbu, str(list(gyeongbu.keys())[:3])))
    dist = get_operation_distance(line_name="경부", from_station="서울", to_station="부산")
    results.append(check("경부 서울→부산 거리", "distance_result" in dist or "error" not in dist,
                          str(dist)[:120]))
except Exception as e:
    results.append(check("get_operation_distance 예외", False, str(e)))

# ── 7. get_ktx_stations ───────────────────────────────────────────────────────
print("\n=== get_ktx_stations ===")
try:
    all_ktx = get_ktx_stations()
    results.append(check("KTX 역 총 ≥ 50개", len(all_ktx) >= 50, f"count={len(all_ktx)}"))
    gyeongbu_ktx = get_ktx_stations(line_name="경부선")
    results.append(check("경부선 KTX 역 존재", len(gyeongbu_ktx) > 0, f"count={len(gyeongbu_ktx)}"))
    seoul_ktx = get_ktx_stations(station_name="서울")
    results.append(check("서울역 KTX 조회", len(seoul_ktx) > 0, str(seoul_ktx[:1])))
except Exception as e:
    results.append(check("get_ktx_stations 예외", False, str(e)))

# ── 요약 ──────────────────────────────────────────────────────────────────────
print(f"\n{'='*40}")
total = len(results)
passed = sum(results)
print(f"결과: {passed}/{total} 통과")
if passed < total:
    sys.exit(1)
