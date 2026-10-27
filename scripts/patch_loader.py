# -*- coding: utf-8 -*-
from pathlib import Path

loader_path = Path("auditor/loader.py")
content = loader_path.read_text(encoding="utf-8")

target = 'def get_common_sheet_names(wb_orig: openpyxl.Workbook, wb_rev: openpyxl.Workbook) -> List[str]:\n    """두 워크북에 공통으로 존재하는 시트명 목록을 반환합니다."""\n    return [s for s in wb_orig.sheetnames if s in wb_rev.sheetnames]'

replacement = '''def get_common_sheet_names(wb_orig: openpyxl.Workbook, wb_rev: openpyxl.Workbook) -> List[str]:
    """두 워크북에 공통으로 존재하는 시트명 목록을 반환합니다."""
    return [s for s in wb_orig.sheetnames if s in wb_rev.sheetnames]

def find_best_estimate_sheet(wb: openpyxl.Workbook, preferred_sheet: Optional[str] = None) -> Tuple[str, int]:
    """워크북 내에서 견적 데이터(단가/금액 및 항목명)가 가장 유효한 최적 시트명과 인덱스를 자동 탐색합니다."""
    if preferred_sheet and preferred_sheet in wb.sheetnames:
        return preferred_sheet, wb.sheetnames.index(preferred_sheet)

    best_sheet = wb.sheetnames[0]
    best_idx = 0
    best_score = -1

    for idx, s in enumerate(wb.sheetnames):
        ws = wb[s]
        name_score = 0
        s_lower = s.lower()
        if any(k in s_lower for k in ["견적", "명세서", "상세", "사업장", "개발", "제작", "공사", "홍대", "수원"]):
            name_score += 5
        if any(k in s_lower for k in ["총괄", "갑지", "표지", "안내", "증빙", "승인"]):
            name_score -= 5

        hdr_row, col_map = find_header_row(ws)
        if hdr_row is not None:
            has_item = ("항목명" in col_map) or ("소항목" in col_map) or ("규격" in col_map)
            has_cost = ("단가" in col_map) or ("금액" in col_map)
            score = name_score + (15 if (has_item and has_cost) else (5 if has_cost else 0)) + min(ws.max_row // 5, 20)
            if score > best_score:
                best_score = score
                best_sheet = s
                best_idx = idx

    return best_sheet, best_idx'''

normalized = content.replace("\r\n", "\n")
assert target in normalized, "Target not found in loader.py"
normalized = normalized.replace(target, replacement, 1)
loader_path.write_text(normalized, encoding="utf-8")
print("SUCCESS: patched find_best_estimate_sheet into auditor/loader.py")
