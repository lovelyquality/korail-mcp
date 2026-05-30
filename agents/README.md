# KORAIL MCP Agent 사용 가이드

## 개요

KORAIL MCP Agent는 Claude Desktop의 **Project 기능**을 활용한 역할별 AI 어시스턴트입니다.
각 Agent는 관련 MCP 서버들을 사용하도록 최적화된 시스템 프롬프트를 가집니다.

## Agent 목록

| 코드 | 이름 | 대상 | 주요 MCP |
|---|---|---|---|
| **C1** | 여행·예매 Agent | 고객 | train-ops, convenience, network, codebook |
| **C2** | 접근성 Agent | 고객 (교통약자) | convenience, codebook, kric |
| **C3** | 고객응대 Agent | 고객·상담원 | train-ops, convenience, codebook, voc-cs |
| **E1** | 통계분석 Agent | 직원 (기획·분석) | stats, carriage, rolling-stock, freight, network |
| **E2** | 현장운영 Agent | 직원 (현장·운영) | rolling-stock, freight, network, codebook, train-ops |
| **E3** | 내부지원 Agent | 직원 (행정·조달) | internal-svc, procurement, codebook |

---

## Claude Desktop Project 생성 방법

### 1단계: Claude Desktop 열기
- 좌측 사이드바에서 **"+"** 버튼 클릭 → **"New Project"** 선택

### 2단계: Project 설정
- **Project 이름** 입력 (예: `KORAIL 여행 도우미`)
- **Project Instructions** (시스템 프롬프트) 입력:
  - 각 Agent 파일(`C1_여행예매_agent.md` 등)을 열어
  - `## 시스템 프롬프트` 섹션의 코드블록 내용을 복사·붙여넣기

### 3단계: 사용할 MCP 서버 확인
- Claude Desktop 설정에 관련 MCP 서버들이 등록되어 있어야 합니다.
- `setup.bat`으로 설치했다면 기본 등록되어 있습니다.

### 4단계: 사용 시작
- 생성한 Project를 선택하면 지정된 역할로 동작합니다.
- 새 대화를 시작하면 시스템 프롬프트가 자동 적용됩니다.

---

## 파일 목록

| 파일 | 내용 |
|---|---|
| `C1_여행예매_agent.md` | 열차 여행·예매 정보 안내 Agent |
| `C2_접근성_agent.md` | 교통약자 접근성 전문 Agent |
| `C3_고객응대_agent.md` | 고객센터·상담 지원 Agent |
| `E1_통계분석_agent.md` | 수송·차량·화물 통계 분석 Agent |
| `E2_현장운영_agent.md` | 차량·화물·노선 현장 업무 지원 Agent |
| `E3_내부지원_agent.md` | 임대·사회공헌·조달 내부 업무 Agent |

---

## 주의사항

- Claude Desktop에 MCP 서버가 정상 연결된 상태에서 사용하세요.
- C2 Agent의 도시철도 시설 조회(`m-urban-rail`)는 API 승인 후 활성화됩니다.
- Agent는 실시간 예매·예약 기능을 제공하지 않습니다.
- 데이터는 data.go.kr 공공데이터 기준으로, 실시간 운행 정보와 다를 수 있습니다.
