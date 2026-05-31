/**
 * KORAIL MCP Proxy Worker
 * data.go.kr / odcloud API 키를 서버에서 보관하고 중계합니다.
 *
 * 라우팅:
 *   /proxy/apis/B551457/...  →  https://apis.data.go.kr/B551457/...
 *   /proxy/odcloud/...       →  https://api.odcloud.kr/api/...
 */

const ROUTES = [
  { prefix: "/proxy/apis/",    target: "https://apis.data.go.kr/" },
  { prefix: "/proxy/odcloud/", target: "https://api.odcloud.kr/api/" },
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
    params.set("serviceKey", env.DATA_GO_KR_API_KEY);

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
