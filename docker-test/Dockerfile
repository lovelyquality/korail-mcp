# KORAIL MCP 클린 설치 검증용 (Linux/python:3.12)
# 직원이 새 환경에서 받아 설치했을 때 동작하는지 재현한다.
# 빌드: docker build -f docker-test/Dockerfile -t korail-mcp-test .
# 실행: docker run --rm korail-mcp-test
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# 11개 서버 requirements 를 공통 환경에 모두 설치 (의존성 충돌까지 검증)
RUN pip install --no-cache-dir --upgrade pip && \
    for d in m-*/ ; do \
      echo "=== pip install ${d} ===" ; \
      pip install --no-cache-dir -r "${d}requirements.txt" || exit 1 ; \
    done

CMD ["python", "docker-test/smoke_test.py"]
