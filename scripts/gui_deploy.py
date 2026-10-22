# -*- coding: utf-8 -*-
"""
사용자 화면에 직접 인증코드를 팝업창으로 띄워주는 24시간 클라우드 영구 배포 도구
"""

import sys
import os
import re
import time
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk
from pathlib import Path

WORKSPACE = Path(r"c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회")
DESKTOP = Path(r"C:\Users\ws081\OneDrive\Desktop")

GH_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe")
GIT_BIN = Path(r"C:\Users\ws081\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe")

def run():
    os.chdir(str(WORKSPACE))

    # 1. Start gh auth login process
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
    for _ in range(25):
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

    # Open device login page
    webbrowser.open("https://github.com/login/device")

    # Background worker to wait for auth & push
    def wait_and_deploy():
        try:
            proc.wait(timeout=600)
        except subprocess.TimeoutExpired:
            proc.kill()
            return

        if proc.returncode == 0:
            user_res = subprocess.run([str(GH_BIN), "api", "user", "--jq", ".login"], capture_output=True, text=True)
            gh_user = user_res.stdout.strip() or "designer01jsw-commits"

            # Create & Push repository
            subprocess.run(
                [str(GH_BIN), "repo", "create", "ax-estimate-director", "--public", "--source=.", "--remote=origin", "--push"],
                capture_output=True,
                text=True
            )
            subprocess.run([str(GIT_BIN), "push", "-u", "origin", "main"], capture_output=True)

            deploy_url = f"https://share.streamlit.io/deploy?repository={gh_user}/ax-estimate-director&branch=main&mainModule=app.py"
            app_url = f"https://{gh_user}-ax-estimate-director.streamlit.app"

            finish_content = f"GH_USER={gh_user}\nDEPLOY_URL={deploy_url}\nAPP_URL={app_url}\n"
            with open(WORKSPACE / "data" / "deploy_finished.txt", "w", encoding="utf-8") as f:
                f.write(finish_content)

            webbrowser.open(deploy_url)

            # Close GUI
            try:
                root.after(500, root.destroy)
            except Exception:
                pass

    t = threading.Thread(target=wait_and_deploy, daemon=True)
    t.start()

    # 2. GUI Window
    root = tk.Tk()
    root.title("제일기획 AX 견적감독관 - 24시간 클라우드 배포")
    root.geometry("560x360")
    root.configure(bg="#0B132B")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    # Copy code to clipboard
    root.clipboard_clear()
    root.clipboard_append(auth_code)

    lbl_title = tk.Label(
        root,
        text="🚀 24시간 365일 클라우드 영구 배포",
        font=("Malgun Gothic", 16, "bold"),
        fg="#00E5FF",
        bg="#0B132B"
    )
    lbl_title.pack(pady=(20, 5))

    lbl_sub = tk.Label(
        root,
        text="컴퓨터 전원이 꺼져 있어도 접속되는 영구 도메인을 생성합니다.",
        font=("Malgun Gothic", 10),
        fg="#94A3B8",
        bg="#0B132B"
    )
    lbl_sub.pack(pady=(0, 15))

    frame_box = tk.Frame(root, bg="#1E293B", padx=20, pady=15, relief="ridge", bd=2)
    frame_box.pack(pady=5, padx=30, fill="x")

    lbl_code_title = tk.Label(
        frame_box,
        text="▼ 브라우저에 입력할 일회용 8자리 인증코드 (클립보드 자동복사 완료) ▼",
        font=("Malgun Gothic", 9, "bold"),
        fg="#38BDF8",
        bg="#1E293B"
    )
    lbl_code_title.pack()

    lbl_code = tk.Label(
        frame_box,
        text=auth_code,
        font=("Consolas", 32, "bold"),
        fg="#FEF08A",
        bg="#1E293B",
        cursor="hand2"
    )
    lbl_code.pack(pady=5)

    lbl_tip = tk.Label(
        root,
        text="열린 브라우저 창의 빈칸에 Ctrl+V (붙여넣기) 후 [Authorize]를 누르시면\n알아서 소스코드가 업로드되고 Streamlit Cloud 배포창이 열립니다!",
        font=("Malgun Gothic", 10),
        fg="#F8FAFC",
        bg="#0B132B",
        justify="center"
    )
    lbl_tip.pack(pady=10)

    btn_open = tk.Button(
        root,
        text="🌐 GitHub 승인 페이지 다시 열기",
        font=("Malgun Gothic", 10, "bold"),
        bg="#0284C7",
        fg="white",
        activebackground="#0369A1",
        activeforeground="white",
        relief="flat",
        padx=15,
        pady=6,
        cursor="hand2",
        command=lambda: webbrowser.open("https://github.com/login/device")
    )
    btn_open.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    run()
