# -*- coding: utf-8 -*-
"""
제일기획 AI 견적감독관 — MOGAM(https://www.mogam.re.kr/) 레퍼런스 기반 프리미엄 코퍼레이트 디자인 시스템 (mogam_theme.py)

핵심 디자인 키워드:
PREMIUM / MINIMAL / MODERN / CORPORATE / SOPHISTICATED / TECHNOLOGY
"""

import base64
from functools import lru_cache
from pathlib import Path
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "mogam"


def clean_html(raw: str) -> str:
    """Markdown 파서가 들여쓰기된 HTML을 코드블록(<pre><code>)으로 오인하지 않도록 정리합니다."""
    return "\n".join(line.strip() for line in raw.splitlines() if line.strip())


@lru_cache(maxsize=16)
def get_asset_data_uri(filename: str) -> str:
    """assets/mogam 폴더 내 고해상도 이미지를 Base64 Data URI로 변환하여 즉시 렌더링합니다."""
    img_path = ASSETS_DIR / filename
    if not img_path.exists():
        return ""
    mime = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
    b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def get_mogam_global_css() -> str:
    """
    MOGAM 홈페이지의 디자인 철학(Deep Blue & Pure White, Pretendard/Inter, CSS clamp(),
    최소한의 선과 넓은 여백, Hero Zoom & Scroll Reveal 모션, 반응형 브레이크포인트)을 구현한 전역 CSS입니다.
    """
    return clean_html(
        """
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        :root {
            --mogam-deep-blue: #002C5F;
            --mogam-navy: #071A33;
            --mogam-royal-blue: #0052CC;
            --mogam-accent-blue: #0066FF;
            --mogam-light-blue: #EBF3FA;
            --mogam-ice-blue: #F3F7FC;
            --mogam-white: #FFFFFF;
            --mogam-sub-bg: #F8F9FB;
            --mogam-charcoal: #111827;
            --mogam-ink-secondary: #374151;
            --mogam-muted: #6B7280;
            --mogam-hairline: #E5E8EB;
            --mogam-hairline-dark: rgba(255, 255, 255, 0.16);

            /* 호환성 변수 */
            --canvas-cream: #FFFFFF;
            --canvas-stone: #F8F9FB;
            --lifted-cream: #FFFFFF;
            --surface-lifted: #FFFFFF;
            --white: #FFFFFF;
            --soft-bone: #F8F9FB;
            --ink-black: #111827;
            --charcoal: #1F2937;
            --slate-gray: #4B5563;
            --granite: #374151;
            --border-stone: #E5E8EB;
            --imweb-blue: #0052CC;
            --signal-orange: #0052CC;
            --link-blue: #0052CC;
            --semantic-success: #059669;
            --semantic-danger: #DC2626;
            --semantic-warning: #D97706;
        }

        /* 1. 전역 타이포그래피 & 퓨어 화이트 베이스 */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: var(--mogam-white) !important;
            color: var(--mogam-charcoal) !important;
            font-family: 'Pretendard', 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
            font-weight: 400 !important;
            line-height: 1.65 !important;
            letter-spacing: -0.015em !important;
            -webkit-font-smoothing: antialiased !important;
            scroll-behavior: smooth !important;
        }

        /* 최대 콘텐츠 너비 1440px 및 넓은 좌우 여백 */
        .block-container {
            max-width: 1440px !important;
            padding-top: 1.2rem !important;
            padding-left: clamp(20px, 4vw, 64px) !important;
            padding-right: clamp(20px, 4vw, 64px) !important;
            padding-bottom: 4rem !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', 'Pretendard', sans-serif !important;
            color: var(--mogam-charcoal) !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em !important;
            line-height: 1.22 !important;
        }

        /* 2. 키프레임 모션 & 애니메이션 (Hero Zoom, Fade Up, Clip Reveal, Pulse) */
        @keyframes mogamHeroZoom {
            0% { transform: scale(1.0); }
            100% { transform: scale(1.09); }
        }
        @keyframes mogamFadeUp {
            0% { opacity: 0; transform: translateY(28px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes mogamClipReveal {
            0% { clip-path: inset(0 100% 0 0); opacity: 0.2; }
            100% { clip-path: inset(0 0 0 0); opacity: 1; }
        }
        @keyframes mogamScrollBounce {
            0%, 100% { transform: translateY(0); opacity: 0.85; }
            50% { transform: translateY(7px); opacity: 0.4; }
        }
        @keyframes mogamCountGlow {
            0% { opacity: 0; transform: translateY(14px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* 3. MOGAM 헤더 (상단 고정형 미니멀 코퍼레이트 내비게이션) */
        .mogam-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px clamp(20px, 3.5vw, 48px);
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--mogam-hairline);
            position: sticky;
            top: 0;
            z-index: 999;
            transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .mogam-logo-group {
            display: flex;
            align-items: center;
            gap: 14px;
            text-decoration: none !important;
        }
        .mogam-logo-mark {
            width: 10px;
            height: 28px;
            background: var(--mogam-deep-blue);
            display: inline-block;
        }
        .mogam-logo-title {
            font-family: 'Inter', 'Pretendard', sans-serif;
            font-size: clamp(16px, 1.4vw, 20px);
            font-weight: 800;
            color: var(--mogam-deep-blue);
            letter-spacing: -0.03em;
        }
        .mogam-logo-sub {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: var(--mogam-muted);
            letter-spacing: 0.12em;
            text-transform: uppercase;
            border-left: 1px solid var(--mogam-hairline);
            padding-left: 12px;
        }
        .mogam-nav-links {
            display: flex;
            align-items: center;
            gap: clamp(18px, 2.5vw, 38px);
            flex-wrap: wrap;
        }
        .mogam-nav-item {
            font-family: 'Inter', 'Pretendard', sans-serif;
            font-size: 13.5px;
            font-weight: 600;
            color: var(--mogam-charcoal) !important;
            text-decoration: none !important;
            letter-spacing: 0.02em;
            position: relative;
            padding: 4px 0;
            transition: color 0.25s ease;
        }
        .mogam-nav-item::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 0%;
            height: 2px;
            background-color: var(--mogam-royal-blue);
            transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .mogam-nav-item:hover {
            color: var(--mogam-royal-blue) !important;
            text-decoration: none !important;
        }
        .mogam-nav-item:hover::after {
            width: 100%;
        }
        .mogam-nav-cta {
            background: var(--mogam-deep-blue);
            color: #FFFFFF !important;
            font-size: 12.5px;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 10px 22px;
            text-decoration: none !important;
            transition: background 0.25s ease, transform 0.25s ease;
        }
        .mogam-nav-cta:hover {
            background: var(--mogam-royal-blue);
            transform: translateY(-1px);
            text-decoration: none !important;
        }

        /* 4. SECTION 01: HERO (88vh, Zoom Animation, Sequential Text Reveal, Transparent Top Bar) */
        .mogam-hero-wrap {
            position: relative;
            width: 100%;
            min-height: clamp(560px, 84vh, 840px);
            overflow: hidden;
            background-color: var(--mogam-navy);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: clamp(64px, 8vw, 112px);
        }
        .mogam-hero-bg {
            position: absolute;
            inset: 0;
            background-size: cover;
            background-position: center;
            animation: mogamHeroZoom 20s ease-out forwards;
            z-index: 1;
        }
        .mogam-hero-overlay {
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(7, 26, 51, 0.72) 0%, rgba(0, 44, 95, 0.58) 50%, rgba(7, 26, 51, 0.88) 100%);
            z-index: 2;
        }
        .mogam-hero-topbar {
            position: relative;
            z-index: 3;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 26px clamp(24px, 4.5vw, 64px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.14);
        }
        .mogam-hero-content {
            position: relative;
            z-index: 3;
            padding: clamp(40px, 6vw, 80px) clamp(24px, 5vw, 76px);
            max-width: 1080px;
        }
        .mogam-hero-kicker {
            font-family: 'Inter', sans-serif;
            font-size: clamp(11px, 1vw, 13px);
            font-weight: 700;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: #7CC4FA;
            margin-bottom: 20px;
            animation: mogamFadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
        }
        .mogam-hero-headline {
            font-family: 'Pretendard', 'Inter', sans-serif !important;
            font-size: clamp(2.1rem, 4.3vw, 4.1rem) !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            line-height: 1.16 !important;
            letter-spacing: -0.035em !important;
            margin: 0 0 24px 0 !important;
            animation: mogamFadeUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both;
        }
        .mogam-hero-subcopy {
            font-size: clamp(1rem, 1.35vw, 1.22rem);
            font-weight: 400;
            color: rgba(255, 255, 255, 0.84);
            line-height: 1.72;
            max-width: 760px;
            margin: 0 0 36px 0;
            animation: mogamFadeUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.42s both;
        }
        .mogam-hero-actions {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            animation: mogamFadeUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.58s both;
        }
        .mogam-btn-white {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: #FFFFFF;
            color: var(--mogam-deep-blue) !important;
            padding: 15px 34px;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-decoration: none !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .mogam-btn-white:hover {
            background: var(--mogam-royal-blue);
            color: #FFFFFF !important;
            transform: translateX(4px);
            text-decoration: none !important;
        }
        .mogam-btn-ghost {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: transparent;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.4);
            padding: 15px 30px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.02em;
            text-decoration: none !important;
            transition: all 0.3s ease;
        }
        .mogam-btn-ghost:hover {
            border-color: #FFFFFF;
            background: rgba(255, 255, 255, 0.1);
            text-decoration: none !important;
        }
        .mogam-scroll-indicator {
            position: relative;
            z-index: 3;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px clamp(24px, 4.5vw, 64px);
            border-top: 1px solid rgba(255, 255, 255, 0.14);
            color: rgba(255, 255, 255, 0.72);
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }
        .mogam-scroll-arrow {
            display: inline-block;
            animation: mogamScrollBounce 2s infinite;
            margin-left: 8px;
        }

        /* 5. 공통 섹션 타이포그래피 & 레이아웃 */
        .mogam-section {
            padding: clamp(56px, 7vw, 104px) 0;
            border-bottom: 1px solid var(--mogam-hairline);
        }
        .mogam-section-subbg {
            background-color: var(--mogam-sub-bg);
            padding: clamp(64px, 7.5vw, 110px) clamp(24px, 4.5vw, 64px);
            margin: 0 0 clamp(56px, 7vw, 96px) 0;
        }
        .mogam-sec-num {
            font-family: 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.18em;
            color: var(--mogam-royal-blue);
            text-transform: uppercase;
            margin-bottom: 14px;
            display: block;
        }
        .mogam-sec-title {
            font-family: 'Pretendard', 'Inter', sans-serif !important;
            font-size: clamp(1.75rem, 3vw, 2.75rem) !important;
            font-weight: 800 !important;
            color: var(--mogam-charcoal) !important;
            line-height: 1.24 !important;
            letter-spacing: -0.03em !important;
            margin: 0 0 20px 0 !important;
        }
        .mogam-sec-lead {
            font-size: clamp(1rem, 1.2vw, 1.14rem);
            color: var(--mogam-ink-secondary);
            line-height: 1.75;
            max-width: 680px;
            margin: 0;
        }

        /* 6. 이미지 프레임 & Hover Zoom / Clip-path Reveal */
        .mogam-img-frame {
            position: relative;
            width: 100%;
            overflow: hidden;
            background-color: var(--mogam-navy);
            animation: mogamClipReveal 1.1s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .mogam-img-frame img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.85s cubic-bezier(0.16, 1, 0.3, 1), filter 0.6s ease;
        }
        .mogam-img-frame:hover img {
            transform: scale(1.06);
        }

        /* 7. SECTION 02: BRAND INTRODUCTION (비대칭 그리드) */
        .mogam-asymmetric-grid {
            display: grid;
            grid-template-columns: 1.05fr 1.2fr;
            gap: clamp(32px, 5vw, 80px);
            align-items: center;
        }

        /* 8. SECTION 03: CORE SERVICE (3단 에디토리얼 컬럼) */
        .mogam-service-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: clamp(24px, 3vw, 44px);
            margin-top: 48px;
        }
        .mogam-service-item {
            display: flex;
            flex-direction: column;
            border-top: 2px solid var(--mogam-deep-blue);
            padding-top: 24px;
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .mogam-service-item:hover {
            transform: translateY(-6px);
        }
        .mogam-service-idx {
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 800;
            color: var(--mogam-royal-blue);
            letter-spacing: 0.14em;
            margin-bottom: 12px;
        }
        .mogam-service-name {
            font-size: clamp(1.25rem, 1.6vw, 1.55rem);
            font-weight: 800;
            color: var(--mogam-charcoal);
            margin-bottom: 14px;
            letter-spacing: -0.025em;
        }
        .mogam-service-desc {
            font-size: 14.5px;
            color: var(--mogam-ink-secondary);
            line-height: 1.7;
            margin-bottom: 22px;
            flex-grow: 1;
        }
        .mogam-link-arrow {
            font-family: 'Inter', 'Pretendard', sans-serif;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.06em;
            color: var(--mogam-deep-blue) !important;
            text-transform: uppercase;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding-top: 14px;
            border-top: 1px solid var(--mogam-hairline);
            transition: gap 0.25s ease, color 0.25s ease;
        }
        .mogam-service-item:hover .mogam-link-arrow {
            gap: 14px;
            color: var(--mogam-royal-blue) !important;
        }

        /* 9. SECTION 04: KEY CONTENT (대표 콘텐츠 대형 비주얼 + 서브 리스트 그리드) */
        .mogam-content-layout {
            display: grid;
            grid-template-columns: 1.15fr 1fr;
            gap: clamp(28px, 4vw, 60px);
            margin-top: 44px;
            align-items: stretch;
        }
        .mogam-content-row {
            padding: 22px 0;
            border-bottom: 1px solid var(--mogam-hairline);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            transition: padding-left 0.25s ease;
        }
        .mogam-content-row:first-child {
            border-top: 1px solid var(--mogam-charcoal);
        }
        .mogam-content-row:hover {
            padding-left: 10px;
        }
        .mogam-cat-tag {
            font-family: 'Inter', sans-serif;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: var(--mogam-royal-blue);
            text-transform: uppercase;
            margin-bottom: 6px;
            display: block;
        }

        /* 10. SECTION 05: TRUST & VALUE (대형 수치 카운터 & 프로세스 아키텍처) */
        .mogam-stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            border-top: 2px solid var(--mogam-deep-blue);
            border-bottom: 1px solid var(--mogam-hairline);
            margin: 44px 0;
        }
        .mogam-stat-cell {
            padding: 36px 28px;
            border-right: 1px solid var(--mogam-hairline);
            animation: mogamCountGlow 0.9s ease-out both;
        }
        .mogam-stat-cell:last-child {
            border-right: none;
        }
        .mogam-stat-num {
            font-family: 'Inter', sans-serif;
            font-size: clamp(2.2rem, 3.6vw, 3.4rem);
            font-weight: 800;
            color: var(--mogam-deep-blue);
            letter-spacing: -0.04em;
            line-height: 1.05;
            margin-bottom: 12px;
        }
        .mogam-stat-unit {
            font-size: 0.55em;
            font-weight: 700;
            color: var(--mogam-royal-blue);
            margin-left: 3px;
        }
        .mogam-stat-label {
            font-size: 15px;
            font-weight: 700;
            color: var(--mogam-charcoal);
            margin-bottom: 6px;
        }
        .mogam-stat-sub {
            font-size: 13px;
            color: var(--mogam-muted);
            line-height: 1.5;
        }

        /* 11. SECTION 06: FINAL CTA (대형 비주얼 배너) */
        .mogam-cta-banner {
            position: relative;
            overflow: hidden;
            background-color: var(--mogam-navy);
            padding: clamp(56px, 7vw, 96px) clamp(28px, 5vw, 76px);
            margin: clamp(48px, 6vw, 84px) 0 44px 0;
            color: #FFFFFF;
        }
        .mogam-cta-bg {
            position: absolute;
            inset: 0;
            background-size: cover;
            background-position: center;
            opacity: 0.38;
            transition: transform 1.2s ease;
        }
        .mogam-cta-banner:hover .mogam-cta-bg {
            transform: scale(1.04);
        }
        .mogam-cta-inner {
            position: relative;
            z-index: 2;
            max-width: 820px;
        }

        /* 12. Streamlit 기본 위젯을 MOGAM 미니멀 코퍼레이트 스타일로 통일 */
        [data-testid="stSidebar"] {
            background-color: var(--mogam-sub-bg) !important;
            border-right: 1px solid var(--mogam-hairline) !important;
        }
        button[kind="primary"], .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] > button {
            background: var(--mogam-deep-blue) !important;
            color: #FFFFFF !important;
            border-radius: 4px !important;
            padding: 12px 28px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em !important;
            border: 1px solid var(--mogam-deep-blue) !important;
            box-shadow: none !important;
            transition: all 0.25s ease !important;
        }
        button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background: var(--mogam-royal-blue) !important;
            border-color: var(--mogam-royal-blue) !important;
            transform: translateY(-1px) !important;
        }
        button[kind="secondary"], .stButton > button, .stDownloadButton > button {
            background-color: var(--mogam-white) !important;
            color: var(--mogam-charcoal) !important;
            border-radius: 4px !important;
            padding: 11px 24px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover, .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--mogam-deep-blue) !important;
            color: var(--mogam-deep-blue) !important;
            background-color: var(--mogam-ice-blue) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent !important;
            border-bottom: 2px solid var(--mogam-hairline) !important;
            border-radius: 0 !important;
            padding: 0 !important;
            gap: 24px !important;
            box-shadow: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 0 !important;
            padding: 14px 6px !important;
            font-size: 14.5px !important;
            font-weight: 600 !important;
            color: var(--mogam-muted) !important;
            background: transparent !important;
            border-bottom: 3px solid transparent !important;
        }
        .stTabs [aria-selected="true"] {
            background: transparent !important;
            color: var(--mogam-deep-blue) !important;
            font-weight: 800 !important;
            border-bottom: 3px solid var(--mogam-deep-blue) !important;
            box-shadow: none !important;
        }
        div[data-testid="stMetric"] {
            background-color: var(--mogam-white) !important;
            border: none !important;
            border-top: 2px solid var(--mogam-deep-blue) !important;
            border-bottom: 1px solid var(--mogam-hairline) !important;
            border-radius: 0 !important;
            padding: 22px 16px !important;
            box-shadow: none !important;
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        input, textarea {
            background-color: var(--mogam-white) !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 4px !important;
            color: var(--mogam-charcoal) !important;
            font-size: 14px !important;
        }
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within,
        input:focus, textarea:focus {
            border-color: var(--mogam-deep-blue) !important;
            box-shadow: 0 0 0 2px rgba(0, 44, 95, 0.12) !important;
        }

        /* 기존 클래스 호환 */
        .mc-floating-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--mogam-white);
            border-bottom: 1px solid var(--mogam-hairline);
            padding: 18px 0;
            margin-bottom: 28px;
        }
        .mc-hero-stadium, .mc-stadium-card {
            background: var(--mogam-sub-bg);
            border-top: 2px solid var(--mogam-deep-blue);
            border-bottom: 1px solid var(--mogam-hairline);
            border-left: none;
            border-right: none;
            border-radius: 0;
            padding: 36px 40px;
            margin-bottom: 28px;
            box-shadow: none;
        }
        .mc-card-20 {
            background: var(--mogam-white);
            border: 1px solid var(--mogam-hairline);
            border-top: 2px solid var(--mogam-deep-blue);
            border-radius: 0;
            padding: 24px 26px;
            box-shadow: none;
        }
        .mc-pill-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            font-size: 11.5px;
            font-weight: 700;
            letter-spacing: 0.04em;
            border-radius: 2px;
        }
        .mc-chip-blue, .mc-chip-ink, .mc-chip-black {
            background: var(--mogam-light-blue);
            color: var(--mogam-deep-blue);
        }
        .mc-chip-green {
            background: #ECFDF5;
            color: #047857;
        }
        .mc-chip-orange {
            background: #FEF3C7;
            color: #B45309;
        }
        .mc-chip-violet {
            background: var(--mogam-ice-blue);
            color: var(--mogam-royal-blue);
        }
        .mc-chip-gray {
            background: var(--mogam-sub-bg);
            color: var(--mogam-ink-secondary);
        }
        .mc-footer {
            background-color: var(--mogam-navy);
            color: #FFFFFF;
            padding: 64px clamp(24px, 5vw, 72px) 48px clamp(24px, 5vw, 72px);
            margin-top: 72px;
            border-radius: 0;
        }
        .mc-footer-title {
            font-family: 'Inter', 'Pretendard', sans-serif !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
            margin-bottom: 12px !important;
        }

        /* 13. 반응형 브레이크포인트 (1440px, 768px, 390px) */
        @media (max-width: 1024px) {
            .mogam-asymmetric-grid,
            .mogam-service-grid,
            .mogam-content-layout {
                grid-template-columns: 1fr;
            }
            .mogam-stat-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .mogam-stat-cell:nth-child(2) {
                border-right: none;
            }
            .mogam-stat-cell {
                border-bottom: 1px solid var(--mogam-hairline);
            }
        }
        @media (max-width: 640px) {
            .mogam-header {
                padding: 14px 16px;
            }
            .mogam-logo-sub {
                display: none;
            }
            .mogam-nav-links {
                gap: 12px;
            }
            .mogam-hero-wrap {
                min-height: 520px;
            }
            .mogam-stat-grid {
                grid-template-columns: 1fr;
            }
            .mogam-stat-cell {
                border-right: none;
                padding: 24px 16px;
            }
        }
        </style>
        """
    )


def render_mogam_full_landing_sections(admin_email: str, is_authenticated: bool = False) -> None:
    """
    MOGAM 레퍼런스 기반 6대 섹션(HEADER + SECTION 01 HERO ~ SECTION 06 FINAL CTA)을 렌더링합니다.
    """
    uri_hero = get_asset_data_uri("hero_main.jpg")
    uri_intro = get_asset_data_uri("brand_intro.jpg")
    uri_audit = get_asset_data_uri("service_audit.jpg")
    uri_vision = get_asset_data_uri("service_vision.jpg")
    uri_asset = get_asset_data_uri("service_asset.jpg")
    uri_cta = get_asset_data_uri("cta_bg.jpg")

    cta_target = "#mogam-workspace-anchor" if is_authenticated else "#mogam-access-gate"
    cta_label = "ENTER AUDIT WORKSPACE →" if is_authenticated else "MEMBER ACCESS & SIGN UP →"

    html = f"""
    <!-- STICKY CORPORATE HEADER -->
    <header class="mogam-header">
        <a href="#top" class="mogam-logo-group">
            <span class="mogam-logo-mark"></span>
            <span class="mogam-logo-title">CHEIL AX</span>
            <span class="mogam-logo-sub">AI ESTIMATE SUPERVISOR</span>
        </a>
        <nav class="mogam-nav-links">
            <a href="#sec-intro" class="mogam-nav-item">PHILOSOPHY</a>
            <a href="#sec-service" class="mogam-nav-item">CORE SERVICE</a>
            <a href="#sec-content" class="mogam-nav-item">BENCHMARK</a>
            <a href="#sec-trust" class="mogam-nav-item">TRUST &amp; VALUE</a>
            <a href="{cta_target}" class="mogam-nav-cta">{'AUDIT STUDIO' if is_authenticated else 'MEMBER GATE'}</a>
        </nav>
    </header>

    <!-- SECTION 01. HERO -->
    <section class="mogam-hero-wrap" id="top">
        <div class="mogam-hero-bg" style="background-image: url('{uri_hero}');"></div>
        <div class="mogam-hero-overlay"></div>
        <div class="mogam-hero-topbar">
            <span style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; letter-spacing: 0.14em; color: rgba(255,255,255,0.8);">
                CHEIL WORLDWIDE · ENTERPRISE COST INTELLIGENCE
            </span>
            <span style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; letter-spacing: 0.1em; color: #7CC4FA;">
                ● SYSTEM ONLINE 24/7
            </span>
        </div>
        <div class="mogam-hero-content">
            <div class="mogam-hero-kicker">BEYOND ESTIMATE, AI GOVERNANCE</div>
            <h1 class="mogam-hero-headline">
                데이터와 AI가 정의하는<br/>
                기업 견적 감리의 새로운 표준
            </h1>
            <p class="mogam-hero-subcopy">
                제일기획 AI 견적감독관은 프로젝트마다 상이한 실행예산과 협력사 내역서를 7대 표준 공종으로 정밀 분해하고,
                정부 공인 6대 물가·노임 기준 및 실물 제작 아카이브와 실시간 교차 검증하여 가장 투명하고 객관적인 의사결정을 지원합니다.
            </p>
            <div class="mogam-hero-actions">
                <a href="{cta_target}" class="mogam-btn-white">
                    <span>{cta_label}</span>
                </a>
                <a href="#sec-service" class="mogam-btn-ghost">
                    <span>EXPLORE CAPABILITIES</span>
                </a>
            </div>
        </div>
        <div class="mogam-scroll-indicator">
            <span>SCROLL DOWN TO DISCOVER<span class="mogam-scroll-arrow">↓</span></span>
            <span>01 / 06 · HERO</span>
        </div>
    </section>

    <!-- SECTION 02. BRAND INTRODUCTION -->
    <section class="mogam-section" id="sec-intro">
        <div class="mogam-asymmetric-grid">
            <div>
                <span class="mogam-sec-num">02 · BRAND PHILOSOPHY</span>
                <h2 class="mogam-sec-title">
                    경험과 직관을 넘어,<br/>
                    객관적 데이터로 증명하는<br/>
                    실행예산 거버넌스
                </h2>
                <p class="mogam-sec-lead" style="margin-bottom: 24px;">
                    전시·팝업·디지털 키트 제작 현장의 견적서는 협력사마다 양식과 단가 체계가 달라 정밀한 비교에 막대한 시간이 소요되었습니다.
                    AI 견적감독관은 비정형 내역서를 표준화된 데이터 구조로 재편하고, 공인된 법적·산업적 기준점을 제시함으로써 감리의 투명성과 속도를 혁신합니다.
                </p>
                <div style="border-top: 1px solid var(--mogam-hairline); padding-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: var(--mogam-royal-blue); letter-spacing: 0.08em; margin-bottom: 6px;">PRECISION</div>
                        <div style="font-size: 14px; color: var(--mogam-charcoal); font-weight: 600;">수량 효과와 단가 효과의 수학적 요인 분해</div>
                    </div>
                    <div>
                        <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: var(--mogam-royal-blue); letter-spacing: 0.08em; margin-bottom: 6px;">COMPLIANCE</div>
                        <div style="font-size: 14px; color: var(--mogam-charcoal); font-weight: 600;">6대 정부 공인 노임·물가 기준 실시간 연동</div>
                    </div>
                </div>
            </div>
            <div class="mogam-img-frame" style="aspect-ratio: 4 / 3;">
                <img src="{uri_intro}" alt="Architectural Precision and Transparency" />
            </div>
        </div>
    </section>

    <!-- SECTION 03. CORE SERVICE -->
    <section class="mogam-section" id="sec-service">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 20px;">
            <div>
                <span class="mogam-sec-num">03 · CORE CAPABILITIES</span>
                <h2 class="mogam-sec-title" style="margin-bottom: 0 !important;">
                    세 가지 AI 코어 엔진이 구현하는<br/>
                    엔드투엔드(E2E) 견적 감리 아키텍처
                </h2>
            </div>
            <p style="font-size: 14.5px; color: var(--mogam-muted); max-width: 420px; margin: 0;">
                사전 예산 산출부터 협력사 변경 내역서 정밀 감리, 최종 확정 실적의 자산화까지 하나의 플랫폼에서 완결됩니다.
            </p>
        </div>

        <div class="mogam-service-grid">
            <!-- Service 01 -->
            <div class="mogam-service-item">
                <div class="mogam-img-frame" style="aspect-ratio: 4 / 3; margin-bottom: 22px;">
                    <img src="{uri_audit}" alt="Cross-Format Estimate Audit" />
                </div>
                <span class="mogam-service-idx">01 / CROSS-FORMAT AUDIT</span>
                <div class="mogam-service-name">양식초월 7대 공종 정밀 감리</div>
                <p class="mogam-service-desc">
                    상이한 시트 구조와 비정형 품목명을 목공사·금속·전기·도장·사인·집기·경비의 7대 표준 공종으로 자동 재분류하고,
                    기준 견적 대비 편차를 3단계 신호등(적정·주의·비적합)으로 즉시 판정합니다.
                </p>
                <a href="{cta_target}" class="mogam-link-arrow">LAUNCH AUDIT ENGINE <span>→</span></a>
            </div>

            <!-- Service 02 -->
            <div class="mogam-service-item">
                <div class="mogam-img-frame" style="aspect-ratio: 4 / 3; margin-bottom: 22px;">
                    <img src="{uri_vision}" alt="Vision AI Spatial Cost Estimator" />
                </div>
                <span class="mogam-service-idx">02 / VISION AI ESTIMATOR</span>
                <div class="mogam-service-name">비전 AI 공간·키트 예상견적 산출</div>
                <p class="mogam-service-desc">
                    전시 부스, 팝업스토어, 인터랙티브 키트의 3D 투시도 또는 현장 사진을 분석하여
                    구조물·마감재·디스플레이·조명 물량을 식별하고 공인 단가 기반 예상 견적서(XLSX)를 생성합니다.
                </p>
                <a href="{cta_target}" class="mogam-link-arrow">EXPLORE VISION AI <span>→</span></a>
            </div>

            <!-- Service 03 -->
            <div class="mogam-service-item">
                <div class="mogam-img-frame" style="aspect-ratio: 4 / 3; margin-bottom: 22px;">
                    <img src="{uri_asset}" alt="Historical Asset & Benchmark Intelligence" />
                </div>
                <span class="mogam-service-idx">03 / DATA FLYWHEEL STUDIO</span>
                <div class="mogam-service-name">확정 실적 자산화 &amp; 공공기준 소명</div>
                <p class="mogam-service-desc">
                    광고주 컨펌 및 정산이 완료된 내역서를 사내 표준 벤치마크 DB로 영구 학습시키고,
                    91종 FAQ 자동 소명 답변서 및 공문형 감리 진단서를 원클릭으로 발행합니다.
                </p>
                <a href="{cta_target}" class="mogam-link-arrow">VIEW ASSET LIBRARY <span>→</span></a>
            </div>
        </div>
    </section>

    <!-- SECTION 04. KEY CONTENT -->
    <section class="mogam-section" id="sec-content">
        <span class="mogam-sec-num">04 · STANDARD BENCHMARK &amp; ARCHIVE</span>
        <h2 class="mogam-sec-title">
            6대 정부 공인 기준과 실물 제작 아카이브의 결합
        </h2>
        <div class="mogam-content-layout">
            <div style="background: var(--mogam-navy); color: #FFFFFF; padding: clamp(32px, 4vw, 52px); display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.16em; color: #7CC4FA; text-transform: uppercase;">
                        GROUND-TRUTH KNOWLEDGE BASE
                    </span>
                    <h3 style="color: #FFFFFF !important; font-size: clamp(1.45rem, 2.1vw, 2rem) !important; font-weight: 800 !important; margin: 14px 0 18px 0 !important; line-height: 1.3 !important;">
                        법적 소명력을 갖춘 공공 단가와<br/>
                        검증된 실물 제작 데이터의 이중 검증
                    </h3>
                    <p style="font-size: 14.5px; color: rgba(255,255,255,0.78); line-height: 1.75; margin-bottom: 28px;">
                        단순 평균값 비교가 아닌, 산업통상자원부·한국SW산업협회·중소기업중앙회·조달청 등 6대 공인 단가 체계와
                        제일기획 실제 전시·키트 정산 백데이터를 동시에 교차 대조하여 과다 청구 항목을 정밀하게 식별합니다.
                    </p>
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.16); padding-top: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; color: rgba(255,255,255,0.85);">
                        VERIFIED BY 6 PUBLIC STANDARDS
                    </span>
                    <a href="{cta_target}" style="color: #7CC4FA !important; font-family: 'Inter', sans-serif; font-size: 12.5px; font-weight: 700; letter-spacing: 0.08em;">
                        VIEW MORE →
                    </a>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: space-between;">
                <div class="mogam-content-row">
                    <div>
                        <span class="mogam-cat-tag">PUBLIC STANDARD 01 · KIDP &amp; KOSA</span>
                        <div style="font-size: 16px; font-weight: 700; color: var(--mogam-charcoal); margin-bottom: 4px;">산업디자인 대가기준 &amp; SW 기술자 평균임금</div>
                        <div style="font-size: 13.5px; color: var(--mogam-muted);">3D 공간 디자인, 그래픽 설계 및 인터랙티브 미디어 개발 인건비 적정성 검증</div>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: var(--mogam-deep-blue);">↗</span>
                </div>
                <div class="mogam-content-row">
                    <div>
                        <span class="mogam-cat-tag">PUBLIC STANDARD 02 · KBIZ &amp; KENCA</span>
                        <div style="font-size: 16px; font-weight: 700; color: var(--mogam-charcoal); margin-bottom: 4px;">중기중앙회 제조·시중노임단가 &amp; 엔지니어링 노임</div>
                        <div style="font-size: 13.5px; color: var(--mogam-muted);">목공·금속·전기·설치 현장 기술자 M/D 단가 및 100% 초과 중복 투입 자동 탐지</div>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: var(--mogam-deep-blue);">↗</span>
                </div>
                <div class="mogam-content-row">
                    <div>
                        <span class="mogam-cat-tag">PUBLIC STANDARD 03 · G2B &amp; LABOR LAW</span>
                        <div style="font-size: 16px; font-weight: 700; color: var(--mogam-charcoal); margin-bottom: 4px;">조달청 나라장터 물가정보 &amp; 근로기준법 할증 기준</div>
                        <div style="font-size: 13.5px; color: var(--mogam-muted);">자재·디스플레이 하드웨어 조달 단가 및 야간·휴일 철거 작업 할증률 준수 여부 검증</div>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: var(--mogam-deep-blue);">↗</span>
                </div>
                <div class="mogam-content-row">
                    <div>
                        <span class="mogam-cat-tag">ENTERPRISE ARCHIVE · 44 KIT &amp;MEGA EXPO DB</span>
                        <div style="font-size: 16px; font-weight: 700; color: var(--mogam-charcoal); margin-bottom: 4px;">실물 체험 키트 44종 &amp; 대형 전시 공인 정산 아카이브</div>
                        <div style="font-size: 13.5px; color: var(--mogam-muted);">실제 제작 사진과 확정 정산 원가가 매핑된 Ground-Truth 레퍼런스 라이브러리</div>
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: var(--mogam-deep-blue);">↗</span>
                </div>
            </div>
        </div>
    </section>

    <!-- SECTION 05. TRUST & VALUE -->
    <section class="mogam-section" id="sec-trust" style="border-bottom: none;">
        <span class="mogam-sec-num">05 · TRUST &amp; MEASURABLE VALUE</span>
        <h2 class="mogam-sec-title">
            수치로 증명되는 엔터프라이즈 감리 성과와 보안 프로세스
        </h2>
        <div class="mogam-stat-grid">
            <div class="mogam-stat-cell">
                <div class="mogam-stat-num">25.6<span class="mogam-stat-unit">억+</span></div>
                <div class="mogam-stat-label">누적 학습 키트·전시 정산 자산</div>
                <div class="mogam-stat-sub">실제 광고주 컨펌 완료 프로젝트 원가 데이터</div>
            </div>
            <div class="mogam-stat-cell">
                <div class="mogam-stat-num">44<span class="mogam-stat-unit">종</span></div>
                <div class="mogam-stat-label">실물 제작 키트 표준 벤치마크</div>
                <div class="mogam-stat-sub">실물 사진·공종별 단가 1:1 매핑 라이브러리</div>
            </div>
            <div class="mogam-stat-cell">
                <div class="mogam-stat-num">6<span class="mogam-stat-unit">대</span></div>
                <div class="mogam-stat-label">정부 공인 단가·법령 기준 연동</div>
                <div class="mogam-stat-sub">KIDP · KOSA · KENCA · KBIZ · G2B · 근로기준법</div>
            </div>
            <div class="mogam-stat-cell">
                <div class="mogam-stat-num">95<span class="mogam-stat-unit">%</span></div>
                <div class="mogam-stat-label">견적 감리·소명 리드타임 단축</div>
                <div class="mogam-stat-sub">수작업 4시간 이상 소요 업무를 3초 내 자동화</div>
            </div>
        </div>

        <!-- E2E 보안 승인 및 감리 프로세스 바 -->
        <div style="background: var(--mogam-sub-bg); border-top: 1px solid var(--mogam-charcoal); border-bottom: 1px solid var(--mogam-hairline); padding: 32px 36px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 22px;">
                <div style="font-size: 15px; font-weight: 800; color: var(--mogam-deep-blue); letter-spacing: -0.01em;">
                    ENTERPRISE SECURITY &amp; GOVERNANCE WORKFLOW
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 600; color: var(--mogam-muted);">
                    ADMIN AUTHORIZATION GATE · {admin_email}
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 24px;">
                <div style="border-left: 2px solid var(--mogam-deep-blue); padding-left: 16px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: var(--mogam-royal-blue); letter-spacing: 0.1em;">STEP 01</div>
                    <div style="font-size: 15px; font-weight: 700; color: var(--mogam-charcoal); margin: 4px 0;">회원신청 및 보안서약</div>
                    <div style="font-size: 12.5px; color: var(--mogam-muted);">성명·소속·직급·연락처·담당 프로젝트 입력</div>
                </div>
                <div style="border-left: 2px solid var(--mogam-deep-blue); padding-left: 16px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: var(--mogam-royal-blue); letter-spacing: 0.1em;">STEP 02</div>
                    <div style="font-size: 15px; font-weight: 700; color: var(--mogam-charcoal); margin: 4px 0;">관리자 승인 메일 자동 발송</div>
                    <div style="font-size: 12.5px; color: var(--mogam-muted);">{admin_email} 으로 신청 정보 즉시 전송</div>
                </div>
                <div style="border-left: 2px solid var(--mogam-deep-blue); padding-left: 16px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: var(--mogam-royal-blue); letter-spacing: 0.1em;">STEP 03</div>
                    <div style="font-size: 15px; font-weight: 700; color: var(--mogam-charcoal); margin: 4px 0;">메일 내 원클릭 [가입 승인]</div>
                    <div style="font-size: 12.5px; color: var(--mogam-muted);">HMAC-SHA256 암호화 서명 검증 및 자격 부여</div>
                </div>
                <div style="border-left: 2px solid var(--mogam-royal-blue); padding-left: 16px;">
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 800; color: var(--mogam-royal-blue); letter-spacing: 0.1em;">STEP 04</div>
                    <div style="font-size: 15px; font-weight: 700; color: var(--mogam-charcoal); margin: 4px 0;">AI 견적감독관 전체 기능 이용</div>
                    <div style="font-size: 12.5px; color: var(--mogam-muted);">정밀 감리 · 비전 AI · 실적 자산화 스튜디오 가동</div>
                </div>
            </div>
        </div>
    </section>

    <!-- SECTION 06. FINAL CTA -->
    <section class="mogam-cta-banner" id="mogam-access-gate">
        <div class="mogam-cta-bg" style="background-image: url('{uri_cta}');"></div>
        <div class="mogam-cta-inner">
            <span style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 700; letter-spacing: 0.18em; color: #7CC4FA; text-transform: uppercase; display: block; margin-bottom: 12px;">
                06 · ENTERPRISE ACCESS &amp; WORKSPACE
            </span>
            <h2 style="color: #FFFFFF !important; font-size: clamp(1.65rem, 2.6vw, 2.35rem) !important; font-weight: 800 !important; margin: 0 0 14px 0 !important; line-height: 1.25 !important;">
                {'승인된 정회원 보안 세션이 활성화되었습니다.' if is_authenticated else '지금 보안 인증을 완료하고 AI 견적감독관을 시작하십시오.'}
            </h2>
            <p style="font-size: 15px; color: rgba(255, 255, 255, 0.82); line-height: 1.7; margin: 0;">
                {'아래 워크스페이스 또는 좌측 컨트롤 패널에서 기준 견적서와 비교 견적서를 선택하여 7대 공종 정밀 감리를 즉시 수행할 수 있습니다.' if is_authenticated else f'대외비 실행예산 및 협력사 단가 보호를 위해 관리자({admin_email})의 이메일 승인을 받은 정회원만 워크스페이스에 접속할 수 있습니다.'}
            </p>
        </div>
    </section>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_mogam_footer() -> None:
    """MOGAM 스타일의 미니멀하고 품격 있는 다크 네이비 코퍼레이트 푸터입니다."""
    html = """
    <footer class="mc-footer">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 32px; padding-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.14);">
            <div style="max-width: 560px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                    <span style="width: 8px; height: 22px; background: #7CC4FA; display: inline-block;"></span>
                    <span style="font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF;">
                        CHEIL AX · AI ESTIMATE SUPERVISOR
                    </span>
                </div>
                <p style="color: rgba(255,255,255,0.68); font-size: 13.5px; line-height: 1.7; margin: 0;">
                    제일기획 AI 견적감독관은 정부 공인 6대 물가·노임 기준(KIDP, KOSA, KENCA, KBIZ, 근로기준법, 조달청 나라장터) 및
                    실물 제작 키트·전시 정산 아카이브를 기반으로 객관적이고 투명한 실행예산 감리 거버넌스를 제공합니다.
                </p>
            </div>
            <div style="display: flex; gap: 48px; flex-wrap: wrap;">
                <div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.14em; color: #7CC4FA; margin-bottom: 12px;">PLATFORM</div>
                    <div style="font-size: 13px; color: rgba(255,255,255,0.75); line-height: 2.0;">
                        <div>7대 공종 양식초월 감리</div>
                        <div>비전 AI 공간 예상견적</div>
                        <div>확정 실적 학습 스튜디오</div>
                    </div>
                </div>
                <div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.14em; color: #7CC4FA; margin-bottom: 12px;">OFFICIAL DOMAINS</div>
                    <div style="font-size: 13px; color: rgba(255,255,255,0.75); line-height: 2.0;">
                        <div><a href="https://ax-estimate-director.onrender.com" target="_blank" style="color: rgba(255,255,255,0.85) !important;">ax-estimate-director.onrender.com ↗</a></div>
                        <div><a href="https://ax-estimate-supervisor.onrender.com" target="_blank" style="color: rgba(255,255,255,0.85) !important;">ax-estimate-supervisor.onrender.com ↗</a></div>
                    </div>
                </div>
            </div>
        </div>
        <div style="padding-top: 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.5);">
            <div>© 2026 CHEIL WORLDWIDE AX ESTIMATE GOVERNANCE. ALL RIGHTS RESERVED.</div>
            <div>DESIGNED WITH ENTERPRISE MINIMALISM &amp; PRECISION</div>
        </div>
    </footer>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)
