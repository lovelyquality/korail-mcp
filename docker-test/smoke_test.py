# -*- coding: utf-8 -*-
"""클린 컨테이너에서 11개 MCP 서버가 설치·기동·호출되는지 검증.
1) 각 server.py import (= 설치된 의존성으로 정상 로드되는가)
2) FastMCP 도구 등록 수
3) 프록시 경유 실제 호출 샘플 3건 (인터넷 가능 시)
"""
import importlib.util
import os
import sys
import traceback

APP = "/app"
servers = sorted(
    d for d in os.listdir(APP)
    if d.startswith("m-") and os.path.isdir(os.path.join(APP, d))
)

loaded = {}
print("=" * 60)
print("1) IMPORT / 도구 등록 스모크")
print("=" * 60)
ok = 0
total_tools = 0
for s in servers:
    p = os.path.join(APP, s, "server.py")
    try:
        os.chdir(os.path.join(APP, s))  # data 상대경로 대비
        spec = importlib.util.spec_from_file_location("srv_" + s.replace("-", "_"), p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        loaded[s] = mod
        n = "?"
        tm = getattr(mod.mcp, "_tool_manager", None)
        if tm is not None:
            tools = getattr(tm, "_tools", None)
            if tools is not None:
                n = len(tools)
                total_tools += n
        print(f"[OK]   {s:<18} 도구 {n}")
        ok += 1
    except Exception as e:
        print(f"[FAIL] {s:<18} {e!r}")
        traceback.print_exc()

print(f"\n→ import 성공 {ok}/{len(servers)} 서버, 도구 합계 {total_tools}")

print("\n" + "=" * 60)
print("2) 프록시 경유 실제 호출 샘플 (인터넷 필요)")
print("=" * 60)


def trycall(label, workdir, fn):
    try:
        os.chdir(workdir)
        r = fn()
        txt = r if isinstance(r, str) else str(r)
        print(f"[OK]   {label} -> {txt[:80].strip()}")
    except Exception as e:
        print(f"[FAIL] {label} -> {e!r}")


if "m-codebook" in loaded:
    trycall("codebook.search_route('경부')", "/app/m-codebook",
            lambda: loaded["m-codebook"].search_route("경부"))
if "m-stats" in loaded:
    trycall("stats.get_transport_stat_codes('mrnt_cd')", "/app/m-stats",
            lambda: loaded["m-stats"].get_transport_stat_codes(code_type="mrnt_cd"))
if "m-network" in loaded:
    trycall("network.search_operation_patterns('고속')", "/app/m-network",
            lambda: loaded["m-network"].search_operation_patterns(query="고속"))

print("\n완료.")
