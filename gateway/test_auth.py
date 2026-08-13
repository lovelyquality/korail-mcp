"""Bearer Token 인증 동작 검증 (포트 8084, MCP_API_KEY=test-secret-123)"""
import httpx, json, sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8084"
MCP = f"{BASE}/mcp/"
BODY = {"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "protocolVersion":"2024-11-05","capabilities":{},
    "clientInfo":{"name":"test","version":"1.0"},
}}

def post(token: str = ""):
    h = {"Accept": "application/json, text/event-stream"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return httpx.post(MCP, json=BODY, headers=h, timeout=5)

# 1. 토큰 없음 → 401 예상
r1 = post()
print(f"토큰 없음:       {r1.status_code}  (401 예상)")

# 2. 잘못된 토큰 → 401 예상
r2 = post("wrong-token")
print(f"잘못된 토큰:     {r2.status_code}  (401 예상)")

# 3. 올바른 토큰 → 200 예상
r3 = post("test-secret-123")
print(f"올바른 토큰:     {r3.status_code}  (200 예상)")
if r3.status_code == 200:
    for line in r3.text.splitlines():
        if line.startswith("data:"):
            data = json.loads(line[5:])
            print(f"  server: {data.get('result',{}).get('serverInfo')}")

# 4. /health는 토큰 없이도 접근 가능 → 200 예상
r4 = httpx.get(f"{BASE}/health", timeout=5)
print(f"/health 인증 없음: {r4.status_code}  (200 예상, 인증 제외)")
