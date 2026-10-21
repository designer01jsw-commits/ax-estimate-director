# -*- coding: utf-8 -*-
"""auditor/diagnostics.py 단위 테스트"""

import pytest
from auditor.diagnostics import (
    OFFICIAL_BENCHMARKS,
    normalize_baseline,
    diagnose_estimate_item,
    diagnose_labor_item,
    generate_audit_judgment_report
)

def test_normalize_baseline():
    orig_items = [
        {"구분": "제작", "항목명": "아크릴", "단가": 100000, "금액": 200000},
        {"구분": "제작", "항목명": "목공", "단가": 200000, "금액": 400000},
    ]
    orig_labor = [
        {"공정": "설치", "역할": "목공", "단가": 300000, "일단가": 300000, "금액": 600000}
    ]
    norms = normalize_baseline(orig_items, orig_labor)
    assert "제작" in norms["cat_unit_prices"]
    assert norms["cat_unit_prices"]["제작"]["avg"] == 150000
    assert norms["role_daily_rates"]["목공"]["avg"] == 300000
    assert norms["total_orig_cost"] == 600000
    assert norms["total_orig_labor"] == 600000

def test_diagnose_rejected_item():
    item = {
        "항목명": "추가 그래픽 패널",
        "구분": "인쇄",
        "차이금액": 500000,
        "단가_최초": 40000,
        "단가_변경": 40000,
        "수량_최초": 10,
        "수량_변경": 20,
        "단가효과": 0,
        "수량효과": 500000,
        "변경유형": "증액",
        "승인상태": "반려",
        "승인번호": "CR-REJ-01"
    }
    diag = diagnose_estimate_item(item, {})
    assert diag["판정"] == "비적합"
    assert "반려" in diag["상세사유"]
    assert any("제외" in diag["조치사항"] or "삭감" in diag["조치사항"] for _ in [1])

def test_diagnose_price_surge():
    item = {
        "항목명": "특수 아크릴 케이스",
        "구분": "제작",
        "차이금액": 1200000,
        "단가_최초": 100000,
        "단가_변경": 160000,  # 60% 인상
        "수량_최초": 20,
        "수량_변경": 20,
        "단가효과": 1200000,
        "수량효과": 0,
        "변경유형": "증액",
        "승인상태": "미확인",
        "승인번호": ""
    }
    diag = diagnose_estimate_item(item, {})
    assert diag["판정"] == "비적합"
    assert "단가" in diag["상세사유"]
    assert any(c["기관"] == "조달청 나라장터 (G2B) / 한국물가협회" for c in diag["공공기준_근거"])

def test_diagnose_labor_excessive_daily_rate():
    # KIDP 총괄디자이너(412,000원)의 115%인 약 473,800원을 초과하는 600,000원 청구
    labor_item = {
        "공정": "디자인",
        "역할": "디자이너",
        "항목명": "원형 디자인",
        "인원_변경": 1.0,
        "일수_변경": 5.0,
        "단가_변경": 600000,
        "차이금액": 1000000
    }
    diag = diagnose_labor_item(labor_item, {})
    assert diag["판정"] == "비적합"
    assert "한국디자인진흥원" in diag["상세사유"]
    assert any("산업디자인진흥법" in c["법령"] for c in diag["공공기준_근거"])

def test_diagnose_labor_over_allocation():
    # 1일에 4명 집중 투입 -> 투입률 400%
    labor_item = {
        "공정": "설치",
        "역할": "목공",
        "항목명": "야간 설치",
        "인원_변경": 4.0,
        "일수_변경": 1.0,
        "단가_변경": 280000,
        "차이금액": 1120000
    }
    diag = diagnose_labor_item(labor_item, {})
    assert diag["판정"] == "비적합"
    assert any("근로기준법" in c["법령"] for c in diag["공공기준_근거"])

def test_generate_audit_judgment_report():
    diag_est = [{
        "항목명": "아크릴",
        "분해축": "단가/제작비",
        "판정": "비적합",
        "변동금액": 500000,
        "상세사유": "단가 과다",
        "공공기준_근거": [{"기관": "조달청", "법령": "국가계약법", "내용": "시장가격 초과", "URL": "https://www.g2b.go.kr"}],
        "조치사항": "단가 환원"
    }]
    diag_lab = [{
        "항목명": "설치/목공",
        "분해축": "인력비/투입률",
        "판정": "적합",
        "변동금액": 0,
        "상세사유": "정상 범위",
        "공공기준_근거": [],
        "조치사항": "승인"
    }]
    report = generate_audit_judgment_report(diag_est, diag_lab, {}, "테스트 프로젝트")
    assert "견적 정밀 감리 진단서 및 시정 요구서" in report
    assert "비적합" in report
    assert "조달청" in report
    assert "g2b.go.kr" in report
