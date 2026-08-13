# KORAIL MCP 게이트웨이 — 원격(Streamable HTTP) 배포용
#
# 98개 도구를 단일 HTTP 엔드포인트로 제공한다. Cloud Run·Fly.io 등
# 컨테이너 플랫폼에 그대로 올릴 수 있다.
#
# 로컬 빌드·실행:
#   docker build -t korail-mcp-gateway .
#   docker run --rm -p 8080:8080 korail-mcp-gateway
#   curl http://localhost:8080/health
#
# Cloud Run 배포 (PORT 는 플랫폼이 주입 → 코드가 자동으로 읽음):
#   gcloud run deploy korail-mcp --source . --region asia-northeast3 \
#     --allow-unauthenticated --memory 512Mi
#
# ⚠️ 인증: MCP_API_KEY 환경변수를 설정하면 Bearer Token 검증이 켜진다.
#    미설정 시 인증 없이 열리므로, 공개 배포 시에는 반드시 설정하거나
#    프록시 단계에서 요청 제한을 걸 것.
#
# 참고: 클린 설치 검증용 이미지는 docker-test/Dockerfile 이다(용도가 다름).

FROM python:3.12-slim

# 파이썬 로그가 버퍼에 갇히지 않게 (Cloud Run 로그 확인용)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 의존성만 먼저 설치해 레이어 캐시를 살린다 (코드 변경 시 재설치 회피)
COPY gateway/requirements.txt /app/gateway/requirements.txt
RUN pip install --no-cache-dir -r /app/gateway/requirements.txt

# 게이트웨이 + 11개 서버 (데이터 포함). .dockerignore 가 venv·.env·발표자산을 제외한다.
COPY gateway/ /app/gateway/
COPY m-codebook/ /app/m-codebook/
COPY m-convenience/ /app/m-convenience/
COPY m-freight/ /app/m-freight/
COPY m-internal-svc/ /app/m-internal-svc/
COPY m-network/ /app/m-network/
COPY m-procurement/ /app/m-procurement/
COPY m-rolling-stock/ /app/m-rolling-stock/
COPY m-stats/ /app/m-stats/
COPY m-train-ops/ /app/m-train-ops/
COPY m-urban-rail/ /app/m-urban-rail/
COPY m-voc-cs/ /app/m-voc-cs/

# 문서상의 기본 포트. Cloud Run 은 PORT 를 주입하며 코드가 그 값을 우선 사용한다.
ENV PORT=8080
EXPOSE 8080

# -m 으로 실행해야 한다 (파일 경로로 직접 실행하면 uvicorn 이 모듈을 못 찾음)
CMD ["python", "-m", "gateway.server", "--transport", "http"]
