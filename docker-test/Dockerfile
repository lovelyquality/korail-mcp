# KORAIL MCP 클린 설치 검증용 (Linux/python:3.12)
# 새 환경에서 받아 설치했을 때 동작하는지 재현한다.
# 빌드: docker build -f docker-test/Dockerfile -t korail-mcp-test .
# 실행: docker run --rm korail-mcp-test
#
# 참고: 배포용 이미지는 저장소 루트의 Dockerfile 이다(용도가 다름).
FROM python:3.12-slim

WORKDIR /app
COPY . /app

# 의존성은 gateway/requirements.txt 한 곳에서만 관리한다.
# (2026-08-17 이전에는 m-*/requirements.txt 11개를 순회 설치했는데,
#  11곳을 동기화해야 해서 버전 상한 누락 사고의 원인이 됐다.)
RUN pip install --no-cache-dir -r gateway/requirements.txt

CMD ["python", "docker-test/smoke_test.py"]
