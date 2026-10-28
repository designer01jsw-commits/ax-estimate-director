# -*- coding: utf-8 -*-
"""
3대 대형 전시 공인 실적 및 비전 AI 200평/300평 대형 전시 산출기 검증 테스트
"""

from pathlib import Path
import pytest
from auditor.projects import load_projects
from auditor.learning_engine import load_learned_cases
from auditor.loader import load_workbook_safe, read_estimate_sheet, find_best_estimate_sheet
from auditor.vision_estimator import estimate_costs_from_vision, find_ground_truth_kit, load_preset_image_bytes, SAMPLE_PRESETS

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_3_real_exhibition_projects_registered():
    """3대 대형 전시 프로젝트가 projects.json에 정상 등록되었는지 검증"""
    projects, warnings = load_projects()
    project_ids = [p["project_id"] for p in projects]

    assert "P_EXHIBITION_KES_2025" in project_ids
    assert "P_EXHIBITION_WIS_2026" in project_ids
    assert "P_EXHIBITION_GALAXY_AUG" in project_ids

    kes_proj = next(p for p in projects if p["project_id"] == "P_EXHIBITION_KES_2025")
    assert kes_proj["total_budget"] == 572898438
    assert kes_proj["default_sheet"] == "2025 KES_전시 제작"
    assert kes_proj["is_studied_asset"] is True

    wis_proj = next(p for p in projects if p["project_id"] == "P_EXHIBITION_WIS_2026")
    assert wis_proj["total_budget"] == 359989875
    assert wis_proj["default_sheet"] == "2026 WIS_전시 제작(수정2)"

    gal_proj = next(p for p in projects if p["project_id"] == "P_EXHIBITION_GALAXY_AUG")
    assert gal_proj["total_budget"] == 231000000
    assert gal_proj["default_sheet"] == "★1. 공통_거래명세서★"

def test_3_real_exhibition_files_readable():
    """3대 엑셀 파일이 data/samples/에 존재하며 시트 파싱이 정상 동작하는지 검증"""
    samples_dir = ROOT_DIR / "data" / "samples"
    
    files_to_check = [
        ("2025_KES_한국전자전_전시제작견적서.xlsx", "2025 KES_전시 제작", 70),
        ("2026_WIS_전시제작_완료견적서.xlsx", "2026 WIS_전시 제작(수정2)", 60),
        ("2026_8월_갤럭시스튜디오_완료견적서.xlsx", "★1. 공통_거래명세서★", 5)
    ]

    for fname, sheet_name, min_items in files_to_check:
        fpath = samples_dir / fname
        assert fpath.exists(), f"File {fname} not found in {samples_dir}"
        wb = load_workbook_safe(fpath, fname)
        assert sheet_name in wb.sheetnames, f"Sheet {sheet_name} not found in {fname}"
        
        items, _, _, _ = read_estimate_sheet(wb[sheet_name], fname, sheet_name)
        assert len(items) >= min_items, f"Expected at least {min_items} items in {sheet_name}, got {len(items)}"
        total_sum = sum(it.get("금액", 0) for it in items)
        assert total_sum > 100000000, f"Expected total > 100M in {sheet_name}, got {total_sum}"

def test_vision_estimator_large_scales_and_presets():
    """비전 AI 200평 이상, 300평 이상 대형 전시 산출 및 3대 프리셋 연동 검증"""
    # 1. 300평 이상 메가 엑스포 산출 테스트
    res_kes = estimate_costs_from_vision(
        features={},
        project_type="대형 행사 / 베뉴 전시",
        scale="초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)",
        tier="고급형 (Premium - 코엑스 메가 전시)",
        preset_key="KES_2025"
    )
    assert res_kes["summary"]["total_cost"] >= 500000000  # 약 5.5억~6.0억 수준
    assert any("트러스" in it["항목명"] for it in res_kes["items"])
    assert any("LED" in it["항목명"] for it in res_kes["items"])
    assert any("보험료" in it["항목명"] for it in res_kes["items"])
    assert res_kes["ground_truth"]["matched"] is True
    assert res_kes["ground_truth"]["settled_amount"] == 572898438

    # 2. 200평 이상 초대형 전시 산출 테스트
    res_wis = estimate_costs_from_vision(
        features={},
        project_type="대형 행사 / 베뉴 전시",
        scale="초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)",
        tier="고급형 (Premium - 코엑스 대형 전시)",
        preset_key="WIS_2026"
    )
    assert res_wis["summary"]["total_cost"] >= 330000000  # 약 3.5억~4.0억 수준
    assert res_wis["ground_truth"]["matched"] is True
    assert res_wis["ground_truth"]["settled_amount"] == 359989875

    # 3. 50~100평 대형 전시 산출 테스트
    res_gal = estimate_costs_from_vision(
        features={},
        project_type="팝업스토어 / 전시 부스",
        scale="대형 전시 (50~100평 / 메인 부스·단독관)",
        tier="표준형 (Standard - 멀티 베뉴 팝업)",
        preset_key="GALAXY_AUG"
    )
    assert res_gal["summary"]["total_cost"] >= 160000000
    assert res_gal["ground_truth"]["matched"] is True
    assert res_gal["ground_truth"]["settled_amount"] == 231000000

def test_preset_image_bytes_loaded():
    """3대 대형 전시 프리셋의 실물 이미지 바이트가 정상 로드되는지 검증"""
    for pkey in ["KES_2025", "WIS_2026", "GALAXY_AUG"]:
        img_bytes = load_preset_image_bytes(pkey)
        assert img_bytes is not None
        assert len(img_bytes) > 10000, f"Preset {pkey} image bytes too small: {len(img_bytes)}"
