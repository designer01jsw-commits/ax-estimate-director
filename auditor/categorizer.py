# -*- coding: utf-8 -*-
"""7대 표준 공종(비목) 자동 분류 및 다차원 적정성 감리 엔진 (양식이 다른 프로젝트 간 비교 지원)"""

import difflib
import re
from typing import Any, Dict, List, Optional, Tuple

# 1. 전천후 7대 표준 제작 공종 정의 및 공공 벤치마크 매핑
COST_CATEGORIES = {
    "DESIGN_DEV": {
        "id": "CAT_1",
        "name": "1. 기획/설계/3D/원형개발",
        "keywords": [
            "기획", "디자인", "3d", "설계", "도면", "감리", "pm", "cmf", "원형", "개발",
            "기능점수", "렌더링", "샵드로잉", "기획비", "컨셉", "uiux", "소프트웨어", "sw"
        ],
        "benchmark_agency": "한국디자인진흥원(KIDP) / KOSA",
        "benchmark_law": "산업디자인진흥법 시행령 제11조 / SW진흥법 제46조",
        "standard_weight": (0.05, 0.15)  # 표준 권장 비중 5%~15%
    },
    "FIXTURE_FABRICATION": {
        "id": "CAT_2",
        "name": "2. 구조체/목공/금속/집기제작",
        "keywords": [
            "집기", "테이블", "목공", "mdf", "갈바", "금속", "스틸", "파이프", "도장",
            "분체", "선반", "벽체", "프레임", "구조", "가구", "진열대", "쇼케이스",
            "제작", "체험존", "키트", "플레이트", "받침대", "케이스", "모듈", "슬로프", "타일", "수장"
        ],
        "benchmark_agency": "중소기업중앙회(KBIZ) / 한국물가협회",
        "benchmark_law": "중소제조업 직종별 임금조사 / 조달청 표준시장단가",
        "standard_weight": (0.30, 0.55)  # 표준 권장 비중 30%~55%
    },
    "ACRYLIC_SPECIAL": {
        "id": "CAT_3",
        "name": "3. 아크릴/특수소재/가공",
        "keywords": [
            "아크릴", "pc", "폴리카보네이트", "포맥스", "가공", "nc", "레이저", "조각",
            "벤딩", "실크", "다이아", "절곡", "abs", "pet", "광학", "절단", "면취"
        ],
        "benchmark_agency": "한국물가협회 / 조달청 나라장터",
        "benchmark_law": "국가계약법 시행령 제9조 (공산품 원자재 단가)",
        "standard_weight": (0.10, 0.25)  # 표준 권장 비중 10%~25%
    },
    "GRAPHIC_SIGN": {
        "id": "CAT_4",
        "name": "4. 그래픽/사인/실사출력",
        "keywords": [
            "그래픽", "실사", "출력", "시트", "uv", "배너", "사인", "래핑", "현수막",
            "백릿", "와이드", "조명필름", "캘지", "유포지", "텍스트", "돔보", "인쇄", "시트지"
        ],
        "benchmark_agency": "한국물가정보 / 한국옥외광고협회",
        "benchmark_law": "공공조달 인쇄·출력 표준품셈",
        "standard_weight": (0.05, 0.15)  # 표준 권장 비중 5%~15%
    },
    "AV_LIGHT_ELEC": {
        "id": "CAT_5",
        "name": "5. AV/조명/전기/인터랙티브",
        "keywords": [
            "led", "조명", "모니터", "패널", "배선", "분전반", "전기", "smps", "스위치",
            "센서", "디스플레이", "tv", "사이니지", "스피커", "음향", "영상", "아답터", "컨트롤러"
        ],
        "benchmark_agency": "전기공사협회 / KOSA",
        "benchmark_law": "전기공사 표준품셈 및 SW 대가기준",
        "standard_weight": (0.05, 0.20)  # 표준 권장 비중 5%~20%
    },
    "LOGISTICS_INSTALL": {
        "id": "CAT_6",
        "name": "6. 운송/물류/설치/철거",
        "keywords": [
            "운송", "화물", "양중", "사다리", "설치", "철거", "폐기", "보관", "포장",
            "차량", "상하차", "반입", "반출", "운임", "용달", "지게차"
        ],
        "benchmark_agency": "화물자동차운수사업법 / 물류표준",
        "benchmark_law": "화물자동차 안전운임 고시",
        "standard_weight": (0.05, 0.15)  # 표준 권장 비중 5%~15%
    },
    "LABOR_ONSITE": {
        "id": "CAT_7",
        "name": "7. 현장 노무/시공 인건비",
        "keywords": [
            "인건비", "목수", "전기공", "도장공", "반장", "조공", "기공", "노무비",
            "테크니션", "m/d", "일당", "설치기사", "지원인력", "안전관리", "현장관리"
        ],
        "benchmark_agency": "고용노동부 / 대한건설협회",
        "benchmark_law": "근로기준법 제53조/제56조 및 시중노임단가",
        "standard_weight": (0.10, 0.25)  # 표준 권장 비중 10%~25%
    }
}

def clean_text(text: str) -> str:
    """공백 및 특수문자를 정규화합니다."""
    if not text:
        return ""
    return re.sub(r"[^\w\s가-힣a-zA-Z0-9]", " ", str(text)).lower().strip()

def classify_item(name: str, spec: str = "", raw_cat: str = "") -> Tuple[str, str]:
    """항목명, 규격, 기존 구분 문자열을 분석하여 7대 표준 공종 코드와 명칭을 반환합니다."""
    text = f"{raw_cat} {name} {spec}".lower()
    
    # 1. 인건비/인력 우선 판별
    if any(k in text for k in ["인원", "일수", "투입률", "m/d", "인건비", "노무비", "목수", "도장공", "전기공", "반장", "조공", "일당"]):
        if not any(k in text for k in ["테이블", "집기", "mdf", "갈바", "가구"]):
            return "LABOR_ONSITE", COST_CATEGORIES["LABOR_ONSITE"]["name"]
            
    # 2. 기획/디자인/설계
    if any(k in text for k in ["기획", "디자인", "3d", "설계", "도면", "감리", "원형", "개발"]):
        if not any(k in text for k in ["제작", "테이블", "체험존", "설치"]):
            return "DESIGN_DEV", COST_CATEGORIES["DESIGN_DEV"]["name"]

    best_cat = "FIXTURE_FABRICATION"
    best_score = 0

    for cat_key, meta in COST_CATEGORIES.items():
        score = sum(1 for kw in meta["keywords"] if kw in text)
        if score > best_score:
            best_score = score
            best_cat = cat_key

    return best_cat, COST_CATEGORIES[best_cat]["name"]

def decompose_estimate_by_category(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """견적 항목 목록을 7대 공종으로 분해하고 카테고리별 통계를 산출합니다."""
    total_amount = sum(it.get("금액", 0.0) or 0.0 for it in items)
    
    cat_summary = {}
    for cat_key, meta in COST_CATEGORIES.items():
        cat_summary[cat_key] = {
            "cat_id": meta["id"],
            "cat_name": meta["name"],
            "agency": meta["benchmark_agency"],
            "law": meta["benchmark_law"],
            "items": [],
            "total_amount": 0.0,
            "weight": 0.0,
            "avg_unit_price": 0.0,
            "item_count": 0
        }

    for it in items:
        name = it.get("항목명", "")
        spec = it.get("규격", "")
        raw_cat = it.get("구분", "")
        cat_key, cat_name = classify_item(name, spec, raw_cat)
        
        amt = it.get("금액", 0.0) or 0.0
        it["표준공종코드"] = cat_key
        it["표준공종명"] = cat_name
        
        cat_summary[cat_key]["items"].append(it)
        cat_summary[cat_key]["total_amount"] += amt
        cat_summary[cat_key]["item_count"] += 1

    for cat_key, cdata in cat_summary.items():
        if total_amount > 0:
            cdata["weight"] = cdata["total_amount"] / total_amount * 100.0
        prices = [it.get("단가", 0.0) for it in cdata["items"] if it.get("단가", 0.0) > 0]
        if prices:
            cdata["avg_unit_price"] = sum(prices) / len(prices)

    return {
        "total_amount": total_amount,
        "item_count": len(items),
        "categories": cat_summary
    }

def compare_decomposed_estimates(
    base_decomp: Dict[str, Any],
    rev_decomp: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """기준 견적과 신규 견적의 7대 공종 분해 결과를 상호 대조하여 적정성 진단표를 생성합니다."""
    comparison = []
    base_cats = base_decomp.get("categories", {})
    rev_cats = rev_decomp.get("categories", {})
    
    for cat_key, meta in COST_CATEGORIES.items():
        b_info = base_cats.get(cat_key, {})
        r_info = rev_cats.get(cat_key, {})
        
        b_amt = b_info.get("total_amount", 0.0)
        r_amt = r_info.get("total_amount", 0.0)
        b_wt = b_info.get("weight", 0.0)
        r_wt = r_info.get("weight", 0.0)
        
        diff_amt = r_amt - b_amt
        diff_pct = ((r_amt - b_amt) / b_amt * 100.0) if b_amt > 0 else (100.0 if r_amt > 0 else 0.0)
        wt_shift = r_wt - b_wt
        
        # 적정성 판정 로직
        status = "🟢 적정"
        findings = []
        
        if r_amt == 0 and b_amt > 0:
            status = "⚪ 미반영"
            findings.append("기준 견적의 공종이 신규 견적에서 누락됨")
        elif b_amt == 0 and r_amt > 0:
            status = "🟡 신규 공종"
            findings.append("기준 견적에 없던 신규 공종 추가 편성")
        else:
            if wt_shift > 15.0 and diff_pct > 30.0:
                status = "🔴 과다 의심"
                findings.append(f"전체 예산 대비 비중이 {b_wt:.1f}% → {r_wt:.1f}%로 {wt_shift:+.1f}%p 급증 (비용 {diff_pct:+.1f}%)")
            elif wt_shift > 8.0 or diff_pct > 25.0:
                status = "🟡 확인 요망"
                findings.append(f"비중이 {wt_shift:+.1f}%p 증가 — 세부 사양 확인 필요")
            elif diff_pct < -20.0:
                status = "🔵 절감"
                findings.append(f"기준 대비 비용 {diff_pct:.1f}% 절감 반영")
            else:
                findings.append("기준 견적의 공종별 비용 배분 구조와 유사하게 적정 편성됨")

        comparison.append({
            "공종코드": cat_key,
            "공종명": meta["name"],
            "기준금액": b_amt,
            "기준비중": b_wt,
            "신규금액": r_amt,
            "신규비중": r_wt,
            "비용증감액": diff_amt,
            "증감률": diff_pct,
            "비중변화": wt_shift,
            "판정": status,
            "소견": " | ".join(findings),
            "공공기준": meta["benchmark_agency"]
        })

    return comparison

def calculate_text_similarity(a: str, b: str) -> float:
    """두 텍스트의 키워드 및 시퀀스 유사도를 종합 산출합니다."""
    if not a or not b:
        return 0.0
    c_a = clean_text(a)
    c_b = clean_text(b)
    if c_a == c_b:
        return 1.0
    
    # 키워드 토큰 교집합 (Jaccard)
    tokens_a = set(c_a.split())
    tokens_b = set(c_b.split())
    jaccard = len(tokens_a & tokens_b) / max(len(tokens_a | tokens_b), 1)
    
    # difflib 시퀀스 매처
    seq_ratio = difflib.SequenceMatcher(None, c_a, c_b).ratio()
    
    return 0.5 * jaccard + 0.5 * seq_ratio

def find_best_baseline_match(
    target_item: Dict[str, Any],
    base_items: List[Dict[str, Any]]
) -> Tuple[Optional[Dict[str, Any]], float]:
    """신규 항목에 대해 기준 견적 항목 중 가장 유사한 항목을 탐색합니다."""
    t_name = target_item.get("항목명", "")
    t_spec = target_item.get("규격", "")
    t_text = f"{t_name} {t_spec}"
    
    best_item = None
    best_sim = 0.0
    
    for b_item in base_items:
        b_name = b_item.get("항목명", "")
        b_spec = b_item.get("규격", "")
        b_text = f"{b_name} {b_spec}"
        
        sim = calculate_text_similarity(t_text, b_text)
        if sim > best_sim:
            best_sim = sim
            best_item = b_item
            
    return best_item, best_sim

def audit_all_new_items(
    new_items: List[Dict[str, Any]],
    base_items: List[Dict[str, Any]],
    base_decomp: Dict[str, Any],
    currency: str = "KRW"
) -> Tuple[List[Dict[str, Any]], float, int, int, int]:
    """신규 견적의 모든 항목에 대해 기준 단가 풀 및 공공 기준 대비 단가 적정성을 정밀 진단합니다.
    
    반환값: (진단결과목록, 과다청구의심액합계, 적정건수, 주의건수, 과다건수)
    """
    results = []
    total_excess_amount = 0.0
    count_fair = 0
    count_caution = 0
    count_excess = 0
    
    curr_sym = "₩" if currency == "KRW" else "$"

    for it in new_items:
        name = it.get("항목명", "")
        spec = it.get("규격", "")
        qty = it.get("수량", 1.0) or 1.0
        unit = it.get("단위", "식") or "식"
        price = it.get("단가", 0.0) or 0.0
        amount = it.get("금액", 0.0) or (price * qty)
        cat_key = it.get("표준공종코드", "FIXTURE_FABRICATION")
        cat_name = it.get("표준공종명", COST_CATEGORIES.get(cat_key, {}).get("name", "구조체/집기"))
        
        # 1. 기준 견적에서 가장 유사한 항목 탐색
        best_base_item, sim = find_best_baseline_match(it, base_items)
        
        benchmark_price = 0.0
        benchmark_name = ""
        benchmark_type = ""
        
        if best_base_item and sim >= 0.25 and best_base_item.get("단가", 0.0) > 0:
            benchmark_price = best_base_item.get("단가", 0.0)
            benchmark_name = f"{best_base_item.get('항목명')} (유사도 {sim*100:.0f}%)"
            benchmark_type = "기준 유사 항목 단가"
        else:
            # 2. 항목 매칭 실패 시 공종별 평균 단가 적용
            c_info = base_decomp.get("categories", {}).get(cat_key, {})
            benchmark_price = c_info.get("avg_unit_price", 0.0)
            benchmark_name = f"기준 [{cat_name}] 공종 평균 단가"
            benchmark_type = "기준 공종 벤치마크"

        # 3. 단가 변동률 및 적정성 판정
        price_diff = price - benchmark_price
        price_diff_pct = ((price - benchmark_price) / benchmark_price * 100.0) if benchmark_price > 0 else 0.0
        
        status = "🟢 적정"
        findings = []
        action = "정상 승인 가능"
        excess_cost = 0.0
        
        if benchmark_price > 0:
            if price_diff_pct > 25.0:
                status = "🔴 과다 의심"
                count_excess += 1
                excess_cost = max(price_diff * qty, 0.0)
                total_excess_amount += excess_cost
                findings.append(f"기준 단가({curr_sym}{benchmark_price:,.0f}) 대비 {price_diff_pct:+.1f}% 과다 책정 (단가 차이: {curr_sym}{price_diff:+,.0f})")
                action = f"단가 인하 요구 또는 스펙 상향 증빙 제출 요청 (예상 절감: {curr_sym}{excess_cost:,.0f})"
            elif price_diff_pct > 10.0:
                status = "🟡 주의/확인"
                count_caution += 1
                findings.append(f"기준 단가 대비 {price_diff_pct:+.1f}% 다소 높음 (물가변동 범위 초과)")
                action = "자재 거래명세표 및 비교 견적 확인"
            elif price_diff_pct < -20.0:
                status = "🟢 적정 (절감)"
                count_fair += 1
                findings.append(f"기준 단가 대비 {price_diff_pct:.1f}% 저렴하게 제안됨")
                action = "정상 승인"
            else:
                status = "🟢 적정"
                count_fair += 1
                findings.append("기준 단가 및 시장 표준 가격 범위(±10%) 내 적정 편성")
                action = "정상 승인"
        else:
            status = "🟡 검토 요망"
            count_caution += 1
            findings.append("기준 견적 내 동종 단가 부재 — 조달청 표준시장단가 확인 필요")
            action = "사양서 세부 검토"

        results.append({
            "항목명": name,
            "표준공종": cat_name,
            "규격": spec,
            "수량": qty,
            "단위": unit,
            "신규단가": price,
            "기준대응단가": benchmark_price,
            "벤치마크기준": benchmark_name,
            "단가차이": price_diff,
            "단가변동률": price_diff_pct,
            "신규금액": amount,
            "과다의심액": excess_cost,
            "판정": status,
            "상세소견": " | ".join(findings),
            "권고조치": action
        })

    return results, total_excess_amount, count_fair, count_caution, count_excess

def generate_cross_project_audit_report(
    base_proj_name: str,
    base_file_name: str,
    rev_file_name: str,
    base_decomp: Dict[str, Any],
    rev_decomp: Dict[str, Any],
    comparison: List[Dict[str, Any]],
    total_excess: float,
    fair_cnt: int,
    caution_cnt: int,
    excess_cnt: int,
    currency: str = "KRW"
) -> str:
    """광고주/감독관을 위한 견적 적정성 총괄 감리 소견서를 작성합니다."""
    curr_sym = "₩" if currency == "KRW" else "$"
    
    b_total = base_decomp.get("total_amount", 0.0)
    r_total = rev_decomp.get("total_amount", 0.0)
    diff_total = r_total - b_total
    diff_pct = (diff_total / b_total * 100.0) if b_total > 0 else 0.0
    
    # 비중 급증 공종 추출
    high_shift_cats = [c for c in comparison if c.get("비중변화", 0) > 8.0 or c.get("증감률", 0) > 30.0]
    shift_bullets = []
    for c in high_shift_cats:
        shift_bullets.append(f"- **{c['공종명']}**: {curr_sym}{c['신규금액']:,.0f} (비중 {c['신규비중']:.1f}%, 기준 대비 {c['비중변화']:+.1f}%p 증가, {c['판정']})")
    
    shift_str = "\n".join(shift_bullets) if shift_bullets else "- 특이 공종 비중 급증 없음 (균형 편성)"
    
    # 종합 판정 등급
    if excess_cnt > 5 or total_excess > 50000000 or diff_pct > 35.0:
        overall_status = "🚨 **[조건부 승인 / 단가 재협상 요구]**"
        recommendation = f"신규 견적의 단가 및 비중이 광고주 컨펌 기준 대비 과다 책정된 항목이 다수 감지되었습니다. 총 과다 청구 의심액 약 **{curr_sym}{total_excess:,.0f}원**에 대한 단가 인하 및 세부 원가계산서 증빙을 요청하시기 바랍니다."
    elif caution_cnt > 5 or diff_pct > 15.0:
        overall_status = "⚠️ **[주의 / 소명자료 보완 후 승인]**"
        recommendation = f"일부 공종 및 단가에서 기준 대비 상승 요인이 확인되었습니다. 주요 인상 항목에 대한 스펙 변경 확인 후 조건부 승인을 권고합니다."
    else:
        overall_status = "✅ **[적합 / 정상 정산 승인 권고]**"
        recommendation = "신규 견적의 공종별 비중 및 세부 단가가 광고주 컨펌 기준 및 공공 표준 범위 내에서 합리적으로 편성되었습니다."

    opinion = f"""### ⚖️ 제일기획 AX 견적감독관 — 프로젝트간 견적 적정성 총괄 감리 소견

**1. 대조 감리 개요**
- **광고주 컨펌 기준가이드:** `{base_proj_name}` (`{base_file_name}`) — 총 {curr_sym}{b_total:,.0f}원 ({base_decomp['item_count']}개 항목)
- **대조·감리 대상 신규 견적:** `{rev_file_name}` — 총 {curr_sym}{r_total:,.0f}원 ({rev_decomp['item_count']}개 항목)
- **총 예산 변동 규모:** {curr_sym}{diff_total:+,.0f}원 ({diff_pct:+.1f}%)

**2. 종합 적정성 판정:** {overall_status}
{recommendation}

**3. 핵심 감리 지표 요약**
- **단가 적정성 분포:** 🟢 적정 **{fair_cnt}건** | 🟡 주의 **{caution_cnt}건** | 🔴 과다 의심 **{excess_cnt}건**
- **과다 청구 의심액 (절감 기회):** **{curr_sym}{total_excess:,.0f}원** (기준 단가 대비 25% 초과 항목 합계)

**4. 7대 공종 비중 이상 감지 현황**
{shift_str}

**5. 광고주/발주처 대응 가이드**
- 본 진단은 프로젝트마다 견적 양식과 품목 분류가 다른 한계를 극복하기 위해 **7대 표준 공종 분해 및 시맨틱 단가 벤치마킹 기법**을 적용하여 도출되었습니다.
- 과다 의심 항목에 대해서는 본 감독관 시스템에서 생성된 공공기준 소명서를 첨부하여 협상 테이블에 활용하시기 바랍니다.
"""
    return opinion
