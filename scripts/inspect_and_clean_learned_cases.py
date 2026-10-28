# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

CASES_FILE = Path("data/learned_cases.json")
if not CASES_FILE.exists():
    print("No learned_cases.json")
    sys.exit(0)

with open(CASES_FILE, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Total entries before clean: {len(cases)}")

# Deduplicate based on name and kit_id/case_id
seen = set()
cleaned = []
for c in cases:
    # Key based on name or kit_id
    kid = c.get("kit_id")
    name = c.get("name")
    key = kid if kid else name
    if key and key not in seen:
        seen.add(key)
        cleaned.append(c)

print(f"Total unique entries after clean: {len(cleaned)}")
for c in cleaned[:15]:
    cid = c.get("case_id") or c.get("kit_id")
    print(f"  [{cid}] {c.get('name')} | {c.get('settled_amount')}")
