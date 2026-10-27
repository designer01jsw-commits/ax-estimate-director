# -*- coding: utf-8 -*-
import re

with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

fs_pat = re.compile(r'font-size:\s*([^;!\"\'\n]+)')
sizes_found = set()
for idx, l in enumerate(lines):
    matches = fs_pat.findall(l)
    if matches:
        for m in matches:
            sizes_found.add(m.strip())
        print(f"Line {idx+1}: {matches}")

print("\n--- Unique font-size values in app.py ---")
print(sorted(sizes_found))
