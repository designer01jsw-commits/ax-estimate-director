# -*- coding: utf-8 -*-
"""Unit test for studying client-confirmed estimate and registering to project database."""

from pathlib import Path
from auditor.projects import load_projects, save_project
from auditor.learning_engine import study_and_assetize_excel_estimate

def test_save_project_and_load():
    test_proj = {
        "project_id": "P_TEST_SAMPLE_99",
        "name": "테스트 자산화 프로젝트",
        "client": "테스트 클라이언트",
        "site": "테스트 베뉴",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "기준견적서4_전시_광고주컨펌.xlsx",
        "sample_change": None,
        "default_sheet": "1. 수원 사업장"
    }
    success = save_project(test_proj)
    assert success is True

    projects, _ = load_projects()
    found = next((p for p in projects if p["project_id"] == "P_TEST_SAMPLE_99"), None)
    assert found is not None
    assert found["name"] == "테스트 자산화 프로젝트"

    # Clean up test entry
    clean_projects = [p for p in projects if p["project_id"] != "P_TEST_SAMPLE_99"]
    import json
    from auditor.projects import DEFAULT_PROJECTS_FILE
    with open(DEFAULT_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_projects, f, ensure_ascii=False, indent=2)

def test_study_and_assetize_excel():
    sample_file = Path("data/samples/전시_홍대점_변경내역.xlsx")
    if not sample_file.exists():
        sample_file = Path("data/전시_홍대점_변경내역.xlsx")
    file_bytes = sample_file.read_bytes()

    proj_rec, decomp, items = study_and_assetize_excel_estimate(
        excel_bytes=file_bytes,
        file_name="테스트_확정견적서.xlsx",
        project_name="테스트 단위 플래그십",
        client="제일기획 테스트",
        venue="테스트 베뉴",
        currency="KRW"
    )

    assert proj_rec["project_id"].startswith("P_STUDIED_")
    assert proj_rec["status"] == "광고주 컨펌 완료"
    assert len(items) > 0
    assert decomp["total_amount"] > 0

    # Clean up
    projects, _ = load_projects()
    clean_projects = [p for p in projects if p["project_id"] != proj_rec["project_id"]]
    import json
    from auditor.projects import DEFAULT_PROJECTS_FILE
    with open(DEFAULT_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_projects, f, ensure_ascii=False, indent=2)
