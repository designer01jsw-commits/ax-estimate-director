# -*- coding: utf-8 -*-
import re
from pathlib import Path

# 1. Patch auditor/loader.py: max_rows 35 and auto-fallback sheet in read_estimate_sheet
loader_path = Path("auditor/loader.py")
l_content = loader_path.read_text(encoding="utf-8")

# Increase max_rows to 35
l_content = l_content.replace(
    "def find_header_row(ws, required_cols: Optional[List[str]] = None, max_rows: int = 15)",
    "def find_header_row(ws, required_cols: Optional[List[str]] = None, max_rows: int = 35)"
)

# Auto fallback to other sheets before raising ValidationError
old_read_head = """    header_row_idx, col_map = find_header_row(ws, required_cols)
    if header_row_idx is None or ("단가" not in col_map and "금액" not in col_map):
        raise ValidationError(
            f"‘{sheet_name}’ 시트에서 ‘단가’ 열을 찾지 못했습니다. 첫 10행 안에 머리글이 있는지 확인해 주세요.",
            file_name=file_name,
            sheet_name=sheet_name
        )"""

new_read_head = """    header_row_idx, col_map = find_header_row(ws, required_cols)
    if header_row_idx is None or ("단가" not in col_map and "금액" not in col_map):
        # 다른 유효한 견적 시트 자동 탐색 (워크북 내 대체 시트 탐색)
        wb = getattr(ws, "parent", None)
        found_alt = False
        if wb is not None:
            for s in wb.sheetnames:
                if s != sheet_name:
                    alt_hdr, alt_map = find_header_row(wb[s], required_cols)
                    if alt_hdr is not None and ("단가" in alt_map or "금액" in alt_map):
                        ws = wb[s]
                        sheet_name = s
                        header_row_idx, col_map = alt_hdr, alt_map
                        found_alt = True
                        break
        if not found_alt and (header_row_idx is None or ("단가" not in col_map and "금액" not in col_map)):
            raise ValidationError(
                f"‘{sheet_name}’ 시트에서 ‘단가’ 또는 ‘금액’ 열을 찾지 못했습니다. 첫 35행 안에 머리글(품명, 단가/금액)이 있는지 확인해 주세요.",
                file_name=file_name,
                sheet_name=sheet_name
            )"""

normalized_l = l_content.replace("\r\n", "\n")
assert old_read_head in normalized_l, "old_read_head not found in loader.py"
normalized_l = normalized_l.replace(old_read_head, new_read_head, 1)
loader_path.write_text(normalized_l, encoding="utf-8")
print("SUCCESS: patched auditor/loader.py with max_rows=35 and auto-fallback sheet")

# 2. Patch app.py: Fix infinite rerun loop bug
app_path = Path("app.py")
a_content = app_path.read_text(encoding="utf-8")

old_upload_check = """    if target_supply_mode == "📁 진단받을 견적서 직접 업로드 (기본)":
        st.session_state["use_sample_change"] = False
        rev_uploaded = st.sidebar.file_uploader(
            "진단받을 신규 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_target_rev_file",
            help="선택된 광고주 컨펌 기준가이드와 비교 감리할 견적서 엑셀 파일을 업로드하세요."
        )
        if rev_uploaded:
            rev_file_input = rev_uploaded
            rev_file_name = rev_uploaded.name"""

new_upload_check = """    if target_supply_mode == "📁 진단받을 견적서 직접 업로드 (기본)":
        st.session_state["use_sample_change"] = False
        rev_uploaded = st.sidebar.file_uploader(
            "진단받을 신규 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_target_rev_file",
            help="선택된 광고주 컨펌 기준가이드와 비교 감리할 견적서 엑셀 파일을 업로드하세요."
        )
        main_uploaded = st.session_state.get("u_main_drag_drop_rev")
        active_upload = rev_uploaded or main_uploaded
        if active_upload:
            rev_file_input = active_upload
            rev_file_name = active_upload.name"""

normalized_a = a_content.replace("\r\n", "\n")
assert old_upload_check in normalized_a, "old_upload_check not found in app.py"
normalized_a = normalized_a.replace(old_upload_check, new_upload_check, 1)

# Remove st.rerun() from main_direct_upload
old_main_uploader = """        with col_main_up:
            main_direct_upload = st.file_uploader(
                "📥 대조·감리할 견적서 파일 바로 업로드 (.xlsx)",
                type=["xlsx"],
                key="u_main_drag_drop_rev",
                help="기준 가이드와 비교 감리할 엑셀 파일을 업로드하세요."
            )
            if main_direct_upload:
                rev_file_input = main_direct_upload
                rev_file_name = main_direct_upload.name
                st.rerun()"""

new_main_uploader = """        with col_main_up:
            main_direct_upload = st.file_uploader(
                "📥 진단받을 신규 견적서 파일 바로 업로드 (.xlsx)",
                type=["xlsx"],
                key="u_main_drag_drop_rev",
                help="에이전트 기준 가이드와 비교 감리할 엑셀 파일을 업로드하세요."
            )
            if main_direct_upload:
                rev_file_input = main_direct_upload
                rev_file_name = main_direct_upload.name"""

assert old_main_uploader in normalized_a, "old_main_uploader not found in app.py"
normalized_a = normalized_a.replace(old_main_uploader, new_main_uploader, 1)

app_path.write_text(normalized_a, encoding="utf-8")
print("SUCCESS: patched app.py to eliminate infinite rerun loop bug!")
