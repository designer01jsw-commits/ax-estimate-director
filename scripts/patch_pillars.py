# -*- coding: utf-8 -*-
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '''            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p1 = supervisor_opinion["pillars"][0]
                p2 = supervisor_opinion["pillars"][1]
                st.info(f"**{p1['title']}** [{p1['status']}]\\n\\n{p1['desc']}")
                st.info(f"**{p2['title']}** [{p2['status']}]\\n\\n{p2['desc']}")
            with p_col2:
                p3 = supervisor_opinion["pillars"][2]
                p4 = supervisor_opinion["pillars"][3]
                st.info(f"**{p3['title']}** [{p3['status']}]\\n\\n{p3['desc']}")
                st.info(f"**{p4['title']}** [{p4['status']}]\\n\\n{p4['desc']}")'''

replacement = '''            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p1 = supervisor_opinion["pillars"][0]
                p2 = supervisor_opinion["pillars"][1]
                b1_cls = "framer-badge-red" if "비적합" in p1['status'] else ("framer-badge-amber" if any(k in p1['status'] for k in ["검토", "주의", "조건부"]) else "framer-badge-green")
                b2_cls = "framer-badge-red" if "비적합" in p2['status'] else ("framer-badge-amber" if any(k in p2['status'] for k in ["검토", "주의", "조건부"]) else "framer-badge-green")
                st.markdown(f"""
                <div class="framer-surface-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.3px;">{p1['title']}</div>
                        <span class="framer-pill-badge {b1_cls}">{p1['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--ink-muted); line-height: 1.5; letter-spacing: -0.14px;">{p1['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="framer-surface-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.3px;">{p2['title']}</div>
                        <span class="framer-pill-badge {b2_cls}">{p2['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--ink-muted); line-height: 1.5; letter-spacing: -0.14px;">{p2['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            with p_col2:
                p3 = supervisor_opinion["pillars"][2]
                p4 = supervisor_opinion["pillars"][3]
                b3_cls = "framer-badge-red" if "비적합" in p3['status'] else ("framer-badge-amber" if any(k in p3['status'] for k in ["검토", "주의", "조건부"]) else "framer-badge-green")
                b4_cls = "framer-badge-red" if "비적합" in p4['status'] else ("framer-badge-amber" if any(k in p4['status'] for k in ["검토", "주의", "조건부"]) else "framer-badge-green")
                st.markdown(f"""
                <div class="framer-surface-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.3px;">{p3['title']}</div>
                        <span class="framer-pill-badge {b3_cls}">{p3['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--ink-muted); line-height: 1.5; letter-spacing: -0.14px;">{p3['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="framer-surface-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: #FFFFFF; letter-spacing: -0.3px;">{p4['title']}</div>
                        <span class="framer-pill-badge {b4_cls}">{p4['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--ink-muted); line-height: 1.5; letter-spacing: -0.14px;">{p4['desc']}</div>
                </div>
                """, unsafe_allow_html=True)'''

# Normalize newlines
code_norm = code.replace("\r\n", "\n")
target_norm = target.replace("\r\n", "\n")

if target_norm in code_norm:
    code_norm = code_norm.replace(target_norm, replacement)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code_norm)
    print("SUCCESS: Pillars patched!")
else:
    print("FAIL: target_norm not in code_norm")
