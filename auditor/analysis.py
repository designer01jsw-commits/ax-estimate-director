# -*- coding: utf-8 -*-
"""견적 분석, 금액 차이 계산, 승인 연결, 검토 필요 목록 및 요약 생성 모듈"""

from typing import Any, Dict, List, Optional, Tuple, Set
from auditor.schema import (
    MATCH_CONFIRMED,
    MATCH_NEEDS_CONFIRM,
    DIFF_TYPE_INCREASE,
    DIFF_TYPE_DECREASE,
    DIFF_TYPE_UNCHANGED,
    DIFF_TYPE_ADDED,
    DIFF_TYPE_DELETED,
    LABOR_DIFF_INCREASE,
    LABOR_DIFF_DECREASE,
    LABOR_DIFF_UNCHANGED,
    LABOR_DIFF_ADDED,
    LABOR_DIFF_DELETED,
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_UNCONFIRMED,
    APPROVAL_NOT_APPLICABLE,
    APPROVAL_NEEDS_CONFIRM,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW
)
from auditor.matching import normalize_name

def parse_approval_status(raw_val: Any) -> Tuple[str, str]:
    """승인여부 원본 값을 표준 승인상태 및 근거로 변환합니다."""
    if raw_val is None:
        return APPROVAL_UNCONFIRMED, "승인여부 공란"
    s = str(raw_val).strip()
    if not s:
        return APPROVAL_UNCONFIRMED, "승인여부 공란"
    
    lowered = s.lower()
    if lowered in ["승인", "승인완료", "y", "o"]:
        return APPROVAL_APPROVED, f"승인 ('{s}')"
    elif lowered in ["반려", "n", "x"]:
        return APPROVAL_REJECTED, f"반려 ('{s}')"
    elif lowered in ["보류"]:
        return APPROVAL_UNCONFIRMED, f"보류 ('{s}')"
    else:
        return APPROVAL_UNCONFIRMED, f"미확인 ('{s}')"

def match_approval_record(
    item_code: str,
    item_name: str,
    approval_records: List[Dict[str, Any]]
) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """항목코드 또는 항목명으로 승인 기록을 찾고 (승인상태, 승인근거, 승인기록)을 반환합니다."""
    if not approval_records:
        return APPROVAL_UNCONFIRMED, "승인 기록 없음 (승인 데이터 부재)", None

    code_matches = []
    if item_code:
        for app in approval_records:
            if app.get("항목코드", "").strip() == item_code:
                code_matches.append(app)

    matched_list = code_matches

    if not matched_list and item_name:
        norm_target = normalize_name(item_name)
        for app in approval_records:
            if normalize_name(app.get("항목명", "")) == norm_target:
                matched_list.append(app)

    if not matched_list:
        return APPROVAL_UNCONFIRMED, "승인 기록 없음", None

    sorted_matches = sorted(
        matched_list,
        key=lambda x: str(x.get("승인일", "") or ""),
        reverse=True
    )
    best_record = sorted_matches[0]
    base_status, reason_detail = parse_approval_status(best_record.get("승인여부_원본"))
    
    count_note = f" (승인 기록 {len(matched_list)}건 중 최신)" if len(matched_list) > 1 else ""
    appr_no = best_record.get("승인번호", "")
    full_reason = f"승인번호 {appr_no}: {reason_detail}{count_note}"

    return base_status, full_reason, best_record

def format_source_str(item: Optional[Dict[str, Any]]) -> str:
    """원본 파일/시트/행 문자열을 안전하게 포맷팅합니다."""
    if not item:
        return "-"
    f = item.get("원본파일", "")
    s = item.get("원본시트", "")
    r = item.get("원본행", "")
    if f or s or r:
        return f"{f} / {s} / {r}행"
    return "-"

def analyze_estimates(
    matched_pairs: List[Dict[str, Any]],
    orig_all_items: List[Dict[str, Any]],
    rev_all_items: List[Dict[str, Any]],
    approval_records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    analyzed_items: List[Dict[str, Any]] = []
    used_approval_keys = set()

    for pair in matched_pairs:
        o_item = pair.get("orig_item")
        r_item = pair.get("rev_item")
        match_status = pair.get("match_status", MATCH_CONFIRMED)
        match_method = pair.get("match_method", "")
        sim = pair.get("similarity", 0.0)

        code = (r_item or o_item).get("항목코드", "")
        category = (r_item or o_item).get("구분", "")
        name = (r_item or o_item).get("항목명", "")
        spec = (r_item or o_item).get("규격", "")
        unit = (r_item or o_item).get("단위", "")

        q1 = float(o_item["수량"]) if o_item and "수량" in o_item else 0.0
        p1 = float(o_item["단가"]) if o_item and "단가" in o_item else 0.0
        amt1 = q1 * p1 if o_item else 0.0

        q2 = float(r_item["수량"]) if r_item and "수량" in r_item else 0.0
        p2 = float(r_item["단가"]) if r_item and "단가" in r_item else 0.0
        amt2 = q2 * p2 if r_item else 0.0

        diff_amt = amt2 - amt1
        rate = (diff_amt / amt1 * 100.0) if amt1 > 0 else None

        if o_item and not r_item:
            diff_type = DIFF_TYPE_DELETED
        elif r_item and not o_item:
            diff_type = DIFF_TYPE_ADDED
        else:
            if abs(diff_amt) < 1e-6:
                diff_type = DIFF_TYPE_UNCHANGED
            elif diff_amt > 0:
                diff_type = DIFF_TYPE_INCREASE
            else:
                diff_type = DIFF_TYPE_DECREASE

        if o_item and r_item:
            qty_effect = (q2 - q1) * p1
            price_effect = (p2 - p1) * q2
        elif r_item and not o_item:
            qty_effect = amt2
            price_effect = 0.0
        else:
            qty_effect = -amt1
            price_effect = 0.0

        matched_app_record = None
        if diff_type == DIFF_TYPE_UNCHANGED:
            approval_status = APPROVAL_NOT_APPLICABLE
            approval_reason = "변동 없음"
        elif match_status == MATCH_NEEDS_CONFIRM:
            approval_status = APPROVAL_NEEDS_CONFIRM
            approval_reason = "항목 연결 확인 필요"
        else:
            approval_status, approval_reason, matched_app_record = match_approval_record(
                code, name, approval_records
            )
            if matched_app_record:
                used_approval_keys.add(matched_app_record["row_key"])

        orig_src = format_source_str(o_item)
        rev_src = format_source_str(r_item)

        analyzed_items.append({
            "항목코드": code,
            "구분": category,
            "항목명": name,
            "규격": spec,
            "단위": unit,
            "수량_최초": q1 if o_item else None,
            "단가_최초": p1 if o_item else None,
            "금액_최초": amt1 if o_item else 0.0,
            "수량_변경": q2 if r_item else None,
            "단가_변경": p2 if r_item else None,
            "금액_변경": amt2 if r_item else 0.0,
            "차이금액": diff_amt,
            "증감률": rate,
            "수량효과": qty_effect,
            "단가효과": price_effect,
            "변경유형": diff_type,
            "연결상태": match_status,
            "연결방식": match_method,
            "유사도": sim,
            "승인상태": approval_status,
            "승인근거": approval_reason,
            "승인번호": matched_app_record.get("승인번호", "") if matched_app_record else "",
            "원본_최초": orig_src,
            "원본_변경": rev_src,
            "orig_row_key": o_item.get("row_key", "") if o_item else "",
            "rev_row_key": r_item.get("row_key", "") if r_item else ""
        })

    orphan_approvals = [
        app for app in approval_records
        if app["row_key"] not in used_approval_keys
    ]

    return analyzed_items, orphan_approvals

def analyze_labor(
    matched_pairs: List[Dict[str, Any]],
    approval_records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    analyzed_labor = []
    used_app_keys = set()

    for pair in matched_pairs:
        o_item = pair.get("orig_item")
        r_item = pair.get("rev_item")
        match_status = pair.get("match_status", MATCH_CONFIRMED)
        match_method = pair.get("match_method", "")
        sim = pair.get("similarity", 0.0)

        code = (r_item or o_item).get("항목코드", "")
        process = (r_item or o_item).get("공정", "")
        role = (r_item or o_item).get("역할", "")
        name = (r_item or o_item).get("항목명", f"{process}/{role}")

        p1 = float(o_item["인원"]) if o_item and "인원" in o_item else 0.0
        d1 = float(o_item["일수"]) if o_item and "일수" in o_item else 0.0
        md1 = p1 * d1 if o_item else 0.0
        rate1 = float(o_item.get("일단가", 0.0) or 0.0) if o_item else 0.0
        cost1 = md1 * rate1

        p2 = float(r_item["인원"]) if r_item and "인원" in r_item else 0.0
        d2 = float(r_item["일수"]) if r_item and "일수" in r_item else 0.0
        md2 = p2 * d2 if r_item else 0.0
        rate2 = float(r_item.get("일단가", 0.0) or 0.0) if r_item else 0.0
        cost2 = md2 * rate2

        diff_md = md2 - md1
        diff_cost = cost2 - cost1

        if o_item and not r_item:
            diff_type = LABOR_DIFF_DELETED
        elif r_item and not o_item:
            diff_type = LABOR_DIFF_ADDED
        else:
            if abs(diff_md) < 1e-6 and abs(diff_cost) < 1e-6:
                diff_type = LABOR_DIFF_UNCHANGED
            elif diff_md > 0 or diff_cost > 0:
                diff_type = LABOR_DIFF_INCREASE
            else:
                diff_type = LABOR_DIFF_DECREASE

        matched_app_record = None
        if diff_type == LABOR_DIFF_UNCHANGED:
            approval_status = APPROVAL_NOT_APPLICABLE
            approval_reason = "변동 없음"
        elif match_status == MATCH_NEEDS_CONFIRM:
            approval_status = APPROVAL_NEEDS_CONFIRM
            approval_reason = "인력 연결 확인 필요"
        else:
            approval_status, approval_reason, matched_app_record = match_approval_record(
                code, name, approval_records
            )
            if matched_app_record:
                used_app_keys.add(matched_app_record["row_key"])

        orig_src = format_source_str(o_item)
        rev_src = format_source_str(r_item)

        analyzed_labor.append({
            "항목코드": code,
            "공정": process,
            "역할": role,
            "항목명": name,
            "인원_최초": p1 if o_item else None,
            "일수_최초": d1 if o_item else None,
            "MD_최초": md1 if o_item else 0.0,
            "인건비_최초": cost1 if o_item else 0.0,
            "인원_변경": p2 if r_item else None,
            "일수_변경": d2 if r_item else None,
            "MD_변경": md2 if r_item else 0.0,
            "인건비_변경": cost2 if r_item else 0.0,
            "차이_MD": diff_md,
            "차이_인건비": diff_cost,
            "변경유형": diff_type,
            "연결상태": match_status,
            "연결방식": match_method,
            "유사도": sim,
            "승인상태": approval_status,
            "승인근거": approval_reason,
            "승인번호": matched_app_record.get("승인번호", "") if matched_app_record else "",
            "원본_최초": orig_src,
            "원본_변경": rev_src,
            "orig_row_key": o_item.get("row_key", "") if o_item else "",
            "rev_row_key": r_item.get("row_key", "") if r_item else ""
        })

    return analyzed_labor, used_app_keys

def build_review_items(
    analyzed_estimates: List[Dict[str, Any]],
    analyzed_labor: List[Dict[str, Any]],
    orphan_approvals: List[Dict[str, Any]],
    formula_mismatches: List[Dict[str, Any]],
    loader_warnings: List[str]
) -> List[Dict[str, Any]]:
    review_list = []

    # 1. 반려된 변경이 견적에 반영됨 (높음)
    for it in analyzed_estimates:
        if it["승인상태"] == APPROVAL_REJECTED and it["변경유형"] != DIFF_TYPE_UNCHANGED:
            review_list.append({
                "심각도": SEVERITY_HIGH,
                "사유": "반려된 변경이 견적에 반영됨",
                "대상": "견적",
                "항목코드": it["항목코드"],
                "항목명": it["항목명"],
                "차이금액_또는_MD": f"{it['차이금액']:+,.0f}",
                "승인상태": it["승인상태"],
                "원본_최초": it["원본_최초"],
                "원본_변경": it["원본_변경"],
                "조치안내": "반려된 변경 사항이 반영되어 있으므로 견적 금액 확인 및 원복이 필요합니다."
            })

    # 2. 승인 미확인 변경 (견적) (높음)
    for it in analyzed_estimates:
        if it["승인상태"] == APPROVAL_UNCONFIRMED and it["변경유형"] != DIFF_TYPE_UNCHANGED and it["연결상태"] == MATCH_CONFIRMED:
            review_list.append({
                "심각도": SEVERITY_HIGH,
                "사유": "승인 미확인 변경 (견적)",
                "대상": "견적",
                "항목코드": it["항목코드"],
                "항목명": it["항목명"],
                "차이금액_또는_MD": f"{it['차이금액']:+,.0f}",
                "승인상태": it["승인상태"],
                "원본_최초": it["원본_최초"],
                "원본_변경": it["원본_변경"],
                "조치안내": f"승인 내역을 확인하거나 변경 승인서(CR)를 보완해 주세요. ({it['승인근거']})"
            })

    # 3. 승인 미확인 변경 (인력) (높음)
    for it in analyzed_labor:
        if it["승인상태"] == APPROVAL_UNCONFIRMED and it["변경유형"] != LABOR_DIFF_UNCHANGED and it["연결상태"] == MATCH_CONFIRMED:
            review_list.append({
                "심각도": SEVERITY_HIGH,
                "사유": "승인 미확인 변경 (인력)",
                "대상": "인력",
                "항목코드": it["항목코드"],
                "항목명": it["항목명"],
                "차이금액_또는_MD": f"{it['차이_MD']:+.1f} M/D ({it['차이_인건비']:+,.0f})",
                "승인상태": it["승인상태"],
                "원본_최초": it["원본_최초"],
                "원본_변경": it["원본_변경"],
                "조치안내": "인력 투입 변경에 대한 승인 기록 확인 및 등록이 필요합니다."
            })

    # 4. 항목 연결 확인 필요 (중간)
    for it in analyzed_estimates:
        if it["연결상태"] == MATCH_NEEDS_CONFIRM:
            review_list.append({
                "심각도": SEVERITY_MEDIUM,
                "사유": "항목 연결 확인 필요",
                "대상": "견적",
                "항목코드": it["항목코드"],
                "항목명": it["항목명"],
                "차이금액_또는_MD": f"{it['차이금액']:+,.0f}",
                "승인상태": it["승인상태"],
                "원본_최초": it["원본_최초"],
                "원본_변경": it["원본_변경"],
                "조치안내": f"유사도({it['유사도']:.2f}) 기반 후보이므로 [연결 확인] 탭에서 동일 항목 여부를 확정해 주세요."
            })

    for it in analyzed_labor:
        if it["연결상태"] == MATCH_NEEDS_CONFIRM:
            review_list.append({
                "심각도": SEVERITY_MEDIUM,
                "사유": "항목 연결 확인 필요",
                "대상": "인력",
                "항목코드": it["항목코드"],
                "항목명": it["항목명"],
                "차이금액_또는_MD": f"{it['차이_MD']:+.1f} M/D",
                "승인상태": it["승인상태"],
                "원본_최초": it["원본_최초"],
                "원본_변경": it["원본_변경"],
                "조치안내": "인력 연결을 확인해 주세요."
            })

    # 5. 산출식 불일치 (중간)
    for mis in formula_mismatches:
        review_list.append({
            "심각도": SEVERITY_MEDIUM,
            "사유": "산출식 불일치 (파일 금액 ≠ 수량×단가)",
            "대상": "견적",
            "항목코드": mis.get("code", ""),
            "항목명": mis.get("item_name", ""),
            "차이금액_또는_MD": f"오차 {mis.get('diff', 0):,.0f}",
            "승인상태": "-",
            "원본_최초": f"{mis.get('file_name', '')} / {mis.get('sheet_name', '')} / {mis.get('row_idx', '')}행",
            "원본_변경": "-",
            "조치안내": f"파일에 기록된 금액({mis.get('file_amount'):,.0f})과 수량×단가({mis.get('calc_amount'):,.0f})가 다릅니다. 재계산 금액을 적용했습니다."
        })

    # 6. 대응 변경 없음 승인 기록 (낮음)
    for app in orphan_approvals:
        review_list.append({
            "심각도": SEVERITY_LOW,
            "사유": "대응 변경 없음 승인 기록",
            "대상": "승인기록",
            "항목코드": app.get("항목코드", ""),
            "항목명": app.get("항목명", ""),
            "차이금액_또는_MD": "-",
            "승인상태": app.get("승인여부_원본", ""),
            "원본_최초": "-",
            "원본_변경": f"{app.get('원본파일', '')} / {app.get('원본시트', '')} / {app.get('원본행', '')}행",
            "조치안내": f"승인번호 {app.get('승인번호', '')}에 해당하는 변경 항목이 견적서에 반영되지 않았습니다."
        })

    # 7. 읽기 경고 (낮음)
    for w in loader_warnings:
        if any(keyword in w for keyword in ["숫자 변환 실패", "음수", "중복 등장"]):
            review_list.append({
                "심각도": SEVERITY_LOW,
                "사유": "읽기 경고",
                "대상": "데이터",
                "항목코드": "-",
                "항목명": "-",
                "차이금액_또는_MD": "-",
                "승인상태": "-",
                "원본_최초": "-",
                "원본_변경": "-",
                "조치안내": w
            })

    return review_list

def calculate_summary(
    orig_items: List[Dict[str, Any]],
    rev_items: List[Dict[str, Any]],
    analyzed_estimates: List[Dict[str, Any]],
    analyzed_labor: List[Dict[str, Any]],
    review_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    orig_total = sum(it["금액"] for it in orig_items)
    rev_total = sum(it["금액"] for it in rev_items)
    diff_total = rev_total - orig_total
    diff_rate = (diff_total / orig_total * 100.0) if orig_total > 0 else 0.0

    confirmed_diff_sum = sum(
        it["차이금액"] for it in analyzed_estimates
        if it["연결상태"] == MATCH_CONFIRMED and it["변경유형"] not in [DIFF_TYPE_ADDED, DIFF_TYPE_DELETED]
    )
    unconfirmed_diff_sum = sum(
        it["차이금액"] for it in analyzed_estimates
        if it["연결상태"] == MATCH_NEEDS_CONFIRM
    )
    added_amount = sum(
        it["금액_변경"] for it in analyzed_estimates
        if it["변경유형"] == DIFF_TYPE_ADDED
    )
    deleted_amount = sum(
        it["금액_최초"] for it in analyzed_estimates
        if it["변경유형"] == DIFF_TYPE_DELETED
    )

    calc_rev_total = orig_total + confirmed_diff_sum + unconfirmed_diff_sum + added_amount - deleted_amount
    is_audit_balanced = abs(calc_rev_total - rev_total) < 1e-4

    approved_diff_sum = sum(
        it["차이금액"] for it in analyzed_estimates
        if it["승인상태"] == APPROVAL_APPROVED
    )
    unapproved_diff_sum = sum(
        it["차이금액"] for it in analyzed_estimates
        if it["승인상태"] in [APPROVAL_UNCONFIRMED, APPROVAL_REJECTED]
    )

    high_count = sum(1 for r in review_items if r["심각도"] == SEVERITY_HIGH)
    med_count = sum(1 for r in review_items if r["심각도"] == SEVERITY_MEDIUM)
    low_count = sum(1 for r in review_items if r["심각도"] == SEVERITY_LOW)
    needs_confirm_count = sum(1 for it in analyzed_estimates if it["연결상태"] == MATCH_NEEDS_CONFIRM)

    orig_md_sum = sum(it["MD_최초"] for it in analyzed_labor)
    rev_md_sum = sum(it["MD_변경"] for it in analyzed_labor)
    diff_md_sum = rev_md_sum - orig_md_sum
    diff_labor_cost = sum(it["차이_인건비"] for it in analyzed_labor)

    return {
        "orig_total": orig_total,
        "rev_total": rev_total,
        "diff_total": diff_total,
        "diff_rate": diff_rate,
        "confirmed_diff_sum": confirmed_diff_sum,
        "unconfirmed_diff_sum": unconfirmed_diff_sum,
        "added_amount": added_amount,
        "deleted_amount": deleted_amount,
        "is_audit_balanced": is_audit_balanced,
        "audit_discrepancy": calc_rev_total - rev_total,
        "approved_diff_sum": approved_diff_sum,
        "unapproved_diff_sum": unapproved_diff_sum,
        "high_count": high_count,
        "med_count": med_count,
        "low_count": low_count,
        "total_review_count": len(review_items),
        "needs_confirm_count": needs_confirm_count,
        "diff_md_sum": diff_md_sum,
        "diff_labor_cost": diff_labor_cost
    }
