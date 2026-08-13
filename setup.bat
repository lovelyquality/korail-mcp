@echo off
chcp 949 > nul
setlocal enabledelayedexpansion

echo ================================================================
echo   KORAIL MCP Agent 설치 스크립트
echo ================================================================
echo.

:: 현재 디렉토리 확인
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
echo 설치 경로: %ROOT%
echo.

:: Python 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org/downloads/ 에서 Python 3.12 이상을 설치하세요.
    echo 설치 시 "Add Python to PATH" 를 반드시 체크하세요.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo Python 확인: %PYVER%
echo.

:: 서버 목록
set SERVERS=m-convenience m-stats m-train-ops m-codebook m-freight m-network m-rolling-stock m-voc-cs m-internal-svc m-procurement m-urban-rail

:: 공용 가상환경 1개 생성 (11개 서버가 공유 - 중복 설치 제거로 약 900MB 절약)
echo ----------------------------------------------------------------
echo 공용 가상환경 및 패키지 설치 중...
echo ----------------------------------------------------------------
echo.

if not exist "%ROOT%\venv" (
    python -m venv "%ROOT%\venv" > nul 2>&1
    if errorlevel 1 (
        echo [오류] 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo 공용 가상환경 생성 완료: %ROOT%\venv
) else (
    echo 공용 가상환경 이미 존재
)
echo.

:: 서버별 requirements.txt 를 공용 가상환경에 설치 (중복 패키지는 자동으로 건너뜀)
for %%s in (%SERVERS%) do (
    if exist "%ROOT%\%%s\requirements.txt" (
        echo [%%s] 패키지 확인 중...
        "%ROOT%\venv\Scripts\pip.exe" install -r "%ROOT%\%%s\requirements.txt" -q
        if errorlevel 1 (
            echo   [오류] 패키지 설치 실패: %%s
            pause
            exit /b 1
        )
    )
)
echo 패키지 설치 완료
echo.

:: 서버별 .env 생성
for %%s in (%SERVERS%) do (
    if exist "%ROOT%\%%s" (
        if not exist "%ROOT%\%%s\.env" (
            if exist "%ROOT%\%%s\.env.example" (
                copy "%ROOT%\%%s\.env.example" "%ROOT%\%%s\.env" > nul
                echo   [%%s] .env 생성 완료
            )
        ) else (
            echo   [%%s] .env 이미 존재
        )
    ) else (
        echo   [경고] 폴더 없음: %%s
    )
)
echo.


:: mcp-config.json 자동 생성 (실제 설치 경로 반영)
echo ----------------------------------------------------------------
echo mcp-config.json 생성 중...
echo ----------------------------------------------------------------
(
echo {
echo   "mcpServers": {
echo     "korail-convenience": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-convenience\\server.py"]
echo     },
echo     "korail-stats": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-stats\\server.py"]
echo     },
echo     "korail-train-ops": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-train-ops\\server.py"]
echo     },
echo     "korail-codebook": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-codebook\\server.py"]
echo     },
echo     "korail-freight": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-freight\\server.py"]
echo     },
echo     "korail-network": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-network\\server.py"]
echo     },
echo     "korail-rolling-stock": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-rolling-stock\\server.py"]
echo     },
echo     "korail-voc-cs": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-voc-cs\\server.py"]
echo     },
echo     "korail-internal-svc": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-internal-svc\\server.py"]
echo     },
echo     "korail-procurement": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-procurement\\server.py"]
echo     },
echo     "korail-urban-rail": {
echo       "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo       "args": ["%ROOT:\=\\%\\m-urban-rail\\server.py"]
echo     }
echo   }
echo }
) > "%ROOT%\mcp-config.json"
echo   mcp-config.json 생성 완료: %ROOT%\mcp-config.json
echo.

:: MCP 서버 설정 출력 (클라이언트 공통)
echo ================================================================
echo   MCP 서버 설정 (Claude Desktop / Cursor / Antigravity 공통)
echo ================================================================
echo.
echo 아래 11개 서버 블록을 사용하는 클라이언트의 mcpServers 안에 넣으세요.
echo (어떤 클라이언트든 형식은 동일하며, 설정 파일 위치만 다릅니다.)
echo.
echo 클라이언트별 설정 파일 위치와 자세한 방법은 README.md 의
echo "클라이언트 연결" 섹션을 참고하세요.
echo.
echo ----------------------------------------------------------------
echo.
echo "korail-convenience": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-convenience\\server.py"]
echo },
echo "korail-stats": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-stats\\server.py"]
echo },
echo "korail-train-ops": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-train-ops\\server.py"]
echo },
echo "korail-codebook": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-codebook\\server.py"]
echo },
echo "korail-freight": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-freight\\server.py"]
echo },
echo "korail-network": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-network\\server.py"]
echo },
echo "korail-rolling-stock": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-rolling-stock\\server.py"]
echo },
echo "korail-voc-cs": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-voc-cs\\server.py"]
echo },
echo "korail-internal-svc": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-internal-svc\\server.py"]
echo },
echo "korail-procurement": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-procurement\\server.py"]
echo },
echo "korail-urban-rail": {
echo   "command": "%ROOT:\=\\%\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-urban-rail\\server.py"]
echo }
echo.
echo ----------------------------------------------------------------
echo.
echo ================================================================
echo   [OK] 설치 완료! (11개 서버 · 98개 도구)
echo ================================================================
echo.
echo [i] API 키 입력 불필요 - 프록시 서버가 대신 처리합니다.
echo   .env 파일에 프록시 URL이 자동으로 기입되었습니다.
echo.
echo 다음 단계:
echo   1. 사용하는 클라이언트(Claude Desktop / Cursor / Antigravity 등)의
echo      설정 파일에 위 서버 블록을 추가  (위치는 README.md 참고)
echo   2. 해당 클라이언트 재시작
echo.
pause
