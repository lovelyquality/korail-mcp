# KORAIL MCP Agent

한국철도공사(KORAIL) 공공데이터포털 데이터를 Claude AI에 연결하는 MCP(Model Context Protocol) 서버 모음.

## 구성

| 서버 | 포트 | 도구 수 | 설명 |
|---|:-:|:-:|---|
| m-convenience | 8001 | 6 | 역사 편의시설·접근성·위치 정보 |
| m-stats | 8002 | 11 | 발권·이동유형·KTX 장기 통계 |
| m-train-ops | 8003 | 4 | 열차 운행계획·운행이력 |
| m-codebook | 8004 | 4 | 역코드·노선코드 조회 |
| m-carriage | 8005 | 4 | 간선·광역·화물 수송실적 |
| m-freight | 8006 | 9 | 화물·컨테이너·물류시설 |
| m-network | 8007 | 7 | 노선·역간거리·운임 정보 |
| m-rolling-stock | 8008 | 5 | 차량 보유·형별제원 |
| m-voc-cs | 8009 | 10 | 고객서비스·정보공개 |
| m-internal-svc | 8010 | 14 | 임대매장·사회공헌·인사 |

## 설치

```bash
cd m-rolling-stock   # 원하는 서버 디렉토리로 이동
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 DATA_GO_KR_API_KEY 입력
```

## 실행

### stdio 방식 (로컬 개발)

```bash
python server.py
```

### SSE 방식 (서버 배포)

```bash
python server.py --transport sse --port 8008
```

## Claude Desktop 설정

### stdio 방식

```json
{
  "mcpServers": {
    "korail-rolling-stock": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/m-rolling-stock/server.py"]
    }
  }
}
```

### SSE 방식 (서버 배포 후)

```json
{
  "mcpServers": {
    "korail-rolling-stock": {
      "url": "http://서버IP:8008/sse"
    }
  }
}
```

## 데이터 출처

- 한국철도공사 공공데이터포털 (data.go.kr)
- REST API (B551457), odcloud 파일 변환 API, 로컬 XLSX/CSV 파일

## 주의사항

- `.env` 파일에 API 키를 보관하며 절대 Git에 포함하지 않습니다.
- `m-network/data/station_distance.csv` (44MB)는 Git LFS로 관리됩니다.
