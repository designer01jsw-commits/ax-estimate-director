with open("auditor/loader.py", "r", encoding="utf-8") as f:
    text = f.read()

old_block = """    if header_row_idx is None:
        sheet_preview = []
        for r in range(1, min(12, ws.max_row + 1)):
            vals = [str(ws.cell(row=r, column=c).value) for c in range(1, min(6, ws.max_column + 1)) if ws.cell(row=r, column=c).value is not None]
            if vals: sheet_preview.append(f"{r}행: {', '.join(vals)}")
        preview_text = " | ".join(sheet_preview[:3])
        raise ValidationError(
            f"‘{sheet_name}’ 시트에서 유효한 견적 머리글(항목명, 수량, 단가/금액)을 찾지 못했습니다. ({preview_text})",
            file_name=file_name,
            sheet_name=sheet_name
        )"""

new_block = """    if header_row_idx is None:
        raise ValidationError(
            f"‘{sheet_name}’ 시트에서 ‘단가’ 열을 찾지 못했습니다. 첫 10행 안에 머리글이 있는지 확인해 주세요.",
            file_name=file_name,
            sheet_name=sheet_name
        )"""

if old_block in text:
    text = text.replace(old_block, new_block)
    with open("auditor/loader.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched successfully!")
else:
    print("Block not found!")
