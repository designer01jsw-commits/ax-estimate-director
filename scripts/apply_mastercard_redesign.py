# -*- coding: utf-8 -*-
"""
Apply Mastercard Inspired Design System to app.py
"""

from pathlib import Path

app_path = Path("app.py")
with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# Mastercard Inspired Design System CSS
mc_css = '''# Mastercard Inspired Design System Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sofia+Sans:ital,wght@0,400;0,450;0,500;0,600;0,700;0,800;1,400;1,500&family=Inter:wght@400;450;500;600;700&display=swap');

    :root {
        --canvas-cream: #F3F0EE;
        --lifted-cream: #FCFBFA;
        --white: #FFFFFF;
        --soft-bone: #F4F4F4;
        --ink-black: #141413;
        --charcoal: #262627;
        --slate-gray: #696969;
        --granite: #555555;
        --dust-taupe: #D1CDC7;
        --signal-orange: #CF4500;
        --light-signal-orange: #F37338;
        --clay-brown: #9A3A0A;
        --link-blue: #3860BE;
        --semantic-success: #10B981;
        --semantic-danger: #CF4500;
        --semantic-warning: #F79E1B;
        
        --radius-pill: 999px;
        --radius-stadium: 40px;
        --radius-card: 20px;
        --radius-button: 20px;
        --radius-circle: 50%;
        
        --shadow-nav: rgba(0, 0, 0, 0.04) 0px 4px 24px 0px;
        --shadow-cushion: rgba(0, 0, 0, 0.06) 0px 18px 40px 0px;
        --shadow-card: rgba(0, 0, 0, 0.03) 0px 6px 20px 0px;
    }

    /* 1. Global Canvas Cream & Sofia Sans Typography */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--canvas-cream) !important;
        color: var(--ink-black) !important;
        font-family: 'Sofia Sans', 'Inter', Arial, sans-serif !important;
        font-weight: 450 !important;
        line-height: 1.4 !important;
        -webkit-font-smoothing: antialiased !important;
        letter-spacing: normal !important;
    }

    /* 2. Sidebar: Lifted Cream with Subtle Border */
    [data-testid="stSidebar"] {
        background-color: var(--lifted-cream) !important;
        border-right: 1.5px solid rgba(20, 20, 19, 0.08) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--slate-gray) !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-top: 18px !important;
        margin-bottom: 8px !important;
    }

    /* 3. Typography Headings: 500 weight with tight -2% letter spacing */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Sofia Sans', sans-serif !important;
        color: var(--ink-black) !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
    }
    h2 {
        font-size: 28px !important;
        margin-top: 36px !important;
        margin-bottom: 16px !important;
    }
    h3 {
        font-size: 22px !important;
    }

    /* 4. Primary Button: Ink Black Pill (20px radius) with Canvas Cream text */
    button[kind="primary"], .stButton > button[kind="primary"], div[data-testid="stButton"] > button[kind="primary"] {
        background-color: var(--ink-black) !important;
        color: var(--canvas-cream) !important;
        border-radius: var(--radius-button) !important;
        padding: 8px 24px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        letter-spacing: -0.32px !important;
        border: 1.5px solid var(--ink-black) !important;
        box-shadow: 0 2px 6px rgba(20, 20, 19, 0.15) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        background-color: var(--charcoal) !important;
        color: var(--canvas-cream) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(20, 20, 19, 0.25) !important;
    }

    /* 5. Secondary Button: White Pill with Ink Black outline & text */
    button[kind="secondary"], .stButton > button, div[data-testid="stButton"] > button, .stDownloadButton > button {
        background-color: var(--white) !important;
        color: var(--ink-black) !important;
        border-radius: var(--radius-button) !important;
        padding: 8px 24px !important;
        font-size: 16px !important;
        font-weight: 450 !important;
        letter-spacing: -0.32px !important;
        border: 1.5px solid var(--ink-black) !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="secondary"]:hover, .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: var(--soft-bone) !important;
        color: var(--ink-black) !important;
        transform: translateY(-1px) !important;
    }

    /* 6. Metric Blocks (Lifted Cream with 20px radius) */
    div[data-testid="stMetric"] {
        background-color: var(--lifted-cream) !important;
        border: 1.5px solid rgba(20, 20, 19, 0.08) !important;
        border-radius: var(--radius-card) !important;
        padding: 22px 24px !important;
        box-shadow: var(--shadow-card) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-cushion) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        color: var(--slate-gray) !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        color: var(--ink-black) !important;
        line-height: 1.15 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    /* 7. Tabs Navigation: Pill Switcher (999px radius) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--lifted-cream) !important;
        border: 1.5px solid rgba(20, 20, 19, 0.08) !important;
        border-radius: var(--radius-pill) !important;
        padding: 6px !important;
        gap: 4px !important;
        display: inline-flex !important;
        box-shadow: var(--shadow-card) !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-pill) !important;
        padding: 8px 20px !important;
        font-size: 14px !important;
        font-weight: 450 !important;
        color: var(--slate-gray) !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.15s ease-in-out !important;
        white-space: nowrap !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--ink-black) !important;
        color: var(--canvas-cream) !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 14px rgba(20, 20, 19, 0.2) !important;
    }
    .stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* 8. Inputs, Selectboxes, Textareas (20px radius & White fill) */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    input, textarea {
        background-color: var(--white) !important;
        border: 1.5px solid rgba(20, 20, 19, 0.15) !important;
        color: var(--ink-black) !important;
        border-radius: 20px !important;
        font-size: 15px !important;
    }
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within,
    input:focus, textarea:focus {
        border-color: var(--ink-black) !important;
        box-shadow: 0 0 0 2px rgba(20, 20, 19, 0.15) !important;
    }

    /* 9. Expanders with 20px radius */
    div[data-testid="stExpander"] {
        background-color: var(--lifted-cream) !important;
        border: 1.5px solid rgba(20, 20, 19, 0.08) !important;
        border-radius: var(--radius-card) !important;
        box-shadow: var(--shadow-card) !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stExpander"] summary {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: var(--ink-black) !important;
        padding: 16px 22px !important;
    }

    /* 10. Dataframe Tables */
    [data-testid="stDataFrame"] {
        border: 1.5px solid rgba(20, 20, 19, 0.08) !important;
        border-radius: var(--radius-card) !important;
        background-color: var(--white) !important;
        box-shadow: var(--shadow-card) !important;
        overflow: hidden !important;
    }

    /* 11. Alerts & Info: Lifted Cream with Signal Orange left border */
    div[data-testid="stAlert"] {
        background-color: var(--lifted-cream) !important;
        border: 1.5px solid rgba(20, 20, 19, 0.08) !important;
        border-left: 4px solid var(--signal-orange) !important;
        border-radius: var(--radius-card) !important;
        color: var(--ink-black) !important;
    }

    /* 12. Links: Dusty Link Blue */
    a {
        color: var(--link-blue) !important;
        text-decoration: none !important;
    }
    a:hover {
        text-decoration: underline !important;
    }

    /* 13. Mastercard Floating Nav Pill */
    .mc-floating-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: var(--white);
        border-radius: var(--radius-pill);
        padding: 12px 32px;
        margin: 6px 0 24px 0;
        box-shadow: var(--shadow-nav);
        border: 1px solid rgba(20, 20, 19, 0.05);
    }
    .mc-brand-mark {
        display: inline-flex;
        align-items: center;
    }
    .mc-circle-red {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #EB001B;
        display: inline-block;
    }
    .mc-circle-yellow {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background-color: #F79E1B;
        display: inline-block;
        margin-left: -9px;
        opacity: 0.92;
    }

    /* 14. Mastercard Hero Stadium Frame (40px radius) */
    .mc-hero-stadium {
        background-color: var(--lifted-cream);
        border-radius: var(--radius-stadium);
        padding: 40px 48px;
        margin-bottom: 28px;
        position: relative;
        border: 1.5px solid rgba(20, 20, 19, 0.08);
        box-shadow: var(--shadow-cushion);
        overflow: hidden;
    }
    .mc-orbital-arc {
        position: absolute;
        top: -60px;
        right: -60px;
        width: 280px;
        height: 280px;
        border: 1.5px solid var(--light-signal-orange);
        border-radius: 50%;
        opacity: 0.35;
        pointer-events: none;
    }
    .mc-eyebrow {
        font-size: 13px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        color: var(--slate-gray) !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 12px;
    }
    .mc-eyebrow-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--signal-orange);
        display: inline-block;
    }
    .mc-hero-title {
        font-family: 'Sofia Sans', sans-serif !important;
        font-size: 52px !important;
        font-weight: 500 !important;
        line-height: 1.05 !important;
        letter-spacing: -0.02em !important;
        color: var(--ink-black) !important;
        margin: 0 0 14px 0 !important;
    }
    .mc-hero-subhead {
        font-size: 18px !important;
        font-weight: 450 !important;
        line-height: 1.45 !important;
        color: var(--slate-gray) !important;
        margin-bottom: 22px !important;
        max-width: 860px;
    }
    .mc-domain-pill {
        display: inline-flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        background-color: var(--white);
        border-radius: var(--radius-pill);
        padding: 8px 22px;
        font-size: 14px;
        color: var(--slate-gray);
        box-shadow: var(--shadow-nav);
        border: 1px solid rgba(20, 20, 19, 0.06);
    }
    .mc-domain-pill a {
        color: var(--link-blue) !important;
        font-weight: 500;
    }

    /* 15. Mastercard Stadium Card (40px) & Card 20 (20px) */
    .mc-stadium-card {
        background-color: var(--lifted-cream);
        border-radius: var(--radius-stadium);
        padding: 34px 40px;
        margin-bottom: 28px;
        border: 1.5px solid rgba(20, 20, 19, 0.08);
        box-shadow: var(--shadow-cushion);
        position: relative;
        overflow: hidden;
    }
    .mc-card-20 {
        background-color: var(--lifted-cream);
        border-radius: var(--radius-card);
        padding: 22px 26px;
        border: 1.5px solid rgba(20, 20, 19, 0.08);
        box-shadow: var(--shadow-card);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .mc-card-20:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-cushion);
    }
    .mc-pill-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: var(--radius-pill);
        padding: 5px 16px;
        font-size: 13px;
        font-weight: 500;
    }
    .mc-chip-ink {
        background-color: var(--ink-black);
        color: var(--canvas-cream);
    }
    .mc-chip-orange {
        background-color: rgba(207, 69, 0, 0.1);
        color: var(--signal-orange);
        border: 1px solid rgba(207, 69, 0, 0.25);
    }
    .mc-chip-green {
        background-color: rgba(16, 185, 129, 0.1);
        color: #0E7C57;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .mc-chip-gray {
        background-color: var(--white);
        color: var(--slate-gray);
        border: 1px solid rgba(20, 20, 19, 0.1);
    }
    .mc-satellite-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: var(--white);
        border-radius: var(--radius-pill);
        padding: 6px 18px;
        box-shadow: var(--shadow-card);
        border: 1px solid rgba(20, 20, 19, 0.08);
        font-size: 13px;
        font-weight: 500;
        color: var(--ink-black);
    }
    .mc-satellite-arrow {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background-color: var(--ink-black);
        color: var(--canvas-cream);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }

    /* 16. Mastercard Warm Dark Footer */
    .mc-footer {
        background-color: var(--ink-black);
        color: var(--white);
        border-radius: 40px 40px 0 0;
        padding: 52px 60px 40px 60px;
        margin-top: 60px;
    }
    .mc-footer-title {
        font-family: 'Sofia Sans', sans-serif !important;
        font-size: 32px !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        color: var(--white) !important;
        margin-bottom: 14px !important;
    }
</style>
""", unsafe_allow_html=True)
'''

# Find existing CSS block in app.py
css_start = content.find("# Framer Dark Canvas Design System Styling")
if css_start == -1:
    css_start = content.find("# CSS 스타일링")

css_end = content.find("def format_currency", css_start)
if css_start != -1 and css_end != -1:
    content = content[:css_start] + mc_css + "\n\n" + content[css_end:]
    print("Replaced CSS styling with Mastercard Design System!")
else:
    print("WARNING: CSS block boundaries not found.")

# New Hero Stadium Frame
mc_hero = '''    st.markdown("""
    <div class="mc-floating-nav">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="mc-brand-mark">
                <span class="mc-circle-red"></span>
                <span class="mc-circle-yellow"></span>
            </div>
            <span style="font-size: 16px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-size: 13px; font-weight: 500; color: var(--slate-gray);">• 정밀 감리 엔진 v2.0</span>
            <span class="mc-pill-chip mc-chip-orange" style="font-size: 12px;">● PROD LIVE 24/7</span>
        </div>
    </div>

    <div class="mc-hero-stadium">
        <div class="mc-orbital-arc"></div>
        <div class="mc-eyebrow">
            <span class="mc-eyebrow-dot"></span>
            <span>EDITORIAL AUDIT INTELLIGENCE</span>
        </div>
        <h1 class="mc-hero-title">제일기획 AX 견적감독관</h1>
        <div class="mc-hero-subhead">
            총체적 견적 진단 소견 · 6대 공공기준 소명 · 25.6억 44종 키트 벤치마크 · 비전 AI 실시간 감리 시스템
        </div>
        <div class="mc-domain-pill">
            <span style="color: var(--ink-black); font-weight: 500;">🌐 배포 도메인:</span>
            <span>신규 견적감독관: <a href="https://ax-estimate-supervisor.onrender.com" target="_blank">ax-estimate-supervisor.onrender.com</a></span>
            <span style="color: #D1CDC7;">|</span>
            <span>기존 견적감리관: <a href="https://ax-estimate-director.onrender.com" target="_blank">ax-estimate-director.onrender.com</a></span>
            <span class="mc-satellite-arrow" style="margin-left: 6px;">↗</span>
        </div>
    </div>
    """, unsafe_allow_html=True)'''

# Replace Hero Header
hero_start = content.find('    st.markdown("""\n    <div style="margin-top: 8px; margin-bottom: 24px;">')
if hero_start != -1:
    hero_end = content.find('    # 1. 프로젝트 목록 로드', hero_start)
    if hero_end != -1:
        content = content[:hero_start] + mc_hero + "\n\n" + content[hero_end:]
        print("Replaced Hero header with Mastercard Stadium Frame!")
    else:
        print("WARNING: Hero end boundary not found.")
else:
    print("WARNING: Hero start boundary not found.")

# New Executive Verdict Box
mc_verdict = '''            # [견적감독관 총체적 종합 진단 소견 란 (Mastercard Stadium Card)]
            st.markdown(f"""
            <div class="mc-stadium-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div class="mc-eyebrow" style="margin-bottom: 6px;">
                            <span class="mc-eyebrow-dot"></span>
                            <span>EXECUTIVE DIAGNOSTIC VERDICT</span>
                        </div>
                        <div style="font-size: 26px; font-weight: 500; letter-spacing: -0.02em; color: var(--ink-black);">
                            🏛️ 견적감독관 총체적 종합 진단 소견
                        </div>
                    </div>
                    <div class="mc-satellite-badge">
                        <span>{supervisor_opinion["risk_badge"]}</span>
                        <span class="mc-satellite-arrow">→</span>
                    </div>
                </div>
                <div style="font-size: 16px; font-weight: 450; color: var(--ink-black); line-height: 1.55; background: var(--white); border: 1.5px solid rgba(20, 20, 19, 0.08); border-radius: 20px; padding: 20px 24px; box-shadow: var(--shadow-card);">
                    <strong style="color: var(--signal-orange);">👉 감독관 핵심 권고:</strong> {supervisor_opinion["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)'''

verdict_start = content.find('            # [견적감독관 총체적 종합 진단 소견 란')
if verdict_start != -1:
    verdict_end = content.find('            # 4대 핵심 감리 지표 카드', verdict_start)
    if verdict_end != -1:
        content = content[:verdict_start] + mc_verdict + "\n\n" + content[verdict_end:]
        print("Replaced Executive Verdict with Mastercard Stadium Card!")
    else:
        print("WARNING: Verdict end boundary not found.")
else:
    print("WARNING: Verdict start boundary not found.")

# New 4 Pillars
mc_pillars = '''            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p1 = supervisor_opinion["pillars"][0]
                p2 = supervisor_opinion["pillars"][1]
                chip1 = "mc-chip-orange" if "비적합" in p1['status'] else ("mc-chip-orange" if any(k in p1['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                chip2 = "mc-chip-orange" if "비적합" in p2['status'] else ("mc-chip-orange" if any(k in p2['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p1['title']}</div>
                        <span class="mc-pill-chip {chip1}">{p1['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p1['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p2['title']}</div>
                        <span class="mc-pill-chip {chip2}">{p2['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p2['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            with p_col2:
                p3 = supervisor_opinion["pillars"][2]
                p4 = supervisor_opinion["pillars"][3]
                chip3 = "mc-chip-orange" if "비적합" in p3['status'] else ("mc-chip-orange" if any(k in p3['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                chip4 = "mc-chip-orange" if "비적합" in p4['status'] else ("mc-chip-orange" if any(k in p4['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p3['title']}</div>
                        <span class="mc-pill-chip {chip3}">{p3['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p3['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p4['title']}</div>
                        <span class="mc-pill-chip {chip4}">{p4['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p4['desc']}</div>
                </div>
                """, unsafe_allow_html=True)'''

pillars_start = content.find('            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")')
if pillars_start != -1:
    pillars_end = content.find('            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")', pillars_start)
    if pillars_end != -1:
        content = content[:pillars_start] + mc_pillars + "\n\n" + content[pillars_end:]
        print("Replaced 4 pillars with Mastercard cards!")
    else:
        print("WARNING: Pillars end boundary not found.")
else:
    print("WARNING: Pillars start boundary not found.")

# New Action Items
mc_actions = '''            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")
            act_cols = st.columns(3)
            for idx, act in enumerate(supervisor_opinion["action_items"]):
                with act_cols[idx]:
                    st.markdown(f"""
                    <div class="mc-card-20" style="min-height: 155px; background: var(--white);">
                        <div class="mc-eyebrow" style="margin-bottom: 4px;">
                            <span class="mc-eyebrow-dot"></span>
                            <span>{act['order']}</span>
                        </div>
                        <div style="font-size: 16px; font-weight: 500; color: var(--ink-black); margin-bottom: 6px; letter-spacing: -0.02em;">{act['title']}</div>
                        <div style="font-size: 16px; font-weight: 700; color: var(--signal-orange); margin-bottom: 8px;">{act['amount']}</div>
                        <div style="font-size: 13px; color: var(--slate-gray); line-height: 1.45;">{act['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)'''

actions_start = content.find('            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")')
if actions_start != -1:
    actions_end = content.find('            with st.expander("📋 결재용 견적감독관 종합소견서 전문', actions_start)
    if actions_end != -1:
        content = content[:actions_start] + mc_actions + "\n\n" + content[actions_end:]
        print("Replaced Action Items with Mastercard cards!")
    else:
        print("WARNING: Actions end boundary not found.")
else:
    print("WARNING: Actions start boundary not found.")

# New Problem Items
mc_problems = '''                problem_items = [d for d in target_diag if d["판정"] in ["비적합", "조건부 적합"]]
                if problem_items:
                    st.markdown("##### 🔍 비적합 / 조건부 적합 항목별 공공 기준 상세 분석 및 산출식")
                    for p_idx, it in enumerate(problem_items):
                        b_cls = "mc-chip-orange" if it["판정"] == "비적합" else "mc-chip-gray"
                        cites_html = ""
                        if it.get("공공기준_근거"):
                            cites_html = '<div style="margin-top: 10px; padding: 12px 16px; background: var(--soft-bone); border-radius: 16px; border: 1px solid rgba(20, 20, 19, 0.06);">'
                            cites_html += '<div class="mc-eyebrow" style="margin-bottom: 4px;"><span class="mc-eyebrow-dot"></span><span>공신력 있는 정부/공공 기준 적용 상세</span></div>'
                            for cite in it["공공기준_근거"]:
                                url_str = f' &nbsp;·&nbsp; <a href="{cite["URL"]}" target="_blank" style="color: var(--link-blue); font-size: 12px;">공식 고시 링크 ↗</a>' if cite.get("URL") else ""
                                cites_html += f'<div style="font-size: 14px; color: var(--ink-black); font-weight: 500; margin-top: 4px;">🏛️ {cite["기관"]} &nbsp;·&nbsp; <code style="color: var(--slate-gray); background: var(--white); padding: 2px 6px; border-radius: 4px;">{cite.get("법령", "")}</code>{url_str}</div>'
                                if "적용기준" in cite:
                                    cites_html += f'<div style="font-size: 12px; color: var(--slate-gray); margin-left: 18px; margin-top: 2px;">• <strong>적용 고시 기준:</strong> {cite["적용기준"]}</div>'
                                if "산출공식" in cite:
                                    cites_html += f'<div style="font-size: 12px; color: var(--slate-gray); margin-left: 18px; margin-top: 2px;">• <strong>정밀 산출 공식:</strong> <code style="color: var(--signal-orange); background: var(--white); padding: 1px 4px; border-radius: 4px;">{cite["산출공식"]}</code></div>'
                                cites_html += f'<div style="font-size: 12px; color: #555555; margin-left: 18px; margin-top: 2px;">{cite["내용"]}</div>'
                            cites_html += '</div>'

                        st.markdown(f"""
                        <div class="mc-card-20" style="margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                                <div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{it['항목명']}</div>
                                <div style="display: flex; gap: 6px; align-items: center;">
                                    <span class="mc-pill-chip mc-chip-gray">분해축: {it['분해축']}</span>
                                    <span class="mc-pill-chip mc-chip-gray">변동액: {format_currency(it['변동금액'], currency)}</span>
                                    <span class="mc-pill-chip {b_cls}">{it['판정']}</span>
                                </div>
                            </div>
                            <div style="font-size: 14px; color: var(--ink-black); line-height: 1.5; margin-bottom: 8px;">
                                <strong>진단 사유:</strong> {it['상세사유']}
                            </div>
                            {cites_html}
                            <div style="margin-top: 12px; padding: 12px 18px; background: rgba(207, 69, 0, 0.08); border-radius: 20px; border-left: 4px solid var(--signal-orange); font-size: 13px; color: var(--signal-orange); line-height: 1.45;">
                                <strong>👉 감독관 시정 조치:</strong> {it['조치사항']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)'''

problem_start = content.find('                problem_items = [d for d in target_diag if d["판정"] in ["비적합", "조건부 적합"]]')
if problem_start != -1:
    problem_end = content.find('            else:\n                st.success("해당 조건의 항목이 없습니다.")', problem_start)
    if problem_end != -1:
        content = content[:problem_start] + mc_problems + "\n" + content[problem_end:]
        print("Replaced Problem Items with Mastercard cards!")
    else:
        print("WARNING: Problem end boundary not found.")
else:
    print("WARNING: Problem start boundary not found.")

# Add Mastercard Warm Dark Footer at end of main()
footer_code = '''
    # Mastercard Warm Dark Footer
    st.markdown("""
    <div class="mc-footer">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 24px; margin-bottom: 32px;">
            <div>
                <div class="mc-footer-title">We're always here when you need rigorous estimate governance.</div>
                <div style="color: #999999; font-size: 14px; max-width: 620px; line-height: 1.5;">
                    제일기획 AX 견적감독관은 6대 공공기준(KIDP, KOSA, KENCA, KBIZ, 근로기준법, 나라장터) 및 25.6억 44종 키트 빅데이터를 기반으로 최상의 객관적 감리 소견을 제공합니다.
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.08); padding: 8px 20px; border-radius: 999px;">
                <div class="mc-brand-mark">
                    <span class="mc-circle-red"></span>
                    <span class="mc-circle-yellow"></span>
                </div>
                <span style="font-size: 13px; font-weight: 500; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>
            </div>
        </div>
        <div style="border-top: 1px solid rgba(255,255,255,0.15); padding-top: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; font-size: 13px; color: #888888;">
            <div>© 2026 CHEIL WORLDWIDE AX ESTIMATE GOVERNANCE. ALL RIGHTS RESERVED.</div>
            <div style="display: flex; gap: 20px;">
                <a href="https://ax-estimate-supervisor.onrender.com" target="_blank" style="color: #BBBBBB;">신규 감독관 도메인 ↗</a>
                <a href="https://ax-estimate-director.onrender.com" target="_blank" style="color: #BBBBBB;">기존 감리관 도메인 ↗</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
'''

# Insert footer right before `if __name__ == "__main__":`
main_end = content.rfind('if __name__ == "__main__":')
if main_end != -1:
    content = content[:main_end] + footer_code + "\n" + content[main_end:]
    print("Added Mastercard Warm Dark Footer!")
else:
    print("WARNING: __main__ not found.")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app.py with Mastercard Inspired Design System successfully.")
