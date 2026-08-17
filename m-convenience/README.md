# 🏢 역 편의시설·접근성 조회

KORAIL 역사 편의시설, 접근성 설비, 환승·위치 정보를 조회하는 MCP 서버 (도구 6개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.**

| 도구 | 설명 |
|---|---|
| `get_station_facilities` | 역 시설 목록 조회 |
| `get_accessible_facilities` | 접근성 편의시설 조회 |
| `list_stations_with_elevator` | 엘리베이터 설치 역 목록 |
| `get_station_facilities_detail` | 시설 상세 정보 |
| `get_station_transfer_info` | 환승 정보 |
| `get_station_location` | 역 위치·주소 정보 |

