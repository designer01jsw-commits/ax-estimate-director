# -*- coding: utf-8 -*-
import urllib.request
import re

url = "https://ax-estimate-director.onrender.com"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
with urllib.request.urlopen(req, timeout=15) as res:
    html = res.read().decode("utf-8")

print("Main page status: 200 OK, length:", len(html))

# Find script src and link href
scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
links = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html)

all_assets = scripts + links
print(f"Found {len(all_assets)} linked assets in HTML")

failures = []
for asset in all_assets:
    asset_url = asset if asset.startswith("http") else (url + "/" + asset.lstrip("/"))
    try:
        a_req = urllib.request.Request(asset_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(a_req, timeout=10) as a_res:
            pass
    except Exception as e:
        failures.append((asset_url, str(e)))

if failures:
    print("FAILED ASSETS:", failures)
else:
    print("ALL assets loaded successfully with 200 OK!")
