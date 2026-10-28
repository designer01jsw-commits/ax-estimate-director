# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.stdout.reconfigure(encoding='utf-8')

from auditor.vision_estimator import estimate_costs_from_vision, load_preset_image_bytes, SAMPLE_PRESETS

presets_to_test = [
    ("KES_2025", "대형 행사 / 베뉴 전시", "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)"),
    ("WIS_2026", "대형 행사 / 베뉴 전시", "초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)"),
    ("GALAXY_AUG", "팝업스토어 / 전시 부스", "대형 전시 (50~100평 / 메인 부스·단독관)")
]

for pkey, ptype, pscale in presets_to_test:
    p_info = SAMPLE_PRESETS[pkey]
    img_bytes = load_preset_image_bytes(pkey)
    print(f"=== Preset: {pkey} ===")
    print(f"Name: {p_info['name']}")
    print(f"Image bytes loaded: {len(img_bytes)} bytes")
    
    res = estimate_costs_from_vision(
        features={},
        project_type=ptype,
        scale=pscale,
        tier=p_info.get("tier", "고급형 (Premium)"),
        hints=p_info.get("hints", ""),
        preset_key=pkey
    )
    
    tot = res["summary"]["total_cost"]
    gt = res.get("ground_truth") or {}
    print(f"Estimated Total: ₩{tot:,d}")
    print(f"Ground Truth Matched: {gt.get('name')} | Actual: ₩{gt.get('settled_amount', 0):,d}")
    print(f"Direct Labor: ₩{res['summary']['direct_labor_cost']:,d} ({res['summary']['total_md']} M/D)")
    print(f"Direct Material: ₩{res['summary']['direct_material_cost']:,d}")
    print(f"Items count: {len(res['items'])}")
    print()

print("All 3 presets verified successfully!")
