# KORAIL 공공데이터 MCP

한국철도공사(KORAIL) 공공데이터를 AI에 연결하는 MCP(Model Context Protocol) 서버 모음입니다.
설치 후 Claude·Cursor·Antigravity 등에서 자연어로 KORAIL 데이터를 조회할 수 있습니다.

> ✅ **API 키 신청 불필요** — 전용 프록시 서버가 공공데이터 API 호출을 대신 처리합니다.
> 직원은 내려받아 `setup.bat`만 실행하면 됩니다.

---

## 📦 제공 서버 (총 11개 · 98개 도구)

| 서버 | 도구 수 | 제공 데이터 |
|---|:-:|---|
| m-convenience | 6 | 역사 편의시설·접근성·엘리베이터·위치 정보 |
| m-stats | 15 | 수송실적·발권 통계·이용유형·KTX 장기 통계 |
| m-train-ops | 4 | 열차 운행계획·운행이력 |
| m-codebook | 4 | 역코드·노선코드 조회 |
| m-freight | 11 | 화물·컨테이너·물류시설·품목·위험물 |
| m-network | 8 | 노선·역간거리·운임·역 선로제원 |
| m-rolling-stock | 6 | 차량 보유현황·형별제원·차종별 운행실적 |
| m-voc-cs | 10 | 고객서비스·정보공개 |
| m-internal-svc | 14 | 임대매장·사회공헌·인사 정보 |
| m-procurement | 4 | 자재그룹·G2B 품명·자재속성·대상장비 |
| m-urban-rail | 16 | 전국 도시철도 역사·노선·차량 시설·접근성·안전·환경·시각표 |

### 서버별 도구 상세 (클릭하여 펼치기)

<details>
<summary><b>m-convenience</b> · 6개 도구 — 역사 편의시설</summary>

| 도구 | 설명 |
|---|---|
| get_station_facilities | 역 이름으로 편의시설 정보 조회 |
| get_accessible_facilities | 역 이름으로 교통약자 편의시설 조회 |
| list_stations_with_elevator | 엘리베이터가 설치된 역 목록 조회 |
| get_station_facilities_detail | 역사 내외부 시설현황 조회 |
| get_station_transfer_info | 역별 타 교통수단 환승현황 조회 |
| get_station_location | 역 위치(좌표) 정보 조회 |
</details>

<details>
<summary><b>m-stats</b> · 15개 도구 — 여객·화물 수송통계</summary>

| 도구 | 설명 |
|---|---|
| get_mainline_station_per | 간선열차 역별 승하차 통계 |
| get_mainline_route_per | 간선열차 노선별 이용인원 통계 |
| get_wide_rail_station_per | 광역철도 역별 승하차 통계 |
| get_wide_rail_route_per | 광역철도 노선별 이용인원 통계 |
| get_mainline_distance_per | 간선열차 거리별 이용인원 통계 |
| get_mainline_model_per | 간선열차 차량별 이용인원 통계 |
| get_mainline_day_of_week_per | 간선열차 요일별 이용인원 통계 |
| get_mainline_grade_per | 간선열차 객실별 이용인원 통계 |
| get_mainline_ticketing_stat | 간선열차 발권유형 통계 |
| get_mainline_person_distance | 간선열차 노선별 인거리 통계 |
| get_ktx_long_term_stats | KTX 장기 통계 |
| get_mainline_carriage | 간선 여객열차 수송실적 조회 |
| get_wide_area_carriage | 광역 여객열차 수송실적 조회 |
| get_freight_carriage | 화물열차 수송실적 조회 |
| get_transport_stat_codes | 수송실적 통계 코드정보 조회 |
</details>

<details>
<summary><b>m-train-ops</b> · 4개 도구 — 열차 운행</summary>

| 도구 | 설명 |
|---|---|
| get_train_codes | 열차운행 코드정보 조회 |
| get_train_run_plan | 여객열차 운행계획 조회 |
| get_train_run_info | 여객열차 실제 운행정보 조회 |
| get_train_run_history | 차세대예약발매 열차 운행내역 조회 |
</details>

<details>
<summary><b>m-codebook</b> · 4개 도구 — 역·노선 코드</summary>

| 도구 | 설명 |
|---|---|
| search_station | 역명으로 역코드·영문명·지역본부 통합 조회 |
| decode_station_code | 역코드로 역명 조회 |
| search_route | 노선명으로 노선코드 조회 |
| list_stations_by_region | 지역본부명으로 관할 역 목록 조회 |
</details>

<details>
<summary><b>m-freight</b> · 11개 도구 — 화물·물류</summary>

| 도구 | 설명 |
|---|---|
| search_freight_code | 내적화물코드 검색 |
| decode_freight_code | 내적화물분류코드 단건 디코딩 |
| search_container_record | 컨테이너 적재 이력 조회 |
| list_freight_work_lines | 화물적하작업 전용 작업선 정보 |
| list_standard_loading_time | 표준 적하시간 마스터 조회 |
| search_loading_time_adjustment | 적하시간 조정 이력 조회 |
| search_consignment_change | 수탁변경요금 검색 |
| search_consignment_change_per_wagon | 수탁변경요금 화차별 조회 |
| get_logistics_facility | 물류시설 정보 통합 조회 |
| get_freight_items | 화물 품목정보 조회 |
| get_hazardous_cargo | 위험물 정보 조회 |
</details>

<details>
<summary><b>m-network</b> · 8개 도구 — 노선·거리·운임</summary>

| 도구 | 설명 |
|---|---|
| search_operation_patterns | 전국 철도 운행계통 검색 |
| get_station_distance | 두 역 간 최단 운행거리 조회 |
| get_freight_minimum_fare | 화물 운송 최저운임 기준 조회 |
| get_freight_rate | 철도 화물 임율 정보 조회 |
| get_segment_info | 철도 전동차 세그먼트 정보 조회 |
| get_operation_distance | 노선별 역간 운행거리 조회 |
| get_ktx_stations | KTX 노선별 역 정보 조회 |
| get_station_track_info | 역별 선로·시설 상세 정보 조회 |
</details>

<details>
<summary><b>m-rolling-stock</b> · 6개 도구 — 철도차량</summary>

| 도구 | 설명 |
|---|---|
| get_train_type_specs | 동력차 형별제원 조회 |
| get_rolling_stock_by_year | 연도별 차량보유현황 조회 |
| get_wagon_by_weight_class | 화차 자중별 보유현황 조회 |
| get_wagon_by_load_capacity | 화차 적재하중별 보유현황 조회 |
| get_maintenance_equipment | 철도차량 검수용 기계 보유현황 조회 |
| get_train_operation_by_type | 차종별 연간 운행실적 조회 |
</details>

<details>
<summary><b>m-voc-cs</b> · 10개 도구 — 고객서비스·정보공개</summary>

| 도구 | 설명 |
|---|---|
| get_customer_satisfaction_stats | 고객의소리 만족도 일별 통계 |
| get_consultation_types | 철도 고객센터 상담유형 코드 조회 |
| get_consultation_departments | 철도 고객센터 담당 부서 목록 조회 |
| get_advance_disclosure | 홈페이지 사전정보공표 목록 조회 |
| get_advance_disclosure_detail | 사전정보공표 세부 내역 조회 |
| get_advance_disclosure_files | 사전정보공표 첨부파일 목록 조회 |
| get_info_disclosure_dept | 정보공개 담당 부서 목록 조회 |
| get_info_disclosure_codes | 정보공개 시스템 공통코드 조회 |
| get_homepage_dept | KORAIL 홈페이지 부서 정보 조회 |
| get_homepage_position | KORAIL 홈페이지 직책 코드 조회 |
</details>

<details>
<summary><b>m-internal-svc</b> · 14개 도구 — 임대·사회공헌·인사</summary>

| 도구 | 설명 |
|---|---|
| get_lease_stores | 역사 내 임대매장 운영정보 조회 |
| get_lease_codes | 임대 시스템 코드 조회 |
| get_leased_assets | 임대자산 현황 조회 |
| get_dormitory_longterm_codes | 직원숙사 장기예약 사유 코드 조회 |
| get_social_funds | 사회공헌 펀드 종류 조회 |
| get_social_volunteer_fields | 사회공헌 봉사 분야 코드 조회 |
| get_social_donations | 사랑의 성금 사용 내역 조회 |
| get_social_volunteer_matching | 봉사활동 매칭 지출 내역 조회 |
| get_social_org | 사회공헌 포털 조직정보 조회 |
| get_support_facilities | 사옥 내 부대시설 목록 조회 |
| get_support_departments | 업무지원 부서별 인원 현황 조회 |
| get_office_meeting_rooms | 본사 사옥 회의실 목록 조회 |
| get_job_grades | 직급 코드 정보 조회 |
| get_cafeteria_menu_stats | 구내식당 메뉴 건수 현황 조회 |
</details>

<details>
<summary><b>m-procurement</b> · 4개 도구 — 조달·자재</summary>

| 도구 | 설명 |
|---|---|
| search_material_group | 자재그룹코드 검색 |
| search_g2b_item | G2B 분류번호·품명 검색 |
| search_material_attr | 자재속성정보 조회 |
| search_material_equipment | 자재대상장비 조회 |
</details>

<details>
<summary><b>m-urban-rail</b> · 16개 도구 — 전국 도시철도 역사·노선·차량 정보 (국가철도공단)</summary>

> 수도권 1~9호선·신분당·공항철도, 부산·대구·대전·광주·인천, 경전철·GTX 등 전국 22개 운영기관 1,108개 역.
> 운영기관·선·역코드가 필요하므로 먼저 `search_urban_station`으로 역을 특정하세요. 환승역 등 동일 역명은 `operator`(운영기관)로 구분합니다.

| 도구 | 설명 |
|---|---|
| search_urban_station | 역명으로 운영기관·선·역코드 검색 (다른 조회의 선행 단계) |
| get_urban_station_info | 역사 기본정보 조회 (주소·좌표·다국어 역명) |
| get_urban_accessibility | 역사 접근성 시설 조회 (엘리베이터·에스컬레이터·휠체어리프트 현황/위치·이동동선·안전발판·이격거리·점자·장애인화장실·인접계단 차량번호 등) |
| get_urban_amenity | 역사 편의시설 조회 (화장실·수유실·물품보관함·ATM·유실물센터·무선인터넷) |
| get_urban_safety | 역사 안전시설 조회 (제세동기·소화설비·비상콜폰·공기호흡기·스크린도어·승강장 안전펜스) |
| get_urban_surroundings | 역 주변 시설 조회 (대중교통·주차장·자전거 주차/대여) |
| get_urban_exit_info | 역사 출구정보 조회 (출구번호·주변시설·거리) |
| get_urban_transfer_info | 역사 환승정보 조회 (환승노선·환승거리·동선) |
| get_urban_movement | 교통약자 출입구→승강장 이동경로(무장애 동선) 조회 |
| get_urban_platform | 역사 승강장 정보 조회 (승강장 유형·복합여부 등) |
| get_urban_environment | 역사 환경측정 조회 (공기질·온도·습도·소음) |
| get_urban_timetable | 역사별 운행시각표 조회 (평일/휴일·급행 선택) |
| get_urban_route | 노선 전체 역 구성(상행~하행 순서) 조회 — 역 무관 |
| get_urban_train_composition | 운영기관별 열차 편성종류(편성코드·호차) 조회 — 차량별 조회 선행 |
| get_urban_train_facility | 차량(호차)별 시설 조회 (소화기·비상콜폰·제세동기·임산부석·노약자석·휠체어 등) |
| get_urban_train_environment | 열차별 차내 환경정보 조회 (온도·습도·미세먼지 등) |
</details>

---

## ⚙️ 설치 (Windows · 공통 3단계)

### 1단계 — Python 설치

1. [python.org/downloads](https://www.python.org/downloads/) → **Python 3.12.x** 다운로드
2. 설치 시 **"Add Python to PATH"** 반드시 체크 ✅
3. 명령 프롬프트에서 `python --version` → `Python 3.12.x` 출력되면 성공

### 2단계 — 저장소 다운로드

**Git 사용 (권장):**
```bash
git lfs install   # 최초 1회 (44MB 대용량 파일용)
git clone https://github.com/lovelyquality/korail-mcp.git C:\korail-mcp
```

**Git 미사용:**
1. [github.com/lovelyquality/korail-mcp](https://github.com/lovelyquality/korail-mcp) → **Code** → **Download ZIP**
2. 압축 해제 후 폴더명을 `korail-mcp`로, `C:\korail-mcp` 위치로 이동

### 3단계 — 자동 설치 스크립트 실행

`C:\korail-mcp\setup.bat` 를 **더블클릭**합니다. 다음이 자동 처리됩니다:

- 11개 서버의 Python 가상환경(venv) 생성
- 필요한 패키지 설치
- `.env` 파일 생성 (프록시 URL 자동 기입 — **API 키 입력 불필요**)
- **`mcp-config.json` 자동 생성** (실제 설치 경로가 반영된 클라이언트 연결 설정)

> ⏳ 인터넷 속도에 따라 3~10분 소요됩니다.

---

## 🔌 4단계 — 클라이언트 연결

본인이 쓰는 도구의 항목을 펼쳐, **그 안에 적힌 대로만** 따라 하면 됩니다.

> 💾 [mcp-config.json 다운로드](https://github.com/lovelyquality/korail-mcp/blob/main/mcp-config.json) — `setup.bat` 실행 시 `C:\korail-mcp` 폴더에도 자동 생성됩니다.

<details>
<summary><b>① Claude Desktop</b></summary>

`C:\korail-mcp\mcp-config.json` 을 **`%APPDATA%\Claude\`** 폴더에 복사
→ 이름을 **`claude_desktop_config.json`** 으로 변경

> 🔁 **반드시 완전히 껐다 켜세요.** 창의 X를 눌러 닫아도 **시스템 트레이(작업표시줄 오른쪽 `^` 안)에 계속 실행 중**이라 적용되지 않습니다.
> → 트레이의 Claude 아이콘 **우클릭 → Quit / 종료** 후 다시 실행하세요. (작업표시줄에서 사라졌는지 확인)

> 채팅창 우측 하단에 🔨 아이콘이 보이면 성공. *(이미 다른 MCP 서버가 있으면 `korail-` 항목만 기존 `mcpServers`에 추가)*
</details>

<details>
<summary><b>② Cursor</b></summary>

`C:\korail-mcp\mcp-config.json` 을 **`C:\Users\[사용자명]\.cursor\`** 폴더에 복사
→ 이름을 **`mcp.json`** 으로 변경 → Cursor에서 **Refresh**.

> *(이미 `mcp.json`이 있으면 `korail-` 항목만 기존 `mcpServers`에 추가)*
</details>

<details>
<summary><b>③ Antigravity</b></summary>

> 💡 Antigravity는 무료로 설치 가능하며, KORAIL MCP 서버 연결에 별도 구독이 필요 없습니다.

Antigravity는 **에이전트에게 자연어로 시키는 방법**이 가장 쉽습니다. (직접 설정 파일을 만질 필요 없음)

1. Antigravity 실행
2. 채팅(에이전트)에 아래 문장을 그대로 입력:
   ```
   C:\korail-mcp\mcp-config.json 을 참고해서 MCP 서버들을 설치해줘
   ```
   → 에이전트가 알아서 `mcp_config.json` 에 등록해 줍니다.
3. **반드시 완전히 껐다 켜세요** — 작업표시줄/트레이에서 Antigravity가 **완전히 종료됐는지 확인**한 뒤 다시 실행하세요. (창만 닫으면 적용되지 않을 수 있습니다.)
</details>

<details>
<summary><b>④ ChatGPT (고급 — 원격 연결 필요)</b></summary>

⚠️ ChatGPT는 **로컬 stdio MCP 서버를 지원하지 않습니다.** 원격(HTTPS) 엔드포인트만 커넥터로 추가할 수 있어, 위 3개 도구처럼 파일 붙여넣기만으로는 연결되지 않습니다.

본 서버들은 SSE 전송 모드를 내장하고 있어 **원격 노출 시** 연결이 가능합니다. (네트워크 구성이 필요한 고급 방법)

1. 서버를 SSE 모드로 실행:
   ```bash
   C:\korail-mcp\m-codebook\venv\Scripts\python.exe C:\korail-mcp\m-codebook\server.py --transport sse --port 8008
   ```
2. 해당 포트를 **공개 HTTPS 주소로 노출** (예: Cloudflare Tunnel, ngrok 등)
3. ChatGPT → **Settings → Connectors → Advanced → Developer Mode** 활성화
4. **Add connector** 에서 `https://<공개주소>/sse` 입력

> 개인 PC에서 간편하게 쓰려면 **Claude Desktop·Cursor·Antigravity** 사용을 권장합니다.
</details>

---

## 💬 사용 예시

```
서울역에 엘리베이터가 있나요?                     (convenience)
2026년 4월 KTX 발권유형 비율을 알려주세요.        (stats)
KTX 101 열차의 운행 계획을 알려주세요.            (train-ops)
서울역 코드가 뭔가요?                             (codebook)
2024년 간선철도 수송실적을 알려주세요.            (stats)
컨테이너 화물 운송 이력을 조회해주세요.           (freight)
경부선 KTX 정차역과 역간 거리를 알려주세요.       (network)
KTX 차량 형별 제원을 보여주세요.                  (rolling-stock)
철도 고객센터 상담유형 코드를 알려주세요.         (voc-cs)
역사 임대매장 현황을 알려주세요.                  (internal-svc)
'EMU용품' 자재그룹코드를 검색해주세요.            (procurement)
강남역(서울교통공사) 엘리베이터 위치를 알려주세요.  (urban-rail)
서울역 도시철도 역사들의 운영기관을 찾아주세요.    (urban-rail)
```

---

## 📚 데이터 출처

- 한국철도공사 공공데이터포털 ([data.go.kr](https://www.data.go.kr))
- 국가철도공단(KRIC) 철도산업정보센터 오픈API ([openapi.kric.go.kr](https://openapi.kric.go.kr)) — 도시철도 역사정보
- REST API(B551457) · odcloud 파일변환 API · 로컬 CSV

## ⚠️ 주의사항

- 데이터 호출은 전용 **Cloudflare Workers 프록시**를 경유하므로 직원 개인 API 키가 필요 없습니다.
- `m-network/data/station_distance.csv`(44MB)는 **Git LFS**로 관리됩니다. `git clone` 전 `git lfs install`을 실행하세요.
- 각 데이터셋의 기준일·갱신주기는 도구 응답의 `_meta` 항목에 표시됩니다.

---

각 서버의 상세 동작은 해당 폴더의 `server.py` docstring을 참조하세요.
