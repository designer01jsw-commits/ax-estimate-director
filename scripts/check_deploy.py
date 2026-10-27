# -*- coding: utf-8 -*-
import urllib.request
import time

url = "https://ax-estimate-director.onrender.com"
print("Probing production URL:", url)

for i in range(12):
    try:
        t0 = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            print(f"[{i+1}/12] Status: {resp.status}, Latency: {time.time()-t0:.2f}s, Content length: {len(content)}")
    except Exception as e:
        print(f"[{i+1}/12] Error: {e}")
    time.sleep(5)
