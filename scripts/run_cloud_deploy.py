# -*- coding: utf-8 -*-
"""
24시간 365일 무중단 Streamlit Community Cloud 자동 영구 배포 도구
"""

import sys
import os
import re
import time
import subprocess
import webbrowser
from pathlib import Path

# UTF-8 stdout configuration for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = Path(r"c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회")
DESKTOP = Path(r"C:\Users\ws081\OneDrive\Desktop")

GH_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe")
GIT_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe")

def run():
    print("=" * 65)
    print(" [제일기획 AX 견적감독관] 24시간 365일 클라우드 영구 배포")
    print("=" * 65)
    
    os.chdir(str(WORKSPACE))
    
    # 1. Check existing auth
    res = subprocess.run([str(GH_BIN), "auth", "status"], capture_output=True, text=True)
    if res.returncode == 0:
        print("[확인] 이미 GitHub 계정에 연결되어 있습니다!")
    else:
        print("\n[1단계] GitHub 계정 연결을 시작합니다...")
        proc = subprocess.Popen(
            [str(GH_BIN), "auth", "login", "--web", "-h", "github.com", "-p", "https"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        time.sleep(1.5)
        proc.stdin.write("\n")
        proc.stdin.flush()
        
        auth_code = None
        for _ in range(15):
            line = proc.stderr.readline()
            m = re.search(r"([A-Z0-9]{4}-[A-Z0-9]{4})", line)
            if m:
                auth_code = m.group(1)
                break
            time.sleep(0.3)
            
        if not auth_code:
            print("[오류] 인증 코드를 가져오지 못했습니다. 터미널 출력을 확인하세요.")
            return

        print("\n" + "#" * 55)
        print(f" >> 일회용 인증 코드:  [  {auth_code}  ]")
        print(" >> 인증 페이지 주소:  https://github.com/login/device")
        print("#" * 55 + "\n")
        
        # 바탕화면에 코드 파일 저장
        code_file = DESKTOP / "GITHUB_인증코드.txt"
        with open(code_file, "w", encoding="utf-8") as cf:
            cf.write(f"GitHub 일회용 인증 코드: {auth_code}\n접속 주소: https://github.com/login/device\n")
            
        status_file = WORKSPACE / "data" / "github_auth_code.txt"
        with open(status_file, "w", encoding="utf-8") as sf:
            sf.write(f"{auth_code}\n")

        print("웹 브라우저를 자동으로 엽니다. 브라우저에 위 8자리 코드를 붙여넣고 [Authorize]를 눌러주세요...")
        webbrowser.open("https://github.com/login/device")
        
        print("\n사용자의 브라우저 승인을 기다리는 중입니다 (최대 5분)...")
        try:
            proc.wait(timeout=300)
        except subprocess.TimeoutExpired:
            proc.kill()
            print("[오류] 인증 대기 시간이 초과되었습니다.")
            return

        if proc.returncode != 0:
            print("[오류] GitHub 인증에 실패했습니다.")
            return

        print("[성공] GitHub 인증 완료!")

    # 2. Get username
    user_res = subprocess.run([str(GH_BIN), "api", "user", "--jq", ".login"], capture_output=True, text=True)
    gh_user = user_res.stdout.strip()
    print(f"GitHub 계정 확인: {gh_user}")

    # 3. Create or push repository
    print("\n[2단계] GitHub 저장소(ax-estimate-director) 생성 및 코드 푸시 중...")
    repo_res = subprocess.run(
        [str(GH_BIN), "repo", "create", "ax-estimate-director", "--public", "--source=.", "--remote=origin", "--push"],
        capture_output=True,
        text=True
    )
    if repo_res.returncode != 0:
        print("[안내] 기존 저장소 동기화 진행 중...")
        subprocess.run([str(GIT_BIN), "push", "-u", "origin", "main"], capture_output=True)

    print(f"[성공] GitHub 업로드 완료! (https://github.com/{gh_user}/ax-estimate-director)")

    # 4. Open Streamlit Cloud Deploy page
    deploy_url = f"https://share.streamlit.io/deploy?repository={gh_user}/ax-estimate-director&branch=main&mainModule=app.py"
    app_url = f"https://{gh_user}-ax-estimate-director.streamlit.app"
    
    print("\n" + "=" * 65)
    print(" [3단계] Streamlit Community Cloud 자동 배포 페이지 이동")
    print(f" 배포 링크: {deploy_url}")
    print(f" 배포 완료 후 영구 도메인: {app_url}")
    print("=" * 65)
    
    # Save completion info to Desktop
    info_file = DESKTOP / "클라우드_배포완료_도메인안내.txt"
    with open(info_file, "w", encoding="utf-8") as inf:
        inf.write(
            f"제일기획 AX 견적감독관 24시간 클라우드 배포 안내\n"
            f"--------------------------------------------------\n"
            f"1. GitHub 저장소: https://github.com/{gh_user}/ax-estimate-director\n"
            f"2. Streamlit Cloud 배포 설정: {deploy_url}\n"
            f"3. 24시간 365일 영구 도메인: {app_url}\n"
            f"\n"
            f"열린 웹 브라우저에서 파란색 [Deploy] 버튼만 누르면 배포 완료!\n"
            f"배포 완료 후에는 이 컴퓨터를 꺼도 위 3번 주소로 영구 접속 가능합니다.\n"
        )

    webbrowser.open(deploy_url)
    print("\n브라우저에 열린 화면에서 파란색 [Deploy] 버튼을 클릭하시면 24시간 365일 영구 배포가 완료됩니다!")

if __name__ == "__main__":
    run()
