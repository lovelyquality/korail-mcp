# 📋 VOC·고객만족도·정보공개

KORAIL 고객만족도 통계, 상담 유형·부서, 사전 공시, 정보공개 현황을 조회하는 MCP 서버 (도구 10개)

> 📌 이 폴더의 도구는 통합 서버 `korail-mcp` 에 포함되어 함께 제공됩니다(개별 등록 불필요). 설치는 [루트 README](../README.md) 참고. 데이터 호출은 전용 Cloudflare Workers 프록시를 경유하여 **API 키가 필요 없습니다.**

| 도구 | 설명 |
|---|---|
| `get_customer_satisfaction_stats` | 고객만족도 통계 조회 |
| `get_consultation_types` | 상담 유형 조회 |
| `get_consultation_departments` | 상담 부서 조회 |
| `get_advance_disclosure` | 사전 공시 조회 |
| `get_advance_disclosure_detail` | 사전 공시 상세 조회 |
| `get_advance_disclosure_files` | 사전 공시 첨부파일 조회 |
| `get_info_disclosure_dept` | 정보공개 담당 부서 |
| `get_info_disclosure_codes` | 정보공개 코드 조회 |
| `get_homepage_dept` | 홈페이지 담당 부서 |
| `get_homepage_position` | 홈페이지 담당자 직위 |

