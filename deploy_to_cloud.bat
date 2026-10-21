@echo off
chcp 65001 > nul
echo ====================================================================
echo  [제일기획 AX 견적감독관] 24시간 클라우드 영구 배포 원클릭 도구
echo ====================================================================
echo.
echo [1단계] GitHub 계정 연결 상태 확인 중...
"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" auth status
if %errorlevel% neq 0 (
    echo.
    echo 🔑 GitHub 로그인이 필요합니다.
    echo 엔터를 누르면 웹 브라우저와 인증 코드가 화면에 나타납니다.
    echo.
    pause
    "C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" auth login --web -h github.com -p https -w
)
echo.
echo [2단계] GitHub 저장소(ax-estimate-director) 자동 생성 및 코드 푸시 중...
"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" repo create ax-estimate-director --public --source=. --remote=origin --push
if %errorlevel% neq 0 (
    echo [안내] 저장소 동기화 중...
    "C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe" push -u origin main
)
echo.
echo [3단계] GitHub 사용자 계정 확인 및 Streamlit Cloud 자동 배포 페이지 연결...
for /f "tokens=*" %%i in (\'"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" api user --jq .login\') do set GH_USER=%%i
if defined GH_USER (
    echo.
    echo ====================================================================
    echo  ✅ GitHub 업로드 성공! 사용자 계정: %GH_USER%
    echo  🌐 24시간 상시 가동 Streamlit Cloud 배포 페이지로 자동 이동합니다...
    echo ====================================================================
    start https://share.streamlit.io/deploy?repository=%GH_USER%/ax-estimate-director^&branch=main^&mainModule=app.py
) else (
    echo.
    start https://share.streamlit.io/
)
echo.
echo [배포 완료 안내]
echo 열린 Streamlit Cloud 웹 화면에서 파란색 [Deploy] 버튼만 누르면 배포 완료!
echo 배포가 끝나면 이 컴퓨터를 꺼도 24시간 365일 어디서나 영구 접속 가능합니다!
echo.
pause
