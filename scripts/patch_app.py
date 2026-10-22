# -*- coding: utf-8 -*-
import sys

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize CRLF to LF for consistent matching, or match with whichever is present
    is_crlf = '\r\n' in content
    line_sep = '\r\n' if is_crlf else '\n'

    # 1. Update title and banner
    old_title_banner = line_sep.join([
        '    st.markdown(\'<div class="main-title">⚖️ 제일기획 AX대회 — 「견적감독관」</div>\', unsafe_allow_html=True)',
        '    st.info("🌐 **팀원 공유용 오픈 도메인 주소:** [https://deposit-ceiling-loving-homework.trycloudflare.com](https://deposit-ceiling-loving-homework.trycloudflare.com) (비밀번호 없음, 모바일/PC 즉시 접속 가능)")'
    ])

    new_title_banner = line_sep.join([
        '    st.markdown(\'<div class="main-title">⚖️ 제일기획 AX대회 — 「견적감독관 (Estimate Supervisor)」</div>\', unsafe_allow_html=True)',
        '    st.markdown(\'<div class="sub-title">총체적 견적 진단 소견 · 6대 공공기준 소명 · 25.6억 44종 키트 벤치마크 · 비전 AI 실시간 감리 시스템</div>\', unsafe_allow_html=True)',
        '    st.info("🌐 **신규 영구 도메인(견적감독관):** [https://ax-estimate-supervisor.onrender.com](https://ax-estimate-supervisor.onrender.com) | **기존 도메인(견적감리관):** [https://ax-estimate-director.onrender.com](https://ax-estimate-director.onrender.com) (24/7 무중단 가동)")'
    ])

    if old_title_banner in content:
        content = content.replace(old_title_banner, new_title_banner, 1)
        print("1. Title banner replaced")
    else:
        print("Warning: old_title_banner not found")

    # 2. Add supervisor_opinion calculation before tabs
    old_calc = line_sep.join([
        '        fit_count = len([d for d in all_diagnosed if d["판정"] == "적합"])',
        '',
        '        # 9대 감리 및 비전/학습 탭'
    ])

    new_calc = line_sep.join([
        '        fit_count = len([d for d in all_diagnosed if d["판정"] == "적합"])',
        '',
        '        # 견적감독관 총체적 종합 진단 소견 생성',
        '        supervisor_opinion = generate_executive_supervisor_opinion(',
        '            diagnosed_estimates=diagnosed_estimates,',
        '            diagnosed_labor=diagnosed_labor,',
        '            summary=summary,',
        '            project_name=selected_proj.get("name", "프로젝트"),',
        '            baseline_norms=baseline_norms',
        '        )',
        '',
        '        # 9대 감리 및 비전/학습 탭'
    ])

    if old_calc in content:
        content = content.replace(old_calc, new_calc, 1)
        print("2. Supervisor opinion calculation inserted")
    else:
        print("Warning: old_calc not found")

    # 3. Update tab name
    old_tab = 'f"⚖️ 견적 진단·감리실 (적합 {fit_count} / 비적합 {unfit_count})"'
    new_tab = 'f"⚖️ 견적감독관 종합진단실 (적합 {fit_count} / 비적합 {unfit_count})"'
    if old_tab in content:
        content = content.replace(old_tab, new_tab, 1)
        print("3. Tab name replaced")
    else:
        print("Warning: old_tab not found")

    # 4. Insert Comprehensive Opinion Box into tab_diagnostics
    old_tab_diag = line_sep.join([
        '        # 0. 견적 진단·감리실 (적합/비적합 & 공공기준 소명)',
        '        with tab_diagnostics:',
        '            st.subheader("⚖️ 견적 진단사 & 감독관 정밀 감리실")',
        '            st.markdown(',
        '                "기준 견적서의 데이터를 분해하여 자체 정규화 기준을 수립한 뒤, 신규 견적서를 "',
        '                "**[인력비 / 인력 투입률 / 단가 / 제작비 / 승인절차]** 5대 축으로 분해하여 적합/비적합을 판정하고 공신력 있는 공공 기준(KIDP, KOSA, KENCA, KBIZ, 근로기준법, 나라장터)을 연계합니다."',
        '            )'
    ])

    new_tab_diag = line_sep.join([
        '        # 0. 견적 진단·감리실 (적합/비적합 & 공공기준 소명)',
        '        with tab_diagnostics:',
        '            st.subheader("⚖️ 견적감독관 종합진단실 — 총체적 종합의견")',
        '',
        '            # [견적감독관 총체적 종합 진단 소견 란 (Executive Diagnostic Verdict)]',
        '            badge_bg = "#FEF2F2" if supervisor_opinion["risk_code"] == "RED" else ("#FFFBEB" if supervisor_opinion["risk_code"] == "AMBER" else "#F0FDF4")',
        '            badge_border = "#EF4444" if supervisor_opinion["risk_code"] == "RED" else ("#F59E0B" if supervisor_opinion["risk_code"] == "AMBER" else "#10B981")',
        '',
        '            st.markdown(f"""',
        '            <div style="background-color: {badge_bg}; border: 2px solid {badge_border}; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">',
        '                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">',
        '                    <span style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">🏛️ 견적감독관 총체적 종합 진단 소견 (Executive Diagnostic Verdict)</span>',
        '                    <span style="font-size: 0.95rem; font-weight: 700; background: white; padding: 4px 12px; border-radius: 20px; border: 1px solid {badge_border};">{supervisor_opinion["risk_badge"]}</span>',
        '                </div>',
        '                <div style="font-size: 1.05rem; font-weight: 600; color: #1E293B; margin-bottom: 6px; line-height: 1.5;">',
        '                    👉 <strong>감독관 핵심 권고:</strong> {supervisor_opinion["recommendation"]}',
        '                </div>',
        '            </div>',
        '            """, unsafe_allow_html=True)',
        '',
        '            # 4대 핵심 감리 지표 카드',
        '            m1, m2, m3, m4 = st.columns(4)',
        '            m1.metric("🚨 종합 리스크 판정", supervisor_opinion["risk_grade"])',
        '            m2.metric("💰 부적정 삭감 타겟액", format_currency(supervisor_opinion["total_cut_demand"], currency), delta="즉시 감액 청구", delta_color="inverse")',
        '            m3.metric("🎯 최종 권고 합의선", format_currency(supervisor_opinion["target_budget"], currency), delta="승인 마지노선")',
        '            m4.metric("🛡️ 공공기준 적합률", f"{supervisor_opinion[\'fit_rate\']:.1f}%", f"적합 {supervisor_opinion[\'fit_count\']}건 / 비적합 {supervisor_opinion[\'unfit_count\']}건")',
        '',
        '            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")',
        '            p_col1, p_col2 = st.columns(2)',
        '            with p_col1:',
        '                p1 = supervisor_opinion["pillars"][0]',
        '                p2 = supervisor_opinion["pillars"][1]',
        '                st.info(f"**{p1[\'title\']}** [{p1[\'status\']}]\\n\\n{p1[\'desc\']}")',
        '                st.info(f"**{p2[\'title\']}** [{p2[\'status\']}]\\n\\n{p2[\'desc\']}")',
        '            with p_col2:',
        '                p3 = supervisor_opinion["pillars"][2]',
        '                p4 = supervisor_opinion["pillars"][3]',
        '                st.info(f"**{p3[\'title\']}** [{p3[\'status\']}]\\n\\n{p3[\'desc\']}")',
        '                st.info(f"**{p4[\'title\']}** [{p4[\'status\']}]\\n\\n{p4[\'desc\']}")',
        '',
        '            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")',
        '            act_cols = st.columns(3)',
        '            for idx, act in enumerate(supervisor_opinion["action_items"]):',
        '                with act_cols[idx]:',
        '                    st.markdown(f"""',
        '                    <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; min-height: 135px;">',
        '                        <div style="font-size: 0.82rem; font-weight: 700; color: #475569;">{act[\'order\']}</div>',
        '                        <div style="font-size: 0.95rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{act[\'title\']}</div>',
        '                        <div style="font-size: 0.92rem; font-weight: 700; color: #DC2626; margin-bottom: 6px;">{act[\'amount\']}</div>',
        '                        <div style="font-size: 0.82rem; color: #334155;">{act[\'detail\']}</div>',
        '                    </div>',
        '                    """, unsafe_allow_html=True)',
        '',
        '            with st.expander("📋 결재용 견적감독관 종합소견서 전문 (원클릭 복사 & 다운로드)", expanded=False):',
        '                st.text_area("결재용 소견서 텍스트 전문", value=supervisor_opinion["verdict_text"], height=220)',
        '                st.download_button(',
        '                    "📥 견적감독관 종합소견서(.md) 다운로드",',
        '                    data=supervisor_opinion["verdict_md"].encode("utf-8"),',
        '                    file_name=f"견적감독관_종합소견서_{selected_proj.get(\'id\', \'PROJ\')}.md",',
        '                    mime="text/markdown"',
        '                )',
        '',
        '            st.markdown("---")',
        '            st.markdown("##### 🔍 세부 항목별 정밀 감리 진단표")'
    ])

    if old_tab_diag in content:
        content = content.replace(old_tab_diag, new_tab_diag, 1)
        print("4. Comprehensive opinion box inserted into tab_diagnostics")
    else:
        print("Warning: old_tab_diag not found")

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done patching app.py!")

if __name__ == '__main__':
    main()
