# -*- coding: utf-8 -*-
"""Patch app.py to integrate cross-project estimate decomposition and reasonableness diagnosis."""

import re
from pathlib import Path

app_path = Path("app.py")
content = app_path.read_text(encoding="utf-8")

# 1. Update imports from auditor.loader and add auditor.categorizer
old_loader_import = """from auditor.loader import (
    load_workbook_safe,
    resolve_sheet,
    read_estimate_sheet,
    read_labor_sheet,
    read_approval_sheet,
    get_common_sheet_names
)"""

new_loader_import = """from auditor.loader import (
    load_workbook_safe,
    resolve_sheet,
    read_estimate_sheet,
    read_labor_sheet,
    read_approval_sheet,
    get_common_sheet_names,
    find_best_estimate_sheet
)
from auditor.categorizer import (
    decompose_estimate_by_category,
    compare_decomposed_estimates,
    audit_all_new_items,
    generate_cross_project_audit_report
)"""

assert old_loader_import in content, "Failed to match old_loader_import"
content = content.replace(old_loader_import, new_loader_import, 1)

# 2. Update sheet matching fallback when common_sheets is empty
old_sheet_fallback = """    else:
        st.sidebar.warning("양쪽 파일에 동일한 이름의 시트가 없습니다. 비교할 시트를 각각 선택해 주세요.")
        sheet_orig_selected = st.sidebar.selectbox("최초 견적서 시트 선택", orig_sheets, index=0)
        sheet_rev_selected = st.sidebar.selectbox("변경 내역서 시트 선택", rev_sheets, index=0)"""

new_sheet_fallback = """    else:
        best_orig_sheet, best_orig_idx = find_best_estimate_sheet(wb_orig, selected_proj.get("default_sheet"))
        best_rev_sheet, best_rev_idx = find_best_estimate_sheet(wb_rev)
        
        st.sidebar.info(f"💡 양쪽 파일의 시트명이 다릅니다.\\n추천 견적 시트: 기준 [{best_orig_sheet}] ⟷ 대조 [{best_rev_sheet}]")
        sheet_orig_selected = st.sidebar.selectbox("기준 견적서 시트 선택", orig_sheets, index=best_orig_idx)
        sheet_rev_selected = st.sidebar.selectbox("대조 견적서 시트 선택", rev_sheets, index=best_rev_idx)"""

assert old_sheet_fallback in content, "Failed to match old_sheet_fallback"
content = content.replace(old_sheet_fallback, new_sheet_fallback, 1)

# 3. Add cross-project decomposition & analysis before st.tabs
old_tab_setup_pattern = re.compile(
    r'(# 견적감독관 총체적 종합 진단 소견 생성.*?'
    r'supervisor_opinion = generate_executive_supervisor_opinion\(.*?\)\s*'
    r')(# 9대 감리 및 비전/학습 탭\s*tab_diagnostics, tab_vision, tab_learning, tab_traffic, tab_decompose, tab_labor, tab_inquiry, tab_confirm, tab_raw = st\.tabs\(\[)',
    re.DOTALL
)

cross_analysis_code = r"""\1
        # 프로젝트간 견적 분해 및 7대 공종 적정성 진단 (양식이 다른 프로젝트 간 비교)
        base_decomp = decompose_estimate_by_category(orig_items)
        rev_decomp = decompose_estimate_by_category(rev_items)
        category_comparison = compare_decomposed_estimates(base_decomp, rev_decomp)
        audited_new_items, total_excess_cost, fair_count, caution_count, excess_count = audit_all_new_items(
            rev_items, orig_items, base_decomp, currency=currency
        )
        cross_audit_opinion = generate_cross_project_audit_report(
            selected_proj.get("name", "기준 프로젝트"), orig_file_name, rev_file_name,
            base_decomp, rev_decomp, category_comparison,
            total_excess_cost, fair_count, caution_count, excess_count, currency=currency
        )

        # 10대 감리 및 비전/학습 탭 (양식초월 적정성 진단 탭 추가)
        tab_cross_audit, tab_diagnostics, tab_vision, tab_learning, tab_traffic, tab_decompose, tab_labor, tab_inquiry, tab_confirm, tab_raw = st.tabs([
            f"🎯 양식초월 견적 분해 & 적정성 진단 (과다 {excess_count} / 적정 {fair_count})",
"""

assert old_tab_setup_pattern.search(content), "Failed to match old_tab_setup_pattern"
content = old_tab_setup_pattern.sub(cross_analysis_code, content, count=1)

# 4. Insert tab_cross_audit rendering code before tab_diagnostics
old_tab_diag = "# 0. 견적 진단·감리실 (적합/비적합 & 공공기준 소명)\n        with tab_diagnostics:"

new_tab_cross_and_diag = """# [신규 핵심] 양식초월 견적 분해 & 다차원 적정성 진단실
        with tab_cross_audit:
            st.subheader("🎯 프로젝트간 견적 분해 & 적정성 진단 (Cross-Project Reasonableness)")
            st.caption("프로젝트마다 견적 양식과 품목이 달라도, 7대 표준 공종 분해 및 시맨틱 단가 벤치마킹을 통해 예산 적정성을 정밀 감리합니다.")

            # 총괄 적정성 판정 카드
            if excess_count > 5 or total_excess_cost > 50000000:
                v_badge = "mc-chip-orange"
                v_title = "🚨 단가 재협상 및 소명 요구 권고 (과다 청구 다수 감지)"
                v_desc = f"기준 견적 대비 단가가 25% 이상 높게 책정된 항목이 총 {excess_count}건 발견되었습니다. 총 <b>{format_currency(total_excess_cost, currency)}</b> 상당의 단가 삭감 또는 거래명세표 증빙이 요구됩니다."
            elif caution_count > 5:
                v_badge = "mc-chip-orange"
                v_title = "⚠️ 조건부 승인 검토 (주요 인상 항목 스펙 확인 필요)"
                v_desc = f"물가변동 범위를 초과하는 인상 항목({caution_count}건)이 감지되었습니다. 사양 상향 여부 확인 후 승인을 권고합니다."
            else:
                v_badge = "mc-chip-black"
                v_title = "🟢 적합 승인 권고 (기준 견적 및 공공 표준 범위 내)"
                v_desc = "신규 견적의 공종별 비중 및 세부 단가가 광고주 컨펌 기준 및 공공 표준시장단가 범위 내에서 안정적으로 편성되었습니다."

            st.markdown(f\"\"\"
            <div class="mc-card" style="padding: 24px 28px; margin-bottom: 24px; border: 1.5px solid var(--border-stone); background: var(--surface-lifted); box-shadow: 0 4px 16px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 20px;">⚖️</span>
                        <span style="font-size: 16px; font-weight: 700; color: var(--ink-black);">{v_title}</span>
                    </div>
                    <span class="mc-pill-chip {v_badge}" style="font-size: 12px;">적정성 총괄 판정</span>
                </div>
                <div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.6; margin-bottom: 16px;">
                    {v_desc}
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; padding-top: 14px; border-top: 1px solid var(--border-stone); font-size: 13px;">
                    <div><span style="color: var(--slate-gray);">기준 총액:</span> <strong style="color: var(--ink-black);">{format_currency(base_decomp['total_amount'], currency)}</strong> ({base_decomp['item_count']}건)</div>
                    <div><span style="color: var(--slate-gray);">신규 총액:</span> <strong style="color: var(--ink-black);">{format_currency(rev_decomp['total_amount'], currency)}</strong> ({rev_decomp['item_count']}건)</div>
                    <div><span style="color: var(--slate-gray);">총액 증감:</span> <strong style="color: var(--signal-orange);">{format_currency(rev_decomp['total_amount'] - base_decomp['total_amount'], currency)}</strong></div>
                    <div><span style="color: var(--slate-gray);">과다 의심액:</span> <strong style="color: #D32F2F;">{format_currency(total_excess_cost, currency)}</strong></div>
                </div>
            </div>
            \"\"\", unsafe_allow_html=True)

            # 1. 7대 표준 공종(비목)별 분해 및 비중(%) 대조표
            st.markdown("#### 📊 1. 7대 공종(비목)별 원가 분해 & 구성비(%) 대조")
            st.caption("양식과 항목 개수가 달라도 모든 제작 견적은 7대 표준 공종으로 분해되어 비중 이상을 감지할 수 있습니다.")

            df_comp = pd.DataFrame([
                {
                    "표준 공종명": c["공종명"],
                    "기준 금액": format_currency(c["기준금액"], currency),
                    "기준 비중": f"{c['기준비중']:.1f}%",
                    "신규 금액": format_currency(c["신규금액"], currency),
                    "신규 비중": f"{c['신규비중']:.1f}%",
                    "비용 증감": format_currency(c["비용증감액"], currency),
                    "비중 변화": f"{c['비중변화']:+.1f}%p",
                    "적정성 판정": c["판정"],
                    "감리 소견": c["소견"],
                    "벤치마크 고시": c["공공기준"]
                }
                for c in category_comparison
            ])
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

            st.markdown("---")

            # 2. 전 항목 단가 적정성 대조표 (기준 단가 풀 + 공공 고시 연계)
            st.markdown("#### 🔍 2. 전 항목 단가 적정성 벤치마크 진단표")
            st.caption("신규 견적의 모든 품목을 기준 견적의 동종 품목 또는 공종별 대표 단가와 1:1 대조하여 과다 여부를 판정합니다.")

            col_flt, col_srch = st.columns([1, 1.5])
            with col_flt:
                status_filter = st.radio(
                    "판정 결과 필터",
                    ["전체 보기", "🔴 과다 의심만", "🟡 주의/확인만", "🟢 적정만"],
                    horizontal=True,
                    key="filter_cross_audit_status"
                )
            with col_srch:
                search_kw = st.text_input("품목명 검색", "", placeholder="예: MDF, 아크릴, 조명, 인건비...", key="search_cross_audit_kw")

            filtered_items = audited_new_items
            if status_filter == "🔴 과다 의심만":
                filtered_items = [it for it in filtered_items if "과다" in it["판정"]]
            elif status_filter == "🟡 주의/확인만":
                filtered_items = [it for it in filtered_items if "주의" in it["판정"] or "검토" in it["판정"]]
            elif status_filter == "🟢 적정만":
                filtered_items = [it for it in filtered_items if "적정" in it["판정"]]

            if search_kw:
                filtered_items = [it for it in filtered_items if search_kw.lower() in it["항목명"].lower() or search_kw.lower() in it.get("규격", "").lower()]

            if filtered_items:
                df_items = pd.DataFrame([
                    {
                        "항목명": it["항목명"],
                        "표준 공종": it["표준공종"],
                        "수량": f"{it['수량']:,.1f} {it['단위']}",
                        "신규 단가": format_currency(it["신규단가"], currency),
                        "기준 대응단가": format_currency(it["기준대응단가"], currency),
                        "단가 변동률": f"{it['단가변동률']:+.1f}%" if it["기준대응단가"] > 0 else "-",
                        "신규 총액": format_currency(it["신규금액"], currency),
                        "과다 의심액": format_currency(it["과다의심액"], currency) if it["과다의심액"] > 0 else "-",
                        "판정": it["판정"],
                        "벤치마크 기준": it["벤치마크기준"],
                        "권고 조치": it["권고조치"]
                    }
                    for it in filtered_items
                ])
                st.dataframe(df_items, use_container_width=True, hide_index=True)
            else:
                st.info("선택한 필터 조건에 부합하는 항목이 없습니다.")

            st.markdown("---")

            # 3. 광고주·감독관 총괄 감리 소견서 및 다운로드
            st.markdown("#### 📝 3. 광고주/발주처 보고용 총괄 감리 소견서")
            st.markdown(cross_audit_opinion)

            st.download_button(
                "📥 견적 적정성 총괄 소견서 다운로드 (.md)",
                cross_audit_opinion,
                file_name=f"견적적정성_총괄감리소견서_{selected_proj.get('project_id', 'PROJ')}.md",
                mime="text/markdown",
                key="btn_download_cross_audit_md"
            )

        # 0. 견적 진단·감리실 (적합/비적합 & 공공기준 소명)
        with tab_diagnostics:"""

assert old_tab_diag in content, "Failed to match old_tab_diag"
content = content.replace(old_tab_diag, new_tab_cross_and_diag, 1)

app_path.write_text(content, encoding="utf-8")
print("SUCCESS: app.py successfully patched with cross-project audit tab and engine!")
