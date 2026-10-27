# -*- coding: utf-8 -*-
from pathlib import Path

engine_path = Path("auditor/learning_engine.py")
content = engine_path.read_text(encoding="utf-8")

function_code = '''

def study_and_assetize_excel_estimate(
    excel_bytes: bytes,
    file_name: str,
    project_name: str,
    client: str = "삼성전자 / 제일기획",
    venue: str = "베뉴 미정",
    currency: str = "KRW"
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    """클라이언트가 확정한 엑셀 견적서를 심층 스터디(자산화)하여 에이전트 기준 데이터베이스에 영구 등록합니다."""
    import datetime
    from auditor.loader import load_workbook_safe, find_best_estimate_sheet, read_estimate_sheet
    from auditor.categorizer import decompose_estimate_by_category
    from auditor.projects import save_project

    # 1. 파일 안전 저장
    safe_fname = file_name.replace(" ", "_")
    target_path = DATA_DIR / safe_fname
    target_sample_path = DATA_DIR / "samples" / safe_fname

    target_path.write_bytes(excel_bytes)
    DATA_DIR.joinpath("samples").mkdir(parents=True, exist_ok=True)
    target_sample_path.write_bytes(excel_bytes)

    # 2. 워크북 및 최적 시트 로드
    wb = load_workbook_safe(target_sample_path, safe_fname)
    best_sheet, _ = find_best_estimate_sheet(wb)
    items, _, _, _ = read_estimate_sheet(wb[best_sheet], safe_fname, best_sheet)

    # 3. 7대 공종 분해 및 원가 구조 스터디
    decomp = decompose_estimate_by_category(items)
    total_budget = int(decomp.get("total_amount", 0))

    # 주요 자재 및 키워드 추출
    mats = set()
    for it in items:
        name = it.get("항목명", "")
        spec = it.get("규격", "")
        for m in ["갈바", "EGI", "스틸", "MDF", "아크릴", "LED", "실사", "포맥스", "조명", "NC가공", "도장"]:
            if m.lower() in (name + spec).lower():
                mats.add(m)
    materials_list = list(mats)[:5] or ["제작 집기 자재", "우레탄 도장", "아크릴"]

    # 4. projects.json 등록용 프로젝트 레코드 생성
    proj_id = f"P_STUDIED_{uuid.uuid4().hex[:6].upper()}"
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    proj_record = {
        "project_id": proj_id,
        "name": f"⭐ [자산화] {project_name}",
        "client": client,
        "site": venue,
        "currency": currency,
        "status": "광고주 컨펌 완료",
        "sample_estimate": safe_fname,
        "sample_change": None,
        "default_sheet": best_sheet,
        "total_budget": total_budget,
        "item_count": len(items),
        "studied_at": today_str,
        "is_studied_asset": True
    }
    save_project(proj_record)

    # 5. learned_cases.json에도 학습 실적으로 동기화 등록
    save_new_learned_case(
        image_bytes=None,
        name=project_name,
        client=client,
        project_type="클라이언트 확정 기준 견적서",
        settled_amount=total_budget or 30000000,
        scale="실적 확정 규모",
        unit_count=max(len(items), 1),
        unit_label="품목수",
        tier="광고주 컨펌 완료 (Standard/Premium)",
        materials=materials_list,
        labor_md=10.0,
        key_specs=f"시트: {best_sheet} | 총 {len(items)}개 품목 정산 완료 | 7대 공종 원가 정규화 완료",
        benchmark_cites="광고주 최종 컨펌 기준 및 공공 표준 단가",
        preset_img_key="DS_CAMPUS"
    )

    return proj_record, decomp, items
'''

normalized = content.replace("\r\n", "\n")
if "def study_and_assetize_excel_estimate" not in normalized:
    normalized += function_code
    engine_path.write_text(normalized, encoding="utf-8")
    print("SUCCESS: added study_and_assetize_excel_estimate to auditor/learning_engine.py")
else:
    print("Already present!")
