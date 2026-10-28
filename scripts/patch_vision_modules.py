# -*- coding: utf-8 -*-
"""
auditor/vision_estimator.py 및 auditor/vision_ui.py 패치 스크립트
1. 200평 이상, 300평 이상 대형 전시 규모 선택 옵션 추가
2. 3대 대형 전시 공인 실적 (KES, WIS, 갤럭시스튜디오) 벤치마크 및 프리셋 연동
3. 비전 AI 예상 견적 산출 시 위 3개 데이터 반영
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent

# 1. Patch vision_ui.py
vision_ui_file = ROOT_DIR / "auditor" / "vision_ui.py"
with open(vision_ui_file, "r", encoding="utf-8") as f:
    ui_content = f.read()

# Replace preset_options
old_preset_start = 'preset_options = {\n                # 실제 제작 키트 백데이터 (실물 사진 연동)'
new_preset_start = '''preset_options = {
                # 3대 대형 전시 공인 실적 (실제 공인 기준견적서 연동)
                "KES_2025": "🏆 [300평 이상 메가 엑스포] 2025 KES 한국전자전 코엑스 메인관 (공인실적 ₩572,898,438)",
                "WIS_2026": "🏆 [200평 이상 초대형 전시] 2026 WIS 월드IT쇼 전시관 제작 (공인실적 ₩359,989,875)",
                "GALAXY_AUG": "🏆 [100평형 복합 팝업] 2026 8월 갤럭시 스튜디오 멀티 베뉴 (공인실적 ₩231,000,000)",
                # 실제 제작 키트 백데이터 (실물 사진 연동)'''

if old_preset_start in ui_content:
    ui_content = ui_content.replace(old_preset_start, new_preset_start, 1)
    print("vision_ui.py: preset_options patched successfully.")
else:
    print("vision_ui.py: old_preset_start not found!")

# Replace scale_list
old_scale_list = '''        scale_list = [
            "소형 (1~3평 / 단일 키트 1~2대)",
            "중형 (5~15평 / 키트 3~5대)",
            "대형 (20평 이상 / 다중 키트 8대 이상)"
        ]'''

new_scale_list = '''        scale_list = [
            "소형 (1~3평 / 단일 키트 1~2대)",
            "중형 (5~15평 / 키트 3~5대)",
            "대형 (20평 이상 / 다중 키트 8대 이상)",
            "대형 전시 (50~100평 / 메인 부스·단독관)",
            "초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)",
            "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)"
        ]'''

if old_scale_list in ui_content:
    ui_content = ui_content.replace(old_scale_list, new_scale_list, 1)
    print("vision_ui.py: scale_list patched successfully.")
else:
    print("vision_ui.py: old_scale_list not found!")

with open(vision_ui_file, "w", encoding="utf-8") as f:
    f.write(ui_content)

# 2. Patch vision_estimator.py
est_file = ROOT_DIR / "auditor" / "vision_estimator.py"
with open(est_file, "r", encoding="utf-8") as f:
    est_content = f.read()

# Replace find_ground_truth_kit signature and implementation
old_find_gt = '''def find_ground_truth_kit(
    hints: str = "",
    project_type: str = "",
    preset_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """실제 44개 키트 백데이터(키트_견적산출_백데이터_v2.xlsx)에서 가장 유사한 실제 프로젝트를 찾아 지상진실(Ground Truth) 벤치마크로 반환합니다."""'''

new_find_gt = '''def find_ground_truth_kit(
    hints: str = "",
    project_type: str = "",
    preset_key: Optional[str] = None,
    scale: str = ""
) -> Optional[Dict[str, Any]]:
    """실제 44개 키트 백데이터 및 3대 대형 전시 공인 실적에서 가장 유사한 실제 프로젝트를 찾아 지상진실(Ground Truth) 벤치마크로 반환합니다."""'''

if old_find_gt in est_content:
    est_content = est_content.replace(old_find_gt, new_find_gt, 1)
    print("vision_estimator.py: find_ground_truth_kit signature patched.")
else:
    print("vision_estimator.py: old_find_gt signature not found!")

# Replace preset matching in find_ground_truth_kit
old_preset_match = '''    # 1. Preset Key 직접 매칭 (M02_CXP -> M02)
    if preset_key:
        kid = preset_key.split("_")[0]
        for c in cases:
            if c.get("kit_id") == kid:'''

new_preset_match = '''    # 1. Preset Key 직접 매칭 (M02_CXP -> M02, KES_2025 -> CASE_2025_KES_MEGA 등)
    if preset_key:
        if preset_key in ("KES_2025", "WIS_2026", "GALAXY_AUG"):
            target_cid = {
                "KES_2025": "CASE_2025_KES_MEGA",
                "WIS_2026": "CASE_2026_WIS_COEX",
                "GALAXY_AUG": "CASE_2026_GALAXY_AUG"
            }[preset_key]
            for c in cases:
                if c.get("case_id") == target_cid or c.get("preset_img_key") == preset_key:
                    tot_amt = c.get("settled_amount", 0)
                    proto_c = c.get("prototype_cost", round(tot_amt * 0.15))
                    fab_c = c.get("fabrication_cost", round(tot_amt * 0.75))
                    u_fab = c.get("unit_cost", round(fab_c / max(c.get("unit_count", 1), 1)))
                    return {
                        "matched": True,
                        "kit_id": preset_key,
                        "case_id": c.get("case_id"),
                        "name": c.get("name"),
                        "project_name": c.get("name"),
                        "settled_amount": tot_amt,
                        "prototype_cost": proto_c,
                        "fabrication_cost": fab_c,
                        "unit_fabrication_cost": u_fab,
                        "labor_md": c.get("labor_md", 0),
                        "image_file": c.get("image_file"),
                        "image_path": str(IMAGES_DIR / c.get("image_file")) if c.get("image_file") else None,
                        "key_specs": c.get("key_specs", ""),
                        "features": c.get("materials", []),
                        "similarity_score": 98.5,
                        "materials": c.get("materials", [])
                    }

        kid = preset_key.split("_")[0]
        for c in cases:
            if c.get("kit_id") == kid or c.get("case_id") == preset_key:'''

if old_preset_match in est_content:
    est_content = est_content.replace(old_preset_match, new_preset_match, 1)
    print("vision_estimator.py: preset matching patched.")
else:
    print("vision_estimator.py: old_preset_match not found!")

# Replace find_ground_truth_kit call in estimate_costs_from_vision
old_call_gt = '''    # 1. 지상 진실 (Ground Truth) 매칭
    gt_match = find_ground_truth_kit(
        hints=hints or features.get("hints_applied", ""),
        project_type=project_type,
        preset_key=preset_key
    )'''

new_call_gt = '''    # 1. 지상 진실 (Ground Truth) 매칭
    gt_match = find_ground_truth_kit(
        hints=hints or features.get("hints_applied", ""),
        project_type=project_type,
        preset_key=preset_key,
        scale=scale
    )'''

if old_call_gt in est_content:
    est_content = est_content.replace(old_call_gt, new_call_gt, 1)
    print("vision_estimator.py: call to find_ground_truth_kit patched.")
else:
    print("vision_estimator.py: old_call_gt not found!")

# Replace scale multiplier logic
old_scale_mult = '''    # 2. 규모 계수 (Scale Multiplier)
    if "소형" in scale:
        scale_qty = 1.0
        kit_units = 1
        area_m2 = 12.0
    elif "대형" in scale:
        scale_qty = 2.5
        kit_units = 8
        area_m2 = 66.0
    else:  # 중형
        scale_qty = 1.5
        kit_units = 3
        area_m2 = 30.0'''

new_scale_mult = '''    # 2. 규모 계수 (Scale Multiplier) 및 대형 전시 규모 판정
    is_mega_expo_300 = "초대형 엑스포" in scale or "300평" in scale
    is_mega_exhibit_200 = "초대형 메가" in scale or "200평" in scale
    is_large_exhibit_100 = "대형 전시" in scale or "50~100평" in scale or "100평" in scale

    if is_mega_expo_300:
        scale_qty = 15.0
        kit_units = 32
        area_m2 = 990.0  # 300평 이상 (KES급 코엑스 메가 전시장)
    elif is_mega_exhibit_200:
        scale_qty = 10.0
        kit_units = 22
        area_m2 = 660.0  # 200평 이상 (WIS급 코엑스 메인 전시관)
    elif is_large_exhibit_100:
        scale_qty = 6.0
        kit_units = 14
        area_m2 = 250.0  # 50~100평 (갤럭시스튜디오 멀티 베뉴 팝업)
    elif "대형" in scale or "20평" in scale:
        scale_qty = 2.5
        kit_units = 8
        area_m2 = 66.0
    elif "중형" in scale or "5~15평" in scale:
        scale_qty = 1.5
        kit_units = 3
        area_m2 = 30.0
    else:  # 소형
        scale_qty = 1.0
        kit_units = 1
        area_m2 = 12.0'''

if old_scale_mult in est_content:
    est_content = est_content.replace(old_scale_mult, new_scale_mult, 1)
    print("vision_estimator.py: scale multiplier patched.")
else:
    print("vision_estimator.py: old_scale_mult not found!")

# Add exhibition items in II. 기구제작·자재비
target_mat_anchor = '''    if has_security:
        items.append({
            "구분": "II. 기구제작·자재비",
            "항목명": "도난방지 무선 시건장치 및 충전 패드",
            "규격사양": "15W 고속 무선충전 및 무선 센서 감응 시건",
            "수량": kit_units,
            "단위": "SET",
            "단가": VISION_RATES["무선충전모듈"] + VISION_RATES["무선시건장치"],
            "금액": kit_units * (VISION_RATES["무선충전모듈"] + VISION_RATES["무선시건장치"]),
            "공공기준_근거": "전자부품 공공 표준시장가",
            "비고": "FAQ 07: 보안 및 충전 일체형"
        })'''

replacement_mat_anchor = '''    if has_security:
        items.append({
            "구분": "II. 기구제작·자재비",
            "항목명": "도난방지 무선 시건장치 및 충전 패드",
            "규격사양": "15W 고속 무선충전 및 무선 센서 감응 시건",
            "수량": kit_units,
            "단위": "SET",
            "단가": VISION_RATES["무선충전모듈"] + VISION_RATES["무선시건장치"],
            "금액": kit_units * (VISION_RATES["무선충전모듈"] + VISION_RATES["무선시건장치"]),
            "공공기준_근거": "전자부품 공공 표준시장가",
            "비고": "FAQ 07: 보안 및 충전 일체형"
        })

    # 대형 전시관(100평, 200평, 300평) 상부 트러스 및 대형 비주얼 구조물 (KES/WIS/갤럭시스튜디오 실적 연동)
    if is_mega_expo_300 or is_mega_exhibit_200 or is_large_exhibit_100:
        truss_rate = 9000000
        items.append({
            "구분": "II. 기구제작·자재비",
            "항목명": "상부 대형 조명 트러스 및 전시장 리깅 시스템",
            "규격사양": "코엑스 전시장 상부 바텐 와이어 리깅 및 알루미늄 조명 트러스 일체",
            "수량": 1,
            "단위": "식",
            "단가": round(truss_rate * scale_qty),
            "금액": round(truss_rate * scale_qty),
            "공공기준_근거": "2025 KES 한국전자전 / 2026 WIS 코엑스 전시제작 공인실적 기준",
            "비고": "대형 베뉴 상부 조명 및 천장 구조물 고정"
        })

        led_wall_rate = 7500000
        items.append({
            "구분": "II. 기구제작·자재비",
            "항목명": "대형 비주얼 LED 디스플레이 파사드 및 맞춤 벽장",
            "규격사양": "75인치 상업용 디스플레이 매립 벽장 및 고해상도 LED 미디어 월",
            "수량": 1,
            "단위": "식",
            "단가": round(led_wall_rate * scale_qty),
            "금액": round(led_wall_rate * scale_qty),
            "공공기준_근거": "조달청 대형 멀티비전 등록단가 및 KES 실적(80개 항목) 준용",
            "비고": "AI HOME Living Room 및 브랜드 메가 비주얼"
        })'''

if target_mat_anchor in est_content:
    est_content = est_content.replace(target_mat_anchor, replacement_mat_anchor, 1)
    print("vision_estimator.py: exhibition material items added.")
else:
    print("vision_estimator.py: target_mat_anchor not found!")

# Add exhibition insurance item in IV. 현장시공·설치/철거
target_freight_anchor = '''    items.append({
        "구분": "IV. 현장시공·설치/철거",
        "항목명": "운송 및 현장 안전 감리",
        "규격사양": "특수 무진동 화물 차량 및 감리원 배치",
        "수량": 1,
        "단위": "식",
        "단가": round(650000 * scale_qty),
        "금액": round(650000 * scale_qty),
        "공공기준_근거": "화물운송 표준요율 및 감리품셈",
        "비고": "키트 안전 상하차 포함"
    })'''

replacement_freight_anchor = '''    items.append({
        "구분": "IV. 현장시공·설치/철거",
        "항목명": "운송 및 현장 안전 감리",
        "규격사양": "특수 무진동 화물 차량 및 감리원 배치",
        "수량": 1,
        "단위": "식",
        "단가": round(650000 * scale_qty),
        "금액": round(650000 * scale_qty),
        "공공기준_근거": "화물운송 표준요율 및 감리품셈",
        "비고": "키트 안전 상하차 포함"
    })

    if is_mega_expo_300 or is_mega_exhibit_200 or is_large_exhibit_100:
        insure_rate = 1500000
        items.append({
            "구분": "IV. 현장시공·설치/철거",
            "항목명": "전시장 필수 법정보험료 및 안전관리자 상주",
            "규격사양": "고용보험, 산재보험, 영업배상책임보험 및 법정 안전관리자 상주",
            "수량": 1,
            "단위": "식",
            "단가": round(insure_rate * scale_qty),
            "금액": round(insure_rate * scale_qty),
            "공공기준_근거": "산업안전보건법 및 코엑스 전시장 안전관리 규정 (KES 3.-111 준용)",
            "비고": "대형 전시장 의무 가입 항목 (공인실적 정합)"
        })'''

if target_freight_anchor in est_content:
    est_content = est_content.replace(target_freight_anchor, replacement_freight_anchor, 1)
    print("vision_estimator.py: exhibition insurance item added.")
else:
    print("vision_estimator.py: target_freight_anchor not found!")

# Add presets to SAMPLE_PRESETS
target_presets_anchor = 'SAMPLE_PRESETS = {\n    # [실제 키트 백데이터 연동]'
replacement_presets_anchor = '''SAMPLE_PRESETS = {
    # [3대 공인 대형 전시 실적 프리셋 (코엑스 및 멀티 베뉴)]
    "KES_2025": {
        "name": "[300평 이상 메가 엑스포] 2025 KES 한국전자전 코엑스 메인관 (공인실적 ₩572,898,438)",
        "project_type": "대형 행사 / 베뉴 전시",
        "scale": "초대형 엑스포 전시 (300평 이상 / KES급 메가 전시관)",
        "tier": "고급형 (Premium - 코엑스 메가 전시)",
        "hints": "코엑스 메인홀 300평 이상 메가 부스, AI HOME Living Room 및 75인치 TV 벽장, 상부 대형 조명 트러스, 필수보험료 및 안전관리자 상주",
        "image_file": "2025_KES_MEGA.png",
        "bg_color": (20, 25, 45),
        "accent_color": (59, 130, 246),
        "actual_total": 572898438,
        "actual_proto": 85000000,
        "actual_unit_fab": 7161230,
        "actual_md": 128.5,
        "case_id": "CASE_2025_KES_MEGA"
    },
    "WIS_2026": {
        "name": "[200평 이상 초대형 전시] 2026 WIS 월드IT쇼 전시관 제작 (공인실적 ₩359,989,875)",
        "project_type": "대형 행사 / 베뉴 전시",
        "scale": "초대형 메가 전시 (200평 이상 / WIS급 코엑스 베뉴)",
        "tier": "고급형 (Premium - 코엑스 대형 전시)",
        "hints": "코엑스 B홀 200평 메인 전시관, Intro 스페이셜 사이니지 거치대 4대, 현장 시공 및 고용/산재/영업배상 보험료 반영",
        "image_file": "2026_WIS_COEX.png",
        "bg_color": (15, 35, 50),
        "accent_color": (14, 165, 233),
        "actual_total": 359989875,
        "actual_proto": 65000000,
        "actual_unit_fab": 5454392,
        "actual_md": 86.0,
        "case_id": "CASE_2026_WIS_COEX"
    },
    "GALAXY_AUG": {
        "name": "[100평형 복합 팝업] 2026 8월 갤럭시 스튜디오 멀티 베뉴 (공인실적 ₩231,000,000)",
        "project_type": "팝업스토어 / 전시 부스",
        "scale": "대형 전시 (50~100평 / 메인 부스·단독관)",
        "tier": "표준형 (Standard - 멀티 베뉴 팝업)",
        "hints": "더현대서울(8,500만원), 홍대점(6,500만원), 삼성강남(6,600만원), 그래픽(1,500만원) 총 4대 사이트 복합 제작 및 설치",
        "image_file": "GALAXY_AUG_HYUNDAI.jpg",
        "bg_color": (30, 25, 40),
        "accent_color": (245, 158, 11),
        "actual_total": 231000000,
        "actual_proto": 45000000,
        "actual_unit_fab": 8250000,
        "actual_md": 64.0,
        "case_id": "CASE_2026_GALAXY_AUG"
    },
    # [실제 키트 백데이터 연동]'''

if target_presets_anchor in est_content:
    est_content = est_content.replace(target_presets_anchor, replacement_presets_anchor, 1)
    print("vision_estimator.py: presets added to SAMPLE_PRESETS.")
else:
    print("vision_estimator.py: target_presets_anchor not found!")

with open(est_file, "w", encoding="utf-8") as f:
    f.write(est_content)

print("All vision patches complete!")
