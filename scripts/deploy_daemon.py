# -*- coding: utf-8 -*-
"""
GitHub Device Login & 자동 레포지토리 푸시 데몬 스크립트
"""

import sys
import os
import re
import time
import subprocess
import webbrowser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

WORKSPACE = Path(r"c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회")
DESKTOP = Path(r"C:\Users\ws081\OneDrive\Desktop")

GH_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe")
GIT_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe")

def run():
    os.chdir(str(WORKSPACE))
    
    # Start gh auth login
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
    for _ in range(20):
        line = proc.stderr.readline()
        m = re.search(r"([A-Z0-9]{4}-[A-Z0-9]{4})", line)
        if m:
            auth_code = m.group(1)
            break
        time.sleep(0.3)

    if not auth_code:
        print("[오류] 인증 코드를 가져오지 못했습니다.")
        return

    # Write auth code to file
    with open(WORKSPACE / "data" / "active_auth_code.txt", "w", encoding="utf-8") as f:
        f.write(auth_code)

    with open(DESKTOP / "GITHUB_인증코드.txt", "w", encoding="utf-8") as f:
        f.write(f"GitHub 인증코드: {auth_code}\n입력주소: https://github.com/login/device\n")

    print(f"ACTIVE_CODE:{auth_code}")
    sys.stdout.flush()

    # Open device login page
    webbrowser.open("https://github.com/login/device")

    # Wait for up to 10 minutes (600 seconds)
    try:
        proc.wait(timeout=600)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("[시간초과] 인증이 완료되지 않았습니다.")
        return

    if proc.returncode != 0:
        print("[오류] 인증 실패.")
        return

    # Authenticated!
    user_res = subprocess.run([str(GH_BIN), "api", "user", "--jq", ".login"], capture_output=True, text=True)
    gh_user = user_res.stdout.strip() or "designer01jsw-commits"
    print(f"USER:{gh_user}")

    # Create & Push repository
    subprocess.run(
        [str(GH_BIN), "repo", "create", "ax-estimate-director", "--public", "--source=.", "--remote=origin", "--push"],
        capture_output=True,
        text=True
    )
    subprocess.run([str(GIT_BIN), "push", "-u", "origin", "main"], capture_output=True)

    deploy_url = f"https://share.streamlit.io/deploy?repository={gh_user}/ax-estimate-director&branch=main&mainModule=app.py"
    app_url = f"https://{gh_user}-ax-estimate-director.streamlit.app"

    # Save finished file
    finish_content = f"GH_USER={gh_user}\nDEPLOY_URL={deploy_url}\nAPP_URL={app_url}\n"
    with open(WORKSPACE / "data" / "deploy_finished.txt", "w", encoding="utf-8") as f:
        f.write(finish_content)

    print(f"FINISHED:{deploy_url}")
    webbrowser.open(deploy_url)

if __name__ == "__main__":
    run()
