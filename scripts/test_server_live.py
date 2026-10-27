# -*- coding: utf-8 -*-
"""Test local streamlit startup and verify HTTP 200."""

import subprocess
import time
import urllib.request
import sys

print("Starting Streamlit process on port 8598...")
proc = subprocess.Popen(
    [
        r"C:\Users\ws081\AppData\Local\Programs\Python\Python311\python.exe",
        "-m", "streamlit", "run", "app.py",
        "--server.port", "8598",
        "--server.headless", "true"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

try:
    print("Waiting 5 seconds for server to start...")
    time.sleep(5)
    
    url = "http://localhost:8598"
    req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        status = resp.status
        body = resp.read().decode("utf-8", errors="ignore")
        print(f"HTTP Status: {status}")
        assert status == 200, f"Expected 200, got {status}"
        assert "제일기획 AX 견적감독관" in body or "Streamlit" in body, "Expected title in HTML"
        print("PASS: Streamlit app started and responded with HTTP 200!")
finally:
    print("Terminating server...")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("Server terminated cleanly.")
