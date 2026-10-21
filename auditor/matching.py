# -*- coding: utf-8 -*-
"""최초 견적 및 변경 견적 항목 연결 모듈"""

import difflib
import re
from typing import Any, Dict, List, Optional, Set, Tuple

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

def normalize_name(text: str) -> str:
    """소문자로 바꾸고 공백과 특수문자(괄호 제외)를 제거합니다."""
    if not text:
        return ""
    # 괄호 '(', ')', '[', ']'는 보존하고, 그 외 특수문자 및 공백 제거
    s = text.lower()
    # 영문, 숫자, 한글, 괄호류만 남기기
    cleaned = re.sub(r"[^\w\(\)\[\]]", "", s)
    return cleaned

def calculate_similarity(a: str, b: str) -> float:
    """두 문자열의 difflib SequenceMatcher 유사도를 계산하고 소수 둘째 자리로 반환합니다."""
    norm_a = normalize_name(a)
    norm_b = normalize_name(b)
    if not norm_a and not norm_b:
        return 1.0
    if not norm_a or not norm_b:
        return 0.0
    ratio = difflib.SequenceMatcher(None, norm_a, norm_b).ratio()
    return round(ratio, 2)

def match_items(
    orig_items: List[Dict[str, Any]],
    rev_items: List[Dict[str, Any]],
    orig_duplicate_codes: Set[str] = None,
    rev_duplicate_codes: Set[str] = None,
    user_decisions: Optional[Dict[Tuple[str, str], str]] = None
) -> List[Dict[str, Any]]:
    """최초 견적 항목과 변경 견적 항목을 5단계 규칙에 따라 매칭합니다.

    Args:
        orig_items: 최초 견적 행 목록
        rev_items: 변경 견적 행 목록
        orig_duplicate_codes: 최초 견적 내 중복 코드 집합
        rev_duplicate_codes: 변경 견적 내 중복 코드 집합
        user_decisions: {(orig_row_key, rev_row_key): "같은 항목" | "다른 항목"} 사용자 수동 결정 맵
    """
    orig_dup = orig_duplicate_codes or set()
    rev_dup = rev_duplicate_codes or set()
    decisions = user_decisions or {}

    matched_pairs: List[Dict[str, Any]] = []
    unmatched_orig = list(orig_items)
    unmatched_rev = list(rev_items)

    # 1. 코드 일치 (유일한 코드)
    # 양쪽에서 중복되지 않은 유효한 코드를 추출
    orig_by_code: Dict[str, List[Dict[str, Any]]] = {}
    for it in unmatched_orig:
        code = it.get("항목코드", "").strip()
        if code and code not in orig_dup:
            orig_by_code.setdefault(code, []).append(it)

    rev_by_code: Dict[str, List[Dict[str, Any]]] = {}
    for it in unmatched_rev:
        code = it.get("항목코드", "").strip()
        if code and code not in rev_dup:
            rev_by_code.setdefault(code, []).append(it)

    common_codes = set(c for c, l in orig_by_code.items() if len(l) == 1) & \
                   set(c for c, l in rev_by_code.items() if len(l) == 1)

    for code in common_codes:
        o_item = orig_by_code[code][0]
        r_item = rev_by_code[code][0]
        sim = calculate_similarity(o_item.get("항목명", ""), r_item.get("항목명", ""))
        
        if sim >= 0.5:
            status = MATCH_CONFIRMED
            method = METHOD_CODE_EXACT
        else:
            status = MATCH_NEEDS_CONFIRM
            method = METHOD_CODE_DIFF_NAME

        matched_pairs.append({
            "orig_item": o_item,
            "rev_item": r_item,
            "match_status": status,
            "match_method": method,
            "similarity": sim,
            "orig_row_key": o_item.get("row_key", ""),
            "rev_row_key": r_item.get("row_key", "")
        })
        unmatched_orig.remove(o_item)
        unmatched_rev.remove(r_item)

    # 2. 이름 일치 (남은 행 중 구분과 정규화한 항목명이 같고 유일한 경우)
    orig_by_cat_name: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for it in unmatched_orig:
        cat = it.get("구분", "").strip()
        norm_name = normalize_name(it.get("항목명", ""))
        if norm_name:
            orig_by_cat_name.setdefault((cat, norm_name), []).append(it)

    rev_by_cat_name: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for it in unmatched_rev:
        cat = it.get("구분", "").strip()
        norm_name = normalize_name(it.get("항목명", ""))
        if norm_name:
            rev_by_cat_name.setdefault((cat, norm_name), []).append(it)

    common_names = set(k for k, l in orig_by_cat_name.items() if len(l) == 1) & \
                   set(k for k, l in rev_by_cat_name.items() if len(l) == 1)

    for k in common_names:
        o_item = orig_by_cat_name[k][0]
        r_item = rev_by_cat_name[k][0]
        matched_pairs.append({
            "orig_item": o_item,
            "rev_item": r_item,
            "match_status": MATCH_CONFIRMED,
            "match_method": METHOD_NAME_EXACT,
            "similarity": 1.0,
            "orig_row_key": o_item.get("row_key", ""),
            "rev_row_key": r_item.get("row_key", "")
        })
        unmatched_orig.remove(o_item)
        unmatched_rev.remove(r_item)

    # 3. 유사 이름 후보 (같은 구분 안에서 유사도 >= 0.6 탐욕 매칭)
    candidate_pairs = []
    for o_item in unmatched_orig:
        o_cat = o_item.get("구분", "").strip()
        o_name = o_item.get("항목명", "")
        for r_item in unmatched_rev:
            r_cat = r_item.get("구분", "").strip()
            # 같은 구분이거나 구분이 둘 다 비어있는 경우
            if o_cat == r_cat:
                sim = calculate_similarity(o_name, r_item.get("항목명", ""))
                if sim >= 0.6:
                    candidate_pairs.append((sim, o_item, r_item))

    # 유사도 내림차순 정렬
    candidate_pairs.sort(key=lambda x: x[0], reverse=True)
    used_orig_keys = set()
    used_rev_keys = set()

    for sim, o_item, r_item in candidate_pairs:
        okey = o_item["row_key"]
        rkey = r_item["row_key"]
        if okey not in used_orig_keys and rkey not in used_rev_keys:
            used_orig_keys.add(okey)
            used_rev_keys.add(rkey)
            matched_pairs.append({
                "orig_item": o_item,
                "rev_item": r_item,
                "match_status": MATCH_NEEDS_CONFIRM,
                "match_method": METHOD_SIMILAR_NAME,
                "similarity": sim,
                "orig_row_key": okey,
                "rev_row_key": rkey
            })
            unmatched_orig.remove(o_item)
            unmatched_rev.remove(r_item)

    # 4. 사용자 결정 반영
    final_pairs = []
    for pair in matched_pairs:
        okey = pair["orig_row_key"]
        rkey = pair["rev_row_key"]
        dec = decisions.get((okey, rkey))
        if dec == "같은 항목":
            pair["match_status"] = MATCH_CONFIRMED
            pair["match_method"] = METHOD_USER_CONFIRMED
            final_pairs.append(pair)
        elif dec == "다른 항목":
            # 연결을 풀고 각각 삭제, 추가로 분리
            unmatched_orig.append(pair["orig_item"])
            unmatched_rev.append(pair["rev_item"])
        else:
            final_pairs.append(pair)

    # 5. 연결되지 않은 행 (삭제 및 추가)
    for o_item in unmatched_orig:
        final_pairs.append({
            "orig_item": o_item,
            "rev_item": None,
            "match_status": MATCH_CONFIRMED,
            "match_method": "삭제 항목",
            "similarity": 0.0,
            "orig_row_key": o_item.get("row_key", ""),
            "rev_row_key": ""
        })

    for r_item in unmatched_rev:
        final_pairs.append({
            "orig_item": None,
            "rev_item": r_item,
            "match_status": MATCH_CONFIRMED,
            "match_method": "추가 항목",
            "similarity": 0.0,
            "orig_row_key": "",
            "rev_row_key": r_item.get("row_key", "")
        })

    return final_pairs
