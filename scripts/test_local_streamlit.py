# -*- coding: utf-8 -*-
import subprocess
import time
import urllib.request
import sys

proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8599", "--server.headless", "true"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(5)

try:
    with urllib.request.urlopen("http://localhost:8599/_stcore/health", timeout=5) as res:
        print("Health status:", res.status)
    with urllib.request.urlopen("http://localhost:8599/", timeout=5) as res:
        print("Root status:", res.status)
        content = res.read().decode("utf-8")
        print("HTML content length:", len(content))
except Exception as e:
    print("Local request error:", e)

proc.terminate()
stdout, stderr = proc.communicate(timeout=5)
print("--- STDOUT ---")
print(stdout[:500])
print("--- STDERR ---")
print(stderr[:1000])
