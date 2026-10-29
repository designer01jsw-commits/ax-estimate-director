# -*- coding: utf-8 -*-
"""
견적감독관 전 기능 정밀 정밀 진단 & 스트레스 검사 스크립트
(System Health & Full Functional Precision Audit)
"""

import sys
import io
import time
import json
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.stdout.reconfigure(encoding='utf-8')

from auditor.projects import load_projects, GUARANTEED_CORE_PROJECTS
from auditor.learning_engine import (
    load_learned_cases,
    preview_excel_estimate,
    study_and_assetize_excel_estimate,
    find_similar_learned_cases,
    get_learning_statistics
)
from auditor.loader import (
    load_workbook_safe,
    read_estimate_sheet,
    find_best_estimate_sheet,
    get_common_sheet_names
)
from auditor.categorizer import decompose_estimate_by_category, COST_CATEGORIES
from auditor.matching import match_items
from auditor.diagnostics import (
    diagnose_estimate_item,
    normalize_baseline,
    generate_audit_judgment_report,
    generate_executive_supervisor_opinion
)
from auditor.export import export_to_csv_bytes, generate_csv_filename
from auditor.vision_estimator import (
    estimate_costs_from_vision,
    find_ground_truth_kit,
    load_preset_image_bytes,
    export_estimate_to_excel_bytes,
    SAMPLE_PRESETS
)
from auditor.vision_ui import convert_vision_estimate_to_auditor_items

RESULTS = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "warnings": [],
    "details": []
}

def log_test(category: str, test_name: str, passed: bool, message: str = ""):
    RESULTS["total_tests"] += 1
    if passed:
        RESULTS["passed_tests"] += 1
        status_sym = "✅ PASS"
    else:
        RESULTS["failed_tests"] += 1
        status_sym = "❌ FAIL"
    
    entry = f"[{category}] {status_sym} - {test_name}: {message}"
    RESULTS["details"].append(entry)
    print(entry)

def run_inspection():
    print("=" * 70)
    print("🚀 [견적감독관 AX] 전 기능 정밀 전수 검사 (Full Functional Precision Audit)")
    print("=" * 70)

    # -------------------------------------------------------------
    # SECTION 1: 데이터베이스 및 실적 에셋 무결성 검사
    # -------------------------------------------------------------
    print("\n[SECTION 1: 데이터베이스 및 공인 실적 에셋 무결성]")
    projects, prj_warnings = load_projects()
    log_test("DB", "projects.json 로드", len(projects) >= 7, f"총 {len(projects)}개 프로젝트 등록됨")
    
    # 3대 대형 전시 프로젝트 등록 확인
    p_ids = [p["project_id"] for p in projects]
    log_test("DB", "2025 KES 메가 전시관 등재", "P_EXHIBITION_KES_2025" in p_ids, "₩572,898,438 / 300평 이상")
    log_test("DB", "2026 WIS 메인 전시관 등재", "P_EXHIBITION_WIS_2026" in p_ids, "₩359,989,875 / 200평 이상")
    log_test("DB", "2026 8월 갤럭시 스튜디오 등재", "P_EXHIBITION_GALAXY_AUG" in p_ids, "₩231,000,000 / 100평 규모")

    # 파일 존재 확인
    samples_dir = ROOT_DIR / "data" / "samples"
    for p in projects[:5]:
        sf = p.get("sample_estimate")
        if sf:
            p_file = samples_dir / sf
            exists = p_file.exists() and p_file.stat().st_size > 1000
            sz_kb = (p_file.stat().st_size / 1024) if exists else 0
            log_test("FILE_ASSET", f"샘플 파일 존재 ({sf})", exists, f"{sz_kb:.1f} KB")

    # 이미지 파일 존재 확인
    images_dir = ROOT_DIR / "data" / "learned_images"
    for img_name in ["2025_KES_MEGA.png", "2026_WIS_COEX.png", "GALAXY_AUG_HYUNDAI.jpg"]:
        ip = images_dir / img_name
        exists = ip.exists() and ip.stat().st_size > 10000
        sz_kb = (ip.stat().st_size / 1024) if exists else 0
        log_test("IMAGE_ASSET", f"실물 사진 존재 ({img_name})", exists, f"{sz_kb:.1f} KB")

    # learned_cases.json 무결성
    cases = load_learned_cases()
    log_test("CBR_DB", "learned_cases.json 로드", len(cases) >= 44, f"총 {len(cases)}개 케이스 로드됨")

    # -------------------------------------------------------------
    # SECTION 2: 1모드 - 기준 견적 정밀 감리 & 진단 엔진 검사
    # -------------------------------------------------------------
    print("\n[SECTION 2: 1모드 - 기준 견적 정밀 감리 & 진단 엔진]")
    
    # Test 2A: 3대 실적 전시(KES / WIS / 갤럭시스튜디오) 시트 파싱 및 7대 공종 분해
    for p_id, expected_sheet, min_items, target_budget in [
        ("P_EXHIBITION_KES_2025", "2025 KES_전시 제작", 75, 572898438),
        ("P_EXHIBITION_WIS_2026", "2026 WIS_전시 제작(수정2)", 60, 359989875),
        ("P_EXHIBITION_GALAXY_AUG", "★1. 공통_거래명세서★", 5, 231000000)
    ]:
        p = next(x for x in projects if x["project_id"] == p_id)
        fpath = samples_dir / p["sample_estimate"]
        wb = load_workbook_safe(fpath, fpath.name)
        best_s, _ = find_best_estimate_sheet(wb, p.get("default_sheet"))
        log_test("AUDIT_PARSE", f"최적 시트 자동선택 ({p_id})", best_s == expected_sheet, f"선택 시트: {best_s}")

        items, mismatches, dupes, warns = read_estimate_sheet(wb[best_s], fpath.name, best_s)
        log_test("AUDIT_PARSE", f"품목 파싱 수량 ({p_id})", len(items) >= min_items, f"{len(items)}개 품목 추출 완료")

        decomp = decompose_estimate_by_category(items)
        tot_amt = int(decomp.get("total_amount", 0))
        pct_err = abs(tot_amt - target_budget) / target_budget * 100 if target_budget else 0
        log_test("AUDIT_DECOMP", f"7대 공종 정규화 예산 정합 ({p_id})", pct_err < 5.0, f"추출 ₩{tot_amt:,d} / 목표 ₩{target_budget:,d} (오차 {pct_err:.2f}%)")

    # Test 2B: 신구 대조 매칭 & 3단계 신호등 판정 & 삭감액 산출
    wb_orig = load_workbook_safe(samples_dir / "2026_WIS_전시제작_완료견적서.xlsx", "WIS.xlsx")
    wb_rev = load_workbook_safe(samples_dir / "전시_홍대점_변경내역.xlsx", "홍대변경.xlsx")
    
    orig_items, _, _, _ = read_estimate_sheet(wb_orig["2026 WIS_전시 제작(수정2)"], "WIS.xlsx", "2026 WIS_전시 제작(수정2)")
    rev_items, _, _, _ = read_estimate_sheet(wb_rev["변경견적"], "홍대변경.xlsx", "변경견적")

    matched_records = match_items(orig_items, rev_items)
    log_test("AUDIT_MATCH", "항목 매칭 실행", len(matched_records) > 0, f"{len(matched_records)}개 매칭 레코드 생성")

    # 공공 기준 진단
    baseline_norms = normalize_baseline(orig_items, [])
    diagnosed = [diagnose_estimate_item(it, baseline_norms) for it in rev_items]
    fit_cnt = len([d for d in diagnosed if d["판정"] == "적합"])
    warn_cnt = len([d for d in diagnosed if d["판정"] == "주의"])
    unfit_cnt = len([d for d in diagnosed if d["판정"] == "비적합"])
    log_test("AUDIT_DIAGNOSE", "3단계 신호등 진단", len(diagnosed) == len(rev_items), f"적합 {fit_cnt}건, 주의 {warn_cnt}건, 비적합 {unfit_cnt}건")

    # 보고서 내보내기 검증
    md_report = generate_audit_judgment_report(
        diagnosed_estimates=diagnosed,
        diagnosed_labor=[],
        summary={"total_orig": 359989875, "total_rev": 48200000, "total_diff": -311789875, "diff_pct": -86.6},
        project_name="정밀 검사 프로젝트"
    )
    opinion = generate_executive_supervisor_opinion(
        diagnosed_estimates=diagnosed,
        diagnosed_labor=[],
        summary={"total_orig": 359989875, "total_rev": 48200000, "total_diff": -311789875, "diff_pct": -86.6}
    )
    opinion_doc = opinion.get("verdict_md", "")
    csv_bytes = export_to_csv_bytes(diagnosed)
    log_test("EXPORT_MD", "공식 감리 진단서 및 시정 요구서 마크다운 생성", len(md_report) > 300 and len(opinion_doc) > 100, f"감리 진단서 {len(md_report)}자, 최고감리관 종합소견 {len(opinion_doc)}자")
    log_test("EXPORT_CSV", "감리 결과 CSV 내보내기", len(csv_bytes) > 500, f"{len(csv_bytes)} 바이트 CSV 생성 완료")

    # Test 2C: 듀얼 직접 업로드 모드 시뮬레이션
    buf_orig = io.BytesIO((samples_dir / "2026_WIS_전시제작_완료견적서.xlsx").read_bytes())
    buf_orig.name = "Custom_Base_WIS.xlsx"
    buf_rev = io.BytesIO((samples_dir / "전시_홍대점_변경내역.xlsx").read_bytes())
    buf_rev.name = "Custom_Target_Hongdae.xlsx"

    wb_custom_orig = load_workbook_safe(buf_orig, buf_orig.name)
    wb_custom_rev = load_workbook_safe(buf_rev, buf_rev.name)
    log_test("DUAL_UPLOAD", "듀얼 업로드 인메모리 스트림 로드", wb_custom_orig is not None and wb_custom_rev is not None, "2개 워크북 스트림 완벽 로드")

    # -------------------------------------------------------------
    # SECTION 3: 2모드 - 비전 AI 이미지 예상견적 산출기 검사
    # -------------------------------------------------------------
    print("\n[SECTION 3: 2모드 - 비전 AI 이미지 예상견적 산출기]")

    # Test 3A: 프리셋 전수 검사 (15개 프리셋)
    preset_keys = list(SAMPLE_PRESETS.keys())
    log_test("VISION_PRESET", "프리셋 총 개수 검증", len(preset_keys) >= 15, f"{len(preset_keys)}개 프리셋 등록")

    for pkey in ["KES_2025", "WIS_2026", "GALAXY_AUG", "M02_CXP", "M03_200MP", "F01_MONUMENT"]:
        p_info = SAMPLE_PRESETS[pkey]
        img_bytes = load_preset_image_bytes(pkey)
        log_test("VISION_IMG", f"프리셋 실물 사진 로드 ({pkey})", img_bytes is not None and len(img_bytes) > 5000, f"{len(img_bytes)/1024:.1f} KB")

    # Test 3B: 대형 전시 규모별 견적 산출 및 실적 정합성 검사
    scales_to_test = [
        ("초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)", "KES_2025", 572898438, 500000000, 650000000),
        ("초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)", "WIS_2026", 359989875, 330000000, 430000000),
        ("대형 전시 (50~100평 / 메인 부스·단독관)", "GALAXY_AUG", 231000000, 160000000, 250000000),
        ("소형 (1~3평 / 단일 키트 1~2대)", "M02_CXP", 214924059, 10000000, 35000000)
    ]

    for scale_lbl, pkey, actual_tgt, min_bound, max_bound in scales_to_test:
        est = estimate_costs_from_vision(
            features={},
            project_type="대형 행사 / 베뉴 전시" if "전시" in scale_lbl else "스마트 체험 키트 / 원형 개발",
            scale=scale_lbl,
            tier="고급형 (Premium)",
            preset_key=pkey
        )
        tot_c = est["summary"]["total_cost"]
        items_c = len(est["items"])
        gt = est.get("ground_truth") or {}
        
        in_bound = min_bound <= tot_c <= max_bound
        log_test("VISION_CALC", f"규모 산출 적정성 ({scale_lbl[:10]}...)", in_bound, f"산출 ₩{tot_c:,d} (목표구간 ₩{min_bound/100000000:.1f}억~{max_bound/100000000:.1f}억, 항목수 {items_c}개)")
        log_test("VISION_GT", f"지상진실(Ground Truth) 연동 ({pkey})", gt.get("matched") is True, f"실제 계약액 ₩{gt.get('settled_amount', 0):,d}")

    # Test 3C: 예상견적서 엑셀 내보내기 & 6대 공공 기준 감리 연동 검사
    xlsx_bytes = export_estimate_to_excel_bytes(est, "테스트_예상견적서")
    log_test("VISION_EXPORT", "제일기획 표준 서식 XLSX 생성", len(xlsx_bytes) > 3000, f"{len(xlsx_bytes)} 바이트 XLSX 생성")

    auditor_items = convert_vision_estimate_to_auditor_items(est)
    log_test("VISION_AUDIT", "비전 견적 -> 공공 감리 변환", len(auditor_items) == len(est["items"]), f"{len(auditor_items)}개 감리 항목 변환 완료")

    # -------------------------------------------------------------
    # SECTION 4: 3모드 - 과거 실적 자산화 & CBR 학습 스튜디오 검사
    # -------------------------------------------------------------
    print("\n[SECTION 4: 3모드 - 과거 실적 자산화 & CBR 학습 스튜디오]")

    # Test 4A: 엑셀 사전 파싱 & 실시간 분석 카드 데이터 추출
    wis_bytes = (samples_dir / "2026_WIS_전시제작_완료견적서.xlsx").read_bytes()
    prev = preview_excel_estimate(wis_bytes, "2026_WIS_전시제작_완료견적서.xlsx")
    log_test("LEARN_PREVIEW", "확정 견적서 사전 파싱", prev["total_budget"] > 300000000, f"시트 {len(prev['sheets'])}개, 품목 {prev['item_count']}개, 예산 ₩{prev['total_budget']:,d}")

    # Test 4B: RAG 유사 실적 검색 (다차원 코사인 유사도)
    similar_cases = find_similar_learned_cases("대형 행사 / 베뉴 전시", "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)", "고급형 (Premium - 코엑스 메가 전시)", top_k=3)
    top_entry = similar_cases[0] if similar_cases else {}
    top_case = top_entry.get("case", {})
    sim_score = top_entry.get("similarity_score", 0.0)
    log_test("CBR_RAG", "유사 실적 랭킹 검색", len(similar_cases) > 0 and "KES" in top_case.get("name", ""), f"1순위: {top_case.get('name')} (유사도 {sim_score:.1f}%)")

    # Test 4C: 실적 자산화 통계 지표 및 신뢰도 검증
    stats = get_learning_statistics()
    log_test("CBR_STATS", "학습 자산 통계 지표", stats.get("total_cases", 0) >= 60 and stats.get("total_learned_budget", 0) > 1000000000, f"누적 실적 {stats.get('total_cases')}건, 누적 예산 ₩{stats.get('total_learned_budget', 0):,d}, 신뢰도: {stats.get('model_confidence')}")

    # -------------------------------------------------------------
    # SECTION 5: 배포 서버 (Render) 실시간 라이브 헬스체크
    # -------------------------------------------------------------
    print("\n[SECTION 5: 운영 배포 서버 (Render) 라이브 헬스체크]")
    url = "https://ax-estimate-director.onrender.com"
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as response:
            latency = time.time() - t0
            status_code = response.status
            log_test("RENDER_LIVE", "도메인 실시간 응답 (Status 200)", status_code == 200, f"응답시간 {latency:.2f}초 / Status {status_code}")
    except Exception as e:
        log_test("RENDER_LIVE", "도메인 실시간 응답", False, str(e))

    # -------------------------------------------------------------
    # 최종 진단 요약
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"📊 [정밀 검사 최종 결과]: 총 {RESULTS['total_tests']}개 항목 중 성공 {RESULTS['passed_tests']}건 / 실패 {RESULTS['failed_tests']}건")
    print(f"🎯 정밀 합격률: {(RESULTS['passed_tests'] / RESULTS['total_tests'] * 100):.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    run_inspection()
