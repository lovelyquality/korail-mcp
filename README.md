# KORAIL MCP Agent

한국철도공사(KORAIL) 공공데이터를 AI에 연결하는 MCP(Model Context Protocol) 서버 모음입니다.
설치 후 Claude·Cursor·Antigravity 등에서 자연어로 KORAIL 데이터를 조회할 수 있습니다.

> ✅ **API 키 신청 불필요** — 전용 프록시 서버가 공공데이터 API 호출을 대신 처리합니다.
> 직원은 내려받아 `setup.bat`만 실행하면 됩니다.

---

## 📦 제공 서버 (총 11개 · 82개 도구)

| 서버 | 도구 수 | 제공 데이터 |
|---|:-:|---|
| m-convenience | 6 | 역사 편의시설·접근성·엘리베이터·위치 정보 |
| m-stats | 11 | 발권 통계·이용유형·KTX 장기 통계 |
| m-train-ops | 4 | 열차 운행계획·운행이력 |
| m-codebook | 4 | 역코드·노선코드 조회 |
| m-carriage | 4 | 간선·광역·화물 수송실적 |
| m-freight | 11 | 화물·컨테이너·물류시설·품목·위험물 |
| m-network | 8 | 노선·역간거리·운임·역 선로제원 |
| m-rolling-stock | 6 | 차량 보유현황·형별제원·차종별 운행실적 |
| m-voc-cs | 10 | 고객서비스·정보공개 |
| m-internal-svc | 14 | 임대매장·사회공헌·인사 정보 |
| m-procurement | 4 | 자재그룹·G2B 품명·자재속성·대상장비 |

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
<summary><b>m-stats</b> · 11개 도구 — 수송·이용 통계</summary>

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
<summary><b>m-carriage</b> · 4개 도구 — 수송실적</summary>

| 도구 | 설명 |
|---|---|
| get_mainline_carriage | 간선 여객열차 수송실적 조회 |
| get_wide_area_carriage | 광역 여객열차 수송실적 조회 |
| get_freight_carriage | 화물열차 수송실적 조회 |
| get_carriage_codes | 열차수송통계 코드정보 조회 |
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
| search_routes | 전국 철도 노선 정보 검색 |
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
- 클라이언트 연결용 설정 내용 출력

> ⏳ 인터넷 속도에 따라 3~10분 소요됩니다.

---

## 🔌 클라이언트 연결 (사용하는 도구 선택)

아래에서 **본인이 쓰는 도구의 토글만 펼쳐** 따라 하세요.
Claude·Antigravity·Cursor는 설정 형식이 **완전히 동일**하며, 파일 위치만 다릅니다.

<details>
<summary><b>① Claude Desktop</b></summary>

**설정 파일 위치:**
```
C:\Users\[사용자명]\AppData\Roaming\Claude\claude_desktop_config.json
```

기존 `mcpServers` 항목 안에 아래 11개 서버를 붙여넣습니다.
(`setup.bat` 실행 시 실제 경로가 반영된 내용이 자동 출력됩니다.)

```json
"korail-convenience": {
  "command": "C:\\korail-mcp\\m-convenience\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-convenience\\server.py"]
},
"korail-stats": {
  "command": "C:\\korail-mcp\\m-stats\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-stats\\server.py"]
},
"korail-train-ops": {
  "command": "C:\\korail-mcp\\m-train-ops\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-train-ops\\server.py"]
},
"korail-codebook": {
  "command": "C:\\korail-mcp\\m-codebook\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-codebook\\server.py"]
},
"korail-carriage": {
  "command": "C:\\korail-mcp\\m-carriage\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-carriage\\server.py"]
},
"korail-freight": {
  "command": "C:\\korail-mcp\\m-freight\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-freight\\server.py"]
},
"korail-network": {
  "command": "C:\\korail-mcp\\m-network\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-network\\server.py"]
},
"korail-rolling-stock": {
  "command": "C:\\korail-mcp\\m-rolling-stock\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-rolling-stock\\server.py"]
},
"korail-voc-cs": {
  "command": "C:\\korail-mcp\\m-voc-cs\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-voc-cs\\server.py"]
},
"korail-internal-svc": {
  "command": "C:\\korail-mcp\\m-internal-svc\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-internal-svc\\server.py"]
},
"korail-procurement": {
  "command": "C:\\korail-mcp\\m-procurement\\venv\\Scripts\\python.exe",
  "args": ["C:\\korail-mcp\\m-procurement\\server.py"]
}
```

설정 후 Claude Desktop을 **완전 종료 후 재시작**합니다.
채팅창 우측 하단에 🔨(도구) 아이콘이 보이면 성공입니다.
</details>

<details>
<summary><b>② Cursor</b></summary>

Cursor는 Claude Desktop과 **동일한 형식**을 사용합니다.

**설정 파일 위치:**
- 전역: `C:\Users\[사용자명]\.cursor\mcp.json`
- 프로젝트별: `<프로젝트>\.cursor\mcp.json`

파일을 만들고 아래 골격에 **① Claude Desktop의 11개 서버 블록을 그대로** `mcpServers` 안에 넣습니다.

```json
{
  "mcpServers": {
    "korail-convenience": {
      "command": "C:\\korail-mcp\\m-convenience\\venv\\Scripts\\python.exe",
      "args": ["C:\\korail-mcp\\m-convenience\\server.py"]
    }
    // ... 나머지 10개 서버 동일하게 추가
  }
}
```

저장 후 Cursor 설정 → MCP 화면에서 **Refresh** 하면 도구가 로드됩니다.
</details>

<details>
<summary><b>③ Antigravity CLI</b></summary>

> 💡 Antigravity CLI는 무료로 설치 가능하며, KORAIL MCP 서버 연결에 별도 구독이 필요 없습니다.

Antigravity도 Claude Desktop과 **동일한 `mcpServers` 형식**을 사용합니다.

**설정 파일 위치:**
```
C:\Users\[사용자명]\.gemini\antigravity\mcp_config.json
```
(또는 IDE에서 `…` 메뉴 → **Manage MCP Servers** → **View raw config**)

```json
{
  "mcpServers": {
    "korail-convenience": {
      "command": "C:\\korail-mcp\\m-convenience\\venv\\Scripts\\python.exe",
      "args": ["C:\\korail-mcp\\m-convenience\\server.py"]
    }
    // ... 나머지 10개 서버 동일하게 추가
  }
}
```

저장 후 MCP Servers 패널에서 **Reload/Refresh** 합니다.
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
2024년 간선철도 수송실적을 알려주세요.            (carriage)
컨테이너 화물 운송 이력을 조회해주세요.           (freight)
경부선 KTX 정차역과 역간 거리를 알려주세요.       (network)
KTX 차량 형별 제원을 보여주세요.                  (rolling-stock)
철도 고객센터 상담유형 코드를 알려주세요.         (voc-cs)
역사 임대매장 현황을 알려주세요.                  (internal-svc)
'EMU용품' 자재그룹코드를 검색해주세요.            (procurement)
```

---

## 📚 데이터 출처

- 한국철도공사 공공데이터포털 ([data.go.kr](https://www.data.go.kr))
- REST API(B551457) · odcloud 파일변환 API · 로컬 CSV

## ⚠️ 주의사항

- 데이터 호출은 전용 **Cloudflare Workers 프록시**를 경유하므로 직원 개인 API 키가 필요 없습니다.
- `m-network/data/station_distance.csv`(44MB)는 **Git LFS**로 관리됩니다. `git clone` 전 `git lfs install`을 실행하세요.
- 각 데이터셋의 기준일·갱신주기는 도구 응답의 `_meta` 항목에 표시됩니다.

---

각 서버의 상세 동작은 해당 폴더의 `server.py` docstring을 참조하세요.
