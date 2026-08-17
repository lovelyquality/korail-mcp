# 🚅 철도차량 현황·제원 조회

KORAIL 철도차량 제원, 연도별 현황, 화차 적재 정보, 정비 장비를 조회하는 MCP 서버 (도구 6개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.**

| 도구 | 설명 |
|---|---|
| `get_train_type_specs` | 차종별 제원 조회 |
| `get_rolling_stock_by_year` | 연도별 차량 현황 |
| `get_wagon_by_weight_class` | 화차 중량 등급별 조회 |
| `get_wagon_by_load_capacity` | 화차 적재량별 조회 |
| `get_maintenance_equipment` | 정비 장비 조회 |
| `get_train_operation_by_type` | 차종별 운행 현황 |

