# test_api.py
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv(encoding='utf-8-sig')  # ← 이 줄만 바뀜

API_KEY = os.getenv("DATA_GO_KR_API_KEY")
BASE_URL = "https://apis.data.go.kr/B551457/convenience"

def test_convenience(endpoint: str, extra_params: dict = {}):
    url = f"{BASE_URL}/{endpoint}"
    params = {
        "serviceKey": API_KEY,
        "pageNo": 1,
        "numOfRows": 3,
        **extra_params
    }
    
    response = httpx.get(url, params=params, timeout=10)
    print(f"\n=== {endpoint} ===")
    print(f"Status: {response.status_code}")
    
    # JSON 또는 XML 응답 모두 처리
    try:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:800])
    except Exception:
        print(response.text[:800])

if __name__ == "__main__":
    print(f"API_KEY 로딩 확인: {'OK' if API_KEY else 'FAIL - .env 확인 필요'}")
    
    test_convenience("stationFacilities")       # 일반 편의시설
    test_convenience("weekPersonFacilities")    # 교통약자 편의시설