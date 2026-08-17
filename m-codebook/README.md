# 📖 역코드·노선 코드북

KORAIL 역 코드 및 노선 정보를 조회하는 MCP 서버 (도구 4개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.**

| 도구 | 설명 |
|---|---|
| `search_station` | 역명으로 역 검색 |
| `decode_station_code` | 역코드 → 역명·지역 해석 |
| `search_route` | 노선 검색 |
| `list_stations_by_region` | 지역별 역 목록 |

