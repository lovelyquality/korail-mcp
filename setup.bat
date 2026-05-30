@echo off
chcp 65001 > nul
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
set SERVERS=m-convenience m-stats m-train-ops m-codebook m-carriage m-freight m-network m-rolling-stock m-voc-cs m-internal-svc m-procurement m-urban-rail m-rail-infra

:: 각 서버 설치
echo ----------------------------------------------------------------
echo 가상환경 및 패키지 설치 중...
echo ----------------------------------------------------------------
echo.

for %%s in (%SERVERS%) do (
    echo [%%s] 설치 중...
    if exist "%ROOT%\%%s" (
        if not exist "%ROOT%\%%s\venv" (
            python -m venv "%ROOT%\%%s\venv" > nul 2>&1
            if errorlevel 1 (
                echo   [오류] 가상환경 생성 실패
            ) else (
                echo   가상환경 생성 완료
            )
        ) else (
            echo   가상환경 이미 존재
        )

        if exist "%ROOT%\%%s\requirements.txt" (
            "%ROOT%\%%s\venv\Scripts\pip.exe" install -r "%ROOT%\%%s\requirements.txt" -q
            if errorlevel 1 (
                echo   [오류] 패키지 설치 실패
            ) else (
                echo   패키지 설치 완료
            )
        )

        if not exist "%ROOT%\%%s\.env" (
            if exist "%ROOT%\%%s\.env.example" (
                copy "%ROOT%\%%s\.env.example" "%ROOT%\%%s\.env" > nul
                echo   .env 파일 생성 완료
            )
        ) else (
            echo   .env 파일 이미 존재
        )
    ) else (
        echo   [경고] 폴더 없음: %%s
    )
    echo.
)

:: API 키 입력 스크립트 생성
echo ----------------------------------------------------------------
echo API 키 입력 스크립트 생성 중...
echo ----------------------------------------------------------------

(
    echo @echo off
    echo chcp 65001 ^> nul
    echo.
    echo set /p "APIKEY=data.go.kr API 키를 입력하세요: "
    echo.
    for %%s in (%SERVERS%) do (
        echo if exist "%ROOT%\%%s\.env" ^(
        echo     echo DATA_GO_KR_API_KEY=!APIKEY! ^> "%ROOT%\%%s\.env"
        echo     echo [%%s] API 키 저장 완료
        echo ^)
    )
    echo.
    echo echo.
    echo echo 모든 서버에 API 키 저장 완료^^!
    echo pause
) > "%ROOT%\set_api_key.bat"

echo set_api_key.bat 생성 완료
echo.

:: Claude Desktop 설정 출력
echo ================================================================
echo   Claude Desktop 설정
echo ================================================================
echo.
echo 아래 내용을 Claude Desktop 설정 파일에 추가하세요.
echo.
echo 설정 파일 위치:
echo   %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo ----------------------------------------------------------------
echo.
echo "korail-convenience": {
echo   "command": "%ROOT:\=\\%\\m-convenience\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-convenience\\server.py"]
echo },
echo "korail-stats": {
echo   "command": "%ROOT:\=\\%\\m-stats\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-stats\\server.py"]
echo },
echo "korail-train-ops": {
echo   "command": "%ROOT:\=\\%\\m-train-ops\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-train-ops\\server.py"]
echo },
echo "korail-codebook": {
echo   "command": "%ROOT:\=\\%\\m-codebook\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-codebook\\server.py"]
echo },
echo "korail-carriage": {
echo   "command": "%ROOT:\=\\%\\m-carriage\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-carriage\\server.py"]
echo },
echo "korail-freight": {
echo   "command": "%ROOT:\=\\%\\m-freight\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-freight\\server.py"]
echo },
echo "korail-network": {
echo   "command": "%ROOT:\=\\%\\m-network\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-network\\server.py"]
echo },
echo "korail-rolling-stock": {
echo   "command": "%ROOT:\=\\%\\m-rolling-stock\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-rolling-stock\\server.py"]
echo },
echo "korail-voc-cs": {
echo   "command": "%ROOT:\=\\%\\m-voc-cs\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-voc-cs\\server.py"]
echo },
echo "korail-internal-svc": {
echo   "command": "%ROOT:\=\\%\\m-internal-svc\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-internal-svc\\server.py"]
echo },
echo "korail-procurement": {
echo   "command": "%ROOT:\=\\%\\m-procurement\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-procurement\\server.py"]
echo },
echo "korail-urban-rail": {
echo   "command": "%ROOT:\=\\%\\m-urban-rail\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-urban-rail\\server.py"]
echo },
echo "korail-rail-infra": {
echo   "command": "%ROOT:\=\\%\\m-rail-infra\\venv\\Scripts\\python.exe",
echo   "args": ["%ROOT:\=\\%\\m-rail-infra\\server.py"]
echo }
echo.
echo ----------------------------------------------------------------
echo.
echo ================================================================
echo   설치 완료!
echo ================================================================
echo.
echo 다음 단계:
echo   1. set_api_key.bat 를 더블클릭하여 API 키 입력
echo   2. 위 설정을 Claude Desktop 설정 파일에 추가
echo   3. Claude Desktop 재시작
echo.
pause
