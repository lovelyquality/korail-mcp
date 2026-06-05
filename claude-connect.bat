@echo off
chcp 949 > nul
title KORAIL MCP - Claude Desktop 연결

echo.
echo ===========================================================
echo  KORAIL MCP - Claude Desktop 설정 도우미
echo ===========================================================
echo.

:: APPDATA 미정의 환경 대비 - USERPROFILE 기반 fallback
if defined APPDATA (
    set CLAUDE_DIR=%APPDATA%\Claude
) else (
    set CLAUDE_DIR=%USERPROFILE%\AppData\Roaming\Claude
)

echo [*] Claude 설정 폴더: %CLAUDE_DIR%
echo.

:: 폴더 없으면 자동 생성
if not exist "%CLAUDE_DIR%\" (
    echo [*] 폴더가 없습니다. 자동으로 생성합니다...
    mkdir "%CLAUDE_DIR%"
    if errorlevel 1 (
        echo.
        echo [!] 폴더 생성에 실패했습니다.
        echo     아래 경로를 탐색기에서 직접 만든 뒤 다시 실행하세요:
        echo     %CLAUDE_DIR%
        echo.
        pause & exit /b 1
    )
    echo [+] 폴더 생성 완료.
    echo.
)

:: 원본 확인
set SRC=%~dp0mcp-config.json
set DST=%CLAUDE_DIR%\claude_desktop_config.json

if not exist "%SRC%" (
    echo [!] mcp-config.json 이 없습니다. setup.bat 을 먼저 실행하세요.
    pause & exit /b 1
)

:: 기존 설정 파일 백업
if exist "%DST%" (
    echo [*] 기존 설정 파일 발견. 백업합니다...
    copy /y "%DST%" "%DST%.bak" > nul
    echo [+] 백업 완료: claude_desktop_config.json.bak
    echo.
)

:: 복사
copy /y "%SRC%" "%DST%" > nul
if errorlevel 1 (
    echo.
    echo [!] 파일 복사에 실패했습니다.
    echo     Claude Desktop 이 실행 중이면 완전히 종료한 뒤 다시 시도하세요.
    echo     (트레이 아이콘 우클릭 -^> Quit / 종료)
    echo.
    pause & exit /b 1
)

echo [+] 설정 파일 복사 완료!
echo.
echo ===========================================================
echo  [필수] Claude Desktop 을 완전히 껐다가 다시 켜세요
echo.
echo   작업표시줄 오른쪽 끝 ^ (숨겨진 아이콘) 안에
echo   Claude 아이콘이 있으면 우클릭 -^> Quit / 종료
echo   그 후 Claude Desktop 을 다시 실행하세요.
echo.
echo   채팅창 우측 하단에 망치(도구) 아이콘이 보이면 성공!
echo ===========================================================
echo.
pause