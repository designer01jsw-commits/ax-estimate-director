# -*- coding: utf-8 -*-
"""Unit tests for 7-category decomposition and cross-project reasonableness audit."""

from auditor.categorizer import (
    classify_item,
    decompose_estimate_by_category,
    compare_decomposed_estimates,
    audit_all_new_items,
    generate_cross_project_audit_report
)

def test_classify_item():
    cat1, _ = classify_item("컨셉 기획 및 3D 모델링")
    assert cat1 == "DESIGN_DEV"

    cat2, _ = classify_item("갈바 프레임 분체도장 및 MDF 집기 제작")
    assert cat2 == "FIXTURE_FABRICATION"

    cat3, _ = classify_item("아크릴 레이저 조각 10T")
    assert cat3 == "ACRYLIC_SPECIAL"

    cat4, _ = classify_item("전면 UV 실사출력 래핑")
    assert cat4 == "GRAPHIC_SIGN"

    cat5, _ = classify_item("쇼룸 매립형 LED 조명 배선")
    assert cat5 == "AV_LIGHT_ELEC"

    cat6, _ = classify_item("5톤 화물차 운송 및 양중 사다리")
    assert cat6 == "LOGISTICS_INSTALL"

    cat7, _ = classify_item("인테리어 목수 및 전기공 인건비 M/D")
    assert cat7 == "LABOR_ONSITE"

def test_decompose_estimate():
    items = [
        {"항목명": "MDF 집기", "규격": "", "수량": 2, "단가": 1000000, "금액": 2000000},
        {"항목명": "UV 실사출력", "규격": "", "수량": 5, "단가": 200000, "금액": 1000000},
    ]
    decomp = decompose_estimate_by_category(items)
    assert decomp["total_amount"] == 3000000
    assert decomp["item_count"] == 2
    assert decomp["categories"]["FIXTURE_FABRICATION"]["total_amount"] == 2000000
    assert decomp["categories"]["GRAPHIC_SIGN"]["total_amount"] == 1000000

def test_audit_new_items_benchmarking():
    base_items = [
        {"항목명": "MDF 집기", "규격": "1000x500", "수량": 1, "단가": 1000000, "금액": 1000000}
    ]
    base_decomp = decompose_estimate_by_category(base_items)
    
    # New item with +50% price -> should be flagged as 과다 의심
    new_items = [
        {"항목명": "MDF 집기", "규격": "1000x500", "수량": 2, "단가": 1500000, "금액": 3000000}
    ]
    new_decomp = decompose_estimate_by_category(new_items)
    
    results, excess_amt, fair, caution, excess = audit_all_new_items(
        new_items, base_items, base_decomp, currency="KRW"
    )
    assert excess == 1
    assert excess_amt == 1000000  # (1,500,000 - 1,000,000) * 2
    assert "과다 의심" in results[0]["판정"]
