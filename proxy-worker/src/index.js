/**
 * KORAIL MCP Proxy Worker
 * data.go.kr / odcloud / KRIC openapi API 키를 서버에서 보관하고 중계합니다.
 * 대국민 서비스로 누구나 설치해 쓸 수 있어야 해서 별도 인증은 두지 않는다.
 * 대신 아래 두 가지로 "회사 serviceKey로 아무거나 대신 호출당하는" 위험과
 * "다들 몰려서 하루 호출한도(개발계정 1,000회)가 바닥나는" 위험을 막는다:
 *
 *   1) 허용 경로 화이트리스트 — 실제로 이 프로젝트 10개 서버가 쓰는 데이터셋만 통과.
 *      (odcloud는 파일ID가 기관으로 구분되지 않아 정확한 목록으로 제한,
 *       apis/B551457은 KORAIL 자체 기관코드라 하위 전체 허용,
 *       KRIC은 실제 쓰는 서비스군 이름만 허용)
 *   2) 엣지 캐싱 — 역코드·노선코드 등 거의 안 바뀌는 데이터라, 한 번 받아온
 *      응답을 CACHE_TTL_SECONDS 동안 재사용. 사용자가 늘어도 실제 정부 API
 *      호출은 거의 안 늘어나게 한다.
 *
 * 라우팅:
 *   /proxy/apis/B551457/...  →  https://apis.data.go.kr/B551457/...   (DATA_GO_KR_API_KEY)
 *   /proxy/odcloud/...       →  https://api.odcloud.kr/api/...        (DATA_GO_KR_API_KEY)
 *   /proxy/kric/{svc}/{op}   →  https://openapi.kric.go.kr/openapi/{svc}/{op}  (KRIC_API_KEY)
 *
 * KRIC은 서비스키가 2개라 stPlf(역사별 승강장 정보) 오퍼레이션만 별도 키(KRIC_API_KEY_STPLF) 사용.
 */

const ROUTES = [
  { prefix: "/proxy/apis/",    target: "https://apis.data.go.kr/",            key: "DATA_GO_KR_API_KEY" },
  { prefix: "/proxy/odcloud/", target: "https://api.odcloud.kr/api/",         key: "DATA_GO_KR_API_KEY" },
  { prefix: "/proxy/kric/",    target: "https://openapi.kric.go.kr/openapi/", key: "KRIC_API_KEY" },
];

// odcloud UDDI 경로 화이트리스트 — 10개 서버의 ENDPOINTS/UDDI 상수에서 실제 쓰는 것만 추출.
// 새 데이터셋을 추가할 때는 여기도 같이 추가해야 한다.
const ODCLOUD_ALLOWED = new Set([
  "/15048398/v1/uddi:daa8f21e-a08d-4b57-8d8f-ac9710467fab",
  "/15053619/v1/uddi:c5b78411-7cd8-4de5-90ea-ab4ca3d3211a",
  "/15053620/v1/uddi:4be7be93-b948-46e3-b20b-f03c0a54ddc6",
  "/15053621/v1/uddi:6a51e6d0-d135-4f49-951c-aecd4f960783",
  "/15053622/v1/uddi:4376e97d-20da-4150-8e2b-f42cb339a96c",
  "/15053623/v1/uddi:d69a42a9-11e9-4f89-add5-ac1a7621ea52",
  "/15090378/v1/uddi:57b94475-833c-4242-9a42-cd7d3bfef4d8",
  "/15090379/v1/uddi:6a8ae00e-4d06-4bdd-af70-c360b9fbbbc6",
  "/15127532/v1/uddi:c1d09745-9e5c-48e4-b26c-c1833592509c",
  "/15127571/v1/uddi:ab540482-aa65-411d-908b-c961aadae08b",
  "/15131262/v1/uddi:cf4a745d-e7e0-4daa-9433-f5377f952f7d",
  "/15131416/v1/uddi:3c8f75b7-85f2-43e4-a93c-e9d899a17331",
  "/15131421/v1/uddi:9777bebc-9212-46a7-aa73-cb5ec86a123c",
  "/15133642/v1/uddi:39614479-48ee-44a3-a99b-93f4e2d84a36",
  "/15135862/v1/uddi:6ac7394e-58a2-4163-a031-90618c85f035",
  "/15135865/v1/uddi:c946542d-d513-44d2-a95d-f0ff8ab01dd6",
  "/15136381/v1/uddi:a192f49b-bd3d-4fc0-bf94-8f6e1bc0d5d7",
  "/15136386/v1/uddi:5540fd8e-af5a-455f-9c39-949eeacd2293",
  "/15137989/v1/uddi:0e875993-8248-49f1-b694-89a406bf18c0",
  "/15137990/v1/uddi:1f3d12f8-0cfb-46b0-915e-d0920bc63e7d",
  "/15138145/v1/uddi:bced7ecb-1c3a-44fa-b0a2-e0579433ab6a",
  "/15138153/v1/uddi:95e7cf38-fea1-40d7-bab1-b63b5155b1f1",
  "/15138437/v1/uddi:cdb563dd-d72f-4759-bf41-faae9b125fc3",
  "/15138441/v1/uddi:d1505fd5-90fb-4342-ac19-9711ed5028cf",
  "/15138442/v1/uddi:01b17f28-7f8d-4b21-9c19-ee35557ee13a",
  "/15138455/v1/uddi:8aea9f31-7bd0-4870-9553-8f0fb49075ec",
  "/15138467/v1/uddi:dcd1dc8d-1fe1-4625-9ec5-fc7eb2542fe4",
  "/15148497/v1/uddi:e6fbbd6a-0252-4a07-968e-ef9b3ca7f9de",
  "/15153539/v1/uddi:69cf6c1d-fbff-4981-a65d-b9e197e14911",
  "/15153559/v1/uddi:a369ea3f-6493-441a-9a5d-b4da591cbeb3",
  "/15153571/v1/uddi:8b1350c1-711c-422a-b68d-e4e27ed31509",
  "/15153575/v1/uddi:106d1522-6c05-4f5a-b95d-9fe4c9453361",
  "/15153586/v1/uddi:9b4fbb34-a309-42bf-a838-cf843ddeedb3",
  "/15153791/v1/uddi:cbe55055-2504-4d8b-8af9-b2f43d87ceb8",
  "/15153818/v1/uddi:02a37f71-0988-43ca-9dc3-fe4b1bb88a7a",
  "/15153898/v1/uddi:7430d02d-b78a-4395-9bf5-b1ab000e1be2",
  "/15153923/v1/uddi:e7467fbe-9dc2-4396-802a-daf4bfbb1468",
  "/15153929/v1/uddi:8996eb87-a404-4acb-80fe-b267fb5325fd",
  "/15153958/v1/uddi:c6e5876a-ea23-4dbe-b7e4-a92095681096",
  "/15153967/v1/uddi:45f3a2bc-628d-4ce8-a8ca-e8789af3a0fd",
  "/15153971/v1/uddi:394df6e4-92f7-4440-b100-93735ab6a5be",
  "/15154148/v1/uddi:a360f730-9fd5-4a1b-90a5-fd1b571b232b",
  "/15154168/v1/uddi:cd6218c1-2bb9-4f0d-bdf9-9a4e5fde9558",
  "/15154169/v1/uddi:cbfb94b1-fa4a-4dab-aa62-e764caa4dbc3",
]);

// KRIC 서비스군 화이트리스트 — m-urban-rail이 실제 쓰는 svc 이름만.
// (op 단위까지 촘촘히 막으면 역사시설 항목 하나 늘 때마다 여기도 고쳐야 해서 svc 단위로 둔다)
const KRIC_ALLOWED_SVC = new Set([
  "convenientInfo",
  "vulnerableUserInfo",
  "trafficWeekInfo",
  "safetyInfo",
  "trainUseInfo",
]);

// 캐시 유효기간. 대부분 역코드·노선코드처럼 정적인 데이터라 넉넉히 잡아도 안전하다.
// ponytail: 데이터셋별로 다르게 두면 더 정확하지만, 우선 전역 1시간으로 통일.
//           운행정보처럼 더 자주 바뀌는 데이터가 늘면 라우트별 TTL 맵으로 갈라낼 것.
const CACHE_TTL_SECONDS = 60 * 60;

function isPathAllowed(route, subPath) {
  if (route.prefix === "/proxy/odcloud/") {
    return ODCLOUD_ALLOWED.has("/" + subPath.replace(/\?.*$/, ""));
  }
  if (route.prefix === "/proxy/kric/") {
    const svc = subPath.split("/")[0];
    return KRIC_ALLOWED_SVC.has(svc);
  }
  // /proxy/apis/B551457/... 은 프리픽스 자체가 우리 기관코드라 하위 전체 허용
  return true;
}

export default {
  async fetch(request, env, ctx) {
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

    const subPath = url.pathname.slice(route.prefix.length);

    if (!isPathAllowed(route, subPath)) {
      return new Response(JSON.stringify({ error: "Forbidden: 허용되지 않은 데이터셋" }), {
        status: 403,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    // 캐시 조회 (GET만) — 요청 URL 그대로를 키로 쓴다.
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), { method: "GET" });
    if (request.method === "GET") {
      const cached = await cache.match(cacheKey);
      if (cached) {
        const hit = new Response(cached.body, cached);
        hit.headers.set("X-Proxy-Cache", "HIT");
        return hit;
      }
    }

    // 타깃 URL 구성
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
      const result = new Response(body, {
        status: response.status,
        headers: {
          "Content-Type": response.headers.get("Content-Type") || "application/json",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": `public, max-age=${CACHE_TTL_SECONDS}`,
          "X-Proxy-Cache": "MISS",
        },
      });

      if (request.method === "GET" && response.status === 200) {
        ctx.waitUntil(cache.put(cacheKey, result.clone()));
      }
      return result;
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 502,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
};
