# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import openpyxl
from auditor.loader import find_header_row

def classify_sheet(ws):
    """Classify whether a worksheet is ESTIMATE, LABOR, or OTHER."""
    hdr_idx, col_map = find_header_row(ws)
    if hdr_idx is None:
        return "UNKNOWN", 0, {}
    
    has_item = ("항목명" in col_map) or ("소항목" in col_map) or ("규격" in col_map)
    has_cost = ("단가" in col_map) or ("금액" in col_map)
    has_labor = ("인원" in col_map) and ("일수" in col_map)
    
    if has_labor and ("공정" in col_map or "역할" in col_map or "직종" in col_map):
        return "LABOR", hdr_idx, col_map
    elif has_item and has_cost:
        return "ESTIMATE", hdr_idx, col_map
    elif has_labor:
        return "LABOR", hdr_idx, col_map
    elif has_cost:
        return "SUMMARY", hdr_idx, col_map
    return "OTHER", hdr_idx, col_map

# Test on 기준견적서4
p_base = Path("data/samples/기준견적서4_전시_광고주컨펌.xlsx")
wb_base = openpyxl.load_workbook(p_base, data_only=True)
print("=== BASE WORKBOOK SHEETS ===")
for s in wb_base.sheetnames:
    stype, hidx, cmap = classify_sheet(wb_base[s])
    print(f"  [{s}] -> {stype} (header at row {hidx}, cols: {list(cmap.keys())})")

# Test on 홍대점 변경내역
p_rev = Path("data/samples/전시_홍대점_변경내역.xlsx")
wb_rev = openpyxl.load_workbook(p_rev, data_only=True)
print("=== REV WORKBOOK SHEETS ===")
for s in wb_rev.sheetnames:
    stype, hidx, cmap = classify_sheet(wb_rev[s])
    print(f"  [{s}] -> {stype} (header at row {hidx}, cols: {list(cmap.keys())})")
