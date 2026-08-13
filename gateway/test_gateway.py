"""gateway 로컬 테스트 스크립트"""
import httpx, json, sys

# Windows cp949 터미널 이모지 깨짐 방지
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8083"
MCP = f"{BASE}/mcp/"   # trailing slash 직접 사용 -> 307 없음

def mcp_post(body: dict, session_id: str = "") -> httpx.Response:
    headers = {"Accept": "application/json, text/event-stream"}
    if session_id:
        headers["mcp-session-id"] = session_id
    return httpx.post(MCP, json=body, headers=headers, timeout=15)

def parse_sse(text: str) -> dict:
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return {}

# 1. 헬스체크
print("=== /health ===")
r = httpx.get(f"{BASE}/health", timeout=5)
print(f"status: {r.status_code}")
print(json.dumps(r.json(), ensure_ascii=False, indent=2))

# 2. initialize
print("\n=== initialize ===")
r2 = mcp_post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{
    "protocolVersion":"2024-11-05","capabilities":{},
    "clientInfo":{"name":"test","version":"1.0"},
}})
session_id = r2.headers.get("mcp-session-id", "")
resp = parse_sse(r2.text)
print(f"status: {r2.status_code}  session: {session_id or '(stateless)'}")
print(f"server: {resp.get('result',{}).get('serverInfo')}")

# 3. tools/list
print("\n=== tools/list ===")
r3 = mcp_post({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}, session_id)
data = parse_sse(r3.text)
tools = data.get("result", {}).get("tools", [])
print(f"status: {r3.status_code}  도구 수: {len(tools)}")
for t in tools:
    name = t["name"]
    desc = t.get("description","").encode("utf-8","replace").decode("utf-8")[:50]
    print(f"  {name:<40} {desc}")

# 4. 실제 도구 호출 -- search_station('서울')
print("\n=== tools/call: search_station('서울') ===")
r4 = mcp_post({"jsonrpc":"2.0","id":3,"method":"tools/call","params":{
    "name":"search_station","arguments":{"name":"서울"},
}}, session_id)
d4 = parse_sse(r4.text)
content = d4.get("result",{}).get("content",[])
if content:
    raw = content[0].get("text","")
    obj = json.loads(raw) if raw else {}
    meta = obj.get("_meta", {})
    ktx = obj.get("차세대예약발매_역", [])
    ops = obj.get("철도운영정보_역", [])
    print(f"status: {r4.status_code}")
    print(f"차세대예약발매_역: {len(ktx)}건  철도운영정보_역: {len(ops)}건")
    if ktx:
        print(f"  첫번째: {ktx[0]}")
else:
    print(f"status: {r4.status_code}  응답: {d4}")
