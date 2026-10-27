# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from auditor.learning_engine import study_and_assetize_excel_estimate
from auditor.projects import load_projects

# Test assetizing a sample confirmed file
sample_file = Path("data/samples/전시 광고주컨펌완료 견적서 (1).xlsx")
file_bytes = sample_file.read_bytes()

print("Studying client confirmed estimate...")
proj_rec, decomp, items = study_and_assetize_excel_estimate(
    excel_bytes=file_bytes,
    file_name="전시_광고주컨펌완료_기준견적서_학습테스트.xlsx",
    project_name="2026 하반기 플래그십 팝업스토어 확정견적서",
    client="삼성전자 / 제일기획",
    venue="강남 / 홍대",
    currency="KRW"
)

print("Study success!")
print(f"Project ID: {proj_rec['project_id']}")
print(f"Name: {proj_rec['name']}")
print(f"Total Budget: ₩{proj_rec['total_budget']:,d}")
print(f"Item Count: {len(items)}")

# Verify load_projects sees it at index 0!
projects, _ = load_projects()
print("\nFirst project in load_projects:", projects[0]["name"])
assert projects[0]["project_id"] == proj_rec["project_id"]
print("VERIFICATION PASS: Newly studied project is immediately available at index 0!")
