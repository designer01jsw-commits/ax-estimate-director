# -*- coding: utf-8 -*-
import io
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from auditor.loader import load_workbook_safe, find_best_estimate_sheet, read_estimate_sheet
from auditor.categorizer import decompose_estimate_by_category

class MockUploadedFile(io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name

# Test with in-memory bytes simulating Streamlit file_uploader
sample_path = Path("data/samples/전시_홍대점_변경내역.xlsx")
file_bytes = sample_path.read_bytes()
uploaded_file = MockUploadedFile(file_bytes, sample_path.name)

wb = load_workbook_safe(uploaded_file, uploaded_file.name)
best_sheet, idx = find_best_estimate_sheet(wb)
print(f"Uploaded file loaded cleanly! Best sheet: {best_sheet}")

items, _, _, _ = read_estimate_sheet(wb[best_sheet], uploaded_file.name, best_sheet)
print(f"Items parsed: {len(items)}")

decomp = decompose_estimate_by_category(items)
print(f"Decomposed total: ₩{decomp['total_amount']:,f}")
print("ALL IN-MEMORY UPLOAD CHECKS PASSED!")
