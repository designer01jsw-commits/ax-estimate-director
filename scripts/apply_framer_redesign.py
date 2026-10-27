# -*- coding: utf-8 -*-
"""
Apply Framer Marketing Canvas Design System to app.py
"""

from pathlib import Path

app_path = Path("app.py")
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS block with comprehensive Framer Design Tokens
framer_css = '''
# Framer Dark Canvas Design System Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --canvas: #0A0A0A;
        --surface-1: #141414;
        --surface-2: #1E1E1E;
        --surface-hover: #222222;
        --hairline: #262626;
        --hairline-soft: #1C1C1C;
        --ink: #FFFFFF;
        --ink-muted: #999999;
        --ink-faint: #666666;
        --accent-blue: #0099FF;
        --accent-glow: rgba(0, 153, 255, 0.28);
        --semantic-success: #10B981;
        --semantic-danger: #FF4D4D;
        --semantic-warning: #F59E0B;
        --radius-sm: 4px;
        --radius-md: 12px;
        --radius-lg: 20px;
        --radius-xl: 30px;
        --radius-pill: 100px;
    }

    /* 1. Global Dark Canvas & Typographic Voice */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--canvas) !important;
        color: var(--ink) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-feature-settings: 'cv01', 'cv05', 'cv09', 'cv11', 'ss03', 'ss07', 'tnum', 'dlig' !important;
        -webkit-font-smoothing: antialiased !important;
        letter-spacing: -0.15px !important;
    }

    /* 2. Sidebar Dark Canvas */
    [data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 1px solid var(--hairline-soft) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--ink-muted) !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        margin-top: 18px !important;
        margin-bottom: 8px !important;
    }

    /* 3. Framer Buttons */
    /* Primary CTA: Pure White Pill */
    button[kind="primary"], .stButton > button[kind="primary"], div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: var(--radius-pill) !important;
        padding: 10px 22px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: -0.14px !important;
        border: none !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background-color: #EAEAEA !important;
        color: #000000 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(255, 255, 255, 0.18) !important;
    }

    /* Secondary CTA: Charcoal Pill */
    button[kind="secondary"], .stButton > button, div[data-testid="stButton"] > button, .stDownloadButton > button {
        background-color: var(--surface-1) !important;
        color: var(--ink) !important;
        border-radius: var(--radius-pill) !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: -0.14px !important;
        border: 1px solid var(--hairline) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="secondary"]:hover, .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: var(--surface-2) !important;
        border-color: #383838 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }

    /* 4. Metric Blocks (Surface 1 with 20px radius) */
    div[data-testid="stMetric"] {
        background-color: var(--surface-1) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius-lg) !important;
        padding: 20px 22px !important;
        transition: border-color 0.2s ease, transform 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #383838 !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: -0.13px !important;
        color: var(--ink-muted) !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: 500 !important;
        letter-spacing: -1.0px !important;
        color: var(--ink) !important;
        line-height: 1.15 !important;
        font-feature-settings: 'tnum' on !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: -0.13px !important;
    }

    /* 5. Framer Tabs Navigation (Pill Switcher) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--surface-1) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: var(--radius-pill) !important;
        padding: 5px !important;
        gap: 4px !important;
        display: inline-flex !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-pill) !important;
        padding: 8px 18px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: -0.13px !important;
        color: var(--ink-muted) !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.15s ease-in-out !important;
        white-space: nowrap !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--surface-2) !important;
        color: var(--ink) !important;
        border: 1px solid #333333 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* 6. Inputs & Selectboxes with Sky Blue Focus Ring */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: var(--surface-1) !important;
        border: 1px solid var(--hairline) !important;
        color: var(--ink) !important;
        border-radius: var(--radius-md) !important;
        font-size: 14px !important;
        letter-spacing: -0.14px !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within,
    input:focus, textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }

    /* 7. Expanders & Containers */
    div[data-testid="stExpander"] {
        background-color: var(--surface-1) !important;
        border: 1px solid var(--hairline) !important;
        border-radius: 18px !important;
        margin-bottom: 14px !important;
    }
    div[data-testid="stExpander"] summary {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: var(--ink) !important;
        padding: 14px 20px !important;
    }

    /* 8. Streamlit Alert & Info Overrides */
    div[data-testid="stAlert"] {
        background-color: var(--surface-1) !important;
        border: 1px solid var(--hairline) !important;
        border-left: 3px solid var(--accent-blue) !important;
        border-radius: 16px !important;
        color: var(--ink) !important;
    }

    /* 9. Dataframe Table Dark Styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--hairline) !important;
        border-radius: 16px !important;
        background-color: var(--surface-1) !important;
        overflow: hidden !important;
    }

    /* 10. Links: Sky Blue Accent Only */
    a {
        color: var(--accent-blue) !important;
        text-decoration: none !important;
        transition: opacity 0.15s ease !important;
    }
    a:hover {
        opacity: 0.8 !important;
        text-decoration: underline !important;
    }

    /* 11. Custom Framer Component Classes */
    .framer-hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: var(--radius-pill);
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 500;
        color: var(--ink-muted);
        letter-spacing: -0.13px;
        margin-bottom: 16px;
    }
    .framer-hero-eyebrow .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: var(--semantic-success);
        box-shadow: 0 0 8px var(--semantic-success);
    }
    .framer-hero-title {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
        font-size: 46px !important;
        font-weight: 600 !important;
        letter-spacing: -2.8px !important;
        line-height: 1.05 !important;
        color: var(--ink) !important;
        margin: 0 0 12px 0 !important;
    }
    .framer-hero-subhead {
        font-size: 17px !important;
        font-weight: 400 !important;
        line-height: 1.45 !important;
        color: var(--ink-muted) !important;
        letter-spacing: -0.18px !important;
        margin-bottom: 18px !important;
    }
    .framer-domain-strip {
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: var(--radius-pill);
        padding: 8px 20px;
        font-size: 13px;
        letter-spacing: -0.13px;
        color: var(--ink-muted);
        margin-bottom: 28px;
    }
    .framer-domain-strip a {
        color: var(--accent-blue) !important;
        font-weight: 500;
    }

    /* Framer Signature Spotlight Card (30px radius) */
    .framer-spotlight-card {
        border-radius: var(--radius-xl);
        padding: 30px 34px;
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .framer-spotlight-card:hover {
        transform: translateY(-2px);
    }
    .framer-spotlight-red {
        background: radial-gradient(120% 120% at 50% 0%, #4A1224 0%, #20070F 55%, #141414 100%);
        border: 1px solid rgba(255, 77, 77, 0.45);
        box-shadow: 0 16px 48px rgba(74, 18, 36, 0.35);
    }
    .framer-spotlight-amber {
        background: radial-gradient(120% 120% at 50% 0%, #4A2B0E 0%, #241405 55%, #141414 100%);
        border: 1px solid rgba(245, 158, 11, 0.45);
        box-shadow: 0 16px 48px rgba(74, 43, 14, 0.35);
    }
    .framer-spotlight-green {
        background: radial-gradient(120% 120% at 50% 0%, #0E3E2B 0%, #051A12 55%, #141414 100%);
        border: 1px solid rgba(16, 185, 129, 0.45);
        box-shadow: 0 16px 48px rgba(14, 62, 43, 0.35);
    }

    /* Framer Surface 1 Card (20px radius) */
    .framer-surface-card {
        background-color: var(--surface-1);
        border: 1px solid var(--hairline);
        border-radius: var(--radius-lg);
        padding: 22px 24px;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .framer-surface-card:hover {
        border-color: #383838;
        transform: translateY(-2px);
    }
    .framer-pill-badge {
        display: inline-flex;
        align-items: center;
        border-radius: var(--radius-pill);
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: -0.12px;
    }
    .framer-badge-green {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .framer-badge-red {
        background-color: rgba(239, 68, 68, 0.15);
        color: #FF6B6B;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .framer-badge-amber {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .framer-badge-gray {
        background-color: rgba(255, 255, 255, 0.08);
        color: var(--ink-muted);
        border: 1px solid var(--hairline);
    }
</style>
""", unsafe_allow_html=True)
'''

# Find old CSS block
old_css_marker = '# CSS 스타일링\nst.markdown("""\n<style>\n    .main-title { font-size: 1.85rem; font-weight: 800; color: #0F172A; margin-bottom: 0.1rem; }\n    .sub-title { font-size: 0.95rem; color: #475569; margin-bottom: 1.2rem; }\n    .sheet-badge { background-color: #E0E7FF; color: #3730A3; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }\n</style>\n""", unsafe_allow_html=True)'

if old_css_marker in content:
    content = content.replace(old_css_marker, framer_css)
    print("Replaced CSS styling block successfully.")
else:
    print("WARNING: Old CSS block marker not found directly.")

# Find hero header block
old_hero = '''    st.markdown('<div class="main-title">⚖️ 제일기획 AX대회 — 「견적감독관 (Estimate Supervisor)」</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">총체적 견적 진단 소견 · 6대 공공기준 소명 · 25.6억 44종 키트 벤치마크 · 비전 AI 실시간 감리 시스템</div>', unsafe_allow_html=True)
    st.info("🌐 **신규 영구 도메인(견적감독관):** [https://ax-estimate-supervisor.onrender.com](https://ax-estimate-supervisor.onrender.com) | **기존 도메인(견적감리관):** [https://ax-estimate-director.onrender.com](https://ax-estimate-director.onrender.com) (24/7 무중단 가동)")'''

new_hero = '''    st.markdown("""
    <div style="margin-top: 8px; margin-bottom: 24px;">
        <div class="framer-hero-eyebrow">
            <span class="live-dot"></span>
            <span>CHEIL AX ESTIMATE SUPERVISOR 2.0</span>
            <span style="color: #404040;">|</span>
            <span style="color: var(--accent-blue);">PROD LIVE</span>
        </div>
        <h1 class="framer-hero-title">제일기획 AX 견적감독관</h1>
        <div class="framer-hero-subhead">
            총체적 견적 진단 소견 · 6대 공공기준 소명 · 25.6억 44종 키트 벤치마크 · 비전 AI 실시간 감리 시스템
        </div>
        <div class="framer-domain-strip">
            <span style="color: #FFFFFF; font-weight: 500;">🌐 배포 도메인:</span>
            <span>신규 견적감독관: <a href="https://ax-estimate-supervisor.onrender.com" target="_blank">ax-estimate-supervisor.onrender.com</a></span>
            <span style="color: #404040;">·</span>
            <span>기존 견적감리관: <a href="https://ax-estimate-director.onrender.com" target="_blank">ax-estimate-director.onrender.com</a></span>
            <span style="color: #10B981; font-size: 12px; margin-left: 4px;">● 24/7 가동중</span>
        </div>
    </div>
    """, unsafe_allow_html=True)'''

if old_hero in content:
    content = content.replace(old_hero, new_hero)
    print("Replaced Hero header successfully.")
else:
    print("WARNING: Old hero header marker not found.")

# Update Executive Verdict Box
old_verdict = '''            # [견적감독관 총체적 종합 진단 소견 란 (Executive Diagnostic Verdict)]
            badge_bg = "#FEF2F2" if supervisor_opinion["risk_code"] == "RED" else ("#FFFBEB" if supervisor_opinion["risk_code"] == "AMBER" else "#F0FDF4")
            badge_border = "#EF4444" if supervisor_opinion["risk_code"] == "RED" else ("#F59E0B" if supervisor_opinion["risk_code"] == "AMBER" else "#10B981")

            st.markdown(f"""
            <div style="background-color: {badge_bg}; border: 2px solid {badge_border}; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">🏛️ 견적감독관 총체적 종합 진단 소견 (Executive Diagnostic Verdict)</span>
                    <span style="font-size: 0.95rem; font-weight: 700; background: white; padding: 4px 12px; border-radius: 20px; border: 1px solid {badge_border};">{supervisor_opinion["risk_badge"]}</span>
                </div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #1E293B; margin-bottom: 6px; line-height: 1.5;">
                    👉 <strong>감독관 핵심 권고:</strong> {supervisor_opinion["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)'''

new_verdict = '''            # [견적감독관 총체적 종합 진단 소견 란 (Framer Signature Gradient Spotlight Card)]
            spotlight_class = (
                "framer-spotlight-red" if supervisor_opinion["risk_code"] == "RED"
                else ("framer-spotlight-amber" if supervisor_opinion["risk_code"] == "AMBER" else "framer-spotlight-green")
            )
            badge_class = (
                "framer-badge-red" if supervisor_opinion["risk_code"] == "RED"
                else ("framer-badge-amber" if supervisor_opinion["risk_code"] == "AMBER" else "framer-badge-green")
            )

            st.markdown(f"""
            <div class="framer-spotlight-card {spotlight_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 26px;">🏛️</span>
                        <div>
                            <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; color: var(--ink-muted);">EXECUTIVE DIAGNOSTIC VERDICT</div>
                            <div style="font-size: 24px; font-weight: 600; letter-spacing: -0.8px; color: #FFFFFF; margin-top: 2px;">견적감독관 총체적 종합 진단 소견</div>
                        </div>
                    </div>
                    <div class="framer-pill-badge {badge_class}" style="padding: 6px 18px; font-size: 13px; font-weight: 600;">
                        {supervisor_opinion["risk_badge"]}
                    </div>
                </div>
                <div style="font-size: 16px; font-weight: 400; color: #E8E8E8; line-height: 1.55; letter-spacing: -0.17px; background: rgba(0,0,0,0.38); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 18px 22px;">
                    <strong style="color: #FFFFFF;">👉 감독관 핵심 권고:</strong> {supervisor_opinion["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)'''

if old_verdict in content:
    content = content.replace(old_verdict, new_verdict)
    print("Replaced Executive Verdict Box successfully.")
else:
    print("WARNING: Old verdict marker not found.")

# Update 4대 공종별 정밀 총체적 감리 소견
old_pillars = '''            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p1 = supervisor_opinion["pillars"][0]
                p2 = supervisor_opinion["pillars"][1]
                st.info(f"**{p1['title']}** [{p1['status']}]\n\n{p1['desc']}")
                st.info(f"**{p2['title']}** [{p2['status']}]\n\n{p2['desc']}")
            with p_col2:
                p3 = supervisor_opinion["pillars"][2]
                p4 = supervisor_opinion["pillars"][3]
                st.info(f"**{p3['title']}** [{p3['status']}]\n\n{p3['desc']}")
                st.info(f"**{p4['title']}** [{p4['status']}]\n\n{p4['desc']}")'''

new_pillars = '''            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
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

if old_pillars in content:
    content = content.replace(old_pillars, new_pillars)
    print("Replaced 4 pillars successfully.")
else:
    print("WARNING: Old pillars marker not found.")

# Update 3대 핵심 실행 조치
old_actions = '''            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")
            act_cols = st.columns(3)
            for idx, act in enumerate(supervisor_opinion["action_items"]):
                with act_cols[idx]:
                    st.markdown(f"""
                    <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; min-height: 135px;">
                        <div style="font-size: 0.82rem; font-weight: 700; color: #475569;">{act['order']}</div>
                        <div style="font-size: 0.95rem; font-weight: 800; color: #0F172A; margin: 4px 0;">{act['title']}</div>
                        <div style="font-size: 0.92rem; font-weight: 700; color: #DC2626; margin-bottom: 6px;">{act['amount']}</div>
                        <div style="font-size: 0.82rem; color: #334155;">{act['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)'''

new_actions = '''            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")
            act_cols = st.columns(3)
            for idx, act in enumerate(supervisor_opinion["action_items"]):
                with act_cols[idx]:
                    st.markdown(f"""
                    <div class="framer-surface-card" style="min-height: 150px; padding: 18px 20px;">
                        <div style="font-size: 12px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.5px;">{act['order']}</div>
                        <div style="font-size: 16px; font-weight: 600; color: #FFFFFF; margin: 6px 0 8px 0; letter-spacing: -0.2px;">{act['title']}</div>
                        <div style="font-size: 16px; font-weight: 600; color: #FF6B6B; margin-bottom: 8px; letter-spacing: -0.2px;">{act['amount']}</div>
                        <div style="font-size: 13px; color: var(--ink-muted); line-height: 1.45; letter-spacing: -0.13px;">{act['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)'''

if old_actions in content:
    content = content.replace(old_actions, new_actions)
    print("Replaced 3 action items successfully.")
else:
    print("WARNING: Old action items marker not found.")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app.py with Framer redesign successfully.")
