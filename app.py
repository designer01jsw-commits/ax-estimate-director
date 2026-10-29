# -*- coding: utf-8 -*-
"""견적감독관 (Estimate Auditor) — 동일 시트명 자동 비교 및 전천후 실전 감리 엔진"""

import traceback
from pathlib import Path
import streamlit as st
import pandas as pd
import openpyxl

from auditor.projects import load_projects
from auditor.errors import ValidationError
from auditor.loader import (
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
)
from auditor.matching import match_items
from auditor.analysis import (
    analyze_estimates,
    analyze_labor,
    build_review_items,
    calculate_summary
)
from auditor.export import export_to_csv_bytes, generate_csv_filename
from auditor.presentation_modules import (
    explain_cost_difference,
    get_traffic_light_status,
    check_labor_over_allocation,
    get_faq_question_templates,
    generate_automated_response
)
from auditor.diagnostics import (
    OFFICIAL_BENCHMARKS,
    get_all_benchmark_details,
    normalize_baseline,
    diagnose_estimate_item,
    diagnose_labor_item,
    generate_audit_judgment_report,
    generate_executive_supervisor_opinion
)
from auditor.vision_ui import render_vision_estimator_ui
from auditor.learning_ui import render_learning_studio_ui
from auditor.schema import (
    MATCH_CONFIRMED,
    MATCH_NEEDS_CONFIRM,
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_UNCONFIRMED
)

# 페이지 설정
st.set_page_config(
    page_title="제일기획 AX 견적감독관 — 동일 시트명 자동 대조 감리",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Mastercard Inspired Design System Styling
st.markdown("""
<style>
    /* ==========================================================================
       Samsung Typography System:
       - English: Samsung Sharp Sans (Bold, Medium, Regular)
       - Korean: Samsung SS Head KR (Bold, Medium, Regular, Light)
       ========================================================================== */

    /* 1. English Font: Samsung Sharp Sans */
    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Regular'), local('Samsung Sharp Sans Regular'), local('Samsung Sharp Sans'),
             url('/app/static/fonts/SamsungSharpSans-Regular.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Regular.ttf') format('truetype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Medium'), local('Samsung Sharp Sans Medium'),
             url('/app/static/fonts/SamsungSharpSans-Medium.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Medium.ttf') format('truetype');
        font-weight: 500;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Bold'), local('Samsung Sharp Sans Bold'),
             url('/app/static/fonts/SamsungSharpSans-Bold.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Bold.ttf') format('truetype');
        font-weight: 700;
        font-weight: 800;
        font-style: normal;
        font-display: swap;
    }

    /* 2. Korean Font: Samsung SS Head KR */
    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Light'), local('Samsung SS Head KR Light'),
             url('/app/static/fonts/SamsungSSHeadKR-Light.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Light.ttf') format('truetype');
        font-weight: 300;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Regular'), local('Samsung SS Head KR Regular'), local('Samsung SS Head KR'),
             url('/app/static/fonts/SamsungSSHeadKR-Regular.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Regular.ttf') format('truetype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Medium'), local('Samsung SS Head KR Medium'),
             url('/app/static/fonts/SamsungSSHeadKR-Medium.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Medium.ttf') format('truetype');
        font-weight: 500;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Bold'), local('Samsung SS Head KR Bold'),
             url('/app/static/fonts/SamsungSSHeadKR-Bold.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Bold.ttf') format('truetype');
        font-weight: 700;
        font-weight: 800;
        font-style: normal;
        font-display: swap;
    }

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

    /* 1. Global Font Stack: English (SamsungSharpSans) -> Korean (SamsungSSHeadKR) */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--canvas-cream) !important;
        color: var(--ink-black) !important;
        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-weight: 400 !important;
        line-height: 1.45 !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* 2. Sidebar: Lifted Cream with Subtle Border */
    [data-testid="stSidebar"] {
        background-color: var(--lifted-cream) !important;
        border-right: 1.5px solid rgba(20, 20, 19, 0.08) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--slate-gray) !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-top: 18px !important;
        margin-bottom: 8px !important;
    }

    /* 3. Typography Headings: 500 weight with tight -2% letter spacing */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;
        color: var(--ink-black) !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
    }
    h2 {
        font-size: 22px !important;
        font-weight: 600 !important;
        margin-top: 32px !important;
        margin-bottom: 14px !important;
    }
    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* 4. Primary Button: Ink Black Pill (20px radius) with Canvas Cream text */
    button[kind="primary"], .stButton > button[kind="primary"], div[data-testid="stButton"] > button[kind="primary"] {
        background-color: var(--ink-black) !important;
        color: var(--canvas-cream) !important;
        border-radius: var(--radius-button) !important;
        padding: 8px 24px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px !important;
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
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px !important;
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
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        color: var(--slate-gray) !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        color: var(--ink-black) !important;
        line-height: 1.15 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 12px !important;
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
        font-size: 14px !important;
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
        font-size: 14px !important;
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
        font-size: 12px !important;
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
        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;
        font-size: 38px !important;
        font-weight: 700 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.02em !important;
        color: var(--ink-black) !important;
        margin: 0 0 10px 0 !important;
    }
    .mc-hero-subhead {
        font-size: 15px !important;
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
        padding: 6px 18px;
        font-size: 13px;
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
        padding: 4px 14px;
        font-size: 12px;
        font-weight: 500;
    }
    .mc-chip-ink, .mc-chip-black {
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
        padding: 6px 16px;
        box-shadow: var(--shadow-card);
        border: 1px solid rgba(20, 20, 19, 0.08);
        font-size: 12px;
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
        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;
        font-size: 22px !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        color: var(--white) !important;
        margin-bottom: 14px !important;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(val: float, currency: str = "KRW") -> str:
    if val is None:
        return "-"
    if currency == "USD":
        return f"${val:,.2f}"
    return f"₩{val:,.0f}"

@st.cache_data(show_spinner=False)
def get_workbook_sheet_names(file_path: str):
    """엑셀 파일의 시트명 목록을 빠르게 추출합니다."""
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        names = list(wb.sheetnames)
        wb.close()
        return names
    except Exception:
        return []

def main():
    st.markdown("""
    <div class="mc-floating-nav">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">⚖️</span>
            <span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>
        </div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <span style="font-size: 12px; font-weight: 500; color: var(--slate-gray);">• 정밀 감리 엔진 v2.0</span>
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
            <span style="color: var(--ink-black); font-weight: 500;">🌐 공식 서비스 도메인:</span>
            <a href="https://ax-estimate-director.onrender.com" target="_blank">https://ax-estimate-director.onrender.com</a>
            <span class="mc-satellite-arrow" style="margin-left: 6px;">↗</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1. 프로젝트 목록 로드
    projects, prj_warnings = load_projects()
    for w in prj_warnings:
        st.warning(w)

    # 모드 선택
    st.sidebar.header("🚀 메인 실행 모드")
    app_mode = st.sidebar.radio(
        "기능 모드 선택",
        [
            "⚖️ 기준 견적서 정밀 감리 & 진단",
            "📷 비전 AI 이미지 예상견적 산출기",
            "🧠 과거 실적 자산화 & AI 학습 스튜디오"
        ],
        index=0,
        key="app_main_mode"
    )

    if app_mode == "📷 비전 AI 이미지 예상견적 산출기":
        render_vision_estimator_ui(currency="KRW")
        return
    elif app_mode == "🧠 과거 실적 자산화 & AI 학습 스튜디오":
        render_learning_studio_ui(currency="KRW")
        return

    # 2. 사이드바 - [1단계] 기준 견적서 데이터셋 (에이전트 DB 또는 직접 업로드)
    root_dir = Path(__file__).resolve().parent

    is_dual_mode = (st.session_state.get("target_supply_mode_radio") == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드")

    st.sidebar.markdown("---")
    st.sidebar.header("📁 [1단계] 기준견적서 데이터셋")

    orig_file_input = None
    orig_file_name = ""
    selected_proj = None
    currency = "KRW"
    proj_id = "PROJ"

    if is_dual_mode:
        st.sidebar.info("💡 **[듀얼 직접 업로드] 모드 활성화됨**\n\n아래 **[2단계]**에서 기준 견적서와 비교 견적서 2개 파일을 모두 직접 업로드합니다.")
    else:
        sb_source_options = ["📚 에이전트 DB에서 선택", "📁 기준 견적서 직접 업로드 (.xlsx)"]
        baseline_source_mode = st.sidebar.radio(
            "기준 견적 공급 출처",
            sb_source_options,
            index=0,
            key="sb_baseline_source_mode"
        )

        if baseline_source_mode == "📚 에이전트 DB에서 선택":
            if not projects:
                st.sidebar.error("등록된 프로젝트가 없습니다.")
                return

            target_idx = 0
            if "selected_proj_id" in st.session_state:
                for idx, p in enumerate(projects):
                    if p.get("project_id") == st.session_state["selected_proj_id"]:
                        target_idx = idx
                        break
            else:
                has_studied = any(p.get("is_studied_asset") for p in projects)
                target_idx = 0 if has_studied else (3 if len(projects) > 3 else 0)

            target_idx = max(0, min(target_idx, len(projects) - 1))

            proj_labels = [f"[{p['project_id']}] {p['name']}" for p in projects]
            selected_idx = st.sidebar.selectbox(
                "기준 견적 데이터셋 선택 (광고주 컨펌 완료)",
                range(len(proj_labels)),
                format_func=lambda x: proj_labels[x],
                index=target_idx,
                key=f"sb_baseline_proj_select_{len(proj_labels)}"
            )
            selected_proj = projects[selected_idx]
            st.session_state["selected_proj_id"] = selected_proj.get("project_id")

            currency = selected_proj.get("currency", "KRW")
            proj_id = selected_proj.get("project_id", "PROJ")

            sample_est_str = selected_proj.get("sample_estimate") or ""
            candidate_orig = []
            if sample_est_str:
                if Path(sample_est_str).is_absolute():
                    candidate_orig.append(Path(sample_est_str))
                candidate_orig.append(root_dir / "data" / sample_est_str)
                candidate_orig.append(root_dir / "data" / "samples" / sample_est_str)
            candidate_orig.extend([
                root_dir / "data" / "기준견적서4_전시_광고주컨펌.xlsx",
                root_dir / "data" / "samples" / "기준견적서4_전시_광고주컨펌.xlsx",
                root_dir / "data" / "samples" / "전시 광고주컨펌완료 견적서 (1).xlsx",
                root_dir / "data" / "samples" / "전시_광고주컨펌완료_기준견적서.xlsx",
                root_dir / "data" / "samples" / "P001_최초견적.xlsx"
            ])
            orig_path = next((p for p in candidate_orig if p and p.exists()), None)
            orig_file_input = str(orig_path) if orig_path and orig_path.exists() else None
            orig_file_name = orig_path.name if orig_path and orig_path.exists() else ""

            with st.sidebar.expander("📌 에이전트 기준 메타데이터", expanded=False):
                st.write(f"**프로젝트 ID:** {proj_id}")
                st.write(f"**기준 파일명:** `{orig_file_name}`")
                st.write(f"**발주처:** {selected_proj.get('client', '-')}")
                st.write(f"**현장/베뉴:** {selected_proj.get('site', '-')}")
                st.write(f"**통화:** {currency}")
                st.write(f"**상태:** {selected_proj.get('status', '광고주 컨펌 완료')} ✅")
                if selected_proj.get("total_budget"):
                    st.write(f"**확정 예산:** ₩{selected_proj['total_budget']:,d}")
                if selected_proj.get("item_count"):
                    st.write(f"**스터디 품목수:** {selected_proj['item_count']}건")

            st.sidebar.caption("💡 새 기준견적서를 에이전트 DB에 영구 등록하려면 상단 모드에서 **[과거 실적 자산화]**를 이용하세요.")
        else:
            u_step1_orig = st.sidebar.file_uploader(
                "기준(확정) 견적서 파일 (.xlsx) *",
                type=["xlsx"],
                key="u_step1_direct_baseline",
                help="비교의 기준(확정/공인)으로 삼을 엑셀 견적서를 업로드하세요."
            )
            if u_step1_orig:
                orig_file_input = u_step1_orig
                orig_file_name = u_step1_orig.name
                clean_title = orig_file_name.replace(".xlsx", "").replace(".xls", "").replace("_", " ")
                proj_id = "P_CUSTOM_BASELINE"
                currency = "KRW"
                selected_proj = {
                    "project_id": proj_id,
                    "name": f"직접 업로드 기준: {clean_title}",
                    "client": "사용자 직접 공급",
                    "site": "현장 미정",
                    "currency": currency,
                    "status": "사용자 확정 기준",
                    "default_sheet": None
                }
                st.sidebar.success(f"기준 견적서 장착: {orig_file_name}")

    # 3. 사이드바 - [2단계] 대조·진단받을 견적서 공급 (사용자 업로드)
    st.sidebar.markdown("---")
    st.sidebar.header("📤 [2단계] 진단받을 견적서 공급")

    if "use_sample_change" not in st.session_state:
        st.session_state["use_sample_change"] = False

    target_mode_options = [
        "📁 신규 비교 견적서 직접 업로드 (1단계 기준과 대조)",
        "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드",
        "⚡ 준비된 실적 샘플로 빠른 체험"
    ]
    default_target_mode_idx = 2 if st.session_state.get("use_sample_change", False) else 0

    target_supply_mode = st.sidebar.radio(
        "견적서 공급 방식",
        target_mode_options,
        index=default_target_mode_idx,
        key="target_supply_mode_radio"
    )

    rev_file_input = None
    rev_file_name = ""

    if target_supply_mode == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드":
        st.session_state["use_sample_change"] = False
        st.sidebar.markdown("##### 1️⃣ 기준(확정) 견적서")
        u_dual_baseline = st.sidebar.file_uploader(
            "기준 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_dual_baseline_file",
            help="비교의 기준(확정/공인)이 될 엑셀 견적서 파일을 업로드하세요."
        )
        if u_dual_baseline:
            orig_file_input = u_dual_baseline
            orig_file_name = u_dual_baseline.name
            clean_b_name = orig_file_name.replace(".xlsx", "").replace(".xls", "").replace("_", " ")
            proj_id = "P_CUSTOM_DUAL_BASE"
            currency = "KRW"
            selected_proj = {
                "project_id": proj_id,
                "name": f"직접 업로드 기준: {clean_b_name}",
                "client": "사용자 직접 공급",
                "site": "사용자 지정 현장",
                "currency": currency,
                "status": "사용자 확정 기준",
                "default_sheet": None
            }
            st.sidebar.success(f"1️⃣ 기준 견적서 공급됨: `{orig_file_name}`")

        st.sidebar.markdown("##### 2️⃣ 비교(진단받을) 견적서")
        u_dual_target = st.sidebar.file_uploader(
            "비교 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_dual_target_file",
            help="기준 견적서와 대조하여 감리·진단받을 신규 견적서 파일입니다."
        )
        if u_dual_target:
            rev_file_input = u_dual_target
            rev_file_name = u_dual_target.name
            st.sidebar.success(f"2️⃣ 비교 견적서 공급됨: `{rev_file_name}`")

    elif target_supply_mode == "📁 신규 비교 견적서 직접 업로드 (1단계 기준과 대조)":
        st.session_state["use_sample_change"] = False
        rev_uploaded = st.sidebar.file_uploader(
            "진단받을 신규 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_target_rev_file",
            help="선택된 광고주 컨펌 기준가이드와 비교 감리할 견적서 엑셀 파일을 업로드하세요."
        )
        if rev_uploaded:
            rev_file_input = rev_uploaded
            rev_file_name = rev_uploaded.name
            st.sidebar.success(f"신규 파일 공급됨: {rev_file_name}")
    else:
        st.session_state["use_sample_change"] = True
        sample_options = [
            ("전시_홍대점_변경내역.xlsx", "홍대점 전시 공사 변경 내역서 (전시 샘플)"),
            ("P001_변경내역.xlsx", "국립과학관 체험전시 변경 내역서 (키트 샘플)"),
            ("P002_변경내역.xlsx", "글로벌 과학 엑스포 변경 내역서 (USD 샘플)")
        ]
        if selected_proj and selected_proj.get("sample_change"):
            sc_name = selected_proj.get("sample_change")
            if not any(s[0] == sc_name for s in sample_options):
                sample_options.insert(0, (sc_name, f"{selected_proj.get('name')} 전용 변경내역서"))

        chosen_sample_idx = st.sidebar.selectbox(
            "체험할 실적 샘플 내역서 선택",
            range(len(sample_options)),
            format_func=lambda i: sample_options[i][1],
            key="chosen_sample_selectbox"
        )
        chosen_sample_fname = sample_options[chosen_sample_idx][0]
        candidate_sample = [
            root_dir / "data" / chosen_sample_fname,
            root_dir / "data" / "samples" / chosen_sample_fname,
            root_dir / "data" / "samples" / "전시_홍대점_변경내역.xlsx",
            root_dir / "data" / "samples" / "P001_변경내역.xlsx"
        ]
        sample_path = next((p for p in candidate_sample if p and p.exists()), None)
        if sample_path and sample_path.exists():
            rev_file_input = str(sample_path)
            rev_file_name = sample_path.name

    # 기준 파일 검증
    if not orig_file_input:
        if target_supply_mode == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드":
            st.markdown('''<div class="mc-stadium-card" style="padding: 32px 36px; margin: 18px 0 28px 0; border: 1.5px solid rgba(207, 69, 0, 0.4); background: var(--surface-lifted); box-shadow: var(--shadow-cushion);">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
<div style="display: flex; align-items: center; gap: 14px;">
<span style="font-size: 32px;">📂</span>
<div>
<div class="mc-eyebrow" style="margin-bottom: 4px;"><span class="mc-eyebrow-dot"></span><span>DUAL ESTIMATE UPLOAD MODE</span></div>
<h3 style="margin: 0; font-size: 20px; font-weight: 700; color: var(--ink-black);">기준 견적서 & 비교 견적서 듀얼 업로드 대기</h3>
<div style="font-size: 13.5px; color: var(--slate-gray); margin-top: 3px;">좌측 사이드바 [2단계]에서 <strong>1️⃣ 기준 견적서</strong>와 <strong>2️⃣ 비교 견적서</strong> 엑셀 파일 2개를 모두 업로드해 주세요.</div>
</div>
</div>
<span class="mc-pill-chip mc-chip-orange" style="font-size: 12px; font-weight: 600;">● 파일 공급 대기 중</span>
</div>
</div>''', unsafe_allow_html=True)
        else:
            st.info("💡 사이드바 [1단계]에서 기준견적서 프로젝트를 선택하거나 기준 견적서 XLSX를 업로드해 주세요.")
        return

    # 대조 파일 미공급 시 메인 화면: 대조 방법 및 3단계 프로세스 디자인화 연출 (중앙화면 업로더 배제)
    if not rev_file_input:
        if target_supply_mode == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드":
            status_chip = '<span class="mc-pill-chip mc-chip-green" style="font-size: 12px; font-weight: 600;">● 1단계 기준 파일 장착 완료</span>'
            eyebrow_text = "STEP 1 BASELINE LOADED"
            main_title = f"1️⃣ 기준 견적서 장착 완료: {orig_file_name}"
            sub_title = "좌측 사이드바 [2단계]의 <strong>2️⃣ 비교 견적서</strong> 파일을 마저 업로드하시면 7대 공종 양식초월 정규화 및 감리가 즉시 실행됩니다."
        else:
            status_chip = '<span class="mc-pill-chip mc-chip-orange" style="font-size: 12px; font-weight: 600;">● 기준가이드 장착됨</span>'
            eyebrow_text = "ACTIVE BASELINE DATASET"
            main_title = "광고주 컨펌 기준가이드 준비 완료"
            sub_title = "대조할 신규 견적서를 공급하시면 7대 공종 양식초월 정규화 및 실시간 단가·인건비 대조가 즉시 시작됩니다."

        st.markdown(f"""<div class="mc-stadium-card" style="padding: 32px 36px; margin: 18px 0 28px 0; border: 1.5px solid rgba(207, 69, 0, 0.3); background: var(--surface-lifted); box-shadow: var(--shadow-cushion);">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
<div style="display: flex; align-items: center; gap: 14px;">
<span style="font-size: 30px;">⚖️</span>
<div>
<div class="mc-eyebrow" style="margin-bottom: 4px;"><span class="mc-eyebrow-dot"></span><span>{eyebrow_text}</span></div>
<h3 style="margin: 0; font-size: 20px; font-weight: 700; color: var(--ink-black);">{main_title}</h3>
<div style="font-size: 13.5px; color: var(--slate-gray); margin-top: 3px;">{sub_title}</div>
</div>
</div>
{status_chip}
</div>
<div style="background: var(--white); border: 1.5px solid var(--border-stone); border-radius: 20px; padding: 18px 24px; box-shadow: var(--shadow-card);">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; font-size: 13.5px;">
<div><span style="color: var(--slate-gray);">기준 프로젝트:</span> <strong style="color: var(--ink-black); margin-left: 6px;">{selected_proj.get('name', '기준견적서')}</strong></div>
<div><span style="color: var(--slate-gray);">기준 파일명:</span> <code style="background: var(--canvas-stone); padding: 3px 8px; border-radius: 6px; color: var(--ink-black); margin-left: 6px;">{orig_file_name}</code></div>
<div><span style="color: var(--slate-gray);">발주처 / 베뉴:</span> <strong style="color: var(--ink-black); margin-left: 6px;">{selected_proj.get('client', '-')} / {selected_proj.get('site', '-')}</strong></div>
<div><span style="color: var(--slate-gray);">통화 / 상태:</span> <strong style="color: var(--ink-black); margin-left: 6px;">{currency}</strong> · <span style="color: #0E7C57; font-weight: 700;">{selected_proj.get('status', '광고주 컨펌 완료')} ✅</span></div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # 3단계 프로세스 안내 카드
        st.markdown("""<div style="margin-bottom: 28px;">
<div class="mc-eyebrow" style="margin-bottom: 6px;"><span class="mc-eyebrow-dot"></span><span>AUDIT EXECUTION WORKFLOW</span></div>
<h2 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 700; color: var(--ink-black);">🚀 견적감독관 3단계 정밀 감리 프로세스</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span class="mc-pill-chip mc-chip-black" style="font-size: 11px; font-weight: 700;">STEP 01</span>
<span class="mc-pill-chip mc-chip-green" style="font-size: 11px;">장착 완료 ✅</span>
</div>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black); margin-bottom: 6px;">기준 가이드 확정</div>
<div style="font-size: 12px; color: var(--signal-orange); font-weight: 600; margin-bottom: 8px;">📍 좌측 사이드바 [1단계]</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.5;">에이전트 DB에 등록된 광고주 승인 프로젝트 또는 실적 자산화 데이터를 대조의 표준 잣대로 선택합니다.</div>
</div>
<div class="mc-card-20" style="background: var(--surface-lifted); border: 2px solid var(--signal-orange); box-shadow: 0 4px 18px rgba(207, 69, 0, 0.08);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span class="mc-pill-chip mc-chip-orange" style="font-size: 11px; font-weight: 700;">STEP 02</span>
<span class="mc-pill-chip mc-chip-orange" style="font-size: 11px;">좌측 바 업로드 대기 👈</span>
</div>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black); margin-bottom: 6px;">신규 견적서 공급</div>
<div style="font-size: 12px; color: var(--signal-orange); font-weight: 600; margin-bottom: 8px;">📍 좌측 사이드바 [2단계]</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.5;">진단받을 신규 견적서(.xlsx)를 좌측 바에서 업로드하거나, 준비된 실적 샘플로 즉시 체험할 수 있습니다.</div>
</div>
<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span class="mc-pill-chip mc-chip-black" style="font-size: 11px; font-weight: 700;">STEP 03</span>
<span class="mc-pill-chip mc-chip-gray" style="font-size: 11px;">자동 가동 대기 ⚡</span>
</div>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black); margin-bottom: 6px;">AI 양식초월 정밀 감리</div>
<div style="font-size: 12px; color: var(--signal-orange); font-weight: 600; margin-bottom: 8px;">📍 중앙 메인 화면</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.5;">7대 공종 자동 분해, 6대 공공 기준 단가 대조, 신호등 적정성 진단 및 과다 청구액 소견 리포트가 즉시 도출됩니다.</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # 핵심 감리 방법론 및 대조 원리 카드
        st.markdown("""<div style="margin-bottom: 28px;">
<div class="mc-eyebrow" style="margin-bottom: 6px;"><span class="mc-eyebrow-dot"></span><span>CORE AUDIT METHODOLOGY</span></div>
<h2 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 700; color: var(--ink-black);">🔬 견적 대조 원리 및 핵심 감리 방법론</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone);">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
<span style="font-size: 22px;">🧩</span>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black);">1. 7대 공종 양식초월 정규화</div>
</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.55; margin-bottom: 12px;">
프로젝트마다 상이한 시트 구조와 계정 과목을 <strong>[목공사, 금속·유리, 전기·조명, 도장·필름, 사인·그래픽, 집기·설치, 현장경비·이윤]</strong>의 7대 표준 체계로 지능형 재분류하여 1:1 비교를 실현합니다.
</div>
<div style="background: var(--canvas-stone); padding: 8px 12px; border-radius: 12px; font-size: 12px; color: var(--ink-black); font-weight: 500;">
💡 양식이 달라도 공종별 비중(%)과 투입 단가를 정밀 대조
</div>
</div>
<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone);">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
<span style="font-size: 22px;">🏛️</span>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black);">2. 6대 공공 기준 벤치마킹</div>
</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.55; margin-bottom: 12px;">
산업통상자원부 산업디자인(<strong>KIDP</strong>), 한국SW산업협회(<strong>KOSA</strong>), 엔지니어링(<strong>KENCA</strong>), 중기중앙회 시중노임(<strong>KBIZ</strong>), 조달청(<strong>G2B</strong>) 가격정보 및 에이전트 실적 빅데이터와 실시간 교차 검증합니다.
</div>
<div style="background: var(--canvas-stone); padding: 8px 12px; border-radius: 12px; font-size: 12px; color: var(--ink-black); font-weight: 500;">
💡 정부 공인 노임 및 물가정보 기반 법적 소명력 확보
</div>
</div>
<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone);">
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
<span style="font-size: 22px;">🚦</span>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black);">3. 3단계 신호등 판정 & 삭감 산출</div>
</div>
<div style="font-size: 13.5px; color: var(--slate-gray); line-height: 1.55; margin-bottom: 12px;">
기준 단가 대비 변동폭과 공공 기준 부합성을 검증하여 <strong>🟢 적정 (인정)</strong>, <strong>🟡 주의 (소명 요청)</strong>, <strong>🔴 비적합 (과다 청구)</strong>으로 명확히 구분하고 삭감 권고액을 계산합니다.
</div>
<div style="background: var(--canvas-stone); padding: 8px 12px; border-radius: 12px; font-size: 12px; color: var(--ink-black); font-weight: 500;">
💡 단가 25% 이상 초과 항목 즉시 감액 청구액 자동 산출
</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        # 빠른 샘플 체험 가이드 카드
        st.markdown("""<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone); padding: 24px 28px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
<div>
<div class="mc-eyebrow" style="margin-bottom: 4px;"><span class="mc-eyebrow-dot"></span><span>QUICK START EXPERIENCE</span></div>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black);">📋 테스트용 신규 견적서 파일이 없으신가요?</div>
<div style="font-size: 13.5px; color: var(--slate-gray); margin-top: 4px;">사전에 준비된 실제 홍대점 전시 변경 내역서 샘플을 즉시 불러와 9대 정밀 진단실과 신호등 감리를 1초 만에 체험해 보세요.</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

        if st.button("⚡ 홍대점 전시 샘플 견적서로 지금 즉시 감리 체험하기", type="primary", use_container_width=True, key="btn_quick_sample_experience"):
            st.session_state["use_sample_change"] = True
            st.rerun()

        if not rev_file_input:
            return

    # 워크북 안전 로드
    try:
        wb_orig = load_workbook_safe(orig_file_input, orig_file_name)
        wb_rev = load_workbook_safe(rev_file_input, rev_file_name)
    except Exception as e:
        st.error(f"❌ 엑셀 파일 로드 실패: {str(e)}")
        return

    # 4. 동일 시트명 자동 감지 및 시트 매칭 UI (핵심 해결책)
    st.sidebar.markdown("---")
    st.sidebar.header("📑 비교 시트 매칭 (동일 시트명 자동 대조)")

    orig_sheets = list(wb_orig.sheetnames)
    rev_sheets = list(wb_rev.sheetnames)
    common_sheets = [s for s in orig_sheets if s in rev_sheets]

    sheet_orig_selected = None
    sheet_rev_selected = None

    if common_sheets:
        st.sidebar.success(f"양쪽 파일에서 공통 시트 {len(common_sheets)}개 자동 감지됨")
        
        # 기본 시트 우선 추천 (예: 수원 사업장, 원형 개발, 홍대점, 또는 공통시트 1번)
        default_idx = 0
        preferred_default = selected_proj.get("default_sheet")
        if preferred_default and preferred_default in common_sheets:
            default_idx = common_sheets.index(preferred_default)
        else:
            for idx, s in enumerate(common_sheets):
                if any(k in s for k in ["수원", "홍대", "원형", "견적", "1."]):
                    default_idx = idx
                    break

        match_mode = st.sidebar.radio(
            "시트 매칭 방식",
            ["동일 시트명 1:1 자동 대조", "서로 다른 시트 수동 매칭"],
            index=0,
            key=f"radio_match_mode_{rev_file_name}"
        )

        safe_default_idx = max(0, min(default_idx, len(common_sheets) - 1))
        if match_mode == "동일 시트명 1:1 자동 대조":
            selected_common = st.sidebar.selectbox(
                "대조할 동일 시트 선택",
                common_sheets,
                index=safe_default_idx,
                key=f"sb_common_sheet_{rev_file_name}"
            )
            sheet_orig_selected = selected_common
            sheet_rev_selected = selected_common
            st.sidebar.caption(f"기준: `{sheet_orig_selected}` ⟷ 변경: `{sheet_rev_selected}`")
        else:
            sheet_orig_selected = st.sidebar.selectbox("최초 견적서 시트 선택", orig_sheets, index=0, key=f"sb_orig_m_{proj_id}")
            sheet_rev_selected = st.sidebar.selectbox("변경 내역서 시트 선택", rev_sheets, index=0, key=f"sb_rev_m_{rev_file_name}")
    else:
        best_orig_sheet, best_orig_idx = find_best_estimate_sheet(wb_orig, selected_proj.get("default_sheet"))
        best_rev_sheet, best_rev_idx = find_best_estimate_sheet(wb_rev)
        
        safe_orig_idx = max(0, min(best_orig_idx, len(orig_sheets) - 1))
        safe_rev_idx = max(0, min(best_rev_idx, len(rev_sheets) - 1))
        
        st.sidebar.info(f"💡 양쪽 파일의 시트명이 다릅니다.\n추천 견적 시트: 기준 [{best_orig_sheet}] ⟷ 대조 [{best_rev_sheet}]")
        sheet_orig_selected = st.sidebar.selectbox("기준 견적서 시트 선택", orig_sheets, index=safe_orig_idx, key=f"sb_orig_diff_{proj_id}")
        sheet_rev_selected = st.sidebar.selectbox("대조 견적서 시트 선택", rev_sheets, index=safe_rev_idx, key=f"sb_rev_diff_{rev_file_name}")

    # 세션 상태 사용자 매칭 결정 맵
    decision_key = f"decisions_{proj_id}_{sheet_orig_selected}_{sheet_rev_selected}"
    if decision_key not in st.session_state:
        st.session_state[decision_key] = {}

    # 1. 기준 견적 시트 로드 & 검증
    try:
        ws_orig_est = wb_orig[sheet_orig_selected]
        orig_items, mismatches_orig, orig_dup, orig_warn = read_estimate_sheet(ws_orig_est, orig_file_name, sheet_orig_selected)
    except Exception as e:
        st.error(f"❌ 기준 견적서 시트(‘{sheet_orig_selected}’) 로드 실패: {str(e)}")
        st.info("💡 좌측 사이드바 [1단계]에서 다른 기준 프로젝트를 선택해 주세요.")
        return

    # 2. 신규 견적 시트 로드 & 자동 폴백 검증
    try:
        ws_rev_est = wb_rev[sheet_rev_selected]
        rev_items, mismatches_rev, rev_dup, rev_warn = read_estimate_sheet(ws_rev_est, rev_file_name, sheet_rev_selected)
    except Exception as e:
        found_working_sheet = False
        for alt_s in rev_sheets:
            if alt_s != sheet_rev_selected:
                try:
                    alt_items, alt_mismatches, alt_dup, alt_warn = read_estimate_sheet(wb_rev[alt_s], rev_file_name, alt_s)
                    if alt_items:
                        rev_items = alt_items
                        mismatches_rev = alt_mismatches
                        rev_dup = alt_dup
                        rev_warn = alt_warn + [f"선택된 ‘{sheet_rev_selected}’ 시트에 견적 항목이 없어, 데이터가 확인된 ‘{alt_s}’ 시트로 자동 전환했습니다."]
                        sheet_rev_selected = alt_s
                        found_working_sheet = True
                        st.sidebar.info(f"💡 견적 데이터가 감지된 ‘{alt_s}’ 시트로 자동 전환되었습니다.")
                        break
                except Exception:
                    continue
        if not found_working_sheet:
            st.error(f"❌ 업로드하신 신규 견적서 파일({rev_file_name})의 ‘{sheet_rev_selected}’ 시트에서 유효한 견적 데이터를 읽지 못했습니다.")
            st.warning(f"상세 사유: {str(e)}")
            st.info(f"💡 업로드 파일 내 전체 시트 목록: **{', '.join(rev_sheets)}**\n\n좌측 사이드바의 **[대조 견적서 시트 선택]**에서 실제 견적 내역(품목명, 단가/금액)이 포함된 시트를 직접 선택해 주세요.")
            return

    # 실제 파싱된 시트명으로 동기화
    if rev_items and rev_items[0].get("원본시트"):
        sheet_rev_selected = rev_items[0]["원본시트"]
    if orig_items and orig_items[0].get("원본시트"):
        sheet_orig_selected = orig_items[0]["원본시트"]

    try:

        # 인력 시트 스마트 탐색
        orig_labor, orig_lab_warn = [], []
        rev_labor, rev_lab_warn = [], []
        
        labor_sheet_candidates_orig = [s for s in orig_sheets if any(k in s for k in ["인력", "투입률", "공통"])]
        labor_sheet_candidates_rev = [s for s in rev_sheets if any(k in s for k in ["인력", "투입률", "공통"])]

        if labor_sheet_candidates_orig and labor_sheet_candidates_rev:
            l_orig_sname = labor_sheet_candidates_orig[0]
            l_rev_sname = labor_sheet_candidates_rev[0]
            try:
                orig_labor, _, orig_lab_warn = read_labor_sheet(wb_orig[l_orig_sname], orig_file_name, l_orig_sname)
                rev_labor, _, rev_lab_warn = read_labor_sheet(wb_rev[l_rev_sname], rev_file_name, l_rev_sname)
            except Exception:
                orig_labor, rev_labor = [], []

        # 변경 승인 시트 스마트 탐색
        approval_records, appr_warn = [], []
        appr_sheet_candidates = [s for s in rev_sheets if any(k in s for k in ["승인", "CR", "변경승인"])]
        if appr_sheet_candidates:
            appr_sname = appr_sheet_candidates[0]
            try:
                approval_records, appr_warn = read_approval_sheet(wb_rev[appr_sname], rev_file_name, appr_sname)
            except Exception:
                approval_records = []
        elif "변경승인" in wb_rev.sheetnames:
            try:
                approval_records, appr_warn = read_approval_sheet(wb_rev["변경승인"], rev_file_name, "변경승인")
            except Exception:
                approval_records = []

        # 매칭 및 분석 실행
        user_decisions = st.session_state[decision_key]
        matches = match_items(orig_items, rev_items, orig_dup, rev_dup, user_decisions)
        
        labor_matches = match_items(orig_labor, rev_labor) if (orig_labor or rev_labor) else []
        analyzed_estimates, orphan_approvals = analyze_estimates(matches, orig_items, rev_items, approval_records)
        analyzed_labor, used_lab_apprs = analyze_labor(labor_matches, approval_records)
        orphan_approvals = [a for a in orphan_approvals if a["row_key"] not in used_lab_apprs]

        all_warnings = orig_warn + rev_warn + orig_lab_warn + rev_lab_warn + appr_warn
        formula_mismatches = mismatches_orig + mismatches_rev
        review_items = build_review_items(
            analyzed_estimates, analyzed_labor, orphan_approvals, formula_mismatches, all_warnings
        )
        summary = calculate_summary(
            orig_items, rev_items, analyzed_estimates, analyzed_labor, review_items
        )

        # 신호등 태그 및 설명 주입
        for it in analyzed_estimates:
            tl_status, tl_desc = get_traffic_light_status(it)
            it["신호등"] = tl_status
            it["판정근거"] = tl_desc
            it["비싼이유_설명"] = explain_cost_difference(it, currency)

        # 현재 대조 중인 시트 안내
        st.markdown(f"""<div style="display: flex; align-items: center; justify-content: space-between; background: var(--surface-lifted); border: 1.5px solid var(--border-stone); border-radius: 20px; padding: 14px 24px; margin-bottom: 24px; box-shadow: var(--shadow-card); flex-wrap: wrap; gap: 12px;">
<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
<span style="font-size: 18px;">⚖️</span>
<span style="font-size: 14px; font-weight: 700; color: var(--ink-black);">대조 감리 매칭</span>
<span class="mc-pill-chip mc-chip-black" style="font-size: 12px;">기준 가이드: {orig_file_name} ❯ <strong>{sheet_orig_selected}</strong></span>
<span style="color: var(--signal-orange); font-weight: 700; font-size: 14px;">⟷</span>
<span class="mc-pill-chip mc-chip-orange" style="font-size: 12px;">대조 대상: {rev_file_name} ❯ <strong>{sheet_rev_selected}</strong></span>
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span class="mc-pill-chip mc-chip-green" style="font-size: 12px;">● 7대 공종 양식초월 정규화 감리 가동 중</span>
</div>
</div>""", unsafe_allow_html=True)

        # 메트릭 카드
        st.subheader("📊 핵심 감리 지표 요약")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("최초(기준) 시트 합계", format_currency(summary["orig_total"], currency))
        diff_label = f"{summary['diff_rate']:+.1f}%" if summary["orig_total"] > 0 else "-"
        c2.metric("변경 시트 합계", format_currency(summary["rev_total"], currency), f"{format_currency(summary['diff_total'], currency)} ({diff_label})")
        c3.metric("승인 확인된 증감액", format_currency(summary["approved_diff_sum"], currency))
        c4.metric("🚨 미승인·반려 증감액", format_currency(summary["unapproved_diff_sum"], currency), delta_color="inverse")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("🚨 고위험 소명 필요", f"{summary['high_count']}건")
        c6.metric("⚠️ 중·저위험 검토", f"{summary['med_count'] + summary['low_count']}건")
        c7.metric("🔗 항목 연결 확인 필요", f"{summary['needs_confirm_count']}건")
        c8.metric("👷 인력 M/D 변동", f"{summary['diff_md_sum']:+.1f} M/D", format_currency(summary["diff_labor_cost"], currency))

        st.markdown("---")

        # 정밀 감리 진단 (자체 기준 정규화 및 적합/비적합 공공기준 소명)
        baseline_norms = normalize_baseline(orig_items, orig_labor)
        diagnosed_estimates = [diagnose_estimate_item(it, baseline_norms) for it in analyzed_estimates]
        diagnosed_labor = [diagnose_labor_item(it, baseline_norms) for it in analyzed_labor]
        all_diagnosed = diagnosed_estimates + diagnosed_labor

        unfit_count = len([d for d in all_diagnosed if d["판정"] == "비적합"])
        cond_count = len([d for d in all_diagnosed if d["판정"] == "조건부 적합"])
        fit_count = len([d for d in all_diagnosed if d["판정"] == "적합"])

        # 견적감독관 총체적 종합 진단 소견 생성
        supervisor_opinion = generate_executive_supervisor_opinion(
            diagnosed_estimates=diagnosed_estimates,
            diagnosed_labor=diagnosed_labor,
            summary=summary,
            project_name=selected_proj.get("name", "프로젝트"),
            baseline_norms=baseline_norms
        )

        
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

            f"⚖️ 견적감독관 종합진단실 (적합 {fit_count} / 비적합 {unfit_count})",
            "📷 비전 AI 이미지 예상견적",
            "🧠 과거 실적 학습 스튜디오",
            f"🚦 신호등 감리 리포트 ({len(review_items)})",
            "🧩 제작비 요인 분해 (비싼 이유)",
            "👷 설치/철거 투입률 100% 검토",
            "💬 광고주 질의 대응 (소명서 생성)",
            f"🔗 연결 확인 ({summary['needs_confirm_count']})",
            "📄 원본 대조 & CSV 내보내기"
        ])

        # [신규 핵심] 양식초월 견적 분해 & 다차원 적정성 진단실
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

            st.markdown(f"""
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
            """, unsafe_allow_html=True)

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
        with tab_diagnostics:
            st.subheader("⚖️ 견적감독관 종합진단실 — 총체적 종합의견")

            # [견적감독관 총체적 종합 진단 소견 란 (Mastercard Stadium Card)]
            st.markdown(f"""
            <div class="mc-stadium-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div class="mc-eyebrow" style="margin-bottom: 6px;">
                            <span class="mc-eyebrow-dot"></span>
                            <span>EXECUTIVE DIAGNOSTIC VERDICT</span>
                        </div>
                        <div style="font-size: 22px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink-black);">
                            🏛️ 견적감독관 총체적 종합 진단 소견
                        </div>
                    </div>
                    <div class="mc-satellite-badge">
                        <span>{supervisor_opinion["risk_badge"]}</span>
                        <span class="mc-satellite-arrow">→</span>
                    </div>
                </div>
                <div style="font-size: 15px; font-weight: 400; color: var(--ink-black); line-height: 1.5; background: var(--white); border: 1.5px solid rgba(20, 20, 19, 0.08); border-radius: 20px; padding: 20px 24px; box-shadow: var(--shadow-card);">
                    <strong style="color: var(--signal-orange);">👉 감독관 핵심 권고:</strong> {supervisor_opinion["recommendation"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 4대 핵심 감리 지표 카드
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🚨 종합 리스크 판정", supervisor_opinion["risk_grade"])
            m2.metric("💰 부적정 삭감 타겟액", format_currency(supervisor_opinion["total_cut_demand"], currency), delta="즉시 감액 청구", delta_color="inverse")
            m3.metric("🎯 최종 권고 합의선", format_currency(supervisor_opinion["target_budget"], currency), delta="승인 마지노선")
            m4.metric("🛡️ 공공기준 적합률", f"{supervisor_opinion['fit_rate']:.1f}%", f"적합 {supervisor_opinion['fit_count']}건 / 비적합 {supervisor_opinion['unfit_count']}건")

            st.markdown("##### 🏛️ 4대 공종별 정밀 총체적 감리 소견")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p1 = supervisor_opinion["pillars"][0]
                p2 = supervisor_opinion["pillars"][1]
                chip1 = "mc-chip-orange" if "비적합" in p1['status'] else ("mc-chip-orange" if any(k in p1['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                chip2 = "mc-chip-orange" if "비적합" in p2['status'] else ("mc-chip-orange" if any(k in p2['status'] for k in ["검토", "주의", "조건부"]) else "mc-chip-green")
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p1['title']}</div>
                        <span class="mc-pill-chip {chip1}">{p1['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p1['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p2['title']}</div>
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
                        <div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p3['title']}</div>
                        <span class="mc-pill-chip {chip3}">{p3['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p3['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="mc-card-20" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p4['title']}</div>
                        <span class="mc-pill-chip {chip4}">{p4['status']}</span>
                    </div>
                    <div style="font-size: 14px; color: var(--slate-gray); line-height: 1.5;">{p4['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")
            act_cols = st.columns(3)
            for idx, act in enumerate(supervisor_opinion["action_items"]):
                with act_cols[idx]:
                    st.markdown(f"""
                    <div class="mc-card-20" style="min-height: 155px; background: var(--white);">
                        <div class="mc-eyebrow" style="margin-bottom: 4px;">
                            <span class="mc-eyebrow-dot"></span>
                            <span>{act['order']}</span>
                        </div>
                        <div style="font-size: 15px; font-weight: 600; color: var(--ink-black); margin-bottom: 6px; letter-spacing: -0.01em;">{act['title']}</div>
                        <div style="font-size: 15px; font-weight: 700; color: var(--signal-orange); margin-bottom: 6px;">{act['amount']}</div>
                        <div style="font-size: 13px; color: var(--slate-gray); line-height: 1.45;">{act['detail']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander("📋 결재용 견적감독관 종합소견서 전문 (원클릭 복사 & 다운로드)", expanded=False):
                st.text_area("결재용 소견서 텍스트 전문", value=supervisor_opinion["verdict_text"], height=220)
                st.download_button(
                    "📥 견적감독관 종합소견서(.md) 다운로드",
                    data=supervisor_opinion["verdict_md"].encode("utf-8"),
                    file_name=f"견적감독관_종합소견서_{selected_proj.get('id', 'PROJ')}.md",
                    mime="text/markdown"
                )

            st.markdown("---")
            st.markdown("##### 🔍 세부 항목별 정밀 감리 진단표")

            # 6대 공공 기준 상세 요강 해설 표
            with st.expander("📚 적용 공공·정부 기준 상세 요강 및 법정 품셈 해설 (KIDP, KOSA, KENCA, KBIZ, 근로기준법, 나라장터)", expanded=False):
                st.markdown("본 감독관 에이전트는 국가 법령 및 공공기관 공시 기준에 기반하여 견적의 타당성을 진단합니다.")
                benchmarks_df = pd.DataFrame(get_all_benchmark_details())
                st.dataframe(benchmarks_df, use_container_width=True)

            unfit_list = [d for d in all_diagnosed if d["판정"] == "비적합"]
            cond_list = [d for d in all_diagnosed if d["판정"] == "조건부 적합"]
            fit_list = [d for d in all_diagnosed if d["판정"] == "적합"]
            total_cut_demand = sum(abs(d.get("변동금액", 0.0)) for d in unfit_list)

            dm1, dm2, dm3, dm4 = st.columns(4)
            dm1.metric("🟢 적합 (Pass)", f"{len(fit_list)}건")
            dm2.metric("🟡 조건부 적합 (Review)", f"{len(cond_list)}건")
            dm3.metric("🔴 비적합 (Fail/Cut)", f"{len(unfit_list)}건", delta_color="inverse")
            dm4.metric("🚨 시정/삭감 요구 규모", format_currency(total_cut_demand, currency), delta_color="inverse")

            st.markdown("---")
            diag_filter = st.radio("판정 필터", ["전체", "🔴 비적합만 보기", "🟡 조건부 적합만 보기", "🟢 적합만 보기"], horizontal=True)
            
            target_diag = all_diagnosed
            if diag_filter == "🔴 비적합만 보기":
                target_diag = unfit_list
            elif diag_filter == "🟡 조건부 적합만 보기":
                target_diag = cond_list
            elif diag_filter == "🟢 적합만 보기":
                target_diag = fit_list

            if target_diag:
                diag_table_data = []
                for d in target_diag:
                    cites_text = ", ".join([f"{c['기관']} ({c.get('법령', '')})" for c in d.get("공공기준_근거", [])])
                    diag_table_data.append({
                        "판정": d["판정"],
                        "분해축": d["분해축"],
                        "항목명": d["항목명"],
                        "변동금액": format_currency(d["변동금액"], currency),
                        "진단 사유": d["상세사유"],
                        "공공/정부 기준 근거": cites_text or "공인 기준 부합",
                        "감독관 시정조치 요구": d["조치사항"]
                    })
                st.dataframe(pd.DataFrame(diag_table_data), use_container_width=True)

                problem_items = [d for d in target_diag if d["판정"] in ["비적합", "조건부 적합"]]
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
                                <div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{it['항목명']}</div>
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
                        """, unsafe_allow_html=True)
            else:
                st.success("해당 조건의 항목이 없습니다.")

            st.markdown("---")
            st.subheader("📑 공식 감리 진단서 및 시정 요구서 발행")
            if st.button("🏛️ 공문형 정식 감리 진단서 생성하기", type="primary", key="btn_gen_audit_report"):
                audit_report_doc = generate_audit_judgment_report(
                    diagnosed_estimates, diagnosed_labor, summary, selected_proj.get("name", "프로젝트")
                )
                st.markdown(audit_report_doc)
                st.download_button(
                    "📥 공식 감리 진단서 마크다운 다운로드",
                    data=audit_report_doc.encode("utf-8"),
                    file_name=f"견적감리진단서_{proj_id}_{sheet_orig_selected}.md",
                    mime="text/markdown"
                )

        # 0.5 비전 AI 이미지 예상 견적 산출기
        with tab_vision:
            render_vision_estimator_ui(currency)

        # 0.6 과거 실적 자산화 & AI 학습 스튜디오
        with tab_learning:
            render_learning_studio_ui(currency)

        # 1. 신호등 감리 리포트
        with tab_traffic:
            st.subheader("신호등 판정 및 감리 결과표")
            tl_filter = st.radio("신호등 필터", ["전체", "🔴 반려 반영", "🔴 승인 미확인", "🟡 확인 필요", "🟢 적정"], horizontal=True)
            filtered_tl = [it for it in analyzed_estimates if tl_filter == "전체" or tl_filter in it.get("신호등", "")]

            if filtered_tl:
                df_tl = pd.DataFrame(filtered_tl)[[
                    "신호등", "판정근거", "항목명", "수량_최초", "단가_최초", "수량_변경", "단가_변경",
                    "차이금액", "승인상태", "승인근거", "원본_최초", "원본_변경"
                ]]
                st.dataframe(df_tl, use_container_width=True)
            else:
                st.success("해당 신호등 조건의 항목이 없습니다.")

            st.markdown("##### 🚨 주요 검토 사유 목록")
            if review_items:
                st.dataframe(pd.DataFrame(review_items), use_container_width=True)

        # 2. 제작비 요인 분해
        with tab_decompose:
            st.subheader("모듈 ①: 제작비 차이 요인별(수량/단가) 분해")
            changed_items = [it for it in analyzed_estimates if it["변경유형"] != "변동없음"]
            if changed_items:
                for it in changed_items:
                    with st.container():
                        st.markdown(f"**📌 {it['항목명']}** (`{it['변경유형']}` | 총 차이: `{format_currency(it['차이금액'], currency)}`)")
                        st.info(f"💡 **AI 자동 소명 분석:** {it['비싼이유_설명']}")
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("수량 효과", format_currency(it["수량효과"], currency))
                        col_b.metric("단가 효과", format_currency(it["단가효과"], currency))
                        col_c.metric("합계 검산", f"{format_currency(it['수량효과'] + it['단가효과'], currency)} (일치)")
                        st.divider()
            else:
                st.success("대조된 두 시트 간에 변동된 항목이 없거나 동일합니다.")

        # 3. 설치/철거 투입률 검토
        with tab_labor:
            st.subheader("모듈 ②: 설치/철거 투입률 100% 초과 자동 탐지")
            labor_alerts = check_labor_over_allocation(analyzed_labor)
            if labor_alerts:
                st.warning(f"⚠️ 투입률 100% 초과 공정 {len(labor_alerts)}건 탐지됨")
                st.dataframe(pd.DataFrame(labor_alerts), use_container_width=True)
            else:
                st.success("🎉 투입률 100% 초과 공정이 없으며 전원 적정 일수 내 배정되었습니다.")

            if analyzed_labor:
                st.markdown("##### 전체 인력 M/D 및 인건비 대조표")
                st.dataframe(pd.DataFrame(analyzed_labor), use_container_width=True)

        # 4. 광고주 질의 대응 (91건 FAQ 소명서 자동완성)
        with tab_inquiry:
            st.subheader("모듈 ③ & ④: 클라이언트 질의 대응 (소명 답변서 자동 생성)")
            faq_templates = get_faq_question_templates()
            faq_choice = st.selectbox("자주 묻는 질의 유형(FAQ) 선택", list(faq_templates.keys()))
            selected_faq_data = faq_templates[faq_choice]
            
            st.text_area("광고주 질의서 원문", value=selected_faq_data["query"], height=70)
            
            item_names = [it["항목명"] for it in analyzed_estimates]
            target_item_selected = st.selectbox("질의 대상 항목 선택", item_names if item_names else ["전체"])
            target_obj = next((it for it in analyzed_estimates if it["항목명"] == target_item_selected), None)

            if st.button("🚀 정식 소명 답변서 생성하기", type="primary"):
                response_doc = generate_automated_response(faq_choice, target_obj, currency)
                st.markdown("---")
                st.markdown(response_doc)
                st.download_button(
                    "📥 소명 답변서 마크다운 저장",
                    data=response_doc.encode("utf-8"),
                    file_name=f"소명서_{target_item_selected}.md",
                    mime="text/markdown"
                )

        # 5. 연결 확인
        with tab_confirm:
            st.subheader("항목 연결 수동 확인 및 확정")
            needs_confirm_items = [it for it in analyzed_estimates if it["연결상태"] == MATCH_NEEDS_CONFIRM]
            if needs_confirm_items:
                for idx, it in enumerate(needs_confirm_items):
                    pair_key = (it["orig_row_key"], it["rev_row_key"])
                    curr_val = st.session_state[decision_key].get(pair_key, "확인 대기")
                    with st.container():
                        st.markdown(f"**후보 #{idx+1}: {it['항목명']}** (유사도: `{it['유사도']:.2f}`)")
                        col_o, col_r, col_act = st.columns([2.5, 2.5, 2])
                        col_o.caption(f"기준 견적: {it['원본_최초']}")
                        col_r.caption(f"변경 견적: {it['원본_변경']}")
                        choice = col_act.radio(
                            f"판정 #{idx+1}",
                            ["확인 대기", "같은 항목", "다른 항목"],
                            index=["확인 대기", "같은 항목", "다른 항목"].index(curr_val),
                            key=f"r_{proj_id}_{idx}"
                        )
                        if choice != curr_val:
                            st.session_state[decision_key][pair_key] = choice
                            st.rerun()
                        st.divider()
            else:
                st.success("모든 항목이 확정 연결되었습니다.")

        # 6. 원본 데이터 및 CSV
        with tab_raw:
            st.subheader("원본 데이터 대조 및 증빙 CSV 내보내기")
            csv_review = export_to_csv_bytes(review_items)
            csv_est = export_to_csv_bytes(analyzed_estimates)
            
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("📥 검토 필요 목록 CSV 다운로드", data=csv_review, file_name=generate_csv_filename(proj_id, f"{sheet_orig_selected}_검토목록"), mime="text/csv")
            c_d2.download_button("📥 전체 비교표 CSV 다운로드", data=csv_est, file_name=generate_csv_filename(proj_id, f"{sheet_orig_selected}_전체비교"), mime="text/csv")

            st.markdown(f"##### 기준 견적 데이터 (`{sheet_orig_selected}` 시트 - {len(orig_items)}건)")
            st.dataframe(pd.DataFrame(orig_items), use_container_width=True)

    except ValidationError as ve:
        st.error(f"❌ {ve.message}")
    except Exception as e:
        st.error("🚨 분석 중 예상하지 못한 문제가 생겼습니다.")
        with st.expander("오류 상세 내용"):
            st.code(traceback.format_exc())


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
            <div style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.08); padding: 8px 20px; border-radius: 999px;">
                <span style="font-size: 16px;">🏛️</span>
                <span style="font-size: 12px; font-weight: 600; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>
            </div>
        </div>
        <div style="border-top: 1px solid rgba(255,255,255,0.15); padding-top: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; font-size: 13px; color: #888888;">
            <div>© 2026 CHEIL WORLDWIDE AX ESTIMATE GOVERNANCE. ALL RIGHTS RESERVED.</div>
            <div>
                <a href="https://ax-estimate-director.onrender.com" target="_blank" style="color: #BBBBBB;">공식 도메인 (24/7 무중단 가동) ↗</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
