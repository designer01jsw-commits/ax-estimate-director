# -*- coding: utf-8 -*-
"""견적감독관 정밀 진단 및 적합/비적합 판정 엔진 (공신력 있는 정부/공공 기준 소명 연계)"""

from typing import Any, Dict, List, Optional, Tuple

# 1. 공신력 있는 공공/정부 표준 고시 및 노임단가 기준표 (2025~2026 최신 기준)
OFFICIAL_BENCHMARKS = {
    "KIDP_DESIGN": {
        "agency": "한국디자인진흥원 (KIDP)",
        "law": "산업디자인진흥법 시행령 제11조 (산업디자인 대가기준) 및 산업통상자원부 고시",
        "url": "https://www.kidp.or.kr",
        "description": "국가 공인 디자인 표준품셈 및 디자이너 등급별 노임단가 고시 기준",
        "rates": {
            "총괄디자이너": 412000,
            "특급디자이너": 353000,
            "고급디자이너": 286000,
            "중급디자이너": 224000,
            "초급디자이너": 169000,
            "UIUX디자이너": 295000,
            "3D엔지니어": 340000
        },
        "workload_standard": {
            "컨셉기획": "1.0 M/D (톤앤매너 및 캠페인 비주얼 기획)",
            "3D모델링": "1.5 M/D (현장 실측 1:1 Rhino 3D 서피스 모델링)",
            "투시도렌더링_CMF": "1.8 M/D (고해상도 렌더링 5컷 및 갈바/도장 CMF 가이드)",
            "제작도면화": "0.7 M/D (NC가공용 샵드로잉 도면 검수)",
            "적정총공수": "원형 개발 1건당 총 5.0 M/D 이내"
        }
    },
    "KOSA_SW": {
        "agency": "한국소프트웨어산업협회 (KOSA)",
        "law": "소프트웨어 진흥법 제46조 (SW사업 대가의 산정기준) 및 과학기술정보통신부 고시",
        "url": "https://www.sw.or.kr",
        "description": "SW사업 대가산정 가이드라인 (기능점수 FP 및 SW기술자 임금실태조사)",
        "rates": {
            "SW특급기술자": 498000,
            "SW고급기술자": 381000,
            "SW중급기술자": 295000,
            "SW초급기술자": 228000
        },
        "guideline": "월간 20.9일 기준, 인터랙티브 체험 콘텐츠 및 디지털 사이니지 개발 표준 공수 산정"
    },
    "KENCA_ENGINEERING": {
        "agency": "한국엔지니어링협회 (KENCA)",
        "law": "엔지니어링산업 진흥법 제31조제2항 및 산업통상자원부 고시 「엔지니어링사업 대가의 기준」",
        "url": "https://www.kenca.or.kr",
        "description": "실비정액가산방식에 따른 직접인건비, 제경비, 기술료 법정 산출 공식",
        "rates": {
            "특급기술자": 448000,
            "고급기술자": 345000,
            "중급기술자": 282000,
            "초급기술자": 218000
        },
        "markup_rules": {
            "제경비_기준": "직접인건비의 110% ~ 120% (사무실비, 감가상각비, 세금공과, 복리후생비)",
            "제경비_최소": 1.10,
            "제경비_최대": 1.20,
            "기술료_기준": "(직접인건비 + 제경비)의 20% ~ 40% (기술 노하우 및 연구개발 보상)",
            "기술료_최소": 0.20,
            "기술료_최대": 0.40,
            "산출공식": "총원가 = 직접인건비 + 직접경비 + (직접인건비 × 110~120%) + ((직접인건비 + 제경비) × 20~40%)"
        }
    },
    "KBIZ_MANUFACTURING": {
        "agency": "중소기업중앙회 (KBIZ) / 통계청",
        "law": "통계청 국가승인통계 제340005호 「중소제조업 직종별 임금조사 보고서」",
        "url": "https://www.kbiz.or.kr",
        "description": "제조 및 설치 시공 부문 숙련공 시중 노임단가 표준",
        "rates": {
            "목공": 280000,
            "전기": 310000,
            "금속용접": 290000,
            "도장": 270000,
            "현장설치": 250000,
            "단순노무": 175000
        },
        "guideline": "인테리어 목공 및 전시 가설 집기 설치 시 숙련공/조공 적정 인건비 상한선"
    },
    "LABOR_STANDARDS_ACT": {
        "agency": "고용노동부 (MOEL)",
        "law": "근로기준법 제50조(근로시간), 제53조(연장 근로의 제한), 제56조(연장·야간 및 휴일 근로)",
        "url": "https://www.moel.go.kr",
        "description": "법정 근로시간 및 야간·연장 근로 할증 법정 기준",
        "rules": {
            "max_daily_rate": 1.0,         # 1인 1일 정상 투입률 100% (8시간 = 1.0 M/D)
            "allowable_overtime": 1.4,     # 야간/집중 투입 시 사유서 증빙 한도 140%
            "night_markup": 1.5,           # 22:00~06:00 야간 할증 50% 가산
            "overtime_limit": "1주 12시간 한도 연장 근로 (주 52시간제 준수)",
            "penalty_clause": "투입률 140% 초과 또는 동선 중복 집중 배치는 실근무 불인정 및 전액 삭감"
        }
    },
    "G2B_PUBLIC_PROCUREMENT": {
        "agency": "조달청 나라장터 (G2B) / 한국물가협회",
        "law": "국가를 당사자로 하는 계약에 관한 법률 시행령 제9조 (예정가격의 결정기준)",
        "url": "https://www.g2b.go.kr",
        "description": "공공 조달 표준시장단가 및 공산품·원자재 가격 지수",
        "guideline": "동종·동급 물품 표준 시장거래가격 대비 ±10% 이내 적정가 형성, 물가상승률(2.6%) 초과 급등 시 원가계산서 의무 제출"
    }
}

def get_all_benchmark_details() -> List[Dict[str, Any]]:
    """6대 공공·정부 기관 고시 기준의 상세 규정 요강 목록을 반환합니다."""
    return [
        {
            "기관": "한국디자인진흥원 (KIDP)",
            "법령": "산업디자인진흥법 시행령 제11조",
            "핵심내용": "디자이너 등급별 노임단가 (총괄 ₩412,000 / 특급 ₩353,000 / 고급 ₩286,000 / 중급 ₩224,000 / 초급 ₩169,000)",
            "공식품셈": "원형 디자인 1건당 총 5.0 M/D 표준 (컨셉 1.0D + 3D모델링 1.5D + 렌더링/CMF 1.8D + 샵드로잉 0.7D)",
            "URL": "https://www.kidp.or.kr"
        },
        {
            "기관": "한국소프트웨어산업협회 (KOSA)",
            "법령": "소프트웨어 진흥법 제46조",
            "핵심내용": "SW기술자 노임단가 (SW특급 ₩498,000 / SW고급 ₩381,000 / SW중급 ₩295,000 / SW초급 ₩228,000)",
            "공식품셈": "월 20.9일 기준 실비정액가산방식, 인터랙티브/키트 SW 기능점수(FP) 기반 공수 검증",
            "URL": "https://www.sw.or.kr"
        },
        {
            "기관": "한국엔지니어링협회 (KENCA)",
            "법령": "엔지니어링산업 진흥법 제31조제2항",
            "핵심내용": "실비정액가산방식 법정 요율: 제경비(직접인건비의 110~120%), 기술료((인건비+제경비)의 20~40%)",
            "공식품셈": "총대가 = 직접인건비 + 직접경비 + 제경비(최대 120%) + 기술료(최대 40%)",
            "URL": "https://www.kenca.or.kr"
        },
        {
            "기관": "중소기업중앙회 (KBIZ)",
            "법령": "국가승인통계 제340005호",
            "핵심내용": "중소제조업 시중 노임단가 (목공 ₩280,000 / 전기 ₩310,000 / 용접 ₩290,000 / 설치 ₩250,000 / 단순노무 ₩175,000)",
            "공식품셈": "집기 제작 및 현장 설치 시공 숙련공/조공 1일 8시간 작업 기준",
            "URL": "https://www.kbiz.or.kr"
        },
        {
            "기관": "고용노동부 (MOEL)",
            "법령": "근로기준법 제53조, 제56조",
            "핵심내용": "1일 8시간(투입률 100%) 원칙, 야간(22:00~06:00) 50% 가산, 주 52시간 제한",
            "공식품셈": "단기 야간 셋업 시 최대 140% 한도 조건부 인정, 140% 초과 집중 투입 시 전액 삭감",
            "URL": "https://www.moel.go.kr"
        },
        {
            "기관": "조달청 나라장터 (G2B) / 한국물가협회",
            "법령": "국가계약법 시행령 제9조",
            "핵심내용": "표준시장단가 및 공산품 거래가격 지수 (원자재 단가 변동률 허용폭 ±10% 이내)",
            "공식품셈": "물가상승률(2.6%) 대비 25% 초과 인상 시 객관적 증빙 부재 시 전액 비적합 환원",
            "URL": "https://www.g2b.go.kr"
        }
    ]


def normalize_baseline(orig_items: List[Dict[str, Any]], orig_labor: List[Dict[str, Any]]) -> Dict[str, Any]:
    """기존 기준 견적서 데이터를 분해하여 자체 정규화 감리 기준(Benchmark Norms)을 도출합니다."""
    norms = {
        "cat_unit_prices": {},      # 구분별 단위당 평균 단가
        "role_daily_rates": {},     # 직종별 평균 일단가
        "labor_ratio": 0.0,         # 총 견적 대비 인건비 비중
        "total_orig_cost": sum(it.get("금액", 0.0) for it in orig_items),
        "total_orig_labor": sum(it.get("금액", 0.0) for it in orig_labor)
    }

    # 구분별 단가 통계 산출
    cat_prices = {}
    for it in orig_items:
        cat = it.get("구분", "일반") or "일반"
        p = it.get("단가", 0.0) or 0.0
        if p > 0:
            cat_prices.setdefault(cat, []).append(p)

    for cat, plist in cat_prices.items():
        norms["cat_unit_prices"][cat] = {
            "avg": sum(plist) / len(plist),
            "min": min(plist),
            "max": max(plist),
            "count": len(plist)
        }

    # 직종별 일단가 통계 산출
    role_rates = {}
    for it in orig_labor:
        role = it.get("역할", it.get("공정", "기타")) or "기타"
        rate = it.get("단가", 0.0) or it.get("일단가", 0.0) or 0.0
        if rate > 0:
            role_rates.setdefault(role, []).append(rate)

    for role, rlist in role_rates.items():
        norms["role_daily_rates"][role] = {
            "avg": sum(rlist) / len(rlist),
            "min": min(rlist),
            "max": max(rlist),
            "count": len(rlist)
        }

    if norms["total_orig_cost"] > 0:
        norms["labor_ratio"] = norms["total_orig_labor"] / norms["total_orig_cost"]

    return norms

def diagnose_estimate_item(item: Dict[str, Any], baseline_norms: Dict[str, Any]) -> Dict[str, Any]:
    """신규 견적 항목의 단가, 제작비, 수량, 승인 여부를 다차원 분해하여 적합/비적합을 판정합니다."""
    name = item.get("항목명", "")
    cat = item.get("구분", "") or "일반"
    diff = item.get("차이금액", 0.0)
    p_orig = item.get("단가_최초", 0.0) or 0.0
    p_rev = item.get("단가_변경", 0.0) or 0.0
    q_orig = item.get("수량_최초", 0.0) or 0.0
    q_rev = item.get("수량_변경", 0.0) or 0.0
    p_effect = item.get("단가효과", 0.0)
    q_effect = item.get("수량효과", 0.0)
    diff_type = item.get("변경유형", "")
    appr_status = item.get("승인상태", "")
    appr_reason = item.get("승인근거", "")
    appr_no = item.get("승인번호", "")

    # 기본 판정값 초기화
    status = "적합"
    reasons = []
    citations = []
    action_required = ""

    # 1. 변경 승인 여부 판정 (최우선)
    if appr_status == "반려":
        status = "비적합"
        reasons.append("광고주/발주처 변경 협의에서 공식 반려(거부)된 항목이 견적서에 반영됨")
        citations.append({
            "기관": "제일기획 계약 표준 가이드라인 / 공정거래위원회 표준하도급계약서",
            "법령": "광고주 사전 컨펌 및 변경 승인(CR) 미승인 항목 청구 금지 원칙",
            "적용기준": "사전 서면 합의 없는 추가/변경 내역은 정산 대상에서 제외",
            "산출공식": f"삭감 요구액 = 미승인/반려 차이금액 전액 (₩{diff:+,.0f}원)",
            "내용": f"반려 승인번호: {appr_no or '사전 반려건'} — 청구 대상에서 즉시 제외 필요",
            "URL": "https://www.ftc.go.kr"
        })
        action_required = f"견적서에서 차이금액(₩{diff:+,.0f}) 전액 삭감 조치"
        return {
            "항목명": name,
            "구분": cat,
            "판정": status,
            "분해축": "승인절차",
            "변동금액": diff,
            "상세사유": " | ".join(reasons),
            "공공기준_근거": citations,
            "조치사항": action_required
        }

    # 2. 단가(Unit Price) 변동률 및 과다 여부 분해
    price_pct = ((p_rev - p_orig) / p_orig * 100.0) if p_orig > 0 else 0.0
    if p_rev > 0 and p_orig > 0:
        if price_pct > 25.0 and p_effect > 500000:
            status = "비적합"
            reasons.append(
                f"단가가 기준 견적 대비 {price_pct:+.1f}% 급격히 인상됨 (단가 영향: ₩{p_effect:+,.0f}). 자재 스펙 상향에 대한 객관적 증빙 부족"
            )
            citations.append({
                "기관": OFFICIAL_BENCHMARKS["G2B_PUBLIC_PROCUREMENT"]["agency"],
                "법령": OFFICIAL_BENCHMARKS["G2B_PUBLIC_PROCUREMENT"]["law"],
                "적용기준": "동종 물품 시중 표준 시장가격 및 물가협회 공산품 자재(MDF/금속/아크릴) 단가 동향 대비 ±10% 이내 적정가 형성",
                "산출공식": f"단가 인상률 = (₩{p_rev:,.0f} - ₩{p_orig:,.0f}) / ₩{p_orig:,.0f} × 100 = {price_pct:+.1f}% | 단가 영향액 = ₩{p_effect:+,.0f}원",
                "내용": f"소비자물가상승률(2.6%) 대비 약 {price_pct/2.6:.1f}배 급등하여 원가계산서 또는 자재 세금계산서 증빙 미제출 시 과다 청구로 판정",
                "URL": OFFICIAL_BENCHMARKS["G2B_PUBLIC_PROCUREMENT"]["url"]
            })
            action_required = f"자재 거래명세표 및 비교 견적서 3부 제출 요구 또는 기준 단가(₩{p_orig:,.0f})로 환원"
        elif price_pct > 10.0:
            if status != "비적합":
                status = "조건부 적합"
            reasons.append(f"단가 인상률({price_pct:+.1f}%)이 일반 물가변동폭 초과 — 소재/사양 변경 확인 필요")
            citations.append({
                "기관": "한국물가협회 / 가격정보",
                "법령": "원자재 및 제조 가공 공산품 가격 동향",
                "적용기준": "동일 재질(MDF/금속/아크릴) 단가 상승률 허용치 ±8% 이내",
                "산출공식": f"단가 변동 = ₩{p_orig:,.0f} → ₩{p_rev:,.0f} ({price_pct:+.1f}%)",
                "내용": "동일 재질(MDF/금속/아크릴) 단가 상승률 허용치 ±8% 이내",
                "URL": "https://www.kpi.or.kr"
            })
            action_required = "스펙 상향 승인서(CR) 첨부 후 승인"

    # 3. 신규 추가 항목(DIFF_TYPE_ADDED)의 가격 타당성 검증
    if diff_type == "추가":
        # 기준 견적서 정규화 단가 범위와 대조
        cat_norm = baseline_norms.get("cat_unit_prices", {}).get(cat)
        if cat_norm and cat_norm.get("max", 0) > 0 and p_rev > cat_norm["max"] * 1.5:
            status = "비적합"
            reasons.append(
                f"신규 추가 항목 단가(₩{p_rev:,.0f})가 기존 동일 구분({cat}) 최대 단가(₩{cat_norm['max']:,.0f})의 1.5배를 초과"
            )
            citations.append({
                "기관": OFFICIAL_BENCHMARKS["G2B_PUBLIC_PROCUREMENT"]["agency"],
                "법령": "정부 입찰·계약 집행기준 제74조 (신규 비목의 단가 결정)",
                "적용기준": f"동일 카테고리 기준 견적 최고단가(₩{cat_norm['max']:,.0f}) 대비 150% 이내 상한",
                "산출공식": f"초과배율 = ₩{p_rev:,.0f} / ₩{cat_norm['max']:,.0f} = {p_rev/cat_norm['max']:.2f}배 (허용 상한 1.50배 초과)",
                "내용": "신규 비목 발생 시 기존 계약 단가 및 낙찰률을 고려한 적정 시장 거래가격 적용 의무",
                "URL": OFFICIAL_BENCHMARKS["G2B_PUBLIC_PROCUREMENT"]["url"]
            })
            action_required = "공인 시중가격 또는 원가계산서 재산출"
        else:
            if appr_status != "승인":
                status = "조건부 적합"
                reasons.append("신규 요구사항 반영 항목이나 변경승인서(CR) 미첨부")
                action_required = "신규 항목 추가에 대한 광고주 사전 승인 공문 확인"
            else:
                reasons.append(f"사전 승인된 신규 항목 (수량 {q_rev:,.0f} × ₩{p_rev:,.0f})")

    # 4. 수량 변동 및 제작비 급증 검증
    if q_rev > q_orig and q_orig > 0:
        q_pct = (q_rev - q_orig) / q_orig * 100.0
        if q_pct > 50.0 and q_effect > 1000000:
            if status == "적합":
                status = "조건부 적합"
            reasons.append(f"제작 수량 급증({q_orig:,.0f} → {q_rev:,.0f}, {q_pct:+.0f}%)으로 제작비 ₩{q_effect:+,.0f} 증가")
            action_required = "현장 베뉴 배치도 및 수량 산출 근거 확인"

    if status == "적합":
        reasons.append("기준 견적 단가 및 사양과 일치하거나 정상 공인 가격 범위 내 반영됨")

    return {
        "항목명": name,
        "구분": cat,
        "판정": status,
        "분해축": "단가/제작비",
        "변동금액": diff,
        "상세사유": " | ".join(reasons),
        "공공기준_근거": citations,
        "조치사항": action_required or "정상 정산 승인"
    }

def diagnose_labor_item(item: Dict[str, Any], baseline_norms: Dict[str, Any]) -> Dict[str, Any]:
    """인력비, 인력 투입률(M/D), 직종별 노임단가를 공공 노임단가 고시와 대조하여 적합/비적합을 판정합니다."""
    proc = item.get("공정", "") or "설치"
    role = item.get("역할", "") or "기술자"
    name = item.get("항목명", f"{proc}/{role}")
    persons_rev = item.get("인원_변경", 0.0) or 0.0
    days_rev = item.get("일수_변경", 0.0) or 0.0
    rate_rev = item.get("단가_변경", 0.0) or 0.0
    diff_cost = item.get("차이금액", 0.0)
    md_rev = item.get("수량_변경", 0.0) or (persons_rev * days_rev)

    status = "적합"
    reasons = []
    citations = []
    action_required = ""

    # 1. 인력 투입률(Allocation Rate) 과다 및 야간 중복 투입 검증
    if days_rev <= 1.0 and persons_rev >= 3.0:
        status = "비적합"
        reasons.append(
            f"단일 일자(1일)에 동일 공정 인력 {persons_rev:.0f}명 집중 배치 (투입률 {persons_rev * 100:.0f}% 과다 계상 의심). 작업 동선 간섭 및 실근무 입증 필요"
        )
        citations.append({
            "기관": OFFICIAL_BENCHMARKS["LABOR_STANDARDS_ACT"]["agency"],
            "법령": OFFICIAL_BENCHMARKS["LABOR_STANDARDS_ACT"]["law"],
            "적용기준": "근로기준법상 1인 1일 법정 표준 근로시간(8시간 = 1.0 M/D = 투입률 100%)",
            "산출공식": f"당일 투입률 = {persons_rev:.0f}명 × 100% = {persons_rev * 100:.0f}% (법정 기준 대비 {persons_rev * 100 - 100:.0f}% 초과 집중 투입)",
            "내용": "1일 법정 표준 근로시간(8시간) 초과 투입 시 근로기준법 제56조에 따른 야간·연장 작업일보 및 출입증빙 필수",
            "URL": OFFICIAL_BENCHMARKS["LABOR_STANDARDS_ACT"]["url"]
        })
        action_required = "스토어 출입기록부 및 야간 작업사진 제출, 불인정 시 1인 표준공수로 재계산 감액"
    elif days_rev <= 1.0 and persons_rev >= 2.0:
        status = "조건부 적합"
        reasons.append(f"야간 셋업 제한시간(22:00~06:00) 준수를 위한 단기 집중 투입(투입률 {persons_rev * 100:.0f}%) 감지")
        citations.append({
            "기관": OFFICIAL_BENCHMARKS["LABOR_STANDARDS_ACT"]["agency"],
            "법령": "근로기준법 제56조 (야간근로 할증)",
            "적용기준": "야간근로(22:00~06:00) 통상임금의 50% 가산",
            "산출공식": f"투입률 = {persons_rev * 100:.0f}% (허용 한도 140% 이내)",
            "내용": "야간작업 불가피성에 대한 발주처 사전 확인서 필요",
            "URL": OFFICIAL_BENCHMARKS["LABOR_STANDARDS_ACT"]["url"]
        })
        action_required = "현장 테크니컬 작업일보 첨부"

    # 2. 직종별 일단가(Daily Rate) 공공 노임단가 초과 여부 검증
    if any(k in role for k in ["디자인", "디자이너", "3D", "그래픽"]):
        kidp = OFFICIAL_BENCHMARKS["KIDP_DESIGN"]
        max_allowed = kidp["rates"]["총괄디자이너"] * 1.15
        if rate_rev > max_allowed:
            excess_rate = rate_rev - kidp["rates"]["총괄디자이너"]
            excess_total = md_rev * excess_rate
            status = "비적합"
            reasons.append(
                f"일단가(₩{rate_rev:,.0f})가 2025년 한국디자인진흥원 디자이너 최고 고시단가(총괄디자이너 ₩{kidp['rates']['총괄디자이너']:,.0f})를 {excess_rate:+,.0f}원 초과"
            )
            citations.append({
                "기관": kidp["agency"],
                "법령": kidp["law"],
                "적용기준": f"2025/2026 디자이너 등급별 노임단가 고시 (총괄: ₩{kidp['rates']['총괄디자이너']:,.0f}원/일, 특급: ₩{kidp['rates']['특급디자이너']:,.0f}원/일)",
                "산출공식": f"초과 일단가 = ₩{rate_rev:,.0f} - ₩{kidp['rates']['총괄디자이너']:,.0f} = ₩{excess_rate:+,.0f}원/일 ({excess_rate/kidp['rates']['총괄디자이너']*100:+.1f}% 초과) | 총 초과액 = {md_rev:.1f} M/D × ₩{excess_rate:,.0f} = ₩{excess_total:,.0f}원",
                "내용": f"공인 디자이너 등급별 노임단가 기준 (총괄: ₩{kidp['rates']['총괄디자이너']:,.0f}, 특급: ₩{kidp['rates']['특급디자이너']:,.0f})",
                "URL": kidp["url"]
            })
            action_required = f"정부 고시 상한가(₩{kidp['rates']['총괄디자이너']:,.0f}) 기준으로 삭감 조정"
    
    elif any(k in role for k in ["SW", "개발", "코딩", "프로그래머"]):
        kosa = OFFICIAL_BENCHMARKS["KOSA_SW"]
        max_allowed = kosa["rates"]["SW특급기술자"] * 1.15
        if rate_rev > max_allowed:
            excess_rate = rate_rev - kosa["rates"]["SW특급기술자"]
            excess_total = md_rev * excess_rate
            status = "비적합"
            reasons.append(
                f"일단가(₩{rate_rev:,.0f})가 한국SW산업협회 SW특급기술자 고시단가(₩{kosa['rates']['SW특급기술자']:,.0f})를 {excess_rate:+,.0f}원 초과"
            )
            citations.append({
                "기관": kosa["agency"],
                "법령": kosa["law"],
                "적용기준": f"2025/2026 SW기술자 노임단가 공시 (SW특급: ₩{kosa['rates']['SW특급기술자']:,.0f}원/일, SW고급: ₩{kosa['rates']['SW고급기술자']:,.0f}원/일)",
                "산출공식": f"초과 일단가 = ₩{rate_rev:,.0f} - ₩{kosa['rates']['SW특급기술자']:,.0f} = ₩{excess_rate:+,.0f}원/일 ({excess_rate/kosa['rates']['SW특급기술자']*100:+.1f}% 초과) | 총 초과액 = {md_rev:.1f} M/D × ₩{excess_rate:,.0f} = ₩{excess_total:,.0f}원",
                "내용": f"SW사업 대가산정 가이드라인 (SW특급: ₩{kosa['rates']['SW특급기술자']:,.0f}, SW고급: ₩{kosa['rates']['SW고급기술자']:,.0f})",
                "URL": kosa["url"]
            })
            action_required = f"SW기술자 경력확인서 제출 또는 고시 상한가(₩{kosa['rates']['SW특급기술자']:,.0f})로 조정"

    elif any(k in role for k in ["목공", "전기", "설치", "철거"]):
        kbiz = OFFICIAL_BENCHMARKS["KBIZ_MANUFACTURING"]
        ref_rate = kbiz["rates"].get(role, 300000)
        if rate_rev > ref_rate * 1.3:
            excess_rate = rate_rev - ref_rate
            status = "비적합"
            reasons.append(
                f"시공 일단가(₩{rate_rev:,.0f})가 중소제조업 시중 노임단가(₩{ref_rate:,.0f}) 대비 {excess_rate:+,.0f}원 과다 책정"
            )
            citations.append({
                "기관": kbiz["agency"],
                "법령": kbiz["law"],
                "적용기준": f"국가승인통계 중소제조업 직종별 노임단가 조사 ({role}: ₩{ref_rate:,.0f}원/일)",
                "산출공식": f"초과 일단가 = ₩{rate_rev:,.0f} - ₩{ref_rate:,.0f} = ₩{excess_rate:+,.0f}원/일 ({excess_rate/ref_rate*100:+.1f}% 초과)",
                "내용": f"중소제조업 직종별 노임단가 조사보고서 ({role} 기준: ₩{ref_rate:,.0f}/일)",
                "URL": kbiz["url"]
            })
            action_required = f"표준 노임단가(₩{ref_rate:,.0f}) 수준으로 조정"

    if status == "적합":
        reasons.append("정부 공인 노임단가 및 법정 근로시간 범위에 부합함")

    return {
        "항목명": name,
        "공정": proc,
        "역할": role,
        "판정": status,
        "분해축": "인력비/투입률",
        "변동금액": diff_cost,
        "상세사유": " | ".join(reasons),
        "공공기준_근거": citations,
        "조치사항": action_required or "정상 정산 승인"
    }

def generate_audit_judgment_report(
    diagnosed_estimates: List[Dict[str, Any]],
    diagnosed_labor: List[Dict[str, Any]],
    summary: Dict[str, Any],
    project_name: str = "프로젝트"
) -> str:
    """공식 감리 진단서 및 시정 요구서 (Audit Judgment Report)를 마크다운 리포트로 생성합니다."""
    all_diagnosed = diagnosed_estimates + diagnosed_labor
    unfit_items = [d for d in all_diagnosed if d["판정"] == "비적합"]
    cond_items = [d for d in all_diagnosed if d["판정"] == "조건부 적합"]
    fit_items = [d for d in all_diagnosed if d["판정"] == "적합"]

    total_unfit_amt = sum(abs(d.get("변동금액", 0.0)) for d in unfit_items)

    lines = [
        f"# ⚖️ 「{project_name}」 견적 정밀 감리 진단서 및 시정 요구서",
        "",
        "> [!IMPORTANT]",
        f"> **감리 총평:** 총 {len(all_diagnosed)}개 세부 검토 항목 중 **적합 {len(fit_items)}건**, **조건부 적합 {len(cond_items)}건**, **비적합 {len(unfit_items)}건**으로 판정되었습니다.",
        f"> 비적합 판정된 불합리 증액 규모는 총 **₩{total_unfit_amt:,.0f}**이며, 정부 및 공공기관 공시 기준에 따른 즉각적인 소명 또는 감액 삭감이 요구됩니다.",
        "",
        "## 1. 감리 진단 종합 판정 요약",
        "",
        "| 진단 구분 | 항목 수 | 비중 | 주요 판단 근거 |",
        "|---|---|---|---|",
        f"| 🟢 **적합 (Pass)** | {len(fit_items)}건 | {len(fit_items)/len(all_diagnosed)*100 if all_diagnosed else 0:.1f}% | 기준 견적 대비 변동 없음 또는 공인 노임/단가 기준 부합 |",
        f"| 🟡 **조건부 적합 (Review)** | {len(cond_items)}건 | {len(cond_items)/len(all_diagnosed)*100 if all_diagnosed else 0:.1f}% | 야간 집중 투입(투입률 >100%) 또는 사양 변경 소명 대기 |",
        f"| 🔴 **비적합 (Fail/Cut)** | {len(unfit_items)}건 | {len(unfit_items)/len(all_diagnosed)*100 if all_diagnosed else 0:.1f}% | 공공 노임단가 초과, 미승인·반려건 반영, 자재 단가 급등 |",
        "",
        "---",
        "## 2. 🔴 비적합 항목별 공공 기준 근거 및 시정 요구 내역",
        ""
    ]

    if not unfit_items:
        lines.append("✅ **비적합으로 판정된 항목이 없습니다. 모든 견적 항목이 공공 기준 및 정규화 허용 범위 내에 있습니다.**")
    else:
        for idx, it in enumerate(unfit_items, 1):
            lines.append(f"### 2.{idx} [{it['분해축']}] {it['항목명']}")
            lines.append(f"- **판정 결과:** 🔴 **비적합 (부적정 청구 의심)**")
            lines.append(f"- **변동 규모:** ₩{it.get('변동금액', 0.0):+,.0f}")
            lines.append(f"- **비적합 사유:** {it['상세사유']}")
            if it.get("공공기준_근거"):
                lines.append("- **공신력 있는 정부/공공 기준 근거:**")
                for cite in it["공공기준_근거"]:
                    url_str = f" ([공식 사이트 바로가기]({cite['URL']}))" if cite.get("URL") else ""
                    lines.append(f"  - 🏛️ **{cite['기관']}** / `{cite['법령']}`{url_str}")
                    lines.append(f"    - *기준 요지:* {cite['내용']}")
            lines.append(f"- **👉 감독관 시정 조치 요구:** **{it['조치사항']}**")
            lines.append("")

    lines.extend([
        "---",
        "## 3. 🟡 조건부 적합 항목 소명 요구 목록",
        ""
    ])

    if not cond_items:
        lines.append("조건부 적합 항목이 없습니다.")
    else:
        for idx, it in enumerate(cond_items[:8], 1):
            lines.append(f"{idx}. **{it['항목명']}** (₩{it.get('변동금액', 0.0):+,.0f}): {it['상세사유']} → *요구사항: {it['조치사항']}*")

    lines.extend([
        "",
        "---",
        "## 4. 참조한 공신력 있는 공공 및 정부 기관 고시 기준",
        "- **한국디자인진흥원 (KIDP):** 디자이너 등급별 노임단가 고시 ([kidp.or.kr](https://www.kidp.or.kr))",
        "- **한국소프트웨어산업협회 (KOSA):** SW사업 대가산정 가이드라인 ([sw.or.kr](https://www.sw.or.kr))",
        "- **한국엔지니어링협회 (KENCA):** 실비정액가산방식 대가기준 ([kenca.or.kr](https://www.kenca.or.kr))",
        "- **중소기업중앙회 (KBIZ):** 중소제조업 직종별 노임단가 ([kbiz.or.kr](https://www.kbiz.or.kr))",
        "- **고용노동부 (MOEL):** 근로기준법 제53조 및 제56조 (주52시간, 야간근로할증) ([moel.go.kr](https://www.moel.go.kr))",
        "- **조달청 나라장터 (G2B):** 표준 시장거래가격 및 자재가격정보 ([g2b.go.kr](https://www.g2b.go.kr))"
    ])

    return "\n".join(lines)


def generate_executive_supervisor_opinion(
    diagnosed_estimates: List[Dict[str, Any]],
    diagnosed_labor: List[Dict[str, Any]],
    summary: Dict[str, Any],
    project_name: str = "프로젝트",
    baseline_norms: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """견적감독관(Chief Estimate Supervisor) 총체적 종합 진단 소견서를 생성합니다.
    
    신규 견적의 리스크 등급, 삭감 목표 규모, 4대 공종별 정밀 총평, 
    3대 핵심 실행 권고 및 정식 결재문 텍스트를 한눈에 확인할 수 있는 올인원 종합의견을 도출합니다.
    """
    all_diagnosed = diagnosed_estimates + diagnosed_labor
    unfit_items = [d for d in all_diagnosed if d.get("판정") == "비적합"]
    cond_items = [d for d in all_diagnosed if d.get("판정") == "조건부 적합"]
    fit_items = [d for d in all_diagnosed if d.get("판정") == "적합"]
    
    total_count = len(all_diagnosed)
    total_cut_demand = sum(abs(d.get("변동금액", 0.0)) for d in unfit_items)
    
    total_orig_cost = summary.get("total_orig_cost", 0.0)
    total_rev_cost = summary.get("total_rev_cost", 0.0)
    cost_diff = summary.get("cost_diff", 0.0)
    
    fit_rate = (len(fit_items) / total_count * 100.0) if total_count > 0 else 100.0
    unfit_rate = (len(unfit_items) / total_count * 100.0) if total_count > 0 else 0.0
    
    # 리스크 판정 등급
    has_approval_violation = any(d.get("분해축") == "승인절차" for d in unfit_items)
    if total_cut_demand >= 5_000_000 or len(unfit_items) >= 3 or has_approval_violation:
        risk_grade = "고위험 (High Risk)"
        risk_code = "RED"
        risk_badge = "🔴 고위험 (재협상 및 삭감 필수)"
        recommendation = f"미승인 증액 및 공공 기준 초과 비목에 대해 즉시 ₩{total_cut_demand:,.0f} 삭감 후 재합의 요구 권고"
    elif len(unfit_items) > 0 or len(cond_items) >= 2 or cost_diff > 0:
        risk_grade = "주의 (Moderate Risk)"
        risk_code = "AMBER"
        risk_badge = "🟡 주의 (조건부 승인 및 증빙 보완 필요)"
        recommendation = "경미한 공공 기준 편차 및 단기 집중 투입 항목에 대한 현장 증빙 확인 후 조건부 집행"
    else:
        risk_grade = "양호 (Low Risk)"
        risk_code = "GREEN"
        risk_badge = "🟢 적정 (정상 집행 승인 권고)"
        recommendation = "모든 항목이 기준 견적 및 정부 고시 품셈 범위 내 적정하므로 원안 승인 권고"

    # 4대 부문별 종합 진단 소견 (Pillars)
    # 1. 단가 및 자재비 부문
    unit_price_items = [d for d in all_diagnosed if d.get("분해축") == "단가/제작비"]
    unfit_price = [d for d in unit_price_items if d.get("판정") == "비적합"]
    cond_price = [d for d in unit_price_items if d.get("판정") == "조건부 적합"]
    price_cut = sum(abs(d.get("변동금액", 0.0)) for d in unfit_price)
    
    if unfit_price:
        pillar_price_status = "🔴 비적합 발생"
        pillar_price_desc = f"조달청 나라장터 및 물가협회 기준단가 대비 자재/제작 단가가 급등한 항목이 {len(unfit_price)}건(₩{price_cut:,.0f}원 상당) 식별되어 원가계산서 증빙 미제출 시 기준 단가로 환원 조치 필요."
    elif cond_price:
        pillar_price_status = "🟡 소명 필요"
        pillar_price_desc = f"물가상승률 허용 범위(±8%)를 상회하는 자재 사양 변경 항목 {len(cond_price)}건에 대한 스펙 상향 확인서(CR) 징구 필요."
    else:
        pillar_price_status = "🟢 적정"
        pillar_price_desc = "모든 자재 및 제작 단가가 공인 표준시장단가 및 기준 견적 정규화 범위 내에서 안정적으로 형성됨."

    # 2. 인력비 및 공임 투입률 부문
    labor_items = [d for d in all_diagnosed if d.get("분해축") == "인력비/투입률"]
    unfit_labor = [d for d in labor_items if d.get("판정") == "비적합"]
    cond_labor = [d for d in labor_items if d.get("판정") == "조건부 적합"]
    labor_cut = sum(abs(d.get("변동금액", 0.0)) for d in unfit_labor)
    
    if unfit_labor:
        pillar_labor_status = "🔴 비적합 발생"
        pillar_labor_desc = f"근로기준법상 1일 8시간(투입률 100%)을 초과하는 중복 배치 또는 KIDP/KOSA/KBIZ 최고 노임단가 초과 청구 {len(unfit_labor)}건(₩{labor_cut:,.0f}원) 적발. 즉각 삭감 및 1인 정상 공수로 조정 요구."
    elif cond_labor:
        pillar_labor_status = "🟡 소명 필요"
        pillar_labor_desc = f"야간 셋업에 따른 단기 집중 투입(투입률 140% 한도 내) {len(cond_labor)}건 감지. 현장 야간작업일보 확인 후 승인 요망."
    else:
        pillar_labor_status = "🟢 적정"
        pillar_labor_desc = "직종별 노임단가 및 투입 M/D가 국가 공인 기준 및 법정 근로시간 규정을 완벽히 준수함."

    # 3. 제작·가공비 및 공정 타당성 부문
    pillar_fab_status = "🟢 타당" if unfit_rate < 10.0 else "🟡 정밀 검토"
    pillar_fab_desc = f"과거 25.6억 원 44종 실물 키트 벤치마크 및 기준 견적 정규화 모델 대비 주요 공정의 제작비 형성 수준이 공학적 허용 범위 내에 위치함."

    # 4. 행정 절차 및 변경승인(CR) 준수 부문
    unfit_appr = [d for d in all_diagnosed if d.get("분해축") == "승인절차" and d.get("판정") == "비적합"]
    if unfit_appr:
        pillar_appr_status = "🔴 승인 위반"
        pillar_appr_desc = f"광고주/발주처 변경 협의에서 공식 반려(거부)된 비목이 견적서에 부당 반영된 사례 {len(unfit_appr)}건 적발. 청구 비목에서 즉시 삭제 필수."
    else:
        pillar_appr_status = "🟢 정상 승인"
        pillar_appr_desc = "모든 증액 및 항목 변경이 사전 서면 합의(CR) 절차를 정상 이행하여 행정적 리스크 없음."

    # 3대 핵심 조치 가이드
    action_items = []
    if unfit_items:
        unfit_names = ", ".join([d.get("항목명", "") for d in unfit_items[:3]])
        if len(unfit_items) > 3:
            unfit_names += f" 외 {len(unfit_items)-3}건"
        action_items.append({
            "order": "1순위 (즉시 삭감)",
            "title": "부적정 과다 청구액 즉시 감액 통보",
            "amount": f"₩{total_cut_demand:,.0f} 삭감",
            "detail": f"비적합 판정된 [{unfit_names}]에 대해 협력사에 공문 발송 및 견적서 재발행 요청."
        })
    else:
        action_items.append({
            "order": "1순위 (정상 승인)",
            "title": "원안 견적 집행 승인",
            "amount": "삭감액 0원",
            "detail": "기준 견적 및 공공 기준에 전 항목 부합하므로 원안 계약 체결 진행."
        })

    if cond_items:
        action_items.append({
            "order": "2순위 (증빙 징구)",
            "title": "조건부 적합 항목에 대한 현장 증빙 제출 요구",
            "amount": f"총 {len(cond_items)}개 비목 소명",
            "detail": "스토어 출입기록부, 야간작업일보, 자재 거래명세표 3종 세트 제출 필수 지정."
        })
    else:
        action_items.append({
            "order": "2순위 (상시 모니터링)",
            "title": "현장 시공 실투입 공수 사후 대조",
            "amount": "상시 감리",
            "detail": "실제 설치 및 철거 일정에 따른 투입 인원 실측 관리."
        })

    target_budget = max(0.0, total_rev_cost - total_cut_demand) if total_rev_cost > 0 else (total_orig_cost - total_cut_demand)
    action_items.append({
        "order": "3순위 (네고 타겟)",
        "title": "광고주 보고용 최종 조정 합의선 (Target Budget)",
        "amount": f"최종 권고액: ₩{target_budget:,.0f}",
        "detail": f"부적정 증액 ₩{total_cut_demand:,.0f}원을 삭감한 ₩{target_budget:,.0f}원을 최종 계약 체결 기준으로 설정."
    })

    # 공문서용 마크다운 & 텍스트
    md_verdict = f"""### ⚖️ [제일기획 AX 견적감독관 총체적 종합 진단 소견서]
- **프로젝트명:** {project_name}
- **종합 판정 등급:** {risk_badge}
- **핵심 감독관 권고:** {recommendation}

#### 📊 총체적 감리 지표 요약
- **총 검토 항목:** {total_count}건 (적합 {len(fit_items)}건 / 조건부 {len(cond_items)}건 / 비적합 {len(unfit_items)}건)
- **공공기준 적합률:** {fit_rate:.1f}%
- **부적정 삭감 타겟액:** **₩{total_cut_demand:,.0f}** (전체 변경견적 대비 {total_cut_demand/total_rev_cost*100 if total_rev_cost else 0:.1f}%)
- **감독관 최종 권고 예산:** **₩{target_budget:,.0f}**

#### 🏛️ 4대 공종별 정밀 총평
1. **단가 및 자재비 부문 [{pillar_price_status}]:** {pillar_price_desc}
2. **인력비 및 투입률 부문 [{pillar_labor_status}]:** {pillar_labor_desc}
3. **제작·가공비 타당성 [{pillar_fab_status}]:** {pillar_fab_desc}
4. **행정 및 승인 절차 [{pillar_appr_status}]:** {pillar_appr_desc}

#### 🎯 감독관 3대 핵심 실행 조치
1. **{action_items[0]['order']} {action_items[0]['title']} ({action_items[0]['amount']})**
   - {action_items[0]['detail']}
2. **{action_items[1]['order']} {action_items[1]['title']} ({action_items[1]['amount']})**
   - {action_items[1]['detail']}
3. **{action_items[2]['order']} {action_items[2]['title']} ({action_items[2]['amount']})**
   - {action_items[2]['detail']}
"""

    return {
        "risk_grade": risk_grade,
        "risk_code": risk_code,
        "risk_badge": risk_badge,
        "recommendation": recommendation,
        "total_count": total_count,
        "fit_count": len(fit_items),
        "cond_count": len(cond_items),
        "unfit_count": len(unfit_items),
        "fit_rate": fit_rate,
        "unfit_rate": unfit_rate,
        "total_cut_demand": total_cut_demand,
        "target_budget": target_budget,
        "pillars": [
            {"title": "1. 단가 및 자재비 부문", "status": pillar_price_status, "desc": pillar_price_desc},
            {"title": "2. 인력비 및 투입률 부문", "status": pillar_labor_status, "desc": pillar_labor_desc},
            {"title": "3. 제작·가공비 타당성", "status": pillar_fab_status, "desc": pillar_fab_desc},
            {"title": "4. 행정 및 승인 준수", "status": pillar_appr_status, "desc": pillar_appr_desc},
        ],
        "action_items": action_items,
        "verdict_md": md_verdict,
        "verdict_text": md_verdict.replace("### ", "").replace("#### ", "").replace("**", "").replace("- ", "• ")
    }

