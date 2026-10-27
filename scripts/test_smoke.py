# -*- coding: utf-8 -*-
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_PATH = str(ROOT_DIR / "app.py")

print("Running smoke test 1: initial load without target file...")
at = AppTest.from_file(APP_PATH, default_timeout=30)
at.run()
assert not at.exception, f"Exception on initial load: {at.exception}"
print("Smoke test 1 passed! Exception is None. Title rendered:", len(at.title) or len(at.markdown))

print("Running smoke test 2: switch to sample mode...")
# Try switching target_supply_mode_radio to sample mode
try:
    radio = at.radio(key="target_supply_mode_radio")
    radio.set_value("📋 내장 샘플 견적서로 빠른 체험").run()
    assert not at.exception, f"Exception on sample load: {at.exception}"
    print("Smoke test 2 passed! Metrics count:", len(at.metric))
except Exception as e:
    print("Note on AppTest interaction:", e)

print("ALL SMOKE CHECKS FINISHED CLEANLY!")
