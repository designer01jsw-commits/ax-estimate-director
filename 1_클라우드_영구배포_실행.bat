@echo off
chcp 65001 > nul
title 제일기획 AX 견적감독관 - 24시간 클라우드 영구 배포
color 0B
cd /d "c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회"

set "GH=C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe"
set "GIT=C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"

cls
echo ===============================================================================
echo   🚀 [제일기획 AX 견적감독관] 24시간 365일 클라우드 영구 배포 가이드
echo ===============================================================================
echo.
echo   [1단계] GitHub 계정 연결을 시작합니다.
echo.
echo   ★ 아래에 바로 영문+숫자 8자리 【 일회용 인증코드 】가 나타납니다!
echo      (예: ! First copy your one-time code: 12AB-34CD)
echo.
echo   ★ 코드를 확인하고 키보드의 [Enter]를 누르면 브라우저가 자동으로 열립니다.
echo      (코드는 이미 클립보드에 자동 복사되어 있으므로 브라우저에서 Ctrl+V 하시면 됩니다)
echo.
echo ===============================================================================
echo.

"%GH%" auth login --web -h github.com -p https

if %errorlevel% neq 0 (
    echo.
    echo ❌ GitHub 로그인에 실패했습니다. 창을 닫고 다시 실행해 주세요.
    pause
    exit /b
)

cls
echo ===============================================================================
echo   🎉 GitHub 계정 인증 성공!
echo ===============================================================================
echo.
echo   [2단계] GitHub에 클라우드 배포용 저장소(ax-estimate-director)를 만들고
echo           견적감독관 소스코드와 44개 키트 백데이터를 업로드합니다...
echo.

"%GH%" repo create ax-estimate-director --public --source=. --remote=origin --push

if %errorlevel% neq 0 (
    echo [안내] 기존 저장소에 최신 코드를 푸시합니다...
    "%GIT%" push -u origin main
)

for /f "tokens=*" %%i in ('"%GH%" api user --jq .login') do set "GH_USER=%%i"

cls
echo ===============================================================================
echo   ✅ 모든 코드와 데이터가 GitHub에 업로드되었습니다!
echo   👤 내 GitHub 계정: %GH_USER%
echo ===============================================================================
echo.
echo   [3단계] Streamlit Community Cloud 배포 화면으로 이동합니다.
echo.
echo   잠시 후 웹 브라우저가 열리면,
echo   화면 우측 하단의 파란색 【 Deploy 】 버튼만 누르시면 끝납니다!
echo.
echo   🌟 영구 도메인 주소: https://%GH_USER%-ax-estimate-director.streamlit.app
echo   (배포 완료 후에는 이 컴퓨터를 꺼도 24시간 365일 어디서나 접속 가능합니다!)
echo.
echo ===============================================================================

start https://share.streamlit.io/deploy?repository=%GH_USER%/ax-estimate-director^&branch=main^&mainModule=app.py

echo.
pause
