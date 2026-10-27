# -*- coding: utf-8 -*-
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '''                problem_items = [d for d in target_diag if d["판정"] in ["비적합", "조건부 적합"]]
                if problem_items:
                    st.markdown("##### 🔍 비적합 / 조건부 적합 항목별 공공 기준 상세 분석 및 산출식")
                    for p_idx, it in enumerate(problem_items):
                        badge_color = "🔴" if it["판정"] == "비적합" else "🟡"
                        with st.container():
                            st.markdown(f"**{badge_color} [{it['판정']}] {it['항목명']}** (분해축: `{it['분해축']}` | 변동액: `{format_currency(it['변동금액'], currency)}`)")
                            st.markdown(f"- **진단 사유:** {it['상세사유']}")
                            if it.get("공공기준_근거"):
                                st.markdown("- **공신력 있는 정부/공공 기준 적용 상세:**")
                                for cite in it["공공기준_근거"]:
                                    url_md = f" [[공식 사이트 바로가기]({cite['URL']})]" if cite.get("URL") else ""
                                    st.markdown(f"  * 🏛️ **{cite['기관']}** / `{cite.get('법령', '')}`{url_md}")
                                    if "적용기준" in cite:
                                        st.markdown(f"    - **적용 고시 기준:** {cite['적용기준']}")
                                    if "산출공식" in cite:
                                        st.markdown(f"    - **정밀 산출 공식:** `{cite['산출공식']}`")
                                    st.markdown(f"    - **법령/기준 요약:** {cite['내용']}")
                            st.markdown(f"- **👉 감독관 시정 조치:** :red[**{it['조치사항']}**]")
                            st.divider()'''

replacement = '''                problem_items = [d for d in target_diag if d["판정"] in ["비적합", "조건부 적합"]]
                if problem_items:
                    st.markdown("##### 🔍 비적합 / 조건부 적합 항목별 공공 기준 상세 분석 및 산출식")
                    for p_idx, it in enumerate(problem_items):
                        b_cls = "framer-badge-red" if it["판정"] == "비적합" else "framer-badge-amber"
                        cites_html = ""
                        if it.get("공공기준_근거"):
                            cites_html = '<div style="margin-top: 10px; padding: 12px 14px; background: rgba(255,255,255,0.03); border-radius: 12px; border: 1px solid var(--hairline-soft);">'
                            cites_html += '<div style="font-size: 12px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase; margin-bottom: 6px;">공신력 있는 정부/공공 기준 적용 상세</div>'
                            for cite in it["공공기준_근거"]:
                                url_str = f' &nbsp;·&nbsp; <a href="{cite["URL"]}" target="_blank" style="color: var(--accent-blue); font-size: 12px;">공식 고시 링크 ↗</a>' if cite.get("URL") else ""
                                cites_html += f'<div style="font-size: 13px; color: #FFFFFF; font-weight: 500; margin-top: 4px;">🏛️ {cite["기관"]} &nbsp;·&nbsp; <code style="color: var(--ink-muted); background: var(--surface-2); padding: 2px 6px; border-radius: 4px;">{cite.get("법령", "")}</code>{url_str}</div>'
                                if "적용기준" in cite:
                                    cites_html += f'<div style="font-size: 12px; color: var(--ink-muted); margin-left: 18px; margin-top: 2px;">• <strong>적용 고시 기준:</strong> {cite["적용기준"]}</div>'
                                if "산출공식" in cite:
                                    cites_html += f'<div style="font-size: 12px; color: var(--ink-muted); margin-left: 18px; margin-top: 2px;">• <strong>정밀 산출 공식:</strong> <code style="color: var(--accent-blue); background: var(--surface-2); padding: 1px 4px; border-radius: 4px;">{cite["산출공식"]}</code></div>'
                                cites_html += f'<div style="font-size: 12px; color: #888888; margin-left: 18px; margin-top: 2px;">{cite["내용"]}</div>'
                            cites_html += '</div>'

                        st.markdown(f"""
                        <div class="framer-surface-card" style="margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                                <div style="font-size: 17px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.3px;">{it['항목명']}</div>
                                <div style="display: flex; gap: 6px; align-items: center;">
                                    <span class="framer-pill-badge framer-badge-gray">분해축: {it['분해축']}</span>
                                    <span class="framer-pill-badge framer-badge-gray">변동액: {format_currency(it['변동금액'], currency)}</span>
                                    <span class="framer-pill-badge {b_cls}">{it['판정']}</span>
                                </div>
                            </div>
                            <div style="font-size: 14px; color: #CCCCCC; line-height: 1.5; margin-bottom: 8px;">
                                <strong style="color: #FFFFFF;">진단 사유:</strong> {it['상세사유']}
                            </div>
                            {cites_html}
                            <div style="margin-top: 12px; padding: 10px 14px; background: rgba(255, 77, 77, 0.08); border-radius: 10px; border-left: 3px solid #FF4D4D; font-size: 13px; color: #FFAAAA; line-height: 1.45;">
                                <strong style="color: #FF6B6B;">👉 감독관 시정 조치:</strong> {it['조치사항']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)'''

code_norm = code.replace("\r\n", "\n")
target_norm = target.replace("\r\n", "\n")

if target_norm in code_norm:
    code_norm = code_norm.replace(target_norm, replacement)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code_norm)
    print("SUCCESS: Problem items patched to Framer cards!")
else:
    print("FAIL: problem items target not found")
