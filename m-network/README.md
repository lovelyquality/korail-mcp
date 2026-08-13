# 🗺️ 선로망·운임·운행거리 조회

KORAIL 노선·역간 거리, 화물 운임, 선로 정보를 조회하는 MCP 서버 (도구 8개)

> 📌 등록명 `korail-network` · 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.** (`data/station_distance.csv.gz` 4.6MB, gzip 압축)

| 도구 | 설명 |
|---|---|
| `search_operation_patterns` | 운행계통(노선) 검색 |
| `get_station_distance` | 역간 거리 조회 |
| `get_freight_minimum_fare` | 화물 최소 운임 조회 |
| `get_freight_rate` | 화물 운임 조회 |
| `get_segment_info` | 구간 정보 조회 |
| `get_operation_distance` | 운행 거리 조회 |
| `get_ktx_stations` | KTX 정차역 목록 |
| `get_station_track_info` | 역 선로 현황 조회 |

