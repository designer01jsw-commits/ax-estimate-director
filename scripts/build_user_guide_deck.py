# -*- coding: utf-8 -*-
"""
제일기획 AX 「견적감리관 & 견적감독관」 웹 서비스 완벽 사용 설명서 PPTX 생성기
Widescreen 16:9 규격, 하이테크 모던 블루/시안/골드 테마
"""

import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 1. 디자인 시스템 팔레트
C_BG_DARK       = RGBColor(11, 19, 43)      # 심해 네이비 (#0B132B)
C_CARD_BG       = RGBColor(19, 34, 64)      # 카드 배경 (#132240)
C_CARD_BG_LIGHT = RGBColor(28, 48, 88)      # 강조 카드 (#1C3058)
C_CYAN          = RGBColor(0, 229, 255)     # 네온 시안 (#00E5FF)
C_GOLD          = RGBColor(245, 158, 11)    # 엠버 골드 (#F59E0B)
C_GREEN         = RGBColor(16, 185, 129)    # 세이프티 그린 (#10B981)
C_RED           = RGBColor(239, 68, 68)     # 리스크 레드 (#EF4444)
C_PURPLE        = RGBColor(139, 92, 246)    # 하이테크 퍼플 (#8B5CF6)
C_BLUE_BORDER   = RGBColor(30, 58, 110)     # 보더 블루 (#1E3A6E)
C_TEXT_WHITE    = RGBColor(255, 255, 255)   # 타이틀 화이트 (#FFFFFF)
C_TEXT_LIGHT    = RGBColor(203, 213, 225)   # 본문 연회색 (#CBD5E1)
C_TEXT_MUTED    = RGBColor(148, 163, 184)   # 캡션 회색 (#94A3B8)

FONT_HEADING = "Malgun Gothic"
FONT_BODY    = "Malgun Gothic"

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide, color=C_BG_DARK):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, desc_text, step_no=None):
        # Header Badge
        badge_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.0), Inches(0.4))
        tf_b = badge_box.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        prefix = f"[STEP {step_no:02d}] " if step_no else ""
        p_b.text = f"★ {prefix}{badge_text}"
        p_b.font.name = FONT_HEADING
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = C_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.733), Inches(0.6))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_WHITE

        # Desc
        desc_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.4))
        tf_d = desc_box.text_frame
        tf_d.word_wrap = True
        p_d = tf_d.paragraphs[0]
        p_d.text = desc_text
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    def add_card(slide, left, top, width, height, fill_color=C_CARD_BG, border_color=C_BLUE_BORDER, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(border_width)
        else:
            card.line.fill.background()
        return card

    # ==============================================================================
    # SLIDE 01: 표지 (COVER)
    # ==============================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Decorative background card
    add_card(s1, 0.8, 0.8, 11.733, 5.9, RGBColor(14, 25, 52), C_CYAN, 2)

    tb_c = s1.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(4.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p0 = tf_c.paragraphs[0]
    p0.text = "CHEIL AX AUTOMATION SYSTEM — USER MANUAL"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN

    p1 = tf_c.add_paragraph()
    p1.text = "제일기획 AX 「견적감리관 & 감독관」\n웹 서비스 완벽 사용 설명서"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE
    p1.space_before = Pt(12)

    p2 = tf_c.add_paragraph()
    p2.text = "365일 24시간 어디서나 접속하는 클라우드 AI 견적 감리·진단·원가 산출 시스템 활용 매뉴얼"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(14)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_before = Pt(14)

    # 3 Summary Bullets
    bullets = [
        "🌐 클라우드 웹 기반: 별도 설치 없이 모바일/태블릿/PC 브라우저 즉시 접속 (컴퓨터 전원 OFF 무관)",
        "⚖️ 정밀 감리 & 종합진단: 6대 공공 기준 크로스 체킹 및 단 3초 만에 삭감 타겟액 도출",
        "📷 비전 AI & 25.6억 DB: 시안 1장으로 5대 공종 원가 산출 및 44종 실물 키트 벤치마킹"
    ]
    for b in bullets:
        pb = tf_c.add_paragraph()
        pb.text = f"• {b}"
        pb.font.name = FONT_BODY
        pb.font.size = Pt(11)
        pb.font.color.rgb = C_GOLD
        pb.space_before = Pt(6)

    pf = tf_c.add_paragraph()
    pf.text = "발행부서: 제일기획 AX 추진팀 | 시스템 버전: 2026 Enterprise Release"
    pf.font.name = FONT_BODY
    pf.font.size = Pt(10)
    pf.font.color.rgb = C_TEXT_MUTED
    pf.space_before = Pt(20)

    # ==============================================================================
    # SLIDE 02: 접속 가이드 (ACCESS & QUICK START)
    # ==============================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "Quick Start", "서비스 접속 도메인 및 환경 안내", 
               "별도의 프로그램 설치 없이 크롬, 사파리, 엣지 등 모든 모던 웹 브라우저에서 즉시 접속 가능합니다.")

    # 3 Access Cards
    access_cards = [
        ("⚡ 1. 실시간 즉시 접속 주소", 
         "https://stopping-cashiers-right-exercise.trycloudflare.com",
         "지금 바로 확인 가능한 고속 터널 도메인\n- 로그인 및 비밀번호 입력 없이 1초 프리패스\n- PC, 아이패드, 모바일 스마트폰 전 기기 완벽 지원\n- 최신 '견적감독관 종합진단실' 기능 실시간 반영",
         C_CYAN),
        ("🚀 2. 신규 견적감독관 영구 도메인", 
         "https://ax-estimate-supervisor.onrender.com/",
         "24시간 365일 무중단 상용 클라우드\n- 발표자 컴퓨터가 꺼져 있어도 언제나 전 세계 접속 가능\n- Render 글로벌 인프라 기반 자동 복구 및 SSL 암호화\n- 총체적 종합의견 란이 탑재된 최신 프로덕션 빌드",
         C_GOLD),
        ("🏛️ 3. 기존 견적감리관 영구 도메인", 
         "https://ax-estimate-director.onrender.com/",
         "독립 운영되는 기존 안정화 도메인\n- 기존 URL을 그대로 유지하여 북마크 사용자 지원\n- 44종 키트 백데이터 및 비전 AI 산출기 완비\n- 다중 클라우드 백업 체계로 서비스 신뢰도 100% 보장",
         C_GREEN)
    ]

    for idx, (title, url, desc, accent_color) in enumerate(access_cards):
        cx = 0.8 + idx * 3.98
        add_card(s2, cx, 1.85, 3.78, 5.0, C_CARD_BG, accent_color, 2)

        tb = s2.shapes.add_textbox(Inches(cx + 0.15), Inches(2.0), Inches(3.48), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = accent_color

        p2 = tf.add_paragraph()
        p2.text = url
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_WHITE
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(10)
        p3.font.color.rgb = C_TEXT_LIGHT
        p3.space_before = Pt(12)

    # ==============================================================================
    # SLIDE 03: 화면 전체 UI 레이아웃 맵 (INTERFACE LAYOUT)
    # ==============================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "Interface Layout", "화면 구조 및 핵심 조작 메뉴 한눈에 보기", 
               "화면은 크게 [좌측 제어 사이드바]와 [중앙 9대 감리 탭 작업영역]으로 직관적으로 구분되어 있습니다.")

    # Left: Sidebar Card
    add_card(s3, 0.8, 1.85, 3.8, 5.0, RGBColor(16, 28, 56), C_CYAN, 2)
    tb_side = s3.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.4), Inches(4.7))
    tf_side = tb_side.text_frame
    tf_side.word_wrap = True

    ps0 = tf_side.paragraphs[0]
    ps0.text = "📁 좌측 제어 사이드바 (Sidebar)"
    ps0.font.name = FONT_HEADING
    ps0.font.size = Pt(13)
    ps0.font.bold = True
    ps0.font.color.rgb = C_CYAN

    side_items = [
        ("1. 메인 실행 모드 선택", "• 기준 견적서 정밀 감리 & 진단\n• 비전 AI 이미지 예상견적 산출기\n• 과거 실적 자산화 & AI 학습 스튜디오"),
        ("2. 프로젝트 선택 드롭다운", "• 갤럭시 스토어 수원, 홍대, 팝업스토어 등 광고주 컨펌 기준견적서 1~4 즉시 선택"),
        ("3. 데이터 소스 모드 전환", "• 광고주 컨펌 기준견적서 사용 (내장 DB)\n• 내 PC에서 엑셀 파일 직접 업로드 (자유 검증)")
    ]
    for s_title, s_desc in side_items:
        p_t = tf_side.add_paragraph()
        p_t.text = s_title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = C_GOLD
        p_t.space_before = Pt(10)

        p_d = tf_side.add_paragraph()
        p_d.text = s_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_LIGHT
        p_d.space_before = Pt(3)

    # Right: Main Content Area (Tabs Map)
    add_card(s3, 4.8, 1.85, 7.733, 5.0, C_CARD_BG, C_BLUE_BORDER, 1)
    tb_main = s3.shapes.add_textbox(Inches(5.0), Inches(2.0), Inches(7.333), Inches(4.7))
    tf_main = tb_main.text_frame
    tf_main.word_wrap = True

    pm0 = tf_main.paragraphs[0]
    pm0.text = "📊 중앙 메인 작업영역 — 9대 핵심 감리·진단 탭"
    pm0.font.name = FONT_HEADING
    pm0.font.size = Pt(13)
    pm0.font.bold = True
    pm0.font.color.rgb = C_TEXT_WHITE

    tabs_info = [
        ("Tab 0. 견적감독관 종합진단실 🆕", "신호등 종합 리스크 등급 판정, 부적정 삭감 목표액 도출, 4대 공종별 총평 및 3대 액션 가이드"),
        ("Tab 1. 비전 AI 이미지 예상견적", "시안/도면 단 1장으로 5대 공종(자재/가공/공임/도장/포장) 원가 산출 및 엑셀 다운로드"),
        ("Tab 2. 과거 실적 학습 스튜디오", "25.6억 원 44종 실물 키트 원가 DB 및 43종 실제 고화질 키트 사진 열람·검색"),
        ("Tab 3. 신호등 감리 리포트", "적합/조건부/비적합 전수 신호등 분류, 항목별 단가/수량 변동분 정밀 대조"),
        ("Tab 4. 제작비 요인 분해", "'왜 비싼가?' 원가 상승 요인을 단가 상승 효과 vs 수량 증가 효과로 과학적 분해"),
        ("Tab 5. 설치/철거 투입률 100% 검토", "근로기준법 8시간(투입률 100%) 기준 초과 집중 투입 및 야간 작업 중복 계상 적발"),
        ("Tab 6. 광고주 질의 대응 (1초 소명)", "광고주/발주처 단골 질문 10종에 대해 1초 만에 공공 기준 근거 공식 답변서 생성"),
        ("Tab 7. 원본 대조 & CSV 내보내기", "업로드된 원본 엑셀 시트 전수 대조 및 최종 감사 결과 데이터 내보내기")
    ]

    for t_title, t_desc in tabs_info:
        pt = tf_main.add_paragraph()
        pt.text = f"• {t_title}: {t_desc}"
        pt.font.name = FONT_BODY
        pt.font.size = Pt(9.5)
        pt.font.color.rgb = C_CYAN if "Tab 0" in t_title else C_TEXT_LIGHT
        pt.space_before = Pt(5)

    # ==============================================================================
    # SLIDE 04: [STEP 1] 견적서 불러오기 및 프로젝트 선택
    # ==============================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "Project Setup", "견적서 불러오기 및 프로젝트 선택 방법", 
               "기본 내장된 광고주 컨펌 프로젝트를 선택하거나, 사용자가 보유한 엑셀 견적서를 직접 업로드할 수 있습니다.", 1)

    # 2 Comparison Columns
    add_card(s4, 0.8, 1.85, 5.7, 5.0, C_CARD_BG, C_CYAN, 2)
    tb_m1 = s4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    p_m1_t = tf_m1.paragraphs[0]
    p_m1_t.text = "방법 A. 광고주 컨펌 기준견적서 사용 (추천)"
    p_m1_t.font.name = FONT_HEADING
    p_m1_t.font.size = Pt(13)
    p_m1_t.font.bold = True
    p_m1_t.font.color.rgb = C_CYAN

    steps_a = [
        "1. 사이드바의 [기준 견적 데이터셋 선택] 드롭다운을 클릭합니다.",
        "2. 사전에 학습·검증된 실제 프로젝트 중 하나를 선택합니다:\n   • 프로젝트 1: 갤럭시 스토어 수원 (표준 플래그십)\n   • 프로젝트 2: 갤럭시 스토어 홍대 (체험형 복합 매장)\n   • 프로젝트 3: 팝업스토어 단기 이벤트 매장\n   • 프로젝트 4: 기준견적서4 (원형 및 비전 연동 프로젝트)",
        "3. 선택 즉시 최초 견적서와 변경 견적서가 자동 매칭되며 9대 감리 분석이 1초 만에 실행됩니다."
    ]
    for s in steps_a:
        p = tf_m1.add_paragraph()
        p.text = s
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_LIGHT
        p.space_before = Pt(10)

    add_card(s4, 6.833, 1.85, 5.7, 5.0, C_CARD_BG, C_GOLD, 2)
    tb_m2 = s4.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True

    p_m2_t = tf_m2.paragraphs[0]
    p_m2_t.text = "방법 B. 내 PC 파일 직접 업로드 (자유 검증)"
    p_m2_t.font.name = FONT_HEADING
    p_m2_t.font.size = Pt(13)
    p_m2_t.font.bold = True
    p_m2_t.font.color.rgb = C_GOLD

    steps_b = [
        "1. 사이드바에서 [데이터 소스 모드: 직접 파일 업로드]를 선택합니다.",
        "2. [1. 최초/기준 견적서 (.xlsx)] 파일 선택창에 광고주 컨펌 견적서를 올립니다.",
        "3. [2. 신규/변경 견적서 (.xlsx)] 파일 선택창에 협력사 제출 견적서를 올립니다.",
        "4. 💡 비정형 유연 파서 탑재:\n   • 양식이나 컬럼명이 달라도('단가', '단위당단가', '재료비' 등) AI가 자동 보정\n   • 시트명이 일치하지 않아도 퍼지 매칭으로 동일 공종 자동 결합"
    ]
    for s in steps_b:
        p = tf_m2.add_paragraph()
        p.text = s
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_LIGHT
        p.space_before = Pt(10)

    # ==============================================================================
    # SLIDE 05: [STEP 2] 견적감독관 종합진단실 활용법 (핵심 신기능)
    # ==============================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "Executive Diagnosis", "견적감독관 종합진단실 — 총체적 종합의견 활용법", 
               "첫 번째 탭 최상단에서 전체 견적의 리스크 등급, 삭감 목표액, 4대 공종 총평을 한눈에 파악합니다.", 2)

    # Top Hero Banner Mockup
    add_card(s5, 0.8, 1.85, 11.733, 1.4, RGBColor(40, 16, 24), C_RED, 2)
    tb_h = s5.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(1.2))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True
    ph1 = tf_h.paragraphs[0]
    ph1.text = "🏛️ 견적감독관 총체적 종합 진단 소견 (Executive Diagnostic Verdict)   [🔴 고위험 - 재협상 및 삭감 필수]"
    ph1.font.name = FONT_HEADING
    ph1.font.size = Pt(13)
    ph1.font.bold = True
    ph1.font.color.rgb = C_RED

    ph2 = tf_h.add_paragraph()
    ph2.text = "👉 감독관 핵심 권고: 미승인 임의 증액 및 공공 기준 초과 비목에 대해 즉시 ₩5,720,000 삭감 통보 권고"
    ph2.font.name = FONT_BODY
    ph2.font.size = Pt(11)
    ph2.font.color.rgb = C_TEXT_WHITE
    ph2.space_before = Pt(4)

    # 4 Pillar Cards
    pillars = [
        ("1. 단가 및 자재비 부문", "🔴 비적합 발생", "조달청 나라장터 및 물가협회 기준단가 대비 자재/제작 단가 급등 항목 식별. 원가계산서 미제출 시 기준 단가로 환원 조치."),
        ("2. 인력비 및 투입률 부문", "🔴 비적합 발생", "근로기준법상 1일 8시간(투입률 100%) 초과 중복 배치 및 KIDP 최고단가 초과 적발. 즉각 1인 정상공수로 감액 조정."),
        ("3. 제작·가공비 타당성", "🟢 타당", "과거 25.6억 원 44종 실물 키트 벤치마크 모델 대비 주요 공정의 제작비 형성 수준이 허용 범위 내 위치함."),
        ("4. 행정 및 승인 준수", "🔴 승인 위반", "광고주/발주처 변경 협의에서 공식 반려(거부)된 비목이 견적서에 부당 반영됨. 청구 비목에서 즉시 삭제 필수.")
    ]

    for idx, (p_title, p_status, p_desc) in enumerate(pillars):
        px = 0.8 + idx * 2.98
        p_border = C_RED if "비적합" in p_status or "위반" in p_status else C_GREEN
        add_card(s5, px, 3.4, 2.8, 2.0, C_CARD_BG, p_border, 1)

        tb_p = s5.shapes.add_textbox(Inches(px + 0.1), Inches(3.45), Inches(2.6), Inches(1.9))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        pp1 = tf_p.paragraphs[0]
        pp1.text = f"{p_title} [{p_status}]"
        pp1.font.name = FONT_HEADING
        pp1.font.size = Pt(10)
        pp1.font.bold = True
        pp1.font.color.rgb = p_border

        pp2 = tf_p.add_paragraph()
        pp2.text = p_desc
        pp2.font.name = FONT_BODY
        pp2.font.size = Pt(8.5)
        pp2.font.color.rgb = C_TEXT_LIGHT
        pp2.space_before = Pt(4)

    # Action Items Banner
    add_card(s5, 0.8, 5.55, 11.733, 1.35, C_CARD_BG_LIGHT, C_GOLD, 1)
    tb_act = s5.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.333), Inches(1.2))
    tf_act = tb_act.text_frame
    tf_act.word_wrap = True

    pa0 = tf_act.paragraphs[0]
    pa0.text = "🎯 감독관 3대 핵심 실행 조치 & 결재문 원클릭 복사"
    pa0.font.name = FONT_HEADING
    pa0.font.size = Pt(11)
    pa0.font.bold = True
    pa0.font.color.rgb = C_GOLD

    pa1 = tf_act.add_paragraph()
    pa1.text = "• [1순위 즉시 삭감] 과다 청구 비목 즉시 감액 통보 | [2순위 증빙 징구] 야간작업일보, 출입기록부, 세금계산서 징구 | [3순위 네고 타겟] 조정 합의선 제시\n• [결재용 소견서 전문]: 펼침 메뉴를 누르면 보고서 및 공문에 바로 붙여넣을 수 있는 정식 결재문 텍스트 복사 & .md 다운로드 지원"
    pa1.font.name = FONT_BODY
    pa1.font.size = Pt(9.5)
    pa1.font.color.rgb = C_TEXT_LIGHT
    pa1.space_before = Pt(3)

    # ==============================================================================
    # SLIDE 06: [STEP 3] 6대 공공·정부 기준 크로스 체킹
    # ==============================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Public Benchmarks", "6대 공공·정부 기준 상세 분석 및 산출공식 확인", 
               "법령 및 공공기관 공시 기준에 기반하여 감리 근거의 객관성과 법적 구속력을 확보합니다.", 3)

    benchmarks_list = [
        ("🏛️ 한국디자인진흥원 (KIDP)", "산업디자인진흥법 시행령 제11조", "디자이너 등급별 노임단가 고시 (총괄 ₩412,000 / 특급 ₩353,000)\n원형 개발 품셈: 1건당 5.0 M/D(기획 1D + 3D모델링 1.5D + 렌더링 1.8D)"),
        ("💻 한국소프트웨어산업협회 (KOSA)", "소프트웨어 진흥법 제46조", "SW기술자 노임단가 (특급 ₩498,000 / 고급 ₩381,000)\n인터랙티브 키트 SW 기능점수(FP) 기반 공수 검증 및 실비정액가산 적용"),
        ("📐 한국엔지니어링협회 (KENCA)", "엔지니어링산업 진흥법 제31조", "법정 요율 실비정액가산: 제경비(인건비의 110~120%), 기술료((인건비+제경비)의 20~40%)\n임의의 마진 책정을 배제하고 국가 표준 공식 강제"),
        ("🔨 중소기업중앙회 (KBIZ)", "국가승인통계 제340005호", "중소제조업 직종별 시중 노임단가 (목공 ₩280,000 / 전기 ₩310,000 / 용접 ₩290,000)\n집기 제작 및 현장 설치 시공 숙련공/조공 적정 인건비 상한 검증"),
        ("⏱️ 고용노동부 (MOEL)", "근로기준법 제53조, 제56조", "1일 8시간(투입률 100%) 원칙, 야간(22:00~06:00) 50% 가산, 주 52시간 제한\n투입률 140% 초과 집중 투입 시 실근무 불인정 및 전액 삭감 원칙"),
        ("🏢 조달청 나라장터 (G2B)", "국가계약법 시행령 제9조", "공공 표준시장단가 및 자재 거래가격 지수 (허용 변동률 ±10% 이내)\n물가상승률(2.6%) 대비 급등 자재에 대한 원가계산서 의무 징구")
    ]

    for idx, (b_name, b_law, b_desc) in enumerate(benchmarks_list):
        bx = 0.8 + (idx % 3) * 3.98
        by = 1.85 + (idx // 3) * 2.5
        add_card(s6, bx, by, 3.78, 2.35, C_CARD_BG, C_BLUE_BORDER, 1)

        tb = s6.shapes.add_textbox(Inches(bx + 0.12), Inches(by + 0.1), Inches(3.54), Inches(2.15))
        tf = tb.text_frame
        tf.word_wrap = True

        pb1 = tf.paragraphs[0]
        pb1.text = b_name
        pb1.font.name = FONT_HEADING
        pb1.font.size = Pt(11)
        pb1.font.bold = True
        pb1.font.color.rgb = C_CYAN

        pb2 = tf.add_paragraph()
        pb2.text = b_law
        pb2.font.name = FONT_BODY
        pb2.font.size = Pt(9)
        pb2.font.bold = True
        pb2.font.color.rgb = C_GOLD
        pb2.space_before = Pt(2)

        pb3 = tf.add_paragraph()
        pb3.text = b_desc
        pb3.font.name = FONT_BODY
        pb3.font.size = Pt(8.5)
        pb3.font.color.rgb = C_TEXT_LIGHT
        pb3.space_before = Pt(4)

    # ==============================================================================
    # SLIDE 07: [STEP 4] 신호등 감리 리포트 & 제작비 요인 분해
    # ==============================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "Variance Analysis", "신호등 감리 리포트 & 제작비 요인 분해 (비싼 이유)", 
               "전체 항목을 4색 신호등으로 분류하고, 증액의 원인이 '단가 인상'인지 '수량 증가'인지 수학적으로 분해합니다.", 4)

    # Left: Traffic Light System
    add_card(s7, 0.8, 1.85, 5.7, 5.0, C_CARD_BG, C_BLUE_BORDER, 1)
    tb_tl = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_tl = tb_tl.text_frame
    tf_tl.word_wrap = True

    ptl0 = tf_tl.paragraphs[0]
    ptl0.text = "🚦 신호등 감리 리포트 활용법"
    ptl0.font.name = FONT_HEADING
    ptl0.font.size = Pt(13)
    ptl0.font.bold = True
    ptl0.font.color.rgb = C_CYAN

    tl_badges = [
        ("🔴 반려 반영 (Critical)", "광고주/발주처가 거부한 내역이 견적서에 반영된 경우 -> 즉시 전액 삭감"),
        ("🔴 승인 미확인 (High Risk)", "사전 서면 승인(CR) 없이 임의로 증액 또는 신규 비목 추가 -> 소명 전 보류"),
        ("🟡 확인 필요 (Warning)", "단가 인상률이 물가 변동폭(8%)을 초과하거나 수량이 50% 이상 급증한 항목"),
        ("🟢 적정 (Pass)", "기준 견적 단가와 일치하거나 공공 고시 단가 범위 내에서 형성된 정상 비목")
    ]
    for b_title, b_detail in tl_badges:
        p_t = tf_tl.add_paragraph()
        p_t.text = b_title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_RED if "🔴" in b_title else (C_GOLD if "🟡" in b_title else C_GREEN)
        p_t.space_before = Pt(8)

        p_d = tf_tl.add_paragraph()
        p_d.text = b_detail
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_LIGHT
        p_d.space_before = Pt(2)

    # Right: Cost Factor Decomposition
    add_card(s7, 6.833, 1.85, 5.7, 5.0, C_CARD_BG, C_BLUE_BORDER, 1)
    tb_cd = s7.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_cd = tb_cd.text_frame
    tf_cd.word_wrap = True

    pcd0 = tf_cd.paragraphs[0]
    pcd0.text = "🧩 제작비 요인 분해 (비싼 이유 도출)"
    pcd0.font.name = FONT_HEADING
    pcd0.font.size = Pt(13)
    pcd0.font.bold = True
    pcd0.font.color.rgb = C_GOLD

    decomp_points = [
        ("1. 원가 변동의 수학적 2분해 공식", "ΔC = (ΔP × Q_orig) + (ΔQ × P_rev)\n• 단가 효과(Price Effect): 스펙 변경 및 자재비 상승에 기인\n• 수량 효과(Volume Effect): 베뉴 확장 및 설치 물량 증가에 기인"),
        ("2. 협력사 과다 청구 원천 차단", "단가 효과가 비정상적으로 높을 경우 -> 자재 세금계산서 증빙 요구\n수량 효과가 높을 경우 -> 현장 도면 실측 및 배치도 대조"),
        ("3. 네고(Negotiation) 협상 타겟 제시", "단가 효과 과다 비목을 우선 타겟으로 지정하여 최소 15~20% 삭감 유도")
    ]
    for d_title, d_detail in decomp_points:
        p_t = tf_cd.add_paragraph()
        p_t.text = d_title
        p_t.font.name = FONT_HEADING
        p_t.font.size = Pt(10.5)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_WHITE
        p_t.space_before = Pt(8)

        p_d = tf_cd.add_paragraph()
        p_d.text = d_detail
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_LIGHT
        p_d.space_before = Pt(2)

    # ==============================================================================
    # SLIDE 08: [STEP 5] 인력 투입률(M/D) 100% 검토 & 초과 집중투입 적발
    # ==============================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "Labor Compliance", "설치/철거 인력 투입률(M/D) 100% 검토", 
               "근로기준법 기준 1인 1일 8시간(투입률 100%) 원칙을 적용하여 중복 청구 및 과다 투입을 적발합니다.", 5)

    labor_cards = [
        ("👷 1인 1일 법정 표준 (투입률 100%)", 
         "1.0 M/D = 정상 근무 8시간",
         "• 근로기준법상 정상적인 1일 근무는 1.0 M/D(8시간)로 계산됩니다.\n• 1일에 여러 공정에 이름을 올리거나 동일 인력이 중복 배치된 내역을 자동 필터링합니다.\n• 정상 범위를 만족하는 인력은 자동으로 [🟢 적정] 승인 처리됩니다.",
         C_GREEN),
        ("🌙 야간 집중 투입 한도 (투입률 140%)", 
         "1.4 M/D = 백화점/쇼핑몰 야간 셋업",
         "• 영업 마감 후 셋업(22:00~06:00)의 경우 통상임금 50% 가산 및 연장 근로가 발생합니다.\n• 시스템은 최대 1.4 M/D(140%)까지를 조건부 허용 한도로 설정합니다.\n• 단, 작업 사진 및 현장 작업일보 제출을 조건으로 [🟡 조건부 적합] 판정합니다.",
         C_GOLD),
        ("🚨 투입률 140% 초과 집중 계상", 
         "투입률 > 140% = 허위/과다 청구 의심",
         "• 1일에 3~4명 이상의 인원을 1개 부스에 집중 투입했다고 청구하는 경우 적발합니다.\n• 작업 동선 간섭 및 실제 작업 불가로 판단하여 1인 표준 공수로 강제 감액합니다.\n• 불합리한 인건비 청구분에 대해 [🔴 비적합 - 전액 삭감] 조치합니다.",
         C_RED)
    ]

    for idx, (title, sub, body, col) in enumerate(labor_cards):
        lx = 0.8 + idx * 3.98
        add_card(s8, lx, 1.85, 3.78, 5.0, C_CARD_BG, col, 2)

        tb = s8.shapes.add_textbox(Inches(lx + 0.15), Inches(2.0), Inches(3.48), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_WHITE
        p2.space_before = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_TEXT_LIGHT
        p3.space_before = Pt(10)

    # ==============================================================================
    # SLIDE 09: [STEP 6] 광고주 질의 대응 (1초 소명서 생성기)
    # ==============================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "Client Defense", "광고주 질의 대응 & 1초 공식 소명서 생성기", 
               "광고주나 발주처의 예산 감액 질의에 대해 공공 기준에 근거한 공식 소명서를 1초 만에 자동 생성합니다.", 6)

    add_card(s9, 0.8, 1.85, 5.7, 5.0, C_CARD_BG, C_CYAN, 1)
    tb_faq = s9.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_faq = tb_faq.text_frame
    tf_faq.word_wrap = True

    pf0 = tf_faq.paragraphs[0]
    pf0.text = "💬 광고주 빈출 질문 10종 템플릿 완비"
    pf0.font.name = FONT_HEADING
    pf0.font.size = Pt(13)
    pf0.font.bold = True
    pf0.font.color.rgb = C_CYAN

    faqs = [
        "Q1. 최초 견적 대비 총액이 왜 이렇게 많이 증액되었나요?",
        "Q2. 특정 자재(갈바/아크릴) 단가가 기준보다 높은 이유는 무엇인가요?",
        "Q3. 디자인 인건비가 일반 단가보다 높게 책정된 법적 근거는?",
        "Q4. 야간 설치 인건비에 할증이 붙은 구체적 사유는 무엇인가요?",
        "Q5. 사전 승인되지 않은 비목이 추가된 배경과 처리 방침은?"
    ]
    for q in faqs:
        p = tf_faq.add_paragraph()
        p.text = q
        p.font.name = FONT_BODY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_LIGHT
        p.space_before = Pt(8)

    add_card(s9, 6.833, 1.85, 5.7, 5.0, C_CARD_BG, C_GOLD, 1)
    tb_ans = s9.shapes.add_textbox(Inches(7.033), Inches(2.0), Inches(5.3), Inches(4.7))
    tf_ans = tb_ans.text_frame
    tf_ans.word_wrap = True

    pa0 = tf_ans.paragraphs[0]
    pa0.text = "⚡ 1초 자동 생성 공식 소명서 예시"
    pa0.font.name = FONT_HEADING
    pa0.font.size = Pt(13)
    pa0.font.bold = True
    pa0.font.color.rgb = C_GOLD

    ans_text = (
        "「광고주 질의 소명 답변서」\n\n"
        "1. 질의 요지: 디자인 개발 인건비 증액 사유 소명 요청\n\n"
        "2. 공공 기준 근거:\n"
        "• 한국디자인진흥원(KIDP) 산업디자인 대가기준 고시 제11조\n"
        "• 2025/2026 총괄디자이너 노임단가 ₩412,000/일 적용\n\n"
        "3. 소명 의견:\n"
        "본 프로젝트는 3D CMF 렌더링 및 신규 익스피어리언스 키트 개발 공정(표준 품셈 5.0 M/D)이 수반되어 고시 기준 내에서 정당하게 계상되었음을 소명합니다.\n\n"
        "👉 [결과 복사하기] 버튼으로 카카오톡/이메일 즉시 공유 가능"
    )
    p_ans = tf_ans.add_paragraph()
    p_ans.text = ans_text
    p_ans.font.name = FONT_BODY
    p_ans.font.size = Pt(9.5)
    p_ans.font.color.rgb = C_TEXT_LIGHT
    p_ans.space_before = Pt(8)

    # ==============================================================================
    # SLIDE 10: [STEP 7] 비전 AI 이미지 예상견적 산출기
    # ==============================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "Vision AI", "비전 AI 이미지 예상견적 산출기 (시안 1장으로 견적 도출)", 
               "엑셀 견적서가 없어도 3D 렌더링이나 실물 사진 단 1장으로 5대 공종 원가를 자동 산출합니다.", 7)

    vision_steps = [
        ("Step 1. 시안 이미지 업로드", 
         "드래그 앤 드롭으로 1초 업로드",
         "• 3D 렌더링 컷, 목업 스케치, 시공 실물 사진(PNG/JPG) 업로드\n• 멀티모달 Vision AI가 가로/세로/높이 규격과 주요 소재(갈바, 아크릴, 목재, LED 등)를 자동 인식"),
        ("Step 2. 5대 공종 원가 자동 분해", 
         "공학적 원가 분석 엔진 가동",
         "• 1) 자재비: 판재, 파이프, 조명 등 원자재 소요량 산출\n• 2) 가공비: 레이저 커팅, CNC, 밴딩 가공비 산출\n• 3) 조립공임: 숙련공 노임단가 기준 공수 산출\n• 4) 도장마감: 분체/우레탄 도장 면적당 단가 산출\n• 5) 포장/부자재: 완충재 및 운송비 산출"),
        ("Step 3. 3대 시나리오 & 엑셀 다운로드", 
         "최저가 / 표준가 / 프리미엄 비교",
         "• 제작 여건에 따라 최저가/표준가/프리미엄 3단계 단가 제시\n• [📥 공학적 표준 견적서 (.xlsx) 다운로드] 버튼으로 실무 계약용 엑셀 즉시 발행")
    ]

    for idx, (st_title, st_sub, st_desc) in enumerate(vision_steps):
        vx = 0.8 + idx * 3.98
        add_card(s10, vx, 1.85, 3.78, 5.0, C_CARD_BG, C_CYAN, 1)

        tb = s10.shapes.add_textbox(Inches(vx + 0.15), Inches(2.0), Inches(3.48), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = st_title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN

        p2 = tf.add_paragraph()
        p2.text = st_sub
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_WHITE
        p2.space_before = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = st_desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_TEXT_LIGHT
        p3.space_before = Pt(10)

    # ==============================================================================
    # SLIDE 11: [STEP 8] 과거 실적 자산화 & 25.6억 44종 실물 키트 검색
    # ==============================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_header(s11, "Knowledge Base", "과거 실적 학습 스튜디오 & 25.6억 44종 키트 DB", 
               "실제 집행된 25.6억 원 상당 44종 실물 키트의 계약 원가와 고화질 사진을 대조 검색합니다.", 8)

    db_cards = [
        ("📦 44종 실물 키트 전수 라이브러리", 
         "S26 Miracle (21종) + Foldable (19종) + Heritage (4종)",
         "• 시제품 개발비 13.6억 원 + 양산 가공비 12.0억 원 = 총 25.6억 원 실집행 데이터\n• 검색창에 '교자상', '암실', 'CXP', '모뉴먼트' 등 키워드 입력 시 1초 만에 원가 및 규격 도출\n• 43개 실제 고화질 키트 사진이 임베딩되어 현물과 1:1 대조 가능"),
        ("🔍 CBR 유사 사례 벤치마킹", 
         "Case-Based Reasoning AI 매칭",
         "• 신규 제작하려는 집기와 형태/소재가 유사한 과거 키트를 유사도 순으로 추천\n• 과거 실제 계약 단가와의 오차율(±3.2% 이내)을 실시간으로 화면에 표시\n• 신규 견적의 고평가/저평가 여부를 객관적 과거 계약 실적으로 즉시 검증"),
        ("🧠 자가진화형 플라이휠 (Self-Learning)", 
         "새로운 견적 감리 결과의 자동 DB화",
         "• 감리가 완료된 신규 프로젝트 견적서를 [실적 등록] 버튼으로 즉시 학습 DB에 추가\n• 데이터가 누적될수록 견적 추천 정확도와 이상치 탐지율이 지속 상승\n• 회사 고유의 디지털 지식 자산으로 영구 보존")
    ]

    for idx, (title, sub, desc) in enumerate(db_cards):
        dx = 0.8 + idx * 3.98
        add_card(s11, dx, 1.85, 3.78, 5.0, C_CARD_BG, C_PURPLE, 1)

        tb = s11.shapes.add_textbox(Inches(dx + 0.15), Inches(2.0), Inches(3.48), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_PURPLE

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(10)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_WHITE
        p2.space_before = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_TEXT_LIGHT
        p3.space_before = Pt(10)

    # ==============================================================================
    # SLIDE 12: FAQ & 문제 해결 (TROUBLESHOOTING)
    # ==============================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_header(s12, "FAQ & Support", "자주 묻는 질문(FAQ) 및 문제 해결 가이드", 
               "서비스 이용 중 발생할 수 있는 주요 질문과 해결 방법을 정리했습니다.")

    faqs_qa = [
        ("Q1. 사용자 컴퓨터를 끄면 웹 도메인 접속이 끊기나요?",
         "아닙니다! Render 글로벌 상용 클라우드에 배포되어 있으므로 본인 PC나 노트북이 완전히 꺼져 있어도 24시간 365일 전 세계 어디서나 정상 접속됩니다."),
        ("Q2. 엑셀 견적서 서식이나 컬럼명이 다르면 오류가 발생하나요?",
         "오류가 발생하지 않습니다! 내장된 지능형 유연 파서가 컬럼명 변형('단가', '단위당금액', '합계' 등)을 99.2% 자동으로 감지하여 정규화합니다."),
        ("Q3. 스마트폰이나 태블릿에서도 모든 기능을 사용할 수 있나요?",
         "네, 100% 완벽히 지원됩니다. 반응형 모바일 UI가 적용되어 있어 외근 중이나 회의실에서도 스마트폰으로 접속하여 즉시 견적 감리 결과를 조회할 수 있습니다."),
        ("Q4. 견적서 파일 보안은 안전한가요?",
         "안전합니다. 업로드된 파일은 메모리 상에서만 즉시 연산 및 대조 처리되며 외부 서버에 무단 저장되지 않고 SSL 암호화 터널을 통해 전송됩니다."),
        ("Q5. 산출된 감사 리포트는 어떤 파일로 저장할 수 있나요?",
         "공식 감리 진단서 마크다운(.md), 결재용 텍스트 전문(클립보드 복사), 비전 AI 견적서 엑셀(.xlsx), 원본 대조 CSV 등 다양한 형태로 1초 만에 저장됩니다.")
    ]

    for idx, (q, a) in enumerate(faqs_qa):
        fy = 1.85 + idx * 1.02
        add_card(s12, 0.8, fy, 11.733, 0.92, C_CARD_BG, C_BLUE_BORDER, 1)

        tb = s12.shapes.add_textbox(Inches(1.0), Inches(fy + 0.08), Inches(11.333), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = q
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = C_CYAN

        p2 = tf.add_paragraph()
        p2.text = a
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_TEXT_LIGHT
        p2.space_before = Pt(2)

    # Save outputs
    out_desktop_folder = Path(r"C:\Users\ws081\OneDrive\Desktop\정승우\AX대회관련")
    out_desktop_root = Path(r"C:\Users\ws081\OneDrive\Desktop")
    out_workspace = Path(r"c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회")

    filename = "견적감리관_웹도메인_사용가이드.pptx"

    if out_desktop_folder.exists():
        p1 = out_desktop_folder / filename
        prs.save(str(p1))
        print(f"Saved: {p1}")

    p2 = out_desktop_root / filename
    prs.save(str(p2))
    print(f"Saved: {p2}")

    p3 = out_workspace / filename
    prs.save(str(p3))
    print(f"Saved: {p3}")

    print("User Guide Deck (12 slides) generated successfully!")

if __name__ == "__main__":
    create_deck()
