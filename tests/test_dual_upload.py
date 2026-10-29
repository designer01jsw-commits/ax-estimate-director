# -*- coding: utf-8 -*-
"""
듀얼 직접 업로드(기준 견적서 + 비교 견적서 2개 동시 직접 업로드) 기능 검증 테스트
"""

import io
from pathlib import Path
import pytest
from auditor.loader import load_workbook_safe, read_estimate_sheet, find_best_estimate_sheet
from auditor.categorizer import decompose_estimate_by_category
from auditor.matching import match_items

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_dual_upload_file_parsing_and_audit():
    """사용자가 직접 업로드한 2개의 견적서 파일(BytesIO/파일객체)로 정밀 감리가 동작하는지 검증"""
    samples_dir = ROOT_DIR / "data" / "samples"
    
    orig_path = samples_dir / "2026_WIS_전시제작_완료견적서.xlsx"
    rev_path = samples_dir / "전시_홍대점_변경내역.xlsx"

    assert orig_path.exists()
    assert rev_path.exists()

    # Streamlit UploadedFile 객체를 흉내내는 BytesIO 파일 객체 생성
    orig_bytes = io.BytesIO(orig_path.read_bytes())
    orig_bytes.name = "사용자업로드_기준_WIS.xlsx"

    rev_bytes = io.BytesIO(rev_path.read_bytes())
    rev_bytes.name = "사용자업로드_비교_홍대.xlsx"

    # 1. 듀얼 파일 안전 로드
    wb_orig = load_workbook_safe(orig_bytes, orig_bytes.name)
    wb_rev = load_workbook_safe(rev_bytes, rev_bytes.name)

    assert len(wb_orig.sheetnames) > 0
    assert len(wb_rev.sheetnames) > 0

    # 2. 최적 시트 자동 탐색
    best_orig_sheet, _ = find_best_estimate_sheet(wb_orig)
    best_rev_sheet, _ = find_best_estimate_sheet(wb_rev)

    assert best_orig_sheet in wb_orig.sheetnames
    assert best_rev_sheet in wb_rev.sheetnames

    # 3. 듀얼 견적서 시트 파싱
    orig_items, _, _, _ = read_estimate_sheet(wb_orig[best_orig_sheet], orig_bytes.name, best_orig_sheet)
    rev_items, _, _, _ = read_estimate_sheet(wb_rev[best_rev_sheet], rev_bytes.name, best_rev_sheet)

    assert len(orig_items) > 0
    assert len(rev_items) > 0

    # 4. 7대 공종 분해
    decomp_orig = decompose_estimate_by_category(orig_items)
    decomp_rev = decompose_estimate_by_category(rev_items)

    assert decomp_orig.get("total_amount", 0) > 0
    assert decomp_rev.get("total_amount", 0) > 0

    # 5. 매칭 및 감리 수행
    matched_records = match_items(orig_items, rev_items)
    assert matched_records is not None
    assert isinstance(matched_records, list)
    assert len(matched_records) > 0

def test_app_py_contains_dual_upload_options():
    """app.py에 2단계 듀얼 직접 업로드 옵션이 정상 배치되어 있는지 검증"""
    app_py_path = ROOT_DIR / "app.py"
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드" in content
    assert "u_dual_baseline_file" in content
    assert "u_dual_target_file" in content
    assert "sb_baseline_source_mode" in content
