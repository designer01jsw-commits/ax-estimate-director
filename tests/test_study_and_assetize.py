# -*- coding: utf-8 -*-
"""Unit test for studying client-confirmed estimate and registering to project database."""

from pathlib import Path
import json
from auditor.projects import load_projects, save_project, DEFAULT_PROJECTS_FILE
from auditor.learning_engine import (
    study_and_assetize_excel_estimate,
    preview_excel_estimate,
    save_new_learned_case,
    load_learned_cases,
    CASES_FILE
)

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

    # Ensure it appears at index 0 of load_projects()
    projects, _ = load_projects()
    assert projects[0]["project_id"] == proj_rec["project_id"]

    # Clean up
    clean_projects = [p for p in projects if p["project_id"] != proj_rec["project_id"]]
    with open(DEFAULT_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_projects, f, ensure_ascii=False, indent=2)

    cases = load_learned_cases()
    deleted_case = next((c for c in cases if c.get("name") == "테스트 단위 플래그십"), None)
    if deleted_case:
        for p in Path("data/learned_images").glob(f"{deleted_case['case_id']}*"):
            p.unlink(missing_ok=True)
    clean_cases = [c for c in cases if c.get("name") != "테스트 단위 플래그십"]
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_cases, f, ensure_ascii=False, indent=2)

    for p in [Path("data/테스트_확정견적서.xlsx"), Path("data/samples/테스트_확정견적서.xlsx")]:
        if p.exists():
            p.unlink(missing_ok=True)

def test_preview_excel_estimate():
    sample_file = Path("data/samples/기준견적서4_전시_광고주컨펌.xlsx")
    if not sample_file.exists():
        sample_file = Path("data/기준견적서4_전시_광고주컨펌.xlsx")
    file_bytes = sample_file.read_bytes()

    preview = preview_excel_estimate(file_bytes, sample_file.name)
    assert len(preview["sheets"]) > 0
    assert preview["item_count"] > 0
    assert preview["total_budget"] > 0
    assert "categories" in preview
    assert len(preview["materials"]) > 0

def test_manual_learned_case_registers_baseline_project():
    saved = save_new_learned_case(
        image_bytes=None,
        name="테스트 수동 등록 실적 2026",
        client="삼성전자 / 제일기획",
        project_type="팝업스토어 / 전시 부스",
        settled_amount=45000000,
        scale="중형 (5~15평 / 키트 3~5대)",
        unit_count=5,
        unit_label="평당 시공비",
        tier="표준형 (Standard)",
        materials=["갈바 EGI 스틸", "우레탄 도장", "아크릴"],
        labor_md=12.0,
        key_specs="맞춤 제작 및 야간 시공 포함",
        benchmark_cites="KBIZ 시중노임 준용",
        preset_img_key="GALAXY_POPUP",
        register_to_projects=True
    )

    assert saved["project_id"] is not None
    assert saved["project_id"].startswith("P_CASE_")

    # Check that it was registered into projects.json and is first in load_projects()
    projects, _ = load_projects()
    assert projects[0]["project_id"] == saved["project_id"]
    assert projects[0]["status"] == "광고주 컨펌 완료"
    assert projects[0]["total_budget"] == 45000000

    # Clean up projects.json
    clean_projects = [p for p in projects if p["project_id"] != saved["project_id"]]
    with open(DEFAULT_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_projects, f, ensure_ascii=False, indent=2)

    # Clean up learned_cases.json
    cases = load_learned_cases()
    clean_cases = [c for c in cases if c.get("case_id") != saved["case_id"]]
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_cases, f, ensure_ascii=False, indent=2)

    # Clean up excel and image file
    for p in [Path(f"data/CONFIRMED_{saved['case_id']}.xlsx"), Path(f"data/samples/CONFIRMED_{saved['case_id']}.xlsx")]:
        if p.exists():
            p.unlink(missing_ok=True)
    for p in Path("data/learned_images").glob(f"{saved['case_id']}*"):
        p.unlink(missing_ok=True)
