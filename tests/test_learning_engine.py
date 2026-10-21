# -*- coding: utf-8 -*-
import pytest
from auditor.learning_engine import (
    load_learned_cases,
    save_new_learned_case,
    find_similar_learned_cases,
    get_learning_statistics
)

def test_load_learned_cases():
    cases = load_learned_cases()
    assert len(cases) >= 4
    first = cases[0]
    assert "case_id" in first
    assert "name" in first
    assert "settled_amount" in first
    assert first["settled_amount"] > 0

def test_find_similar_learned_cases():
    results = find_similar_learned_cases(
        target_type="스마트 체험 키트 / 원형 개발",
        target_scale="소형 (1~3평 / 단일 키트 1~2대)",
        target_tier="고급형 (Premium)",
        hints="갈바 EGI 프레임 턴테이블 서보모터",
        top_k=2
    )
    assert len(results) >= 1
    top_res = results[0]
    assert top_res["similarity_score"] >= 70.0
    assert "case" in top_res
    assert "S26" in top_res["case"]["name"] or "키트" in top_res["case"]["name"]

def test_save_new_learned_case_and_stats():
    initial_stats = get_learning_statistics()
    initial_count = initial_stats["total_cases"]

    new_case = save_new_learned_case(
        image_bytes=None,
        name="테스트 전시 부스 프로젝트 2026",
        client="제일기획 테스트",
        project_type="팝업스토어 / 전시 부스",
        settled_amount=50000000,
        scale="중형 (5~15평 / 키트 3~5대)",
        unit_count=10,
        unit_label="평당 시공비",
        tier="표준형 (Standard)",
        materials=["목재 가벽", "도장 마감"],
        labor_md=12.0,
        key_specs="MDF 가벽 및 목공 시공",
        benchmark_cites="KBIZ 시중노임 준용",
        preset_img_key="GALAXY_POPUP"
    )

    assert new_case["unit_cost"] == 5000000
    assert new_case["settled_amount"] == 50000000

    updated_stats = get_learning_statistics()
    assert updated_stats["total_cases"] == initial_count + 1
    assert updated_stats["total_learned_budget"] >= 50000000
