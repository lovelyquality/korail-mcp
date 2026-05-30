# KORAIL MCP Agent

한국철도공사(KORAIL) 공공데이터를 Claude AI에 연결하는 MCP(Model Context Protocol) 서버 모음입니다.  
설치 후 Claude Desktop에서 자연어로 KORAIL 데이터를 조회할 수 있습니다.

---

## 제공 서버 (총 11개, 82개 도구)

| 서버 | 도구 수 | 제공 데이터 |
|---|:-:|---|
| m-convenience | 6 | 역사 편의시설·접근성·엘리베이터·위치 정보 |
| m-stats | 11 | 발권 통계·이동유형·KTX 장기 통계 |
| m-train-ops | 4 | 열차 운행계획·운행이력 |
| m-codebook | 4 | 역코드·노선코드 조회 |
| m-carriage | 4 | 간선·광역·화물 수송실적 |
| m-freight | 11 | 화물·컨테이너·물류시설·품목·위험물 |
| m-network | 8 | 노선·역간거리·운임·역 선로제원 |
| m-rolling-stock | 6 | 차량 보유현황·형별제원·차종별 운행실적 |
| m-voc-cs | 10 | 고객서비스·정보공개 |
| m-internal-svc | 14 | 임대매장·사회공헌·인사 정보 |
| m-procurement | 4 | 자재그룹·G2B 품명·자재속성·대상장비 |

---

## 설치 방법 (Windows)

### 1단계 — Python 설치

1. [python.org/downloads](https://www.python.org/downloads/) 접속 → **Download Python 3.12.x** 클릭
2. 설치 시 **"Add Python to PATH"** 반드시 체크 ✅
3. 설치 완료 후 명령 프롬프트(cmd)에서 확인:
   ```
   python --version
   ```
   `Python 3.12.x` 출력되면 성공

### 2단계 — 저장소 다운로드

**Git이 있는 경우:**
```bash
git clone https://github.com/lovelyquality/korail-mcp.git C:\korail-mcp
```

**Git이 없는 경우:**
1. [github.com/lovelyquality/korail-mcp](https://github.com/lovelyquality/korail-mcp) 접속
2. 초록색 **Code** 버튼 → **Download ZIP** 클릭
3. 압축 해제 후 폴더 이름을 `korail-mcp`로 변경, `C:\` 드라이브로 이동
4. 최종 경로: `C:\korail-mcp`

### 3단계 — API 키 발급

1. [data.go.kr](https://www.data.go.kr) 접속 → 회원가입 / 로그인
2. 상단 검색창에 **"한국철도공사"** 검색
3. 원하는 데이터셋의 **활용신청** 클릭 → 승인 (즉시 또는 1~2일 소요)
4. 마이페이지 → **API 키** 복사

> 💡 하나의 API 키로 data.go.kr의 모든 KORAIL 데이터셋을 사용할 수 있습니다.

### 4단계 — 자동 설치 스크립트 실행

`C:\korail-mcp` 폴더에서 `setup.bat`를 **더블클릭**합니다.

- 11개 서버의 Python 가상환경 자동 생성
- 필요한 패키지 자동 설치
- Claude Desktop 설정 파일 자동 생성
- `.env` 파일 자동 생성

> ⏳ 인터넷 속도에 따라 3~10분 소요됩니다.

### 5단계 — API 키 입력

설치 완료 후 각 서버 폴더의 `.env` 파일에 API 키를 입력합니다.

```
C:\korail-mcp\m-convenience\.env
C:\korail-mcp\m-stats\.env
... (각 폴더마다 동일)
```

`.env` 파일을 메모장으로 열어 아래와 같이 수정:
```
DATA_GO_KR_API_KEY=여기에_발급받은_키_입력
```

> 💡 `setup.bat` 실행 후 생성된 `set_api_key.bat`를 더블클릭하면 한 번에 전체 입력 가능합니다.

### 6단계 — Claude Desktop 설정

`setup.bat` 실행 시 자동으로 Claude Desktop 설정 내용이 출력됩니다.  
또는 아래 내용을 Claude Desktop 설정 파일에 직접 붙여넣기 하세요.

**설정 파일 위치:**
```
C:\Users\[사용자명]\AppData\Roaming\Claude\claude_desktop_config.json
```

**추가할 내용** (기존 `mcpServers` 항목 안에 붙여넣기):
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

### 7단계 — Claude Desktop 재시작

Claude Desktop을 완전히 종료 후 다시 시작합니다.  
채팅창 우측 상단에 🔨 아이콘이 생기면 성공입니다.

---

## 사용 예시

### 편의시설 (korail-convenience)
```
서울역에 엘리베이터가 있나요?
부산역의 장애인 편의시설을 알려주세요.
수서역의 편의시설 목록을 보여주세요.
```

### 통계 (korail-stats)
```
2023년 KTX 이용객 통계를 알려주세요.
최근 5년간 KTX 발권 통계 추이를 분석해주세요.
노선별 수송 실적을 비교해주세요.
```

### 열차 운행 (korail-train-ops)
```
KTX 101 열차의 운행 계획을 알려주세요.
서울-부산 구간 KTX 운행 이력을 조회해주세요.
```

### 역코드 (korail-codebook)
```
서울역 코드가 뭔가요?
경부선 노선 코드를 알려주세요.
경상남도 역 목록을 보여주세요.
```

### 수송실적 (korail-carriage)
```
2023년 간선철도 수송실적을 알려주세요.
광역철도 연도별 수송 현황을 보여주세요.
```

### 화물 (korail-freight)
```
컨테이너 화물 운송 실적을 조회해주세요.
물류시설 현황을 알려주세요.
표준 하역 시간을 확인해주세요.
```

### 노선·거리·운임 (korail-network)
```
서울역에서 부산역까지 거리가 얼마나 되나요?
경부선 노선 정보를 알려주세요.
KTX 정차역 목록을 보여주세요.
화물 운임을 계산해주세요.
```

### 차량 (korail-rolling-stock)
```
KTX 차량 보유 현황을 알려주세요.
전동차 형별 제원을 보여주세요.
연도별 차량 보유 현황 변화를 분석해주세요.
```

### 고객서비스 (korail-voc-cs)
```
고객 만족도 통계를 알려주세요.
사전정보공개 목록을 보여주세요.
정보공개 부서 목록은 어떻게 되나요?
```

### 내부 서비스 (korail-internal-svc)
```
역사 임대매장 현황을 알려주세요.
사회공헌 활동 현황을 보여주세요.
사내 지원시설 목록을 알려주세요.
회의실 현황을 조회해주세요.
```

### 조달·자재 (korail-procurement)
```
KTX-산천에 쓰이는 자재그룹코드를 알려주세요.
G2B 품명에서 '방열기'를 검색해주세요.
자재번호 1109275의 속성값이 뭔가요?
```

---

## 데이터 출처

- 한국철도공사 공공데이터포털 ([data.go.kr](https://www.data.go.kr))
- REST API (B551457), odcloud 파일 변환 API

## 주의사항

- `.env` 파일에 API 키를 보관하며 절대 외부에 공유하지 마세요.
- `m-network/data/station_distance.csv` (44MB)는 Git LFS로 관리됩니다.
- Git clone 시 Git LFS가 설치되어 있어야 대용량 파일이 정상 다운로드됩니다.
  ```bash
  git lfs install   # 최초 1회
  git clone https://github.com/lovelyquality/korail-mcp.git C:\korail-mcp
  ```
