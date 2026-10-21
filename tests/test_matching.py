# -*- coding: utf-8 -*-
"""auditor/matching.py 단위 테스트"""

import pytest
from auditor.matching import match_items, normalize_name, calculate_similarity
from auditor.schema import (
    MATCH_CONFIRMED,
    MATCH_NEEDS_CONFIRM,
    METHOD_CODE_EXACT,
    METHOD_CODE_DIFF_NAME,
    METHOD_NAME_EXACT,
    METHOD_SIMILAR_NAME,
    METHOD_USER_CONFIRMED,
    DIFF_TYPE_ADDED,
    DIFF_TYPE_DELETED
)

def test_normalize_name():
    assert normalize_name("LED 조명 모듈 (12V)") == "led조명모듈(12v)"
    assert normalize_name("  아크릴-케이스!  ") == "아크릴케이스"

def test_calculate_similarity():
    sim = calculate_similarity("LED 조명 모듈", "LED 조명모듈(고휘도)")
    assert sim >= 0.6

def test_match_code_exact():
    """코드 일치 & 유사도 >= 0.5 -> 확정"""
    orig = [{"row_key": "o1", "항목코드": "E-001", "구분": "제작", "항목명": "아크릴 케이스"}]
    rev = [{"row_key": "r1", "항목코드": "E-001", "구분": "제작", "항목명": "아크릴 케이스 (개선)"}]
    matches = match_items(orig, rev)
    assert len(matches) == 1
    assert matches[0]["match_status"] == MATCH_CONFIRMED
    assert matches[0]["match_method"] == METHOD_CODE_EXACT

def test_match_code_diff_name():
    """코드 일치 & 유사도 < 0.5 -> 확인 필요"""
    orig = [{"row_key": "o1", "항목코드": "E-001", "구분": "제작", "항목명": "완전 다른 품목명"}]
    rev = [{"row_key": "r1", "항목코드": "E-001", "구분": "제작", "항목명": "알 수 없는 기계"}]
    matches = match_items(orig, rev)
    assert len(matches) == 1
    assert matches[0]["match_status"] == MATCH_NEEDS_CONFIRM
    assert matches[0]["match_method"] == METHOD_CODE_DIFF_NAME

def test_match_name_exact():
    """코드 없고 구분+이름 일치 -> 확정"""
    orig = [{"row_key": "o1", "항목코드": "A", "구분": "인쇄", "항목명": "그래픽 패널 출력"}]
    rev = [{"row_key": "r1", "항목코드": "", "구분": "인쇄", "항목명": "그래픽 패널 출력"}]
    matches = match_items(orig, rev)
    assert len(matches) == 1
    assert matches[0]["match_status"] == MATCH_CONFIRMED
    assert matches[0]["match_method"] == METHOD_NAME_EXACT

def test_match_similar_name():
    """같은 구분 내 유사 이름 후보 -> 확인 필요"""
    orig = [{"row_key": "o1", "항목코드": "E-004", "구분": "전기전자", "항목명": "LED 조명 모듈"}]
    rev = [{"row_key": "r1", "항목코드": "", "구분": "전기전자", "항목명": "LED 조명모듈(고휘도)"}]
    matches = match_items(orig, rev)
    assert len(matches) == 1
    assert matches[0]["match_status"] == MATCH_NEEDS_CONFIRM
    assert matches[0]["match_method"] == METHOD_SIMILAR_NAME

def test_match_user_decision():
    """사용자 수동 결정: 같은 항목 확정 및 다른 항목 분리"""
    orig = [{"row_key": "o1", "항목코드": "E-004", "구분": "전기전자", "항목명": "LED 조명 모듈"}]
    rev = [{"row_key": "r1", "항목코드": "", "구분": "전기전자", "항목명": "LED 조명모듈(고휘도)"}]
    
    # 1. '같은 항목' 결정
    matches_same = match_items(orig, rev, user_decisions={("o1", "r1"): "같은 항목"})
    assert len(matches_same) == 1
    assert matches_same[0]["match_status"] == MATCH_CONFIRMED
    assert matches_same[0]["match_method"] == METHOD_USER_CONFIRMED

    # 2. '다른 항목' 결정 -> 삭제 1개 + 추가 1개로 분리
    matches_diff = match_items(orig, rev, user_decisions={("o1", "r1"): "다른 항목"})
    assert len(matches_diff) == 2
    del_item = [m for m in matches_diff if m["rev_item"] is None][0]
    add_item = [m for m in matches_diff if m["orig_item"] is None][0]
    assert del_item["orig_item"]["항목코드"] == "E-004"
    assert add_item["rev_item"]["항목명"] == "LED 조명모듈(고휘도)"
