# -*- coding: utf-8 -*-
"""
projects.json 및 learned_cases.json 영구 자산화 동기화 스크립트
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECTS_FILE = ROOT_DIR / "data" / "projects.json"
CASES_FILE = ROOT_DIR / "data" / "learned_cases.json"

REAL_PROJECTS = [
    {
        "project_id": "P_EXHIBITION_KES_2025",
        "name": "⭐ [공인실적] 2025 KES 한국전자전 메가 전시관 (300평 이상 / ₩5.73억)",
        "client": "삼성전자 / 한국전자정보통신산업진흥회",
        "site": "코엑스 A·C홀 (300평 이상 메가 엑스포)",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "2025_KES_한국전자전_전시제작견적서.xlsx",
        "sample_change": None,
        "default_sheet": "2025 KES_전시 제작",
        "total_budget": 572898438,
        "item_count": 80,
        "studied_at": "2025-11-17",
        "is_studied_asset": True,
        "scale": "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)"
    },
    {
        "project_id": "P_EXHIBITION_WIS_2026",
        "name": "⭐ [공인실적] 2026 WIS (월드IT쇼) 메인 전시관 (200평 이상 / ₩3.60억)",
        "client": "삼성전자 / 제일기획",
        "site": "코엑스 B홀 (200평 이상 메가 베뉴)",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "2026_WIS_전시제작_완료견적서.xlsx",
        "sample_change": None,
        "default_sheet": "2026 WIS_전시 제작(수정2)",
        "total_budget": 359989875,
        "item_count": 66,
        "studied_at": "2026-06-24",
        "is_studied_asset": True,
        "scale": "초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)"
    },
    {
        "project_id": "P_EXHIBITION_GALAXY_AUG",
        "name": "⭐ [공인실적] 2026 8월 갤럭시 스튜디오 복합 팝업 (더현대/홍대/강남 / ₩2.31억)",
        "client": "삼성전자 / 제일기획",
        "site": "더현대 서울 / 홍대점 / 삼성강남 (100평형 멀티 베뉴)",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "2026_8월_갤럭시스튜디오_완료견적서.xlsx",
        "sample_change": None,
        "default_sheet": "★1. 공통_거래명세서★",
        "total_budget": 231000000,
        "item_count": 7,
        "studied_at": "2026-08-29",
        "is_studied_asset": True,
        "scale": "대형 전시 (50~100평 / 메인 부스·단독관)"
    }
]

REAL_CASES = [
    {
        "case_id": "CASE_2025_KES_MEGA",
        "project_id": "P_EXHIBITION_KES_2025",
        "name": "2025 KES 한국전자전 메가 전시관 (300평 이상)",
        "client": "삼성전자 / 한국전자정보통신산업진흥회",
        "project_type": "대형 행사 / 베뉴 전시",
        "settled_amount": 572898438,
        "scale": "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)",
        "unit_count": 80,
        "unit_cost": 7161230,
        "unit_label": "공정별 제작단가",
        "tier": "고급형 (Premium - 코엑스 메가 전시)",
        "materials": ["갈바 스틸 트러스", "MDF 가벽", "우레탄 조색 도장", "75인치 TV 벽장", "LED 라이팅 파사드", "AI HOME 리빙룸"],
        "labor_md": 128.5,
        "key_specs": "코엑스 메인홀 300평 이상 메가 부스, AI HOME Living Room 및 75인치 TV 벽장, 상부 대형 조명 트러스, 필수보험료 및 안전관리자 상주",
        "benchmark_cites": "KIDP 총괄품셈 + KOSA SW대가 + KBIZ 전시목공/전기노임 + KENCA 제경비 공식 준용",
        "preset_img_key": "KES_2025",
        "image_file": "2025_KES_MEGA.png",
        "created_at": "2025-11-17"
    },
    {
        "case_id": "CASE_2026_WIS_COEX",
        "project_id": "P_EXHIBITION_WIS_2026",
        "name": "2026 WIS (월드IT쇼) 메인 전시관 (200평 이상)",
        "client": "삼성전자 / 제일기획",
        "project_type": "대형 행사 / 베뉴 전시",
        "settled_amount": 359989875,
        "scale": "초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)",
        "unit_count": 66,
        "unit_cost": 5454392,
        "unit_label": "공정별 제작단가",
        "tier": "고급형 (Premium - 코엑스 대형 전시)",
        "materials": ["스페이셜 사이니지 거치대", "EGI 갈바 프레임", "아크릴 및 조광판", "독립형 키트 연동", "우레탄 2색 도장"],
        "labor_md": 86.0,
        "key_specs": "코엑스 B홀 200평 메인 전시관, Intro 스페이셜 사이니지 거치대 4대, 현장 시공 및 고용/산재/영업배상 보험료 반영",
        "benchmark_cites": "KIDP 5단계 표준품셈 + KBIZ 시중노임단가 + 조달청 G2B 시장거래가격",
        "preset_img_key": "WIS_2026",
        "image_file": "2026_WIS_COEX.png",
        "created_at": "2026-06-24"
    },
    {
        "case_id": "CASE_2026_GALAXY_AUG",
        "project_id": "P_EXHIBITION_GALAXY_AUG",
        "name": "2026 8월 갤럭시 스튜디오 복합 팝업 (더현대/홍대/강남)",
        "client": "삼성전자 / 제일기획",
        "project_type": "팝업스토어 / 전시 부스",
        "settled_amount": 231000000,
        "scale": "대형 전시 (50~100평 / 메인 부스·단독관)",
        "unit_count": 28,
        "unit_cost": 8250000,
        "unit_label": "베뉴별 제작단가",
        "tier": "표준형 (Standard - 멀티 베뉴 팝업)",
        "materials": ["더현대서울 공간연출", "홍대점 공간디자인", "삼성강남 체험존", "갤럭시스튜디오 그래픽 실사출력"],
        "labor_md": 64.0,
        "key_specs": "더현대서울(8,500만원), 홍대점(6,500만원), 삼성강남(6,600만원), 그래픽(1,500만원) 총 4대 사이트 복합 제작 및 설치",
        "benchmark_cites": "KIDP 공간디자인 품셈 + KBIZ 전시목공/도장 노임 + 화물운송 표준요율",
        "preset_img_key": "GALAXY_AUG",
        "image_file": "GALAXY_AUG_HYUNDAI.jpg",
        "created_at": "2026-08-29"
    }
]

def update_projects():
    projects = []
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, "r", encoding="utf-8-sig") as f:
            try:
                projects = json.load(f)
            except Exception:
                projects = []

    # Filter out any existing entries with these IDs
    real_ids = {p["project_id"] for p in REAL_PROJECTS}
    filtered_existing = [p for p in projects if p.get("project_id") not in real_ids]

    # Prepend the 3 real exhibition projects so they appear right at the top of the selectbox
    updated_projects = REAL_PROJECTS + filtered_existing

    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_projects, f, ensure_ascii=False, indent=2)

    print(f"Updated projects.json: {len(updated_projects)} projects registered.")

def update_learned_cases():
    cases = []
    if CASES_FILE.exists():
        with open(CASES_FILE, "r", encoding="utf-8-sig") as f:
            try:
                cases = json.load(f)
            except Exception:
                cases = []

    # Clean and deduplicate existing
    real_case_ids = {c["case_id"] for c in REAL_CASES}
    seen = set()
    cleaned = []
    for c in cases:
        cid = c.get("case_id") or c.get("kit_id")
        name = c.get("name")
        key = cid if cid else name
        if key and key not in seen and cid not in real_case_ids:
            seen.add(key)
            cleaned.append(c)

    # Prepend REAL_CASES
    final_cases = REAL_CASES + cleaned

    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(final_cases, f, ensure_ascii=False, indent=2)

    print(f"Updated learned_cases.json: {len(final_cases)} cases registered.")

if __name__ == "__main__":
    update_projects()
    update_learned_cases()
