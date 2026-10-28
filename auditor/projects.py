# -*- coding: utf-8 -*-
"""프로젝트 목록 관리 모듈 (영구 자산화 및 보존 보장)"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

DEFAULT_PROJECTS_FILE = Path(__file__).resolve().parent.parent / "data" / "projects.json"

# 공인 기준 실적 데이터셋 (서버 재기동/리셋 시에도 영구 보존되는 핵심 3대 전시 및 키트 프로젝트)
GUARANTEED_CORE_PROJECTS: List[Dict[str, Any]] = [
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
    },
    {
        "project_id": "P_BASE_KIT_MAIN",
        "name": "S26 Miracle 키트/컨텐츠 메인 기준견적서 (260511)",
        "client": "삼성전자 / 제일기획",
        "site": "삼성 강남 / 홍대 / KT",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "기준견적서_키트컨텐츠_광고주컨펌_260511.xlsx",
        "sample_change": None,
        "default_sheet": "1-1. 개발 상세"
    },
    {
        "project_id": "P_BASE_KIT_V2",
        "name": "키트/컨텐츠 원형개발 및 제작설치 기준견적서 v2",
        "client": "삼성전자 / 제일기획",
        "site": "원형 개발 / 강남 / 홍대 / KT",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "기준견적서2_키트컨텐츠_광고주컨펌.xlsx",
        "sample_change": None,
        "default_sheet": "1-2) 원형 개발"
    },
    {
        "project_id": "P_BASE_KIT_BASEBALL",
        "name": "프로야구 베뉴 키트제작 및 설치/철거 기준견적서 v3",
        "client": "삼성전자 / KBO 프로야구",
        "site": "올스타 / 수원 / 잠실 / 대구 베뉴",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "기준견적서3_키트컨텐츠_광고주컨펌.xlsx",
        "sample_change": None,
        "default_sheet": "1-1) 키트 및 컨텐츠 원형 개발(야구)"
    },
    {
        "project_id": "P_BASE_EXHIBIT_CAMPUS",
        "name": "삼성 사업장 전시 및 공통 인건비 증빙 기준견적서 v4",
        "client": "삼성전자 DS부문",
        "site": "수원 / 기흥 / 화성 사업장",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "기준견적서4_전시_광고주컨펌.xlsx",
        "sample_change": None,
        "default_sheet": "1. 수원 사업장"
    },
    {
        "project_id": "P_EXHIBIT_HONGDAE",
        "name": "갤럭시 스튜디오 홍대점 집기제작 및 전시공사",
        "client": "삼성전자 / 제일기획",
        "site": "홍대점 (한국)",
        "currency": "KRW",
        "status": "광고주 컨펌 완료",
        "sample_estimate": "전시 광고주컨펌완료 견적서 (1).xlsx",
        "sample_change": "전시_홍대점_변경내역.xlsx",
        "default_sheet": "● 홍대점_거래명세서"
    },
    {
        "project_id": "P001",
        "name": "국립과학관 체험전시 키트 제작 (샘플 데모)",
        "client": "[가상] 국립과학관",
        "site": "한국",
        "currency": "KRW",
        "status": "진행 중",
        "sample_estimate": "P001_최초견적.xlsx",
        "sample_change": "P001_변경내역.xlsx"
    },
    {
        "project_id": "P002",
        "name": "글로벌 과학 엑스포 전시관 구축 (북미 USD)",
        "client": "[가상] Global Science Expo",
        "site": "북미",
        "currency": "USD",
        "status": "진행 중",
        "sample_estimate": "P002_최초견적.xlsx",
        "sample_change": "P002_변경내역.xlsx"
    }
]

def load_projects(file_path: Path | str = DEFAULT_PROJECTS_FILE) -> Tuple[List[Dict[str, Any]], List[str]]:
    """프로젝트 목록을 로드하고 (프로젝트 리스트, 경고 메시지 목록) 튜플을 반환합니다.
    사용자가 과거 실적 자산화로 추가한 프로젝트는 영구 보존되며,
    3대 핵심 전시 프로젝트(KES, WIS, 갤럭시스튜디오)는 누락 없이 영구 등재됩니다.
    """
    path = Path(file_path)
    warnings = []
    
    projects: List[Dict[str, Any]] = []

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                if isinstance(data, list):
                    projects = data
                else:
                    warnings.append("프로젝트 목록 형식 오류: JSON 루트가 배열이어야 합니다.")
        except json.JSONDecodeError as e:
            warnings.append(f"프로젝트 목록({path.name}) 형식이 올바르지 않습니다: {e.msg}")
        except Exception as e:
            warnings.append(f"프로젝트 목록을 읽는 중 문제가 발생했습니다: {str(e)}")

    # 보장된 핵심 프로젝트가 누락되지 않도록 영구 보존 머지
    existing_ids = {p.get("project_id") for p in projects if isinstance(p, dict)}
    missing_cores = [cp for cp in GUARANTEED_CORE_PROJECTS if cp.get("project_id") not in existing_ids]

    if missing_cores or not projects:
        # 누락된 핵심 프로젝트 보강
        # 신규 자산화 프로젝트(is_studied_asset: True)가 최상단에 올 수 있도록 순서 정렬
        studied_user_projects = [p for p in projects if p.get("is_studied_asset") and p.get("project_id") not in {cp["project_id"] for cp in GUARANTEED_CORE_PROJECTS}]
        remaining_existing = [p for p in projects if p not in studied_user_projects and p.get("project_id") not in {cp["project_id"] for cp in GUARANTEED_CORE_PROJECTS}]
        
        projects = studied_user_projects + GUARANTEED_CORE_PROJECTS + remaining_existing
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    return projects, warnings

def save_project(new_proj: Dict[str, Any], file_path: Path | str = DEFAULT_PROJECTS_FILE) -> bool:
    """새로운 기준 견적 프로젝트를 projects.json에 저장(등록)합니다.
    과거 실적 자산화를 통해 DB에 추가된 자료는 맨 위에 자동 등록되고 영구 보존됩니다.
    """
    path = Path(file_path)
    projects, _ = load_projects(path)
    
    # 중복 ID 확인 후 업데이트 또는 추가
    existing_idx = next((i for i, p in enumerate(projects) if p.get("project_id") == new_proj.get("project_id")), None)
    if existing_idx is not None:
        projects[existing_idx] = new_proj
    else:
        # 맨 앞에 추가하여 사용자가 방금 학습시킨 프로젝트가 즉시 1순위로 표시되도록 함
        projects.insert(0, new_proj)
        
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    return True
