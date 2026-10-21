# -*- coding: utf-8 -*-
"""auditor/analysis.py 단위 테스트 및 P001 기대값 검증"""

from pathlib import Path
import pytest

from auditor.loader import (
    load_workbook_safe,
    resolve_sheet,
    read_estimate_sheet,
    read_labor_sheet,
    read_approval_sheet
)
from auditor.matching import match_items
from auditor.analysis import (
    analyze_estimates,
    analyze_labor,
    build_review_items,
    calculate_summary,
    parse_approval_status
)
from auditor.schema import (
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_UNCONFIRMED,
    MATCH_CONFIRMED,
    MATCH_NEEDS_CONFIRM,
    SEVERITY_HIGH
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLES_DIR = DATA_DIR / "samples"

def test_parse_approval_status():
    assert parse_approval_status("승인")[0] == APPROVAL_APPROVED
    assert parse_approval_status("Y")[0] == APPROVAL_APPROVED
    assert parse_approval_status("반려")[0] == APPROVAL_REJECTED
    assert parse_approval_status("N")[0] == APPROVAL_REJECTED
    assert parse_approval_status("")[0] == APPROVAL_UNCONFIRMED
    assert parse_approval_status(None)[0] == APPROVAL_UNCONFIRMED
    assert parse_approval_status("보류")[0] == APPROVAL_UNCONFIRMED

def test_qty_price_effect_equation():
    """수량효과 + 단가효과 = 차이금액 검증"""
    orig_item = {"row_key": "o1", "항목코드": "E-001", "구분": "제작", "항목명": "아크릴", "수량": 20, "단가": 85000, "금액": 1700000}
    rev_item = {"row_key": "r1", "항목코드": "E-001", "구분": "제작", "항목명": "아크릴", "수량": 25, "단가": 90000, "금액": 2250000}
    
    matches = match_items([orig_item], [rev_item])
    analyzed, _ = analyze_estimates(matches, [orig_item], [rev_item], [])
    
    res = analyzed[0]
    expected_diff = 2250000 - 1700000
    assert res["차이금액"] == expected_diff
    assert res["수량효과"] + res["단가효과"] == expected_diff

def test_p001_full_analysis_expectation():
    """P001 샘플 데이터 전체 파이프라인 기대값 손계산 일치 검증"""
    wb_orig = load_workbook_safe(SAMPLES_DIR / "P001_최초견적.xlsx", "P001_최초견적.xlsx")
    ws_orig_est, sname_o, _ = resolve_sheet(wb_orig, "견적", "P001_최초견적.xlsx")
    orig_items, mismatches, orig_dup, orig_warn = read_estimate_sheet(ws_orig_est, "P001_최초견적.xlsx", sname_o)

    ws_orig_lab, sname_ol, _ = resolve_sheet(wb_orig, "인력", "P001_최초견적.xlsx")
    orig_labor, _, orig_lab_warn = read_labor_sheet(ws_orig_lab, "P001_최초견적.xlsx", sname_ol)

    wb_rev = load_workbook_safe(SAMPLES_DIR / "P001_변경내역.xlsx", "P001_변경내역.xlsx")
    ws_rev_est, sname_r, _ = resolve_sheet(wb_rev, "변경견적", "P001_변경내역.xlsx")
    rev_items, _, rev_dup, rev_warn = read_estimate_sheet(ws_rev_est, "P001_변경내역.xlsx", sname_r)

    ws_rev_app, sname_ra, _ = resolve_sheet(wb_rev, "변경승인", "P001_변경내역.xlsx")
    approval_records, _ = read_approval_sheet(ws_rev_app, "P001_변경내역.xlsx", sname_ra)

    ws_rev_lab, sname_rl, _ = resolve_sheet(wb_rev, "변경인력", "P001_변경내역.xlsx")
    rev_labor, _, rev_lab_warn = read_labor_sheet(ws_rev_lab, "P001_변경내역.xlsx", sname_rl)

    # 1. 항목 매칭
    matches = match_items(orig_items, rev_items, orig_dup, rev_dup)
    labor_matches = match_items(orig_labor, rev_labor)

    # 2. 분석 수행
    analyzed_estimates, orphan_apprs = analyze_estimates(matches, orig_items, rev_items, approval_records)
    analyzed_labor, used_lab_apprs = analyze_labor(labor_matches, approval_records)
    
    # 인력에서 사용된 승인은 고아 승인에서 제거
    orphan_apprs = [a for a in orphan_apprs if a["row_key"] not in used_lab_apprs]

    all_warnings = orig_warn + orig_lab_warn + rev_warn + rev_lab_warn
    review_items = build_review_items(
        analyzed_estimates, analyzed_labor, orphan_apprs, mismatches, all_warnings
    )
    summary = calculate_summary(
        orig_items, rev_items, analyzed_estimates, analyzed_labor, review_items
    )

    # 3. 손계산 금액 일치 검증
    # 최초 합계: 11,170,000원
    assert summary["orig_total"] == 11170000.0
    # 변경 합계: 13,550,000원
    assert summary["rev_total"] == 13550000.0
    # 증감액: 2,380,000원
    assert summary["diff_total"] == 2380000.0
    
    # 4. 검산 일치 검증 (최초합계 + 확정차이 + 미확정차이 + 추가 - 삭제 == 변경합계)
    assert summary["is_audit_balanced"] is True

    # 5. 주요 검토 항목 확인
    # 운송비: 반려됐는데 반영됨 (높음)
    assert any(r["항목코드"] == "E-006" and r["사유"] == "반려된 변경이 견적에 반영됨" for r in review_items)
    # 목공 받침대: 승인 미확인 (높음)
    assert any(r["항목코드"] == "E-002" and r["사유"] == "승인 미확인 변경 (견적)" for r in review_items)
    # LED 조명 모듈: 연결 확인 필요 (중간)
    assert any("LED 조명" in r["항목명"] and r["사유"] == "항목 연결 확인 필요" for r in review_items)
    # CR-07: 대응 변경 없음 (낮음)
    assert any("E-099" in r["항목코드"] and r["사유"] == "대응 변경 없음 승인 기록" for r in review_items)
