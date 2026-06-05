@echo off
chcp 949 > nul
title KORAIL MCP - Grok 연결 도우미

echo.
echo ===========================================================
echo  KORAIL MCP - Grok 연결 도우미  v1.0
echo  Cloudflare Tunnel + SSE 로 공개 URL 을 자동 발급합니다
echo ===========================================================
echo.

:: --- cloudflared 확인 / 자동 다운로드 ---
set CF=%~dp0cloudflared.exe
if not exist "%CF%" (
    where cloudflared >nul 2>&1
    if %errorlevel% equ 0 (
        set CF=cloudflared
    ) else (
        echo [*] cloudflared.exe 자동 다운로드 중... (약 30~60초 소요)
        powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CF%'"
        if not exist "%CF%" (
            echo.
            echo [!] 다운로드 실패. 인터넷 연결을 확인하고 다시 실행하세요.
            pause & exit /b 1
        )
        echo [+] cloudflared.exe 다운로드 완료.
        echo.
    )
)

:: --- 서버 선택 ---
echo  연결할 서버를 선택하세요 (번호 입력):
echo.
echo   [1]  m-codebook      - 역코드 / 노선 코드북
echo   [2]  m-convenience   - 역사 편의시설 / 접근성
echo   [3]  m-freight       - 화물 / 컨테이너 / 물류
echo   [4]  m-internal-svc  - 임대매장 / 사회공헌 / 인사
echo   [5]  m-network       - 노선망 / 운행거리 / 운임
echo   [6]  m-procurement   - 조달 / 자재 정보
echo   [7]  m-rolling-stock - 철도차량 현황 / 제원
echo   [8]  m-stats         - 여객 / 화물 수송 통계
echo   [9]  m-train-ops     - 열차 운행계획 / 이력
echo   [10] m-urban-rail    - 도시철도 역사 시설
echo   [11] m-voc-cs        - VOC / 고객만족 / 정보공개
echo.
set /p CHOICE="번호 선택 (1-11): "

if "%CHOICE%"=="1"  set SV=m-codebook
if "%CHOICE%"=="2"  set SV=m-convenience
if "%CHOICE%"=="3"  set SV=m-freight
if "%CHOICE%"=="4"  set SV=m-internal-svc
if "%CHOICE%"=="5"  set SV=m-network
if "%CHOICE%"=="6"  set SV=m-procurement
if "%CHOICE%"=="7"  set SV=m-rolling-stock
if "%CHOICE%"=="8"  set SV=m-stats
if "%CHOICE%"=="9"  set SV=m-train-ops
if "%CHOICE%"=="10" set SV=m-urban-rail
if "%CHOICE%"=="11" set SV=m-voc-cs

if not defined SV (
    echo.
    echo [!] 잘못된 번호입니다. 다시 실행하세요.
    pause & exit /b 1
)

set PORT=8008
set PY=%~dp0%SV%\venv\Scripts\python.exe
set SC=%~dp0%SV%\server.py

if not exist "%PY%" (
    echo.
    echo [!] %SV% 의 가상환경이 없습니다. setup.bat 을 먼저 실행하세요.
    pause & exit /b 1
)

echo.
echo [*] %SV% 서버를 SSE 모드 (포트 %PORT%) 로 시작합니다...
start "KORAIL-%SV%" /min "%PY%" "%SC%" --transport sse --port %PORT%
timeout /t 3 /nobreak > nul

echo [*] Cloudflare Tunnel 을 열어 공개 HTTPS URL 을 발급합니다...
echo     (URL 이 나타나기까지 10~20초 걸릴 수 있습니다)
echo.
echo ===========================================================
echo  [Grok 연결 방법]
echo  1. 아래에서 https://xxxx.trycloudflare.com 형태의 URL 확인
echo  2. 끝에 /sse 를 붙여서 복사:
echo     예) https://abc-def-123.trycloudflare.com/sse
echo  3. grok.com/connectors -^> New Connector -^> Custom -^> 붙여넣기
echo  *** 이 창을 닫으면 Grok 연결이 끊깁니다 ***
echo ===========================================================
echo.

"%CF%" tunnel --url http://localhost:%PORT%

echo.
pause