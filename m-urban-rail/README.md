# 🚇 도시철도 역사 시설 조회

전국 도시철도 역사·노선·차량의 시설·접근성·안전·환경·시각표를 통합 조회하는 MCP 서버 (도구 16개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터는 **국가철도공단(KRIC) 오픈API**를 전용 프록시가 대신 호출하므로 직원 개인 API 키가 필요 없습니다.

> 💡 수도권 1~9호선·신분당·공항철도, 부산·대구·대전·광주·인천, 경전철·GTX 등 **전국 22개 운영기관 1,108개 역**.
> KRIC API는 운영기관·선·역코드가 필요해, 먼저 `search_urban_station`으로 역을 특정합니다. 환승역 등 동일 역명은 `operator`(운영기관)로 구분합니다.

| 도구 | 설명 |
|---|---|
| `search_urban_station` | 역명으로 운영기관·선·역코드 검색 (선행 단계) |
| `get_urban_station_info` | 역사 기본정보 (주소·좌표·다국어 역명) |
| `get_urban_accessibility` | 접근성 시설 (엘리베이터·에스컬레이터·휠체어리프트 현황/위치·이동동선·안전발판·이격거리·점자·장애인화장실·인접계단 차량번호 등) |
| `get_urban_amenity` | 편의시설 (화장실·수유실·물품보관함·ATM·유실물센터·무선인터넷) |
| `get_urban_safety` | 안전시설 (제세동기·소화설비·비상콜폰·공기호흡기·스크린도어·승강장 안전펜스) |
| `get_urban_surroundings` | 역 주변 시설 (대중교통·주차장·자전거 주차/대여) |
| `get_urban_exit_info` | 출구정보 (출구번호·주변시설·거리) |
| `get_urban_transfer_info` | 환승정보 (환승노선·거리·동선) |
| `get_urban_movement` | 교통약자 출입구→승강장 이동경로(무장애 동선) |
| `get_urban_platform` | 승강장 정보 (유형·복합여부 등) |
| `get_urban_environment` | 역사 환경측정 (공기질·온도·습도·소음) |
| `get_urban_timetable` | 역사별 운행시각표 (평일/휴일·급행) |
| `get_urban_route` | 노선 전체 역 구성(상행~하행 순서) — 역 무관 |
| `get_urban_train_composition` | 운영기관별 열차 편성종류(편성코드·호차) — 차량별 조회 선행 |
| `get_urban_train_facility` | 차량(호차)별 시설 (소화기·비상콜폰·제세동기·임산부석·노약자석·휠체어 등) |
| `get_urban_train_environment` | 열차별 차내 환경정보 (온도·습도·미세먼지 등) |

> 데이터 출처: 국가철도공단 철도산업정보센터 오픈API ([openapi.kric.go.kr](https://openapi.kric.go.kr))
