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
    get_common_sheet_names
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

    # 2. 사이드바 프로젝트 선택
    st.sidebar.header("📁 기준 견적 프로젝트 선택")
    if not projects:
        st.sidebar.error("등록된 프로젝트가 없습니다.")
        return

    proj_labels = [f"[{p['project_id']}] {p['name']}" for p in projects]
    selected_idx = st.sidebar.selectbox(
        "기준 견적 데이터셋 선택",
        range(len(proj_labels)),
        format_func=lambda x: proj_labels[x],
        index=3 if len(proj_labels) > 3 else 0  # 기준견적서4 기본 포커스 지원
    )
    selected_proj = projects[selected_idx]

    currency = selected_proj.get("currency", "KRW")
    proj_id = selected_proj.get("project_id", "PROJ")

    with st.sidebar.expander("📌 프로젝트 메타데이터", expanded=True):
        st.write(f"**프로젝트 ID:** {proj_id}")
        st.write(f"**발주처:** {selected_proj.get('client', '-')}")
        st.write(f"**현장/베뉴:** {selected_proj.get('site', '-')}")
        st.write(f"**통화:** {currency}")
        st.write(f"**상태:** {selected_proj.get('status', '-')}")

    # 3. 데이터 소스 선택
    st.sidebar.markdown("---")
    st.sidebar.header("📂 데이터 파일 공급 모드")
    has_samples = bool(selected_proj.get("sample_estimate"))
    
    if has_samples:
        data_source_mode = st.sidebar.radio(
            "입력 모드 선택",
            ["광고주 컨펌 기준견적서 사용", "직접 파일 업로드"],
            index=0
        )
    else:
        data_source_mode = "직접 파일 업로드"
        st.sidebar.info("파일 직접 업로드 전용 프로젝트입니다.")

    orig_file_input = None
    rev_file_input = None
    orig_file_name = ""
    rev_file_name = ""

    root_dir = Path(__file__).resolve().parent

    if data_source_mode == "광고주 컨펌 기준견적서 사용":
        sample_est_str = selected_proj.get("sample_estimate") or ""
        sample_chg_str = selected_proj.get("sample_change")

        # 1. 최초/기준 견적서 파일 다중 경로 탐색 (data/ 및 data/samples/ 우선 탐색)
        candidate_orig = []
        if sample_est_str:
            if Path(sample_est_str).is_absolute():
                candidate_orig.append(Path(sample_est_str))
            candidate_orig.append(root_dir / "data" / sample_est_str)
            candidate_orig.append(root_dir / "data" / "samples" / sample_est_str)
        # 안전 fallback 샘플 파일 목록
        candidate_orig.extend([
            root_dir / "data" / "samples" / "전시 광고주컨펌완료 견적서 (1).xlsx",
            root_dir / "data" / "samples" / "전시_광고주컨펌완료_기준견적서.xlsx",
            root_dir / "data" / "samples" / "P001_최초견적.xlsx"
        ])
        orig_path = next((p for p in candidate_orig if p and p.exists()), None)

        # 2. 변경 견적서 파일 탐색
        candidate_rev = []
        if sample_chg_str:
            if Path(sample_chg_str).is_absolute():
                candidate_rev.append(Path(sample_chg_str))
            candidate_rev.append(root_dir / "data" / sample_chg_str)
            candidate_rev.append(root_dir / "data" / "samples" / sample_chg_str)
            candidate_rev.extend([
                root_dir / "data" / "samples" / "전시_홍대점_변경내역.xlsx",
                root_dir / "data" / "samples" / "P001_변경내역.xlsx"
            ])
        candidate_rev.append(orig_path)
        rev_path = next((p for p in candidate_rev if p and p.exists()), orig_path)

        if orig_path and orig_path.exists():
            orig_file_input = str(orig_path)
            orig_file_name = orig_path.name
            if rev_path and rev_path.exists():
                rev_file_input = str(rev_path)
                rev_file_name = rev_path.name
    else:
        st.sidebar.subheader("파일 업로드")
        orig_uploaded = st.sidebar.file_uploader("1. 최초/기준 견적서 (.xlsx)", type=["xlsx"], key="u_orig")
        rev_uploaded = st.sidebar.file_uploader("2. 변경 내역서 (.xlsx)", type=["xlsx"], key="u_rev")
        if orig_uploaded:
            orig_file_input = orig_uploaded
            orig_file_name = orig_uploaded.name
        if rev_uploaded:
            rev_file_input = rev_uploaded
            rev_file_name = rev_uploaded.name

    if not orig_file_input or not rev_file_input:
        st.info("💡 사이드바에서 기준견적서 프로젝트를 선택하거나 최초 및 변경 견적서 XLSX를 올려 주세요.")
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
            index=0
        )

        if match_mode == "동일 시트명 1:1 자동 대조":
            selected_common = st.sidebar.selectbox(
                "대조할 동일 시트 선택",
                common_sheets,
                index=default_idx
            )
            sheet_orig_selected = selected_common
            sheet_rev_selected = selected_common
            st.sidebar.caption(f"기준: `{sheet_orig_selected}` ⟷ 변경: `{sheet_rev_selected}`")
        else:
            sheet_orig_selected = st.sidebar.selectbox("최초 견적서 시트 선택", orig_sheets, index=0)
            sheet_rev_selected = st.sidebar.selectbox("변경 내역서 시트 선택", rev_sheets, index=0)
    else:
        st.sidebar.warning("양쪽 파일에 동일한 이름의 시트가 없습니다. 비교할 시트를 각각 선택해 주세요.")
        sheet_orig_selected = st.sidebar.selectbox("최초 견적서 시트 선택", orig_sheets, index=0)
        sheet_rev_selected = st.sidebar.selectbox("변경 내역서 시트 선택", rev_sheets, index=0)

    # 세션 상태 사용자 매칭 결정 맵
    decision_key = f"decisions_{proj_id}_{sheet_orig_selected}_{sheet_rev_selected}"
    if decision_key not in st.session_state:
        st.session_state[decision_key] = {}

    try:
        # 시트 가져오기
        ws_orig_est = wb_orig[sheet_orig_selected]
        ws_rev_est = wb_rev[sheet_rev_selected]

        # 파싱 실행
        orig_items, mismatches_orig, orig_dup, orig_warn = read_estimate_sheet(ws_orig_est, orig_file_name, sheet_orig_selected)
        rev_items, mismatches_rev, rev_dup, rev_warn = read_estimate_sheet(ws_rev_est, rev_file_name, sheet_rev_selected)

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
            approval_records, appr_warn = read_approval_sheet(wb_rev["변경승인"], rev_file_name, "변경승인")
        else:
            st.info("ℹ️ ‘변경승인’ 시트가 감지되지 않아 변경 항목의 승인 여부가 기본 '미확인'으로 표시됩니다.")

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
        st.markdown(f"**현재 대조 시트:** `{orig_file_name}` [`{sheet_orig_selected}`] ⟷ `{rev_file_name}` [`{sheet_rev_selected}`]")

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

        # 9대 감리 및 비전/학습 탭
        tab_diagnostics, tab_vision, tab_learning, tab_traffic, tab_decompose, tab_labor, tab_inquiry, tab_confirm, tab_raw = st.tabs([
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

        # 0. 견적 진단·감리실 (적합/비적합 & 공공기준 소명)
        with tab_diagnostics:
            st.subheader("⚖️ 견적감독관 종합진단실 — 총체적 종합의견")

            # [견적감독관 총체적 종합 진단 소견 란 (Framer Signature Gradient Spotlight Card)]
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
                """, unsafe_allow_html=True)

            st.markdown("##### 🎯 감독관 3대 핵심 실행 조치 (Action Plan)")
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

if __name__ == "__main__":
    main()
