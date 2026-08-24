🇰🇷 **한국어** · 🇬🇧 [English](README.en.md)

# KORAIL 공공데이터 MCP

한국철도공사(KORAIL) 공공데이터를 AI에 연결하는 MCP(Model Context Protocol) 서버 모음입니다.
설치 후 Claude Desktop·Claude Code·Cursor·Antigravity·GitHub Copilot(CLI/VS Code) 등에서 자연어로 KORAIL 데이터를 조회할 수 있습니다.

> ✅ **API 키 신청 불필요** — 전용 프록시 서버가 공공데이터 API 호출을 대신 처리합니다.
>
> 💻 **로컬 설치형 (stdio)** — 별도 서버 없이 개인 PC에서 직접 실행됩니다. Claude Desktop·Claude Code·Cursor·Antigravity·GitHub Copilot(CLI/VS Code) 등 로컬 MCP 클라이언트에 연결합니다. ChatGPT·Grok 같은 웹 서비스는 원격 연결이 필요합니다(하단 "그 밖의 방식" 참고).
>
> 📦 **필요 디스크 공간** — 약 **100MB** (`uv`가 관리하는 Python과 패키지 포함)

> 👉 **처음이신가요?** 바로 아래 "제일 쉬운 방법"부터 시도해보세요. 98개 도구 전체 목록은 설치를 마친 뒤 필요할 때 참고하세요.

---

## 🤖 제일 쉬운 방법 — AI에게 그대로 시키기

**Claude Code·Cursor·GitHub Copilot(CLI/VS Code)·Antigravity처럼 터미널 명령을 직접 실행할 수 있는 AI**를 쓰고 있다면, 그 채팅창에 아래 문장을 그대로 붙여넣으세요.

```
https://github.com/lovelyquality/korail-mcp 의 README를 참고해서 이 MCP 서버를 설치하고 내 클라이언트에 연결해줘.
```

AI가 README를 직접 읽고 `uv` 설치 → `korail-mcp` 설치 → 클라이언트 설정 파일 등록까지 알아서 처리합니다. 완료되면 "서울역에 엘리베이터가 있나요?" 같은 질문으로 확인해보세요.

> ⚠️ **ChatGPT·Grok처럼 로컬 명령을 실행하지 못하는 AI**에서는 이 방법이 통하지 않습니다(왜인지는 하단 "그 밖의 방식" 참고). 그리고 AI가 중간에 막히거나, 애초에 이런 방식의 AI 도구가 없다면 → **바로 아래 "수동 설치"를 그대로 따라 하시면 됩니다.**

---

## ⚙️ 수동 설치 (Windows · 2단계)

Python을 따로 설치하거나 저장소를 다운로드할 필요가 없습니다. **`uv`가 필요한 것을 알아서 준비합니다.**

### 1단계 — uv 설치 (최초 1회)

PowerShell을 열고 아래를 붙여넣습니다. **관리자 권한이 필요 없습니다.**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 PowerShell을 **새로 열고** `uv --version`이 출력되면 성공입니다.

### 2단계 — KORAIL MCP 설치 (최초 1회)

```powershell
uv tool install --from git+https://github.com/lovelyquality/korail-mcp.git korail-mcp
```

마지막에 `Installed 1 executable: korail-mcp` 가 나오면 성공입니다.

> ⏳ 첫 설치는 1~3분 걸립니다(Python과 패키지를 받는 시간). 설치 후 실행은 **약 5초**입니다.
>
> 🔄 **최신 버전으로 갱신** — `uv tool upgrade korail-mcp` 실행 후 클라이언트를 재시작하세요.
>
> ⚠️ **갱신 전에는 korail-mcp를 쓰는 클라이언트(Claude Desktop·Cursor·Antigravity·VS Code 등)를 먼저 완전히 종료하세요.** 실행 중인 상태로 갱신하면 실행파일이 잠겨 있어 내부 패키지만 새 버전으로 바뀌고 실행파일은 그대로 남아 **`ModuleNotFoundError: No module named 'gateway'`로 깨질 수 있습니다** (2026-08-24 실측으로 재현·확인). 이미 이 에러가 나면 `korail-mcp.exe`를 쓰는 모든 프로세스를 작업 관리자에서 종료한 뒤 `uv tool install --from git+https://github.com/lovelyquality/korail-mcp.git korail-mcp --force`로 재설치하세요. **여러 클라이언트가 같은 설치를 동시에 쓰는 것 자체는 문제 없습니다** — 충돌은 갱신하는 그 순간에만 일어납니다.

---

## 🔌 3단계 — 클라이언트 연결

아래 JSON을 클라이언트 설정 파일의 `mcpServers` 안에 넣고, **`<사용자명>` 부분만 본인 윈도우 계정명으로 바꿉니다.**

```json
{
  "mcpServers": {
    "korail-mcp": {
      "command": "C:\\Users\\<사용자명>\\.local\\bin\\korail-mcp.exe"
    }
  }
}
```

> 💡 계정명을 모르면 PowerShell에 `echo $env:USERNAME` 을 입력하세요. 경로의 역슬래시는 JSON 규칙상 **두 개(`\\`)** 로 씁니다.
>
> ⚠️ 이미 다른 MCP 서버를 쓰고 있다면 **`korail-mcp` 항목만** 기존 `mcpServers` 안에 추가하세요(전체를 덮어쓰면 기존 서버가 사라집니다).

### 설정 파일 위치

| 클라이언트 | 설정 파일 |
|---|---|
| **Claude Desktop** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Claude Code** | `claude mcp add` 명령으로 등록 (아래 별도 안내) |
| **Cursor** | `C:\Users\<사용자명>\.cursor\mcp.json` |
| **Antigravity** | `C:\Users\<사용자명>\.gemini\antigravity\mcp_config.json` |
| **GitHub Copilot CLI** | `copilot mcp add` 명령으로 등록 (아래 별도 안내) |
| **VS Code (GitHub Copilot Chat)** | 아래 별도 안내 참고 (JSON 형식이 다름) |

<details>
<summary>Claude Desktop — 폴더가 없을 때</summary>

1. 탐색기 주소창에 `%APPDATA%` 입력 → Enter
2. `Claude` 폴더가 없으면 직접 만드세요
3. 그 안에 `claude_desktop_config.json` 파일을 만들고 위 JSON을 넣으세요

`AppData`가 안 보이면 탐색기 → 보기 → **숨긴 항목**을 체크하세요.
</details>

<details>
<summary>Claude Code — 실제 계정으로 도구 호출까지 실측 완료</summary>

터미널에서 쓰는 **Claude Code CLI**(`claude`, VS Code나 Claude Desktop 없이도 동작)로 실제 계정 붙여서 검증했습니다.

```powershell
# 1) korail-mcp를 MCP 서버로 등록 (최초 1회)
claude mcp add korail-mcp -s user -- "C:\Users\<사용자명>\.local\bin\korail-mcp.exe"

# 2) 실제 질문 (해당 도구만 허용)
claude -p "korail-mcp 도구를 사용해서 서울역에 엘리베이터가 있는지 알려줘" --allowedTools "mcp__korail-mcp__*"
```

> ✅ **2026-08-24 실측 결과** — 위 명령을 실제로 실행해서 실데이터 답변까지 확인했습니다:
>
> ```
> 서울역 — 엘리베이터 있음 (18개)
> 에스컬레이터: 23개 · 일반화장실: 있음 · 수유실: 있음 · 종합안내센터: 있음
> (출처: 한국철도공사 공공데이터포털 편의시설정보, 실시간 API 기준)
> ```
>
> `claude mcp list`로 등록 확인, `claude mcp remove korail-mcp`로 제거할 수 있습니다. 대화형으로 쓸 때는 `--allowedTools` 없이 실행하면 첫 도구 호출 시 승인 여부를 물어봅니다.
</details>

<details>
<summary>Cursor / Antigravity — 파일이나 폴더가 없을 때</summary>

`.cursor` 또는 `.gemini\antigravity` 폴더나 그 안의 설정 파일이 없다면 직접 만들면 됩니다.

1. 탐색기 주소창에 `%USERPROFILE%` 입력 → Enter (본인 계정 폴더로 이동)
2. 없는 폴더(`.cursor` 또는 `.gemini\antigravity`)를 새로 만드세요
3. 그 안에 `mcp.json`(Cursor) 또는 `mcp_config.json`(Antigravity) 파일을 만들고 위 JSON을 넣으세요

Antigravity는 채팅에 위 JSON을 붙여넣고 "이 MCP 서버를 등록해줘"라고 요청하는 방법이 더 쉽습니다. 무료로 설치 가능하며, KORAIL MCP 연결에 별도 구독이 필요 없습니다.
</details>

<details>
<summary>GitHub Copilot CLI — 실제 계정으로 도구 호출까지 실측 완료</summary>

터미널에서 쓰는 공식 **GitHub Copilot CLI**(`@github/copilot`, VS Code 없이도 동작)로 실제 계정 붙여서 검증했습니다. **무료 플랜에서도 MCP 서버 연결이 됩니다** (다만 월 채팅 50회, 모델은 Claude Haiku 4.5 / GPT-5 mini로 제한).

> ⚠️ **사전 준비 — Node.js 22 이상**이 필요합니다. `node --version`으로 확인하고, 없으면 [nodejs.org](https://nodejs.org)에서 LTS 버전을 설치하세요(uv와 달리 자동으로 준비되지 않습니다).

```powershell
# 1) 설치 (최초 1회)
npm install -g @github/copilot

# 2) korail-mcp를 MCP 서버로 등록 (최초 1회)
copilot mcp add korail-mcp -- "C:\Users\<사용자명>\.local\bin\korail-mcp.exe"

# 3) 실제 질문 (도구 자동 승인)
copilot -p "서울역에 엘리베이터가 있는지 korail-mcp 도구로 조회해줘" --allow-all-tools
```

> ✅ **2026-08-24 실측 결과** — 위 명령을 실제로 실행해서 GitHub Copilot이 `get_urban_accessibility` 도구를 스스로 호출하고 실데이터로 답변하는 것까지 확인했습니다:
>
> ```
> ● get_urban_accessibility (MCP: korail-mcp) · station_name: "서울역", facility_type: "elevator"
>
> 네, 서울역에는 엘리베이터가 있습니다! 총 17개의 엘리베이터가 설치되어 있습니다.
> - 공항철도(AR): 9개 · 경의중앙선(KR): 1개 · 1호선(S1): 4개 · 4호선(S1): 3개
> ```
>
> 설정 파일은 `~/.copilot/mcp-config.json`에 `mcpServers.korail-mcp`로 저장되며, `copilot mcp list`로 등록 확인, `copilot mcp remove korail-mcp`로 제거할 수 있습니다.
</details>

<details>
<summary>VS Code (GitHub Copilot Chat) — JSON 형식이 다릅니다 (서버 프로토콜은 실측, VS Code GUI 자체는 미확인)</summary>

VS Code 확장 형태의 Copilot Chat은 위 CLI와 별개 제품이라 설정 파일이 다릅니다. 최상위 키가 `mcpServers`가 아니라 **`servers`** 라서 위 JSON을 그대로 쓸 수 없습니다.

1. 저장소(작업 폴더) 루트에 `.vscode\mcp.json` 파일을 만들고 아래 내용을 넣습니다.
   (모든 작업 폴더에서 쓰려면 명령 팔레트(Ctrl+Shift+P) → **MCP: Open User Configuration** 으로 열리는 `%APPDATA%\Code\User\mcp.json` 에 넣으세요.)

```json
{
  "servers": {
    "korail-mcp": {
      "command": "C:\\Users\\<사용자명>\\.local\\bin\\korail-mcp.exe"
    }
  }
}
```

2. 파일을 저장하면 상단에 나타나는 **Start** 버튼을 클릭합니다.
3. Copilot Chat을 열고 **Agent 모드**를 선택 → 도구 아이콘에서 `korail-mcp` 98개 도구가 보이면 연결 완료입니다.

> ⚠️ **위 CLI 테스트로 서버 쪽(stdio 프로토콜·98개 도구·실데이터 응답)은 이미 검증됐지만, VS Code 화면에서 Start를 눌러 실제로 붙는지는 GUI 조작 도구가 없어 확인하지 못했습니다.** 안 되면 알려주세요.
</details>

### 연결 후 반드시 — 클라이언트를 완전히 종료했다 다시 실행

> ℹ️ **Claude Code·GitHub Copilot CLI는 이 단계가 필요 없습니다** — 명령을 실행할 때마다 설정을 새로 읽습니다. 아래는 Claude Desktop·Cursor·Antigravity·VS Code처럼 **창을 띄워두는 클라이언트**에만 해당합니다.

창의 X를 눌러 닫아도 **트레이(작업표시줄 오른쪽 `^` 안)에 계속 실행 중**이라 설정이 적용되지 않습니다.
→ 트레이 아이콘 **우클릭 → Quit / 종료** 후 다시 실행하세요.

정상 연결되면 설정의 MCP 서버 목록에 `korail-mcp`가 **running** 으로 표시되고, 98개 도구를 쓸 수 있습니다.

### 💬 설치 확인 — 이렇게 물어보세요

```
서울역에 엘리베이터가 있나요?
2024년 간선철도 수송실적을 알려주세요.
KTX 101 열차의 운행 계획을 알려주세요.
```

정상 응답이 오면 설치 완료입니다. 더 많은 사용 예시는 문서 하단의 "사용 예시" 섹션을 참고하세요.

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

## 🧩 그 밖의 방식

<details>
<summary>ChatGPT · Grok — 원격 연결이 필요합니다</summary>

ChatGPT와 Grok은 **로컬 MCP 서버를 지원하지 않습니다.** 공개 HTTPS 엔드포인트만 커넥터로 추가할 수 있어, 위 방법으로는 연결되지 않습니다.

게이트웨이에 원격(Streamable HTTP) 모드가 내장되어 있어 **공개 주소로 노출하면** 연결이 가능합니다. 다만 서버 운영과 공개 범위 문제가 따르므로 상세는 [gateway/README.md](gateway/README.md)를 참고하세요.
</details>

<details>
<summary>uvx 로 설치 없이 실행 — 권장하지 않습니다</summary>

설치 과정 없이 `uvx` 로 바로 실행할 수도 있습니다.

```json
{
  "mcpServers": {
    "korail-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/lovelyquality/korail-mcp.git", "korail-mcp"]
    }
  }
}
```

계정명을 넣지 않아도 되는 장점이 있으나, **실행할 때마다 GitHub에 최신 커밋이 있는지 확인**하기 때문에 클라이언트를 켤 때마다 기동이 느립니다.

| 방식 | 기동 시간(실측) |
|---|---|
| `uv tool install` 후 실행 | **약 5초** |
| `uvx` (매번 원격 확인) | 약 40초 |

기동이 느리면 클라이언트가 서버를 기다리다 놓쳐 도구가 나타나지 않을 수 있습니다.
</details>

<details>
<summary>개발자용 — 저장소를 직접 받아서 실행</summary>

서버 코드를 수정하려면 저장소를 clone 해서 실행합니다.

```bash
git clone https://github.com/lovelyquality/korail-mcp.git
cd korail-mcp
uv run gateway/server.py
```

의존성은 `gateway/server.py` 상단에 선언되어 있어 `uv`가 자동으로 준비합니다. 변경 후에는
`python docker-test/smoke_test.py` 로 11개 서버·98개 도구·반환 타입 선언을 한 번에 검증하세요.

상세는 [gateway/README.md](gateway/README.md) 참고.
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
- 각 데이터셋의 기준일·갱신주기는 도구 응답의 `_meta` 항목에 표시됩니다.

---

각 서버의 상세 동작은 해당 폴더의 `server.py` docstring을 참조하세요.
