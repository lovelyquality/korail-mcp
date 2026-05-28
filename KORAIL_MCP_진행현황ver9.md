# KORAIL MCP Agent 프로젝트 진행현황 ver9

> 최종 업데이트: 2026-05-28 (GitHub 배포 테스트 준비 / SSE Transport 전환 계획 수립)
> 이 문서 하나로 전체 컨텍스트 파악 가능 (ver1~ver8 읽을 필요 없음)
> 데이터 목록 분석 필요 시 → `01_filtering_result.csv` 참고

---

## 1. 개발 환경

| 항목 | 내용 |
|---|---|
| OS | Windows 11, PowerShell 5.1 |
| 터미널 | Warp |
| Python | 3.12.4 (m-freight venv 기준), 시스템 3.13 |
| 작업 폴더 | `E:\AI\MCP\` |
| venv 활성화 | `.\venv\Scripts\Activate.ps1` |
| venv 확인 | `Get-Command python \| Select-Object Source` |
| Claude Desktop | 설치됨, MCP 11개 연결 (tavily 포함) |
| Claude Desktop 설정 위치 | `%APPDATA%\Claude\claude_desktop_config.json` |

---

## 2. 전체 아키텍처 개요

```
기획서 목표: 10개 MCP (M1~M10) + 6종 Agent (C1~C3, E1~E3)
+ M11 m-kric (KRIC 전국 도시철도 API, 신규 제안)

[현재] stdio 로컬 방식:
  Claude Desktop → subprocess → server.py (로컬 실행)
  각 PC에 venv + 파일 + API 키 필요

[목표] SSE 서버 방식:
  Claude Desktop → HTTP SSE → 중앙 MCP 서버
  서버에만 API 키·로컬 파일 보관, 사용자는 URL 한 줄만 추가

데이터 레이어:
  공공데이터포털(data.go.kr) 개방 데이터 341건
  → 사용 가능 판정: 136건
    · odcloud 자동변환 API (파일데이터) → API 키 서버에 1개만 보유
    · B551457 REST API 2종
    · 로컬 XLSX/CSV 파일 → 서버에 보관
```

---

## 3. 완료된 MCP 서버 (10개, 전부 검증 완료)

### 3-1. m-convenience (korail-convenience) ✅
- **경로**: `E:\ai\mcp\m-convenience\` ← 소문자 ai/mcp 주의
- **API**: B551457 REST + odcloud 혼합
- **도구 6개**: `get_station_facilities`, `get_accessible_facilities`, `list_stations_with_elevator`, `get_station_facilities_detail`, `get_station_transfer_info`, `get_station_location`

### 3-2. m-stats (korail-stats) ✅
- **경로**: `E:\ai\mcp\m-stats\` ← 소문자 ai/mcp 주의
- **API**: B551457 REST + 로컬 XLSX
- **⚠️ `type=json` 필수**, 조건 파라미터 `cond[필드::연산자]`
- **도구 11개**: issueStatistics 10개 + `get_ktx_long_term_stats`(로컬 XLSX)
- **로컬 파일**: `data/ktx_segment_stats.xlsx`

### 3-3. m-train-ops (korail-train-ops) ✅
- **경로**: `E:\AI\MCP\m-train-ops\`
- **API**: B551457 REST + odcloud
- **⚠️ 실제 필드명이 스펙 문서와 다름**
- **도구 4개**: `get_train_codes`, `get_train_run_plan`, `get_train_run_info`, `get_train_run_history`

### 3-4. m-codebook (korail-codebook) ✅
- **경로**: `E:\AI\MCP\m-codebook\`
- **API**: odcloud 전용 (5종 캐시)
- **도구 4개**: `search_station`, `decode_station_code`, `search_route`, `list_stations_by_region`

### 3-5. m-carriage (korail-carriage) ✅
- **경로**: `E:\AI\MCP\m-carriage\`
- **API**: B551457 REST
- **도구 4개**: `get_mainline_carriage`, `get_wide_area_carriage`, `get_freight_carriage`, `get_carriage_codes`

### 3-6. m-freight (korail-freight) ✅
- **경로**: `E:\AI\MCP\m-freight\`
- **방식**: odcloud 4종 + 로컬 파일 6종
- **도구 9개**: `search_freight_code`, `decode_freight_code`, `search_container_record`, `search_consignment_change`, `search_consignment_change_per_wagon`, `list_freight_work_lines`, `get_logistics_facility`, `list_standard_loading_time`, `search_loading_time_adjustment`
- **로컬 파일**: `data/` 내 6개 (freight_codes.xlsx 등)

### 3-7. m-network (korail-network) ✅
- **경로**: `E:\AI\MCP\m-network\`
- **방식**: odcloud 4종 + 로컬 파일 3종
- **도구 7개**: `search_routes`, `get_station_distance`, `get_freight_minimum_fare`, `get_freight_rate`, `get_segment_info`, `get_operation_distance`, `get_ktx_stations`
- **로컬 파일**: `data/station_distance.csv` (44MB ⚠️), `segment_*.csv`, `operation_distance_all.xlsx`

### 3-8. m-rolling-stock (korail-rolling-stock) ✅
- **경로**: `E:\AI\MCP\m-rolling-stock\`
- **API**: odcloud 전용 (5종 캐시)
- **도구 5개**: `get_train_type_specs`, `get_rolling_stock_by_year`, `get_wagon_by_weight_class`, `get_wagon_by_load_capacity`, `get_maintenance_equipment`

### 3-9. m-voc-cs (korail-voc-cs) ✅
- **경로**: `E:\AI\MCP\m-voc-cs\`
- **API**: odcloud 전용 (10종 캐시)
- **도구 10개**: `get_customer_satisfaction_stats`, `get_consultation_types`, `get_consultation_departments`, `get_advance_disclosure`, `get_advance_disclosure_detail`, `get_advance_disclosure_files`, `get_info_disclosure_dept`, `get_info_disclosure_codes`, `get_homepage_dept`, `get_homepage_position`

### 3-10. m-internal-svc (korail-internal-svc) ✅
- **경로**: `E:\AI\MCP\m-internal-svc\`
- **API**: B551457 REST(`/lease`) + odcloud 12종
- **도구 14개**: `get_lease_stores`, `get_lease_codes`, `get_leased_assets`, `get_dormitory_longterm_codes`, `get_social_funds`, `get_social_volunteer_fields`, `get_social_donations`, `get_social_volunteer_matching`, `get_social_org`, `get_support_facilities`, `get_support_departments`, `get_office_meeting_rooms`, `get_job_grades`, `get_cafeteria_menu_stats`
- **⚠️ `get_lease_codes`**: /codes 엔드포인트 현재 빈 응답
- **⚠️ `get_social_org` / `get_support_departments`**: 대용량 → 필터 없으면 200건 제한

---

## 4. Claude Desktop 설정 (현재 stdio 모드)

```json
{
  "mcpServers": {
    "tavily-mcp": { "command": "npx", "args": ["-y", "tavily-mcp@0.1.2"], "env": { "TAVILY_API_KEY": "..." } },
    "korail-convenience": { "command": "E:/ai/mcp/m-convenience/venv/Scripts/python.exe", "args": ["E:/ai/mcp/m-convenience/server.py"] },
    "korail-stats": { "command": "E:/ai/mcp/m-stats/venv/Scripts/python.exe", "args": ["E:/ai/mcp/m-stats/server.py"] },
    "korail-codebook": { "command": "E:/AI/MCP/m-codebook/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-codebook/server.py"] },
    "korail-train-ops": { "command": "E:/AI/MCP/m-train-ops/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-train-ops/server.py"] },
    "korail-carriage": { "command": "E:/AI/MCP/m-carriage/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-carriage/server.py"] },
    "korail-freight": { "command": "E:/AI/MCP/m-freight/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-freight/server.py"] },
    "korail-network": { "command": "E:/AI/MCP/m-network/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-network/server.py"] },
    "korail-rolling-stock": { "command": "E:/AI/MCP/m-rolling-stock/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-rolling-stock/server.py"] },
    "korail-voc-cs": { "command": "E:/AI/MCP/m-voc-cs/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-voc-cs/server.py"] },
    "korail-internal-svc": { "command": "E:/AI/MCP/m-internal-svc/venv/Scripts/python.exe", "args": ["E:/AI/MCP/m-internal-svc/server.py"] }
  }
}
```

**⚠️ Claude Desktop 재시작 절차**: 시스템 트레이 → Quit → 재실행  
**⚠️ GUI Connector 메뉴 건드리지 말 것** (수동 추가 서버 누락 위험)

---

## 5. 핵심 개발 패턴

### 5-1. B551457 REST API 서버

```python
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv
import os

load_dotenv(encoding='utf-8-sig')  # ⚠️ BOM 처리 필수
API_KEY = os.getenv("DATA_GO_KR_API_KEY")
mcp = FastMCP("서버명")

def fetch(endpoint, cond={}):
    params = {"serviceKey": API_KEY, "pageNo": 1, "numOfRows": 1000}
    for k, v in cond.items():
        params[f"cond[{k}]"] = v
    r = httpx.get(f"BASE_URL/{endpoint}", params=params, timeout=15)
    body = r.json().get("response", {}).get("body", {})
    items = (body.get("items") or {}).get("item", [])
    return items if isinstance(items, list) else [items]

if __name__ == "__main__":
    mcp.run()
```

### 5-2. odcloud 파일 데이터 서버

```python
ODCLOUD_BASE = "https://api.odcloud.kr/api"
_cache: dict = {}

def _load(key: str) -> list:
    if key in _cache:
        return _cache[key]
    path = ENDPOINTS[key]
    all_data, page = [], 1
    while True:
        r = httpx.get(f"{ODCLOUD_BASE}{path}",
            params={"serviceKey": API_KEY, "page": page, "perPage": 1000}, timeout=20)
        body = r.json()
        data = body.get("data", [])
        all_data.extend(data)
        if len(all_data) >= body.get("totalCount", 0) or not data:
            break
        page += 1
    _cache[key] = all_data
    return all_data
```

### 5-3. `_wrap()` 메타데이터 표준

```python
def _wrap(data: list, dataset: str, ref_date: str) -> str:
    return json.dumps({
        "data": data,
        "_meta": {
            "출처": "한국철도공사 공공데이터포털 (data.go.kr)",
            "데이터셋": dataset,
            "데이터기준일": ref_date,
            "건수": len(data),
        },
    }, ensure_ascii=False, indent=2)
```

### 5-4. SSE Transport 전환 (배포 시)

```python
# stdio (현재, 로컬 개발용)
if __name__ == "__main__":
    mcp.run()

# SSE (배포용, 서버에서 실행)
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"])
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    if args.transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=args.port)
    else:
        mcp.run()
```

**SSE 배포 시 Claude Desktop config (사용자 측)**:
```json
{
  "korail-codebook": {
    "url": "http://서버IP:8004/sse"
  }
}
```

---

## 6. 데이터 출처 3종 비교

| 항목 | B551457 REST | odcloud 파일 변환 | 로컬 XLSX/CSV |
|---|---|---|---|
| Base URL | `apis.data.go.kr/B551457/...` | `api.odcloud.kr/api/{ID}/v1/uddi:{UUID}` | 파일 시스템 |
| 필터링 | `cond[필드::연산자]` | ❌ page/perPage만 | 코드 내 필터 |
| 응답 구조 | `response.body.items.item[]` | `data[]` | dict 리스트 |
| 필드명 | 영문 코드 | 한글 그대로 | 한글 그대로 |
| API 키 배포 방식 | **서버에만 1개** | **서버에만 1개** | 불필요 |

---

## 7. 알려진 이슈 및 주의사항

1. **PowerShell 5.1 인코딩**: `Out-File`/`Set-Content` 금지 → `[System.IO.File]::WriteAllText()` 사용
2. **.env BOM**: `load_dotenv(encoding='utf-8-sig')` 필수
3. **issueStatistics API**: `type=json` 파라미터 필수
4. **새 API 연결 시**: 실제 응답 1건 확인 후 필드명 사용 (스펙과 다를 수 있음)
5. **get_train_codes / get_carriage_codes**: `code_type` 없이 호출 시 0건
6. **odcloud 활용신청**: 미신청 시 400 + `"등록되지 않은 서비스키입니다."`
7. **경로 대소문자**: m-convenience·m-stats는 `E:\ai\mcp\` (소문자), 이후는 `E:\AI\MCP\` (대문자)
8. **API 키 보안**: .env는 절대 Git에 포함 금지, .gitignore 필수
9. **Python 콘솔 한글**: `sys.stdout.reconfigure(encoding='utf-8')` 사용
10. **m-network station_distance.csv 44MB**: GitHub 단일 파일 25MB 경고 → Git LFS 사용
11. **m-internal-svc `get_lease_codes`**: /codes 빈 응답
12. **m-internal-svc `get_social_org`/`get_support_departments`**: 필터 없으면 200건 제한
13. **m-network 노선명 "KTX" 없음**: "경부고속", "호남고속선" 등
14. **SSE 배포 시 포트 충돌**: 서버별 포트 별도 지정 필요 (예: 8001~8011)
15. **API 키 단일 관리**: data.go.kr API 키 1개로 모든 서버 운영 가능. 서버에만 보관, 사용자에게 노출 불필요 (웹서비스 개발 목적으로 활용승인 완료)

---

## 8. 데이터 기준일 정책

모든 도구는 `_wrap()` 표준으로 출처·데이터기준일·건수를 응답에 포함한다.

---

## 9. 활용신청 현황 (data.go.kr)

| API명 | 상태 |
|---|---|
| 한국철도공사_편의시설정보 (B551457) | ✅ |
| 한국철도공사_발권/이동유형 통계정보 (B551457) | ✅ |
| 한국철도공사_열차수송통계정보 (B551457) | ✅ |
| 한국철도공사_열차운행정보 (B551457) | ✅ |
| 한국철도공사_임대매장정보 (B551457) | ✅ |
| odcloud 44개 (M1~M10) | ✅ |
| 로컬 파일 10개 (m-freight 6 + m-network 3 + m-stats 1) | 📁 |

---

## 10. 데이터 사용 현황

| 유형 | 현재 MCP 사용 |
|---|:-:|
| REST API (B551457) | 5건 |
| odcloud 파일 데이터 | 44건 |
| 로컬 파일 | 10건 |

---

## 11. 전체 계획 대비 현황

| # | MCP 서버명 | 현재 상태 | 도구 수 |
|---|---|:-:|:-:|
| M1 | m-train-ops | 🟡 일부 | 4 |
| M2 | m-convenience | 🟡 일부 | 6 |
| M3 | m-stats + m-carriage | 🟡 일부 | 15 |
| M4 | m-rolling-stock | ✅ 완료 | 5 |
| M5 | m-freight | ✅ 완료 | 9 |
| M6 | m-network | ✅ 완료 | 7 |
| M7 | m-codebook | 🟡 일부 | 4 |
| M8 | m-internal-svc | ✅ 완료 | 14 |
| M9 | m-procurement | ⏸ 대기 | - |
| M10 | m-voc-cs | ✅ 완료 | 10 |
| M11 | m-kric | 💡 신규 제안 | - |
| **합계** | | | **74** |

---

## 12. Agent × MCP 매트릭스

| | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **C1 여행·예매** | ● | ● | | | | ○ | ● | | | |
| **C2 접근성** | | ● | | | | | ● | | | |
| **C3 고객응대** | ● | ● | | | | | ● | | | ● |
| **E1 통계분석** | ○ | ○ | ● | ● | ● | ● | ● | | | ○ |
| **E2 현장운영** | ○ | ○ | | ● | ● | ● | ● | | | |
| **E3 내부지원** | | | | | | | ● | ● | ● | |

---

## 13. 다음 작업 우선순위

### ① 🔵 현재: GitHub 배포 테스트 (SSE Transport)

**목표**: stdio → SSE 전환, GitHub 레포 구성, 원격 접속 검증

**작업 내용:**
1. GitHub 레포 생성 (`korail-mcp`, private)
2. `.gitignore` 작성 (`.env`, `venv/`, `__pycache__/`, `*.pyc`)
3. 각 서버 `requirements.txt` 작성
4. `.env.example` 작성
5. `server.py` SSE 전환 코드 추가 (argparse, `--transport` 옵션)
6. **대용량 파일 처리**: `station_distance.csv` (44MB) → Git LFS
7. 테스트 서버 선정: **m-rolling-stock** (odcloud 전용, 로컬 파일 없음, 단순)
8. 로컬 SSE 실행 → Claude Desktop에서 URL 방식으로 연결 검증
9. (선택) ngrok으로 외부 URL 테스트

**배포 아키텍처:**
```
[서버] python server.py --transport sse --port 8008
                ↑
[Claude Desktop] "url": "http://서버IP:8008/sse"
```

**포트 배정안:**
| 서버 | 포트 |
|---|---|
| m-convenience | 8001 |
| m-stats | 8002 |
| m-train-ops | 8003 |
| m-codebook | 8004 |
| m-carriage | 8005 |
| m-freight | 8006 |
| m-network | 8007 |
| m-rolling-stock | 8008 |
| m-voc-cs | 8009 |
| m-internal-svc | 8010 |

### ② ⏸ 대기: M9 m-procurement

**데이터 재평가 결과** (2026-05-28):

| # | 데이터셋 | 판정 | 사유 |
|---|---|:-:|---|
| 1 | 조달_입찰공고 | ❌ | 2024년 데이터, 의미없음 |
| 2 | 조달_관계법령 | ❌ | 의미없음 |
| 3 | 조달_공사용역 발주계획 | ❌ | 옛날 데이터 |
| 4 | 물품정보_메뉴정보 | ❌ | 옛날 데이터 |
| 5 | 물품정보_코드정보 | ❌ | 의미없음 |
| 6 | **물품_자재그룹코드** | ✅ | odcloud API, 999건, 그룹코드·명칭·사용여부 |
| 7 | 물품정보_게시판 | ❌ | 의미없음 |
| 8 | 물품정보_자재바구니 | ❌ | 의미없음 |
| 9 | **물품정보_자재속성** | 🟡 | API 없음, CSV 6개 (로컬 파일 처리 예정) |
| 10 | **철도운영정보_품목정보** | ✅→M5 | odcloud 861건, **m-freight로 이동** |

**M9 결론**: 유효 데이터 2개 → 규모 축소하거나 m-freight 합류 검토  
**철도운영정보_품목정보**: `get_freight_items` 도구로 **m-freight에 추가** (M5 보강)

### ③ 💡 신규 제안: M11 m-kric
- KRIC openapi.kric.go.kr 61개 API (전국 도시철도)
- 별도 KRIC API 키 필요
- GitHub 배포 테스트 및 M9 처리 후 결정

---

## 부록: GitHub 레포 예상 구조

```
korail-mcp/                          ← GitHub repo root
├── .gitignore
├── README.md
├── m-convenience/
│   ├── server.py
│   ├── requirements.txt
│   └── .env.example
├── m-stats/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env.example
│   └── data/
│       └── ktx_segment_stats.xlsx   ← Git 포함 (소형)
├── m-freight/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env.example
│   └── data/                        ← Git 포함 (6개, 소형)
├── m-network/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env.example
│   └── data/
│       ├── station_distance.csv     ← ⚠️ 44MB → Git LFS
│       ├── segment_*.csv
│       └── operation_distance_all.xlsx
├── m-rolling-stock/  (← SSE 테스트 대상)
│   ├── server.py
│   ├── requirements.txt
│   └── .env.example
├── ... (나머지 서버들)
└── docker-compose.yml               ← (선택) 전체 서버 한번에 실행
```

**.gitignore 내용:**
```
.env
venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
```

**.env.example 내용:**
```
# data.go.kr 공공데이터포털 API 키
# 발급: https://www.data.go.kr → 마이페이지 → 일반 인증키
DATA_GO_KR_API_KEY=여기에_발급받은_키_입력
```
