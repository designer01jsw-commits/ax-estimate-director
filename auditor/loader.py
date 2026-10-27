# -*- coding: utf-8 -*-
"""엑셀 파일 로드, 머리글 탐색, 검증 및 원본 추적 모듈 (동일 시트명 자동 대조 지원)"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

from auditor.errors import ValidationError
from auditor.schema import (
    COLUMN_ALIASES,
    REQUIRED_ESTIMATE_COLS,
    REQUIRED_LABOR_COLS,
    REQUIRED_APPROVAL_COLS,
    SHEET_ESTIMATE,
    SHEET_CHANGE_ESTIMATE,
    SHEET_LABOR,
    SHEET_CHANGE_LABOR,
    SHEET_CHANGE_APPROVAL
)

def clean_col_name(name: Any) -> str:
    """열 이름의 공백 및 특수문자를 정규화하고 별칭 맵을 적용합니다."""
    if name is None:
        return ""
    text = str(name).strip().replace(" ", "").replace("\n", "").replace("\r", "")
    lowered = text.lower()
    return COLUMN_ALIASES.get(lowered, COLUMN_ALIASES.get(text, text))

def parse_number(val: Any) -> Optional[float]:
    """통화 기호, 쉼표, 한글 단위 등을 제거하고 숫자로 변환합니다. 실패 시 None 반환."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    
    s = str(val).strip()
    if not s:
        return None
    
    cleaned = re.sub(r"[₩$€원,\s]", "", s)
    try:
        return float(cleaned)
    except ValueError:
        return None

def find_header_row(ws, required_cols: Optional[List[str]] = None, max_rows: int = 35) -> Tuple[Optional[int], Dict[str, int]]:
    """첫 max_rows 행 안에서 유효한 머리글 행을 찾아 (행번호, {정규화열이름: 열인덱스(0-based)})를 반환합니다.
    단가나 수량 열이 없더라도 항목명과 금액(또는 소항목/규격)이 있으면 유효 머리글로 인정합니다.
    """
    best_row = None
    best_map = {}
    best_score = -1

    for row_idx in range(1, min(max_rows + 1, ws.max_row + 1)):
        row_vals = [ws.cell(row=row_idx, column=col_idx).value for col_idx in range(1, ws.max_column + 1)]
        cleaned_map = {}
        for col_idx, val in enumerate(row_vals):
            if val is not None:
                cname = clean_col_name(val)
                if cname and cname not in cleaned_map:
                    cleaned_map[cname] = col_idx
        
        if required_cols:
            if all(req in cleaned_map for req in required_cols):
                return row_idx, cleaned_map
            continue

        # 견적 머리글 검증 조건:
        has_item = ("항목명" in cleaned_map) or ("소항목" in cleaned_map) or ("규격" in cleaned_map)
        has_cost = ("단가" in cleaned_map) or ("금액" in cleaned_map)
        has_qty = ("수량" in cleaned_map) or ("인원" in cleaned_map) or ("일수" in cleaned_map)

        if has_item and (has_cost or has_qty):
            score = (4 if has_item else 0) + (4 if has_cost else 0) + (2 if has_qty else 0) + len(cleaned_map)
            if len(cleaned_map) >= 2 and score > best_score:
                best_score = score
                best_row = row_idx
                best_map = cleaned_map

    if best_row is not None:
        return best_row, best_map

    return None, {}

def load_workbook_safe(file_input: Union[str, Path, Any], file_name: str) -> openpyxl.Workbook:
    """엑셀 워크북을 안전하게 로드합니다."""
    try:
        wb = openpyxl.load_workbook(file_input, data_only=True)
        return wb
    except (InvalidFileException, Exception) as e:
        raise ValidationError(
            f"‘{file_name}’는 엑셀(.xlsx) 파일이 아닙니다. .xlsx로 저장한 뒤 다시 올려 주세요.",
            file_name=file_name
        )

def get_common_sheet_names(wb_orig: openpyxl.Workbook, wb_rev: openpyxl.Workbook) -> List[str]:
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

    return best_sheet, best_idx

def resolve_sheet(
    wb: openpyxl.Workbook,
    target_sheet_name: str,
    file_name: str,
    required_cols: Optional[List[str]] = None
) -> Tuple[Any, str, Optional[str]]:
    """대상 시트를 찾습니다.
    1. 정확히 일치하는 이름 우선
    2. 유효한 헤더를 포함한 시트 스마트 탐색
    3. 단일 시트 대체 허용
    """
    if target_sheet_name in wb.sheetnames:
        return wb[target_sheet_name], target_sheet_name, None

    # 부분 일치 검색
    for s in wb.sheetnames:
        if target_sheet_name in s or ("거래명세서" in s and ("견적" in target_sheet_name or "명세서" in target_sheet_name)):
            return wb[s], s, f"시트 ‘{target_sheet_name}’ 대신 ‘{s}’ 시트를 사용합니다."

    # 헤더가 있는 유효한 첫 번째 시트 탐색
    for s in wb.sheetnames:
        ws = wb[s]
        hdr, _ = find_header_row(ws, required_cols)
        if hdr is not None:
            notice = f"‘{target_sheet_name}’ 시트 대신 데이터가 확인된 ‘{s}’ 시트를 사용합니다."
            return ws, s, notice

    if len(wb.sheetnames) == 1:
        single_sheet = wb.sheetnames[0]
        notice = f"‘{target_sheet_name}’ 시트 대신 단일 시트 ‘{single_sheet}’를 사용합니다."
        return wb[single_sheet], single_sheet, notice
    
    sheet_list_str = ", ".join(wb.sheetnames)
    raise ValidationError(
        f"‘{target_sheet_name}’ 시트를 찾지 못했습니다. 현재 시트: {sheet_list_str}. 시트 이름을 확인해 주세요.",
        file_name=file_name
    )

def read_estimate_sheet(
    ws,
    file_name: str,
    sheet_name: str,
    required_cols: Optional[List[str]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Set[str], List[str]]:
    """견적/변경견적 시트를 파싱하고 (항목리스트, 산출식불일치리스트, 중복코드셋, 경고리스트)를 반환합니다.
    단가나 수량이 명시되지 않은 갑지(총괄표) 및 요약 시트도 금액/항목을 기반으로 자동 계산 및 감리합니다.
    """
    header_row_idx, col_map = find_header_row(ws, required_cols)
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
                f"‘{sheet_name}’ 시트에서 ‘단가’ 열을 찾지 못했습니다. 첫 35행 안에 머리글이 있는지 확인해 주세요.",
                file_name=file_name,
                sheet_name=sheet_name
            )

    items = []
    mismatches = []
    warnings = []
    code_counts: Dict[str, int] = {}
    
    raw_rows = []
    current_cat = ""
    current_main_item = ""

    for r in range(header_row_idx + 1, ws.max_row + 1):
        row_vals = [ws.cell(row=r, column=c + 1).value for c in range(ws.max_column)]
        if all(v is None or str(v).strip() == "" for v in row_vals):
            continue
        
        raw_cat_str = str(row_vals[col_map["구분"]]).strip() if "구분" in col_map and col_map["구분"] < len(row_vals) and row_vals[col_map["구분"]] is not None else ""
        raw_item_str = str(row_vals[col_map["항목명"]]).strip() if "항목명" in col_map and col_map["항목명"] < len(row_vals) and row_vals[col_map["항목명"]] is not None else ""
        raw_sub_str = str(row_vals[col_map["소항목"]]).strip() if "소항목" in col_map and col_map["소항목"] < len(row_vals) and row_vals[col_map["소항목"]] is not None else ""
        raw_spec_str = str(row_vals[col_map["규격"]]).strip() if "규격" in col_map and col_map["규격"] < len(row_vals) and row_vals[col_map["규격"]] is not None else ""

        # 만약 현재 행에 합계/소계/총계/수수료 키워드가 명시적으로 있다면 즉시 건너뜀
        row_summary_check = f"{raw_cat_str} {raw_item_str} {raw_sub_str}"
        if any(keyword in row_summary_check for keyword in ["합계", "소계", "총계", "수수료", "당사는 본"]):
            warnings.append(f"‘{raw_item_str or raw_cat_str or '합계'}’ 행(엑셀 {r}행)을 건너뛰었습니다.")
            continue

        # 구분 및 항목명 병합 셀 대응 (forward fill)
        if raw_cat_str:
            current_cat = raw_cat_str
        if raw_item_str:
            current_main_item = raw_item_str

        detail_str = raw_sub_str or raw_spec_str

        # 결합 항목명 생성 (대항목 + 소항목/세부내역)
        if current_main_item and detail_str and current_main_item != detail_str:
            full_item_name = f"{current_main_item} - {detail_str}"
        elif detail_str:
            full_item_name = detail_str
        elif current_main_item:
            full_item_name = current_main_item
        else:
            full_item_name = current_cat

        if not full_item_name:
            continue
            
        code_raw = row_vals[col_map["항목코드"]] if "항목코드" in col_map and col_map["항목코드"] < len(row_vals) else ""
        code = str(code_raw or "").strip()
        if not code:
            prefix = current_cat[:2] if current_cat else "ITM"
            code = f"{prefix}-{r:03d}"
            
        code_counts[code] = code_counts.get(code, 0) + 1
        raw_rows.append((r, row_vals, code, current_cat, full_item_name, raw_spec_str))

    duplicate_codes = {c for c, count in code_counts.items() if count > 1}
    for dup in duplicate_codes:
        warnings.append(f"항목코드 ‘{dup}’가 {code_counts[dup]}회 중복 등장하여 코드 기반 연결에서 제외됩니다.")

    for r, row_vals, code, cat, full_item_name, spec_str in raw_rows:
        spec = spec_str if spec_str else (str(row_vals[col_map["규격"]] or "").strip() if "규격" in col_map and col_map["규격"] < len(row_vals) else "")
        unit = str(row_vals[col_map["단위"]] or "").strip() if "단위" in col_map and col_map["단위"] < len(row_vals) else ""
        
        qty_val = row_vals[col_map["수량"]] if "수량" in col_map and col_map["수량"] < len(row_vals) else None
        if qty_val is None and "인원" in col_map and col_map["인원"] < len(row_vals):
            qty_val = row_vals[col_map["인원"]]
            
        price_val = row_vals[col_map["단가"]] if "단가" in col_map and col_map["단가"] < len(row_vals) else None
        amt_val = row_vals[col_map["금액"]] if "금액" in col_map and col_map["금액"] < len(row_vals) else None
        
        qty = parse_number(qty_val)
        price = parse_number(price_val)
        amt = parse_number(amt_val)
        
        # 단가 열이 없고 금액 열만 있는 경우: 단가 = 금액 / 수량 자동 역산
        if price is None and amt is not None:
            if qty is not None and qty != 0:
                price = amt / qty
            else:
                price = amt
                qty = 1.0

        # 수량 기본값 보완 (수량 누락 시 1)
        if qty is None and (price is not None or amt is not None):
            qty = 1.0
            if not unit:
                unit = "식"

        # 금액 누락 시: 금액 = 단가 * 수량
        if amt is None and price is not None and qty is not None:
            amt = price * qty
        
        if qty is None or price is None:
            failed_part = []
            if qty is None: failed_part.append(f"수량('{qty_val}')")
            if price is None: failed_part.append(f"단가/금액('{price_val or amt_val}')")
            warnings.append(f"{r}행 숫자 변환 실패: {', '.join(failed_part)} - 해당 행은 계산에서 제외됩니다.")
            continue
            
        if qty < 0 or price < 0:
            warnings.append(f"{r}행 음수 값 감지: 수량={qty}, 단가={price}")

        calculated_amount = qty * price
        
        # 산출식 검증 (파일 금액 열이 따로 있는 경우)
        if amt is not None:
            diff = abs(amt - calculated_amount)
            if diff > 1.0:
                mismatches.append({
                    "row_idx": r,
                    "code": code,
                    "item_name": full_item_name,
                    "file_amount": amt,
                    "calc_amount": calculated_amount,
                    "diff": diff,
                    "file_name": file_name,
                    "sheet_name": sheet_name
                })
                warnings.append(
                    f"{r}행 ‘{full_item_name}’ 산출식 불일치: 파일 금액({amt:,.2f}) ≠ 재계산({calculated_amount:,.2f})"
                )

        row_key = f"{file_name}|{sheet_name}|{r}"
        items.append({
            "row_key": row_key,
            "원본파일": file_name,
            "원본시트": sheet_name,
            "원본행": r,
            "항목코드": code,
            "구분": cat,
            "항목명": full_item_name,
            "규격": spec,
            "수량": qty,
            "단위": unit or "식",
            "단가": price,
            "금액": calculated_amount,
            "원본_파일금액": amt
        })

    if not items:
        raise ValidationError(
            f"‘{sheet_name}’ 시트에 계산할 수 있는 항목이 없습니다.",
            file_name=file_name,
            sheet_name=sheet_name
        )

    return items, mismatches, duplicate_codes, warnings

def read_labor_sheet(
    ws,
    file_name: str,
    sheet_name: str
) -> Tuple[List[Dict[str, Any]], Set[str], List[str]]:
    header_row_idx, col_map = find_header_row(ws, REQUIRED_LABOR_COLS)
    if header_row_idx is None:
        sample_map = {}
        for r in range(1, min(16, ws.max_row + 1)):
            for c in range(1, ws.max_column + 1):
                val = ws.cell(row=r, column=c).value
                if val: sample_map[clean_col_name(val)] = True
        missing = [req for req in REQUIRED_LABOR_COLS if req not in sample_map]
        missing_str = missing[0] if missing else "필수"
        raise ValidationError(
            f"‘{sheet_name}’ 시트에서 ‘{missing_str}’ 열을 찾지 못했습니다. 첫 10행 안에 머리글이 있는지 확인해 주세요.",
            file_name=file_name,
            sheet_name=sheet_name
        )

    items = []
    warnings = []
    code_counts: Dict[str, int] = {}
    raw_rows = []

    for r in range(header_row_idx + 1, ws.max_row + 1):
        row_vals = [ws.cell(row=r, column=c + 1).value for c in range(ws.max_column)]
        if all(v is None or str(v).strip() == "" for v in row_vals):
            continue

        role_raw = row_vals[col_map["역할"]] if "역할" in col_map and col_map["역할"] < len(row_vals) else ""
        if str(role_raw or "").strip() in ["합계", "소계", "총계"]:
            warnings.append(f"‘{role_raw}’ 인력 행(엑셀 {r}행)을 건너뛰었습니다.")
            continue

        code_raw = row_vals[col_map["항목코드"]] if "항목코드" in col_map and col_map["항목코드"] < len(row_vals) else ""
        code = str(code_raw or "").strip()
        if not code:
            code = f"LBR-{r:03d}"
            
        code_counts[code] = code_counts.get(code, 0) + 1
        raw_rows.append((r, row_vals, code))

    duplicate_codes = {c for c, count in code_counts.items() if count > 1}
    for dup in duplicate_codes:
        warnings.append(f"인력 항목코드 ‘{dup}’가 중복 등장하여 코드 기반 연결에서 제외됩니다.")

    for r, row_vals, code in raw_rows:
        process = str(row_vals[col_map["공정"]] or "").strip() if "공정" in col_map and col_map["공정"] < len(row_vals) else ""
        role = str(row_vals[col_map["역할"]] or "").strip() if "역할" in col_map and col_map["역할"] < len(row_vals) else ""
        
        persons_val = row_vals[col_map["인원"]] if "인원" in col_map and col_map["인원"] < len(row_vals) else None
        days_val = row_vals[col_map["일수"]] if "일수" in col_map and col_map["일수"] < len(row_vals) else None
        rate_val = row_vals[col_map["일단가"]] if "일단가" in col_map and col_map["일단가"] < len(row_vals) else None

        persons = parse_number(persons_val)
        days = parse_number(days_val)
        daily_rate = parse_number(rate_val) if rate_val is not None else 0.0

        if persons is None or days is None:
            failed_part = []
            if persons is None: failed_part.append(f"인원('{persons_val}')")
            if days is None: failed_part.append(f"일수('{days_val}')")
            warnings.append(f"인력 {r}행 숫자 변환 실패: {', '.join(failed_part)} - 해당 행은 계산에서 제외됩니다.")
            continue

        md = persons * days
        labor_cost = md * (daily_rate or 0.0)
        item_name = f"{process}/{role}" if process and role else (role or process or "인력")
        row_key = f"{file_name}|{sheet_name}|{r}"

        items.append({
            "row_key": row_key,
            "원본파일": file_name,
            "원본시트": sheet_name,
            "원본행": r,
            "항목코드": code,
            "구분": process,
            "공정": process,
            "역할": role,
            "항목명": item_name,
            "인원": persons,
            "일수": days,
            "MD": md,
            "일단가": daily_rate,
            "인건비": labor_cost,
            "수량": md,
            "단가": daily_rate or 0.0,
            "금액": labor_cost
        })

    return items, duplicate_codes, warnings

def read_approval_sheet(
    ws,
    file_name: str,
    sheet_name: str
) -> Tuple[List[Dict[str, Any]], List[str]]:
    header_row_idx, col_map = find_header_row(ws, REQUIRED_APPROVAL_COLS)
    if header_row_idx is None:
        sample_map = {}
        for r in range(1, min(16, ws.max_row + 1)):
            for c in range(1, ws.max_column + 1):
                val = ws.cell(row=r, column=c).value
                if val: sample_map[clean_col_name(val)] = True
        missing = [req for req in REQUIRED_APPROVAL_COLS if req not in sample_map]
        missing_str = missing[0] if missing else "필수"
        raise ValidationError(
            f"‘{sheet_name}’ 시트에서 ‘{missing_str}’ 열을 찾지 못했습니다. 첫 10행 안에 머리글이 있는지 확인해 주세요.",
            file_name=file_name,
            sheet_name=sheet_name
        )

    records = []
    warnings = []

    for r in range(header_row_idx + 1, ws.max_row + 1):
        row_vals = [ws.cell(row=r, column=c + 1).value for c in range(ws.max_column)]
        if all(v is None or str(v).strip() == "" for v in row_vals):
            continue

        appr_id = str(row_vals[col_map["승인번호"]] or "").strip() if "승인번호" in col_map and col_map["승인번호"] < len(row_vals) else ""
        code = str(row_vals[col_map["항목코드"]] or "").strip() if "항목코드" in col_map and col_map["항목코드"] < len(row_vals) else ""
        item_name = str(row_vals[col_map["항목명"]] or "").strip() if "항목명" in col_map and col_map["항목명"] < len(row_vals) else ""
        detail = str(row_vals[col_map["변경내용"]] or "").strip() if "변경내용" in col_map and col_map["변경내용"] < len(row_vals) else ""
        status_raw = str(row_vals[col_map["승인여부"]] or "").strip() if "승인여부" in col_map and col_map["승인여부"] < len(row_vals) else ""
        date = str(row_vals[col_map["승인일"]] or "").strip() if "승인일" in col_map and col_map["승인일"] < len(row_vals) else ""
        approver = str(row_vals[col_map["승인자"]] or "").strip() if "승인자" in col_map and col_map["승인자"] < len(row_vals) else ""

        row_key = f"{file_name}|{sheet_name}|{r}"
        records.append({
            "row_key": row_key,
            "원본파일": file_name,
            "원본시트": sheet_name,
            "원본행": r,
            "승인번호": appr_id,
            "항목코드": code,
            "항목명": item_name,
            "변경내용": detail,
            "승인여부_원본": status_raw,
            "승인일": date,
            "승인자": approver
        })

    return records, warnings
