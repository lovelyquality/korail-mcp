# 📊 여객·화물 수송 통계

KORAIL 간선·광역 여객 수송 통계, 화물 수송실적, KTX 장기 통계를 조회하는 MCP 서버 (도구 15개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.**

| 도구 | 설명 |
|---|---|
| `get_mainline_station_per` | 간선 역별 수송 통계 |
| `get_mainline_route_per` | 간선 노선별 통계 |
| `get_wide_rail_station_per` | 광역 역별 통계 |
| `get_wide_rail_route_per` | 광역 노선별 통계 |
| `get_mainline_distance_per` | 거리별 수송 통계 |
| `get_mainline_model_per` | 차종별 수송 통계 |
| `get_mainline_day_of_week_per` | 요일별 수송 통계 |
| `get_mainline_grade_per` | 등급별 수송 통계 |
| `get_mainline_ticketing_stat` | 발권 통계 |
| `get_mainline_person_distance` | 인킬로(여객 수송량) 통계 |
| `get_ktx_long_term_stats` | KTX 장기 통계 |
| `get_mainline_carriage` | 간선 여객열차 수송실적(역별 승하차 인원) |
| `get_wide_area_carriage` | 광역 여객열차 수송실적(시간대별 승하차) |
| `get_freight_carriage` | 화물열차 수송실적(발송톤·연톤키로) |
| `get_transport_stat_codes` | 수송실적 통계 코드정보 (구 get_carriage_codes) |

