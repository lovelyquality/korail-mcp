"""Smoke test for korail-freight server tools."""
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

import server


def show(title, result):
    print(f"\n=== {title} ===")
    if isinstance(result, dict):
        if "total" in result:
            print(f"total={result.get('total')}")
        if "totalCount" in result:
            print(f"totalCount={result.get('totalCount')}, matched_in_page={result.get('matched_in_page')}")
        data = result.get("data") or result.get("basic") or []
        if isinstance(data, list) and data:
            print(f"sample[0]: {json.dumps(data[0], ensure_ascii=False)[:300]}")
        elif "error" in result:
            print(result["error"])
        else:
            print(f"keys={list(result.keys())}")


# 1. local XLSX
show("search_freight_code('구리')", server.search_freight_code(query="구리", limit=2))
show("decode_freight_code('7404')", server.decode_freight_code(code="7404"))

# 2. odcloud large (page fetch)
show("search_container_record(page=1, per_page=3)",
     server.search_container_record(page=1, per_page=3))

# 3. odcloud small (full cache)
show("list_freight_work_lines('서울')",
     server.list_freight_work_lines(station_name="서울", limit=3))

# 4. odcloud master
show("list_standard_loading_time()", server.list_standard_loading_time())

# 5. odcloud adjustment
show("search_loading_time_adjustment(page=1, per_page=3)",
     server.search_loading_time_adjustment(page=1, per_page=3))

# 6. local CSV
show("search_consignment_change(station='적량')",
     server.search_consignment_change(station="적량", limit=2))
show("search_consignment_change_per_wagon(wagon_number='975234')",
     server.search_consignment_change_per_wagon(wagon_number="975234", limit=2))

# 7. facility
show("get_logistics_facility('의왕')",
     server.get_logistics_facility(station_name="의왕", limit=3))

print("\n=== OK ===")
