/**
 * KORAIL MCP Proxy Worker
 * data.go.kr / odcloud / KRIC openapi API 키를 서버에서 보관하고 중계합니다.
 *
 * 라우팅:
 *   /proxy/apis/B551457/...  →  https://apis.data.go.kr/B551457/...   (DATA_GO_KR_API_KEY)
 *   /proxy/odcloud/...       →  https://api.odcloud.kr/api/...        (DATA_GO_KR_API_KEY)
 *   /proxy/kric/{svc}/{op}   →  https://openapi.kric.go.kr/openapi/{svc}/{op}  (KRIC_API_KEY)
 *
 * KRIC은 서비스키가 2개라 stPlf(역사별 승강장 정보) 오퍼레이션만 별도 키(KRIC_API_KEY_STPLF) 사용.
 *
 * 인증: PROXY_AUTH_TOKEN secret 설정 시 Bearer 토큰 검증(/health 제외).
 *   `wrangler secret put PROXY_AUTH_TOKEN` 로 설정할 것 — 미설정 시 완전 공개
 *   프록시가 되어 회사 serviceKey로 data.go.kr/KRIC를 대신 호출당할 수 있다.
 */

const ROUTES = [
  { prefix: "/proxy/apis/",    target: "https://apis.data.go.kr/",            key: "DATA_GO_KR_API_KEY" },
  { prefix: "/proxy/odcloud/", target: "https://api.odcloud.kr/api/",         key: "DATA_GO_KR_API_KEY" },
  { prefix: "/proxy/kric/",    target: "https://openapi.kric.go.kr/openapi/", key: "KRIC_API_KEY" },
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    // 헬스체크
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({ status: "ok", service: "korail-mcp-proxy" }), {
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    // 인증: PROXY_AUTH_TOKEN이 설정된 경우에만 검증(미설정 시 개발 모드로 통과)
    if (env.PROXY_AUTH_TOKEN) {
      const auth = request.headers.get("Authorization") || "";
      if (auth !== `Bearer ${env.PROXY_AUTH_TOKEN}`) {
        return new Response(JSON.stringify({ error: "Unauthorized" }), {
          status: 401,
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        });
      }
    }

    // 라우팅
    const route = ROUTES.find(r => url.pathname.startsWith(r.prefix));
    if (!route) {
      return new Response(JSON.stringify({ error: "Not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    // 타깃 URL 구성
    const subPath = url.pathname.slice(route.prefix.length);
    const params = new URLSearchParams(url.search);

    // 라우트별 서비스키 선택. KRIC stPlf 오퍼레이션만 별도 키.
    let keyName = route.key;
    if (route.prefix === "/proxy/kric/" && /(^|\/)stPlf(\/|$|\?)/.test(subPath)) {
      keyName = "KRIC_API_KEY_STPLF";
    }
    params.set("serviceKey", env[keyName]);

    const targetUrl = `${route.target}${subPath}?${params.toString()}`;

    try {
      const response = await fetch(targetUrl, {
        headers: { Accept: "application/json" },
      });
      const body = await response.text();
      return new Response(body, {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("Content-Type") || "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 502,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
};
