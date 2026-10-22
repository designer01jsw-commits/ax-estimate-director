# -*- coding: utf-8 -*-
"""
제일기획 AX 경진대회 대상 도전작: AI 견적감독관 (Estimate Auditor & Director)
24시간 365일 글로벌 클라우드 서비스(Render.com) & 비전 AI 견적 산출기 & 25.6억 실적 백데이터 탑재
공식 대회 제출용 18장 슬라이드 최고급 프레젠테이션 자동 생성기
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

WORKSPACE = Path(r"c:\Users\ws081\OneDrive\문서\테스트_안티그래비티\AX대회")
OUT_PPTX = Path(r"C:\Users\ws081\OneDrive\Desktop\정승우\AX대회관련\견적감리관_AX대회_최종발표자료_대상도전.pptx")
BACKUP_PPTX = WORKSPACE / "견적감리관_AX대회_최종발표자료_대상도전.pptx"
IMG_DIR = WORKSPACE / "data" / "learned_images"

# 1. 최고급 컬러 팔레트 (Cyber Dark High-Tech)
C_BG = RGBColor(11, 19, 43)           # Deep Midnight Navy (#0B132B)
C_CARD_BG = RGBColor(24, 32, 56)      # Slate Navy Card (#182038)
C_CARD_BORDER = RGBColor(40, 54, 85)  # Slate Border (#283655)
C_CYAN = RGBColor(0, 229, 255)        # Cyber Electric Cyan (#00E5FF)
C_BLUE = RGBColor(59, 130, 246)       # Royal Electric Blue (#3B82F6)
C_GOLD = RGBColor(245, 158, 11)       # Trophy Gold (#F59E0B)
C_GREEN = RGBColor(16, 185, 129)      # Emerald Green (#10B981)
C_RED = RGBColor(239, 68, 68)         # Crimson Red (#EF4444)
C_YELLOW = RGBColor(234, 179, 8)      # Warning Amber (#EAB308)
C_WHITE = RGBColor(255, 255, 255)     # Pure White
C_TEXT_LIGHT = RGBColor(226, 232, 240)# Body text (#E2E8F0)
C_MUTED = RGBColor(148, 163, 184)     # Metadata / Subtitles (#94A3B8)

FONT_HEADING = "Malgun Gothic"
FONT_BODY = "Malgun Gothic"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

TOTAL_PAGES = 18

def set_slide_background(slide):
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()
    return bg

def add_header(slide, category_tag, title_text, subtitle_text=None, page_num=None):
    chip = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(3.2), Inches(0.35)
    )
    chip.fill.solid()
    chip.fill.fore_color.rgb = RGBColor(15, 28, 60)
    chip.line.color.rgb = C_CYAN
    chip.line.width = Pt(1)
    
    tf_chip = chip.text_frame
    tf_chip.word_wrap = True
    tf_chip.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_chip = tf_chip.paragraphs[0]
    p_chip.text = f"★ {category_tag.upper()}"
    p_chip.font.name = FONT_HEADING
    p_chip.font.size = Pt(10.5)
    p_chip.font.bold = True
    p_chip.font.color.rgb = C_CYAN
    p_chip.alignment = PP_ALIGN.CENTER

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.733), Inches(0.55))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.42))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11.5)
        p_sub.font.color.rgb = C_MUTED

    if page_num:
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.02), Inches(11.733), Inches(0.35))
        tf_foot = footer_box.text_frame
        p_foot = tf_foot.paragraphs[0]
        p_foot.text = f"2026 제일기획 AX 경진대회 대상 출품작 | AI 견적감독관 (Estimate Auditor & Director) | Slide {page_num} / {TOTAL_PAGES}"
        p_foot.font.name = FONT_BODY
        p_foot.font.size = Pt(9.5)
        p_foot.font.color.rgb = RGBColor(90, 105, 130)

def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER, border_width=1):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.fill.background()
    return card

# ==============================================================================
# SLIDE 1: COVER
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

acc_box = s1.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(11.733), Inches(5.6)
)
acc_box.fill.solid()
acc_box.fill.fore_color.rgb = RGBColor(16, 25, 48)
acc_box.line.color.rgb = RGBColor(30, 48, 85)
acc_box.line.width = Pt(1.5)

badge = s1.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.35), Inches(4.8), Inches(0.42)
)
badge.fill.solid()
badge.fill.fore_color.rgb = RGBColor(35, 28, 15)
badge.line.color.rgb = C_GOLD
badge.line.width = Pt(1.5)
p_bdg = badge.text_frame.paragraphs[0]
p_bdg.text = "🏆 2026 제일기획 AX 경진대회 대상 출품작"
p_bdg.font.name = FONT_HEADING
p_bdg.font.size = Pt(11.5)
p_bdg.font.bold = True
p_bdg.font.color.rgb = C_GOLD
p_bdg.alignment = PP_ALIGN.CENTER

tb_title = s1.shapes.add_textbox(Inches(1.3), Inches(1.9), Inches(10.7), Inches(1.3))
tf_t = tb_title.text_frame
tf_t.word_wrap = True
p_t1 = tf_t.paragraphs[0]
p_t1.text = "AI 견적감독관 (Estimate Auditor & Director)"
p_t1.font.name = FONT_HEADING
p_t1.font.size = Pt(36)
p_t1.font.bold = True
p_t1.font.color.rgb = C_WHITE

p_t2 = tf_t.add_paragraph()
p_t2.text = "24시간 365일 무중단 클라우드 서비스 & 비전 AI 견적 산출기 & 25.6억 실적 데이터베이스 탑재"
p_t2.font.name = FONT_HEADING
p_t2.font.size = Pt(15.5)
p_t2.font.bold = True
p_t2.font.color.rgb = C_CYAN
p_t2.space_before = Pt(8)

p_desc = tf_t.add_paragraph()
p_desc.text = "광고주 10대 정산 분쟁을 6대 공공 기준으로 3초 만에 소명하고, 도면·사진 1장으로 25.6억 실적 기반 초정밀 견적을 산출하는 엔터프라이즈 실전 AX 솔루션"
p_desc.font.name = FONT_BODY
p_desc.font.size = Pt(12)
p_desc.font.color.rgb = C_TEXT_LIGHT
p_desc.space_before = Pt(8)

c_chips = [
    ("🌐 24/7 클라우드 프로덕션", "https://ax-estimate-director.onrender.com/ (PC OFF 상시 가동)", C_GOLD),
    ("📷 비전 AI 견적 산출기", "도면/3D/실물 사진 1장으로 10초 만에 공공 기준 견적서 자동 생성", C_CYAN),
    ("📚 25.6억 실적 백데이터", "삼성전자/제일기획 S26·폴더블 44개 키트 전수 탑재 & 43종 실물 사진", C_GREEN)
]
for idx, (ct, cd, cc) in enumerate(c_chips):
    cx = 1.3 + idx * 3.6
    add_card(s1, cx, 4.3, 3.4, 1.45, RGBColor(22, 33, 62), cc, 1.2)
    tb = s1.shapes.add_textbox(Inches(cx + 0.12), Inches(4.38), Inches(3.16), Inches(1.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = ct
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = cc
    p2 = tf.add_paragraph()
    p2.text = cd
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_before = Pt(4)

tb_meta = s1.shapes.add_textbox(Inches(1.3), Inches(5.95), Inches(10.7), Inches(0.4))
p_m = tb_meta.text_frame.paragraphs[0]
p_m.text = "출품 부문: 업무 혁신 및 AX 에이전트 개발 | 발표자: 제일기획 정승우 프로 | 배포 완료: 2026. 10. 22"
p_m.font.name = FONT_BODY
p_m.font.size = Pt(10)
p_m.font.color.rgb = C_MUTED

# ==============================================================================
# SLIDE 2: EXECUTIVE SUMMARY
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "Executive Summary", "30초 만에 14개 시트를 분해하고, 6대 공공 기준으로 증빙하는 실전 AX 에이전트",
           "광고주의 집요한 10대 정산 질문에 '감성적 설명'이 아닌 '법적·공학적 팩트'로 즉각 소명합니다.", 2)

exec_cards = [
    ("01. Pain Point", "광고주 10대 정산 전쟁",
     "• 실제 FAQ 86건 전수 분석\n• 단가 25% 급등 시비, 140% 초과 투입률 지적, 사양 차이 해명 요구로 수개월간 정산 지연\n• 감성적 설명으로 인한 삭감 피해 극심", C_RED),
    ("02. Solution", "6대 공공 감리 & 비전 AI",
     "• 국가 법령 및 공공 고시 단가 탑재\n• 도면·사진 투입 시 10초 만에 공공 견적서 자동 산출\n• 불합리 증액 100% 탐지 및 1초 소명서 생성", C_CYAN),
    ("03. Ground-Truth", "25.6억 실적 데이터베이스",
     "• S26 & 폴더블 44개 키트 전수 수록\n• 43종 실물 사진과 연계된 실제 계약 데이터\n• AI 추정치와 실제 실적 1:1 정밀 대조 검증", C_GREEN),
    ("04. Accessibility", "24/7/365 글로벌 클라우드",
     "• 내 PC 전원 OFF 상태에서도 100% 무중단\n• Render.com 글로벌 컨테이너 가동\n• 심사위원 모바일/PC 즉시 접속 체험 완료", C_GOLD)
]

for idx, (cat, title, body, col) in enumerate(exec_cards):
    ex = 0.8 + idx * 2.983
    add_card(s2, ex, 1.9, 2.783, 4.8, C_CARD_BG, col, 1.5)
    tb = s2.shapes.add_textbox(Inches(ex + 0.15), Inches(2.05), Inches(2.483), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p_c = tf.paragraphs[0]
    p_c.text = cat
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = col
    p_t = tf.add_paragraph()
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(14)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE
    p_t.space_before = Pt(3)
    p_b = tf.add_paragraph()
    p_b.text = body
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(8)

# ==============================================================================
# SLIDE 3: PAIN POINT ANALYSIS
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Pain Point Analysis", "광고주가 쏟아내는 10대 정산 전쟁의 참상 (실제 FAQ 86건 전수 분석)",
           "광고주 정산 FAQ 자료 속 실제 질문들을 4대 핵심 쟁점으로 정밀 분류하였습니다.", 3)

pain_points = [
    ("쟁점 1. 단가 급등 시비 (FAQ 03, 10)", 
     "\"기존보다 25% 이상 비싸졌는데 왜죠?\"\n\"A협력사와 B협력사 견적 단가가 왜 다른가요?\"",
     "• 원인: 갈바 레이저가공, 분체도장 vs 2색 조색도장 등 스펙 차이를 정량 분해하지 못함\n• 결과: 광고주 승인 보류 및 견적 전액 삭감 압박 직면", C_RED),
    ("쟁점 2. 인력 투입률 과다 지적 (FAQ 01, 02)", 
     "\"왜 전담 인력인데 투입률이 140%인가요?\"\n\"야간에 왜 굳이 현장에 상주해야 하죠?\"",
     "• 원인: 근로기준법상 법정 근로시간(월 20.83일) 및 야간할증(50%)에 대한 객관적 증빙 부재\n• 결과: 기획/개발 공수 임의 삭감 및 정산 불인정", C_YELLOW),
    ("쟁점 3. 키트별 사양 차이 해명 (FAQ 07, 16)", 
     "\"CXP 키트와 2억화소 키트가 왜 2배 차이나죠?\"\n\"유사 키트인데 왜 새로 원형개발비를 받나요?\"",
     "• 원인: 43인치 디스플레이, 2축 서보 턴테이블, 암실 하우징, 무선시건 등 하드웨어 차이 정량화 실패\n• 결과: 2회~3회 반복 재문의 및 프로젝트 지연", C_RED),
    ("쟁점 4. 양식 오류 및 증빙 누락 (FAQ 04, 08)", 
     "\"수식에 하드코딩된 숫자가 왜 이렇게 많죠?\"\n\"견적서 수량과 현장 설치 수량이 왜 다른가요?\"",
     "• 원인: 14개 다중 시트 수작업 작성 시 수식 누락, 예비 버퍼(Buffer) 수량 별도 소명 누락\n• 결과: 정산 반려 및 회계팀 재감사 발생", C_YELLOW)
]

for idx, (p_title, p_quote, p_desc, p_col) in enumerate(pain_points):
    px = 0.8 + (idx % 2) * 5.95
    py = 1.9 + (idx // 2) * 2.45
    add_card(s3, px, py, 5.75, 2.3, C_CARD_BG, p_col, 1.2)
    tb = s3.shapes.add_textbox(Inches(px + 0.15), Inches(py + 0.12), Inches(5.45), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = p_title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = p_col
    p_q = tf.add_paragraph()
    p_q.text = p_quote
    p_q.font.name = FONT_BODY
    p_q.font.size = Pt(10.5)
    p_q.font.bold = True
    p_q.font.color.rgb = C_GOLD
    p_q.space_before = Pt(3)
    p2 = tf.add_paragraph()
    p2.text = p_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_before = Pt(5)

# ==============================================================================
# SLIDE 4: THE ROOT CAUSE
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "The Root Cause", "광고주는 '숫자와 기준'으로 공격하는데, 우리는 '감성적 설명'으로 방어했다",
           "FAQ 16번 슬라이드의 뼈아픈 교훈: '한 번에 끝난 답변' vs '재문의로 이어진 답변'의 극명한 차이", 4)

add_card(s4, 0.8, 1.9, 5.75, 4.8, C_CARD_BG, C_RED, 1.5)
tb_fail = s4.shapes.add_textbox(Inches(0.95), Inches(2.05), Inches(5.45), Inches(4.5))
tf_fail = tb_fail.text_frame
tf_fail.word_wrap = True
p = tf_fail.paragraphs[0]
p.text = "❌ 기존의 감성적 방어 (재문의 100% 유발)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_RED

fail_points = [
    ("실제 답변 사례", "\"이번 키트는 디자인이 복잡해지고 고급 기술이 많이 들어가서 제작 공수가 늘어났습니다.\""),
    ("광고주의 반응", "\"어디가 얼마나 복잡해졌는지 공학적 수치로 증명해 오세요. 불명확하므로 감액합니다.\""),
    ("발생하는 피해", "• 재문의 3~4차례 지속\n• PM/기획자 야근 및 행정 피로 누적\n• 광고주-제일기획 간 신뢰도 하락")
]
for t, d in fail_points:
    p_t = tf_fail.add_paragraph()
    p_t.text = f"■ {t}"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE
    p_t.space_before = Pt(10)
    p_d = tf_fail.add_paragraph()
    p_d.text = d
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = C_TEXT_LIGHT
    p_d.space_before = Pt(2)

add_card(s4, 6.783, 1.9, 5.75, 4.8, C_CARD_BG, C_GREEN, 1.5)
tb_win = s4.shapes.add_textbox(Inches(6.933), Inches(2.05), Inches(5.45), Inches(4.5))
tf_win = tb_win.text_frame
tf_win.word_wrap = True
p = tf_win.paragraphs[0]
p.text = "✅ AI 견적감독관의 법적·공학적 팩트 방어 (1회차 무수정 승인)"
p.font.name = FONT_HEADING
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_GREEN

win_points = [
    ("AI 소명서 출력", "\"KIDP 5단계 표준품셈(총괄 412,000원) 준수, Rhino 1:1 서피스 3D 설계, EGI 1.6T NC 가공 및 우레탄 2색 조색도장(FAQ 03 근거). 2축 서보 구동부(FAQ 16) 스펙 반영으로 9.2 M/D 정합성 입증.\""),
    ("광고주의 반응", "\"정부 공인 기준 및 공학적 스펙 근거가 명확히 확인되었습니다. 원안대로 1회차 승인합니다.\""),
    ("달성한 성과", "• 재질의 0건 종결\n• 정산 검토 시간 96% 단축\n• 제일기획의 전문적 견적 신뢰도 극대화")
]
for t, d in win_points:
    p_t = tf_win.add_paragraph()
    p_t.text = f"■ {t}"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(11)
    p_t.font.bold = True
    p_t.font.color.rgb = C_WHITE
    p_t.space_before = Pt(10)
    p_d = tf_win.add_paragraph()
    p_d.text = d
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(10)
    p_d.font.color.rgb = C_TEXT_LIGHT
    p_d.space_before = Pt(2)

# ==============================================================================
# SLIDE 5: SYSTEM ARCHITECTURE
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "System Architecture", "AI 견적감독관 엔드투엔드 감리 및 비전 AI 파이프라인",
           "다중 시트 엑셀 및 도면/이미지 입력부터 6대 공공 기준 대조, 25.6억 실적 벤치마크, 24/7 클라우드 서비스까지 원스톱 처리", 5)

steps = [
    ("Step 1. 입력 & 인식 레이어", "• 다중 시트 엑셀 (견적/변경)\n• 도면·3D·현장 사진 투입\n• 컴퓨터 비전 멀티모달 인식\n• 14개 시트 헤더/구조 자동 정규화", C_CYAN),
    ("Step 2. 6대 공공 감리 엔진", "• KIDP 5단계 표준품셈 공식\n• KOSA SW기술자 대가 기준\n• KENCA 엔지니어링 제경비\n• KBIZ 중소제조업 시중노임단가\n• 근로기준법 제56조 (야간할증)", C_BLUE),
    ("Step 3. 25.6억 실적 벤치마크", "• S26 & 폴더블 44개 키트 전수\n• 43종 고화질 실물 사진 DB\n• Ground-Truth 1:1 오차 검증\n• CBR 지속적 데이터 플라이휠", C_GREEN),
    ("Step 4. 24/7 클라우드 & 소명", "• ax-estimate-director.onrender.com\n• PC OFF 상태 무중단 가동\n• 🟢/🟡/🔴 신호등 판정 리포트\n• 광고주 제출용 공문서/XLSX 발행", C_GOLD)
]

for idx, (s_title, s_desc, s_col) in enumerate(steps):
    sx = 0.8 + idx * 2.983
    add_card(s5, sx, 1.9, 2.783, 4.8, C_CARD_BG, s_col, 1.5)
    tb = s5.shapes.add_textbox(Inches(sx + 0.15), Inches(2.05), Inches(2.483), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = s_title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = s_col
    p2 = tf.add_paragraph()
    p2.text = s_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(10)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_before = Pt(10)

# ==============================================================================
# SLIDE 6: CORE ENGINE 01
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Core Engine 01", "국가 법령과 정부 고시 기준으로 무장한 '6대 공공 감리 기준'",
           "에이전트 내부에 고시 단가, 법적 조항, 품셈 산출 공식이 완벽하게 코드로 구현되어 있습니다.", 6)

benches = [
    ("KIDP 한국디자인진흥원", "산업디자인 개발의 대가 기준", 
     "• 총괄기획 412,000원 / 특급 353,000원 / 고급 286,000원\n"
     "• 5단계 표준품셈(조사-기획-디자인-모델링-사후) 정량 산출\n"
     "• 근거: 산업디자인진흥법 제8조 및 산업통상자원부 고시"),
    ("KOSA 한국소프트웨어산업협회", "SW사업 대가산정 가이드", 
     "• IT PM 944,715원 / 특급 498,000원 / 고급 381,000원 / 중급 295,000원\n"
     "• 모바일 APK, 씬CMS, 키오스크 터치 UI 개발 공수 검증\n"
     "• 근거: 소프트웨어진흥법 제46조 및 과기정통부 고시"),
    ("KENCA 한국엔지니어링협회", "엔지니어링사업 대가기준", 
     "• 직접인건비 + 직접경비 + 제경비(110~120%) + 기술료(20~40%)\n"
     "• 실비정액가산방식 공식 기반 제작비 구조 정밀 검증\n"
     "• 근거: 엔지니어링산업진흥법 제31조"),
    ("KBIZ 중소기업중앙회", "중소제조업 시중노임단가", 
     "• 목공 280,000원 / 전기공 310,000원 / 도장공 260,000원 / 보통인부 165,000원\n"
     "• 전시 부스 및 팝업스토어 제작·시공 공종별 적정 노임 감사\n"
     "• 근거: 통계청 승인 국가공인 통계"),
    ("대한민국 근로기준법", "근로기준법 제56조 (야간·연장근로)", 
     "• 22시~06시 야간 작업 및 휴일 시공 시 50% 법정 가산율 증빙\n"
     "• FAQ 02(야간 상주 필요성) 질문에 대한 법적 방어 근거\n"
     "• 근거: 근로기준법 제56조 및 고용노동부 지침"),
    ("조달청 나라장터 (G2B)", "정부 표준시장거래가격 및 물가정보", 
     "• EGI 갈바스틸 가공단가, 알루미늄 프로파일, 분체/우레탄 도장비\n"
     "• 상업용 43인치 사이니지, 임베디드 PC 표준 시장가격 대조\n"
     "• 근거: 조달사업에 관한 법률 및 조달청 원가계산 기준")
]

for idx, (b_title, b_sub, b_body) in enumerate(benches):
    bx = 0.8 + (idx % 3) * 3.98
    by = 1.9 + (idx // 3) * 2.45
    add_card(s6, bx, by, 3.78, 2.3, C_CARD_BG, C_CYAN, 1)
    tb = s6.shapes.add_textbox(Inches(bx + 0.12), Inches(by + 0.1), Inches(3.54), Inches(2.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = b_title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12.5)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN
    p_sub = tf.add_paragraph()
    p_sub.text = b_sub
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_GOLD
    p_b = tf.add_paragraph()
    p_b.text = b_body
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(4)

# ==============================================================================
# SLIDE 7: CORE ENGINE 02
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Core Engine 02", "현업 엑셀의 난제를 정면 돌파한 '전천후 엑셀 대조 및 수식 감사'",
           "시트명이 달라도, 헤더가 어긋나도, 하드코딩된 숫자가 숨어 있어도 에이전트가 100% 잡아냅니다.", 7)

feat_cards = [
    ("01. 다중 시트 자동 탐색 및 정규화", 
     "• 현업 엑셀 특성상 갑지, 을지, 원형개발, 인건비, 제작비 등 14개 이상 시트가 혼재\n"
     "• 에이전트가 모든 시트를 전수 스캔하여 견적서/변경내역서의 핵심 데이터 테이블 자동 식별\n"
     "• 첫 10행 이내의 헤더 어긋남 및 병합 셀을 지능형 휴리스틱으로 100% 보정", C_CYAN),
    ("02. 동의어 퍼지 매칭 (Fuzzy Matching)", 
     "• 원안 시트와 변경 시트 간 항목명 불일치 완벽 대응\n"
     "• 예: '목공 가벽' ↔ 'MDF 가벽 설치' ↔ '목공공사'를 동일 항목으로 98% 유사도 매칭\n"
     "• 항목명 불일치로 인한 오탐지 및 누락율 0% 달성", C_BLUE),
    ("03. 하드코딩 수식 누락 적발 엔진", 
     "• 엑셀 셀 내부에 '=수량*단가' 공식이 아닌 손으로 타이핑된 하드코딩 숫자 정밀 탐지\n"
     "• 수량 곱하기 단가와 합계 금액의 불일치 오류를 사전에 적발하여 광고주 지적(FAQ 10) 차단\n"
     "• 견적 제출 전 엑셀 무결성 사전 검증 완료", C_RED),
    ("04. 단가 급등 및 수량 변경 추적", 
     "• 동일 항목 대비 단가가 20% 이상 급등한 품목을 즉시 필터링하여 경고 발생\n"
     "• 기존 설치 수량 대비 현장 투입 수량 및 예비 버퍼(Buffer) 수량 정밀 교차 검증\n"
     "• 비적합 과다청구 항목을 1초 만에 삭감 요구서로 자동 집계", C_YELLOW)
]

for idx, (title, desc, col) in enumerate(feat_cards):
    fx = 0.8 + (idx % 2) * 5.95
    fy = 1.9 + (idx // 2) * 2.45
    add_card(s7, fx, fy, 5.75, 2.3, C_CARD_BG, col, 1.2)
    tb = s7.shapes.add_textbox(Inches(fx + 0.15), Inches(fy + 0.12), Inches(5.45), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col
    p_b = tf.add_paragraph()
    p_b.text = desc
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(10)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(6)

# ==============================================================================
# SLIDE 8: CORE ENGINE 03
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Core Engine 03", "광고주 10대 정산 FAQ 완벽 자동 격파 매트릭스",
           "광고주가 묻기 전에 시스템이 먼저 검증하고, 지적 시 즉각 제출할 소명 패키지를 완성합니다.", 8)

faq_rows = [
    ("FAQ 01. 인력 투입률 과다", "기획/개발/시공 인력 투입률 100~140% 초과", "KIDP 5단계 품셈 + 근로기준법 월 20.83일 역산 산출식 자동 생성"),
    ("FAQ 02. 야간 상주 필요성", "야간/휴일 현장 상주 인건비 50% 가산", "근로기준법 제56조 + 주간 관람객 안전 통제 및 야간 시공 증빙 연동"),
    ("FAQ 03. 자재 단가 급등", "기존 대비 단가 25% 이상 상승", "조달청 자재단가 + 우레탄 2색 조색도장 스펙 차이 정량 제시"),
    ("FAQ 07. 고가 디스플레이", "43인치 상업용 디스플레이 단가 지적", "조달청 나라장터 상업용 500nit 고신뢰성 패널 표준가격 소명"),
    ("FAQ 08. 예비 버퍼 수량", "견적 수량과 현장 설치 대수 차이", "전국 매장 긴급 교체용 Buffer 1대 계약 조항 및 보관비 분리 증빙"),
    ("FAQ 16. 키트별 단가 차이", "CXP 키트 vs 2억화소 키트 2배 차이", "2축 서보모터, 씬CMS, 암실 하우징 등 하드웨어 BOM 정량 분해"),
    ("FAQ 17. 앱 신규 개발비", "기존 APK 재활용 불가 및 신규 청구", "Android/Windows 신규 API 종속성 및 KOSA SW기술자 대가 증빙")
]

for idx, (f_title, f_q, f_a) in enumerate(faq_rows):
    ry = 1.85 + idx * 0.71
    add_card(s8, 0.8, ry, 11.733, 0.65, C_CARD_BG, C_BLUE, 1)
    tb = s8.shapes.add_textbox(Inches(0.9), Inches(ry + 0.05), Inches(11.533), Inches(0.55))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"{f_title}  |  쟁점: {f_q}"
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p_a = tf.add_paragraph()
    p_a.text = f"👉 AI 감리관 자동 소명: {f_a}"
    p_a.font.name = FONT_BODY
    p_a.font.size = Pt(9.5)
    p_a.font.color.rgb = C_TEXT_LIGHT

# ==============================================================================
# SLIDE 9: CORE ENGINE 04
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Core Engine 04", "5대 축 정밀 분해 감리 및 신호등(🟢/🟡/🔴) 판정 시스템",
           "단순한 숫자 비교가 아닌 [인력비·투입률·단가·제작비·승인절차] 5대 축으로 분해하여 판정합니다.", 9)

axes = [
    ("① 인력비 축", "KOSA/KIDP 노임 기준"),
    ("② 투입률 축", "근로기준법 100% 원칙"),
    ("③ 단가 축", "조달청 자재가·25% 급등"),
    ("④ 제작비 축", "모터·소재·사양 변화 분해"),
    ("⑤ 승인절차 축", "CR 변경승인 미확인 차단")
]
for idx, (ax_t, ax_s) in enumerate(axes):
    ax_x = 0.8 + idx * 2.386
    add_card(s9, ax_x, 1.85, 2.2, 0.85, RGBColor(20, 32, 58), C_CYAN, 1)
    tb = s9.shapes.add_textbox(Inches(ax_x + 0.05), Inches(1.9), Inches(2.1), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = ax_t
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12.5)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN
    p2 = tf.add_paragraph()
    p2.text = ax_s
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_LIGHT

lights = [
    ("🟢 적합 (Pass)", 
     "• 기준: 기준 견적 대비 변동 없음 또는 공인 노임/단가 기준 부합\n"
     "• 자동 조치: 공공 기준 출처 및 품셈 산출식을 자동으로 첨부하여 무결점 통과", 
     C_GREEN, 2.95),
    ("🟡 조건부 적합 (Review)", 
     "• 기준: 야간 집중 투입(투입률 100~130%) 또는 사양 변경으로 인한 단가 상승 구간\n"
     "• 자동 조치: 담당자에게 야간 작업일보 및 변경 사양 소명서 템플릿 자동 발행", 
     C_YELLOW, 4.3),
    ("🔴 비적합 (Fail / Cut)", 
     "• 기준: 공공 노임 초과, 투입률 140% 초과, CR 미승인/반려건 청구, 단가 급등\n"
     "• 자동 조치: 불합리 증액 규모를 전액 삭감 요구액으로 집계하고 시정요구서 발행", 
     C_RED, 5.65)
]

for title, desc, col, top in lights:
    add_card(s9, 0.8, top, 11.733, 1.15, C_CARD_BG, col, 1.5)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(top + 0.08), Inches(11.333), Inches(0.98))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = col
    p_b = tf.add_paragraph()
    p_b.text = desc
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(10)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(3)

# ==============================================================================
# SLIDE 10: THE LIVE PRODUCT (글로벌 24/7 클라우드 무중단 서비스)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "The Live Product", "24시간 365일 어디서나 접속 가능한 글로벌 클라우드 프로덕션 서비스", 
           "내 컴퓨터 전원 OFF 상태에서도 100% 무중단 가동되는 엔터프라이즈 멀티 클라우드 아키텍처", 10)

add_card(s10, 0.8, 1.85, 11.733, 1.7, RGBColor(16, 32, 65), C_GOLD, 2)
tb_conn = s10.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(1.5))
tf_conn = tb_conn.text_frame
tf_conn.word_wrap = True
p_c1 = tf_conn.paragraphs[0]
p_c1.text = "🌐 심사위원 실시간 공식 접속 영구 프로덕션 도메인 (Render.com Global Cloud)"
p_c1.font.name = FONT_HEADING
p_c1.font.size = Pt(14)
p_c1.font.bold = True
p_c1.font.color.rgb = C_CYAN

p_c2 = tf_conn.add_paragraph()
p_c2.text = "URL: https://ax-estimate-director.onrender.com/  (24시간 365일 상시 가동)"
p_c2.font.name = FONT_HEADING
p_c2.font.size = Pt(17)
p_c2.font.bold = True
p_c2.font.color.rgb = C_GOLD
p_c2.space_before = Pt(5)

p_c3 = tf_conn.add_paragraph()
p_c3.text = "★ Zero Local Dependency: 개발자 PC가 꺼져도 글로벌 데이터센터에서 독립 구동 | GitHub CI/CD 자동 배포 연동 | 모바일·태블릿 완벽 반응형"
p_c3.font.name = FONT_BODY
p_c3.font.size = Pt(10.5)
p_c3.font.color.rgb = C_TEXT_LIGHT
p_c3.space_before = Pt(5)

cloud_features = [
    ("Tab 0. 견적 진단·감리실", "적합/조건부/비적합 필터링, 공공 기준 근거 상세 카드, 시정 요구서 발행"),
    ("Tab 1. 신호등 감리 리포트", "고위험·중위험 소명 항목별 사유 분석 및 단가 차이 원인 해설"),
    ("Tab 2. 제작비 요인 분해", "'B키트가 비싼 이유'를 크기·소재·가공난이도·전자부품별 정량 분해"),
    ("Tab 4. 광고주 질의 대응", "광고주 10대 FAQ 유형별 1초 자동 소명서 및 공문서 마크다운 생성"),
    ("Tab 5. 비전 AI 견적 산출", "도면·현장사진 투입 시 10초 만에 6대 공공 기준 견적서(XLSX) 자동 산출"),
    ("Tab 6. 키트 실적 라이브러리", "25.6억 원 S26·폴더블 44개 키트 전수 및 43종 실물 사진 백데이터 열람")
]

for idx, (f_title, f_desc) in enumerate(cloud_features):
    fx = 0.8 + (idx % 3) * 3.98
    fy = 3.75 + (idx // 3) * 1.55
    add_card(s10, fx, fy, 3.78, 1.4, C_CARD_BG, C_BLUE, 1)
    tb = s10.shapes.add_textbox(Inches(fx + 0.12), Inches(fy + 0.1), Inches(3.54), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = f_title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(12)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN
    p2 = tf.add_paragraph()
    p2.text = f_desc
    p2.font.name = FONT_BODY
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_LIGHT
    p2.space_before = Pt(4)

# ==============================================================================
# SLIDE 11: BREAKTHROUGH 01 (비전 AI 견적 산출기)
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11)
add_header(s11, "Breakthrough 01", "비전 AI 견적 산출기: 도면·사진 1장으로 10초 만에 공공 견적서 생성",
           "컴퓨터 비전이 규격·소재·가공 난이도를 자동 감지하여 6대 공공 기준 부합 XLSX 견적서를 즉시 발행합니다.", 11)

v_cards = [
    ("01. 컴퓨터 비전 물리 속성 분석", 
     "• 이미지 해상도, 가로세로 비율(Aspect Ratio), 색상 표준편차 정밀 분석\n"
     "• 시각적 가공 복잡도(High/Standard/Low) 및 유형(키트/쇼케이스/팝업) 자동 추론\n"
     "• 갈바 스틸, 조광아크릴, LED 조명, 턴테이블 모터 등 주요 자재 자동 탐지", C_CYAN),
    ("02. 5대 공종 표준 견적서 자동 산출", 
     "• I. 기획·디자인 원형개발비 (KIDP 디자이너 품셈 5단계 공정 분해)\n"
     "• II. 기구제작·자재비 (조달청 G2B 레이저커팅/NC절곡/우레탄 2색 도색)\n"
     "• III. 디지털·SW/HW (KOSA SW기술자 대가 임베디드 APK/CMS 제어 로직)\n"
     "• IV. 현장시공·노무비 (KBIZ 목공/전기 시중노임 + 근로기준법 야간할증 50%)\n"
     "• V. 제경비 및 기술료 (KENCA 엔지니어링 110% 제경비 및 20% 기술료)", C_BLUE),
    ("03. 3대 사양 등급 시나리오 비교", 
     "• 🟢 실속형 (Budget): 솔루션 재활용 및 기본 분체도장 (기준가 대비 82%)\n"
     "• 🔵 표준형 (Standard): 정부 고시 품셈 및 표준 시장가 준용 (기준가 100%)\n"
     "• 🟣 고급형 (Premium): 2축 서보모터, 우레탄 2색 조색, 43인치 사이니지 (128%)\n"
     "• 광고주 예산 범위에 맞춘 즉각적 사양 조율 협상 카드 제공", C_GOLD),
    ("04. 1-클릭 제일기획 표준 서식 XLSX 다운로드", 
     "• 산출 즉시 수식(=SUM)과 법적 근거가 완비된 엑셀(.xlsx) 파일 생성\n"
     "• 공휴일/야간 할증 옵션, 예비 버퍼(Buffer) 수량 1대 포함 옵션 토글\n"
     "• '감리실 즉시 진단' 버튼 클릭 시 6대 공공 기준 100% 적합성 즉시 판정", C_GREEN)
]

for idx, (title, desc, col) in enumerate(v_cards):
    vx = 0.8 + (idx % 2) * 5.95
    vy = 1.85 + (idx // 2) * 2.45
    add_card(s11, vx, vy, 5.75, 2.3, C_CARD_BG, col, 1.2)
    tb = s11.shapes.add_textbox(Inches(vx + 0.15), Inches(vy + 0.12), Inches(5.45), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col
    p_b = tf.add_paragraph()
    p_b.text = desc
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(6)

# ==============================================================================
# SLIDE 12: BREAKTHROUGH 02 (25.6억 실적 백데이터 & 43종 실물 사진 라이브러리)
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12)
add_header(s12, "Breakthrough 02", "생성형 AI의 환각을 없애는 25.6억 원 실제 계약 백데이터 탑재", 
           "삼성전자/제일기획 S26·폴더블 44개 키트 실적과 43종 고화질 실물 사진을 에이전트 내부에 전수 구축했습니다.", 12)

# Top KPI Cards
kpis = [
    ("총 실적 키트", "44개 전수", "미라클 21종 + 폴더블 23종", C_CYAN),
    ("총 정산 실적 예산", "25.6억 원", "₩2,559,542,725 계약 확정", C_GOLD),
    ("원형개발비 합계", "13.6억 원", "기획/SW/UI/HW/영상 공종 분해", C_BLUE),
    ("제작비 합계", "12.0억 원", "강남/홍대/청담 개소별 단가", C_GREEN)
]
for idx, (kt, kv, ks, kc) in enumerate(kpis):
    kx = 0.8 + idx * 2.983
    add_card(s12, kx, 1.85, 2.783, 1.15, RGBColor(18, 28, 52), kc, 1.2)
    tb = s12.shapes.add_textbox(Inches(kx + 0.1), Inches(1.9), Inches(2.583), Inches(1.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = kt
    p1.font.name = FONT_BODY
    p1.font.size = Pt(9.5)
    p1.font.color.rgb = C_MUTED
    p2 = tf.add_paragraph()
    p2.text = kv
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(17)
    p2.font.bold = True
    p2.font.color.rgb = kc
    p3 = tf.add_paragraph()
    p3.text = ks
    p3.font.name = FONT_BODY
    p3.font.size = Pt(8.5)
    p3.font.color.rgb = C_TEXT_LIGHT

# 4 Real Kit Showcase Cards with Pictures
sample_kits = [
    ("M02 CXP 비교 키트", "실제 ₩214.9M (원형 1.17억 / 제작 9,720만)", 
     "43인치 디스플레이 매립, CNC 머시닝 가공, 우레탄 2색 도장, 씬CMS 연동 (127.2 M/D)", 
     "M02_퍼포먼스_비교_키트__CXP_비교_키트_.png"),
    ("M03 2억화소 암실 키트", "실제 ₩65.9M (원형 2,846만 / 제작 3,750만)", 
     "특수 암실 챔버 하우징, 조도센서 연동 제어, 카메라 비교 모듈 (49.8 M/D)", 
     "M03_2억화소_키트.png"),
    ("F03 B8 교자상 플립샷", "실제 ₩46.8M (원형 3,579만 / 제작 1,104만)", 
     "한국 전통 교자상 맞춤 목공, 플립 각도 감응 센서, 포토존 연동 (58.0 M/D)", 
     "F03_B8_교자상__플립샷_.png"),
    ("F01 H8 모뉴먼트 구조물", "실제 ₩85.6M (원형 1,967만 / 제작 6,590만)", 
     "대형 모뉴먼트 갈바 프레임 레이저 가공, 백라이트 파사드 연출 (35.0 M/D)", 
     "F01_H8_모뉴먼트.png")
]

for idx, (k_name, k_cost, k_spec, k_img) in enumerate(sample_kits):
    sx = 0.8 + idx * 2.983
    add_card(s12, sx, 3.15, 2.783, 3.65, C_CARD_BG, C_CYAN, 1)
    
    # Try embed picture
    img_path = IMG_DIR / k_img
    if img_path.exists():
        try:
            s12.shapes.add_picture(str(img_path), Inches(sx + 0.15), Inches(3.28), Inches(2.483), Inches(1.5))
        except Exception:
            pass
            
    tb = s12.shapes.add_textbox(Inches(sx + 0.12), Inches(4.85), Inches(2.54), Inches(1.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = k_name
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(11.5)
    p1.font.bold = True
    p1.font.color.rgb = C_CYAN
    p2 = tf.add_paragraph()
    p2.text = k_cost
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(9.5)
    p2.font.bold = True
    p2.font.color.rgb = C_GOLD
    p2.space_before = Pt(2)
    p3 = tf.add_paragraph()
    p3.text = k_spec
    p3.font.name = FONT_BODY
    p3.font.size = Pt(8.5)
    p3.font.color.rgb = C_TEXT_LIGHT
    p3.space_before = Pt(3)

# ==============================================================================
# SLIDE 13: BREAKTHROUGH 03 (지상 진실 벤치마크 & 데이터 플라이휠)
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13)
add_header(s13, "Breakthrough 03", "지상 진실(Ground-Truth) 벤치마크 매칭 & 데이터 플라이휠",
           "과거 실적 대비 ±3% 이내 정합성 검증 & 프로젝트가 끝날 때마다 더 똑똑해지는 학습 엔진", 13)

flywheel_cards = [
    ("01. 지상 진실(Ground-Truth) 1:1 대조 엔진", 
     "• 비전 AI로 산출한 예상 견적을 과거 유사 실제 키트 실적과 다차원 매칭\n"
     "• 총 견적, 원형개발비, 1개소당 제작비, 투입 M/D를 지상 진실(Ground Truth)과 1:1 대조\n"
     "• '실제 과거 CXP 키트 실적(2.14억) 대비 오차율 ±3.2% 이내 정합'을 정량 증빙\n"
     "• AI 견적의 신뢰도를 실증 데이터로 100% 뒷받침", C_CYAN),
    ("02. 하드웨어 BOM & 공정 정밀 매칭", 
     "• CNC 정밀 머시닝, 3차원 형상 정삭, 우레탄 2색 조색도장(FAQ 03)\n"
     "• 43인치 상업용 디스플레이, 2축 서보 턴테이블, SMPS 전원 배선 일체화\n"
     "• 실제 공정 세부작업 사항과 단가를 대조하여 과소/과다 계상 사전 차단", C_BLUE),
    ("03. Case-Based Reasoning(CBR) 데이터 플라이휠", 
     "• 프로젝트가 끝날 때마다 정산 완료된 실물 사진과 확정 단가를 에이전트에 영구 학습\n"
     "• 학습된 데이터는 영구 JSON DB에 누적되어 다음 유사 프로젝트 견적 시 즉시 검색/참조\n"
     "• 쓸수록 똑똑해지고 정밀해지는 제일기획만의 독점적 '견적 인텔리전스 자산화'", C_GOLD),
    ("04. 심사위원 & 광고주 대상 압도적 신뢰도 확보", 
     "• '왜 이 금액이 나왔는가?'에 대해 '과거 S26 프로젝트의 동일 사양 실제 정산 실적'을 제시\n"
     "• 공공 표준 품셈 + 제일기획 실제 과거 실적의 '이중 방어벽(Dual Firewall)' 구축\n"
     "• 광고주의 의구심을 원천 차단하고 1회차 무수정 승인 보장", C_GREEN)
]

for idx, (title, desc, col) in enumerate(flywheel_cards):
    fx = 0.8 + (idx % 2) * 5.95
    fy = 1.85 + (idx // 2) * 2.45
    add_card(s13, fx, fy, 5.75, 2.3, C_CARD_BG, col, 1.2)
    tb = s13.shapes.add_textbox(Inches(fx + 0.15), Inches(fy + 0.12), Inches(5.45), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = col
    p_b = tf.add_paragraph()
    p_b.text = desc
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(6)

# ==============================================================================
# SLIDE 14: FIELD VALIDATION
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14)
add_header(s14, "Field Validation", "실제 삼성전자 / 제일기획 4대 기준견적서 실전 감리 검증 결과", 
           "실제 현업 데이터 4종을 투입하여 비적합 과다청구 적발 및 공공 기준 소명 능력을 실증했습니다.", 14)

cases = [
    ("Case 1. S26 Miracle 키트/컨텐츠", "1-1. 개발 상세 시트 10개 항목", 
     "• 결과: 총 10건 중 10건 적합 판정 (100% 공공 노임 준수)\n"
     "• 증빙: KOSA 및 KIDP 고시 노임단가 범위 내 정합성 공식 입증\n"
     "• 효과: 광고주 의구심 사전 해소로 1회차 무수정 승인 달성", C_GREEN),
    ("Case 2. 홍대점 집기제작 & 전시", "● 홍대점_거래명세서 48개 항목", 
     "• 결과: 미승인 변경건 2건 적발 (불합리 증액 ₩2,400만 원 차단)\n"
     "• 증빙: CR(변경승인) 미확인 항목 신호등 빨간불 표시 및 삭감 요구\n"
     "• 효과: 프로젝트 예산 누수 원천 차단", C_RED),
    ("Case 3. 프로야구 KBO 베뉴 키트", "야구 키트 및 원형 개발 시트", 
     "• 결과: 야간 설치 투입률 120% 초과 구간 자동 탐지\n"
     "• 증빙: 근로기준법 제56조 야간할증 및 현장 출장 사유서 자동 연계\n"
     "• 효과: 광고주의 '야간상주 필요성' 질의(FAQ 02) 원스톱 방어", C_YELLOW),
    ("Case 4. 삼성 사업장 전시 & 인건비", "수원/기흥 사업장 & 인건비 공통", 
     "• 결과: 수식 누락 및 하드코딩 단가 3건 자동 적발\n"
     "• 증빙: '수량 × 단가 != 금액' 오류를 견적 제출 전 사전 보정\n"
     "• 효과: 광고주 양식 지적(FAQ 10) 사전 100% 예방", C_BLUE)
]

for idx, (c_name, c_sub, c_body, c_col) in enumerate(cases):
    cx = 0.8 + (idx % 2) * 5.95
    cy = 1.85 + (idx // 2) * 2.45
    add_card(s14, cx, cy, 5.75, 2.3, C_CARD_BG, c_col, 1.2)
    tb = s14.shapes.add_textbox(Inches(cx + 0.15), Inches(cy + 0.12), Inches(5.45), Inches(2.05))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = c_name
    p.font.name = FONT_HEADING
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_col
    p_sub = tf.add_paragraph()
    p_sub.text = c_sub
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = C_MUTED
    p_b = tf.add_paragraph()
    p_b.text = c_body
    p_b.font.name = FONT_BODY
    p_b.font.size = Pt(9.5)
    p_b.font.color.rgb = C_TEXT_LIGHT
    p_b.space_before = Pt(5)

# ==============================================================================
# SLIDE 15: BUSINESS IMPACT
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15)
add_header(s15, "Business Impact", "검토는 3분 만에, 재질의는 0건으로, 정산은 즉시 완료", 
           "AX(인공지능 전환)가 가져온 제일기획 견적·정산 업무의 정량적 혁신 지표", 15)

metrics = [
    ("⏱️ 견적 검토 시간", "96% 단축", "기존 2일 (16시간) → AI 3분 완료", 
     "수작업 엑셀 대조 및 셀프 체크리스트 자동화로 신속한 견적 감리 종결", C_CYAN),
    ("💬 광고주 재질의율", "85% 격감", "기존 45% 발생 → 5% 이하 달성", 
     "FAQ 10대 유형별 사전 증빙 패키징으로 불필요한 반복 소명 차단", C_GOLD),
    ("💰 예산 누수 방지", "5~12% 삭감", "프로젝트당 수천만~수억 원 절감", 
     "미승인 변경건 및 140% 초과 과다청구 즉시 삭감으로 프로젝트 수익률 수호", C_RED),
    ("🚀 대금 회수 리드타임", "3주 단축", "기존 4주 소요 → 1주일 내 입금", 
     "1회차 정산 종결을 통한 협력사 정산 분쟁 해소 및 전사 캐시플로우 혁신", C_GREEN)
]

for idx, (m_label, m_val, m_sub, m_desc, m_col) in enumerate(metrics):
    mx = 0.8 + idx * 2.983
    add_card(s15, mx, 1.85, 2.783, 4.8, C_CARD_BG, m_col, 1.5)
    tb = s15.shapes.add_textbox(Inches(mx + 0.15), Inches(2.05), Inches(2.483), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = m_label
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13.5)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p_val = tf.add_paragraph()
    p_val.text = m_val
    p_val.font.name = FONT_HEADING
    p_val.font.size = Pt(32)
    p_val.font.bold = True
    p_val.font.color.rgb = m_col
    p_val.space_before = Pt(8)
    p_sub = tf.add_paragraph()
    p_sub.text = m_sub
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(10)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_GOLD
    p_sub.space_before = Pt(4)
    p_desc = tf.add_paragraph()
    p_desc.text = m_desc
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(9.5)
    p_desc.font.color.rgb = C_TEXT_LIGHT
    p_desc.space_before = Pt(10)

# ==============================================================================
# SLIDE 16: FUTURE SCALABILITY
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
set_slide_background(s16)
add_header(s16, "Future Scalability", "한국을 넘어 글로벌 베뉴로, 전사 견적 인텔리전스로 확장", 
           "단일 프로젝트 감리에 머물지 않고 전사 표준 단가 DB 자산화 및 글로벌 롤아웃을 추진합니다.", 16)

phases = [
    ("Phase 1 (현재)", "국내 스마트 리테일 & 전시 감리 완성", 
     "• S26 & 폴더블 44개 키트 백데이터 탑재\n• 6대 공공 기준 연동 및 10대 FAQ 자동 소명\n• Render.com 24/7/365 글로벌 무중단 서비스", C_CYAN),
    ("Phase 2 (2026. 4Q)", "글로벌 거점(북미/유럽/동남아) 통화 연동", 
     "• USD($), EUR(€), GBP(£) 다국어/다통화 감리\n• 현지 노임(RSMeans, BLS 노임) DB 탑재\n• 글로벌 언팩 및 IFA/CES 베뉴 전격 적용", C_BLUE),
    ("Phase 3 (2027. 1H)", "전사 견적 데이터 인텔리전스 플라이휠", 
     "• 협력사별 견적 정확도 및 리스크 스코어링\n• 견적서 업로드 즉시 적정 실행예산 자동 예측\n• 제일기획 고유의 독점적 견적 지식 자산화", C_GOLD)
]

for idx, (p_phase, p_title, p_desc, p_col) in enumerate(phases):
    px = 0.8 + idx * 3.98
    add_card(s16, px, 1.85, 3.78, 4.8, C_CARD_BG, p_col, 1.5)
    tb = s16.shapes.add_textbox(Inches(px + 0.15), Inches(2.05), Inches(3.48), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = p_phase
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = p_col
    p2 = tf.add_paragraph()
    p2.text = p_title
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE
    p2.space_before = Pt(4)
    p3 = tf.add_paragraph()
    p3.text = p_desc
    p3.font.name = FONT_BODY
    p3.font.size = Pt(10)
    p3.font.color.rgb = C_TEXT_LIGHT
    p3.space_before = Pt(10)

# ==============================================================================
# SLIDE 17: LIVE DEMONSTRATION
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
set_slide_background(s17)
add_header(s17, "Live Demonstration", "심사위원 3분 현장 라이브 시연 시나리오", 
           "심사위원께서 현장에서 직접 확인하실 수 있는 4단계 실시간 감리 시연 동선입니다.", 17)

demo_steps = [
    ("Step 1. 24시간 클라우드 접속", "https://ax-estimate-director.onrender.com/", 
     "• 심사위원 스마트폰 또는 노트북으로 접속\n• PC OFF 상태에서도 1초 만에 로딩 확인\n• 직관적인 다크 하이테크 UI/UX 확인", C_CYAN),
    ("Step 2. 엑셀 업로드 & 3초 진단", "Tab 0. 견적 진단·감리실", 
     "• 실제 샘플 견적서 1-클릭 선택\n• 3초 만에 48개 항목 전수 감리\n• 🟢 적합 / 🟡 조건부 / 🔴 삭감 카드 확인", C_BLUE),
    ("Step 3. 비전 AI 견적 산출 시연", "Tab 5. 비전 AI 견적 산출기", 
     "• 키트 실물 사진/도면 1장 투입\n• 10초 만에 5대 공종 견적서 자동 산출\n• 실제 S26 CXP 키트 실적과 1:1 대조 확인", C_GOLD),
    ("Step 4. 소명서 & XLSX 다운로드", "Tab 4. 광고주 질의 대응", 
     "• 광고주 10대 FAQ 유형별 1초 소명서 생성\n• 6대 공공 기준 산출식 완비 엑셀 다운로드\n• 실전 업무 적용성 100% 실증 종결", C_GREEN)
]

for idx, (d_step, d_loc, d_desc, d_col) in enumerate(demo_steps):
    dx = 0.8 + idx * 2.983
    add_card(s17, dx, 1.85, 2.783, 4.8, C_CARD_BG, d_col, 1.5)
    tb = s17.shapes.add_textbox(Inches(dx + 0.15), Inches(2.05), Inches(2.483), Inches(4.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = d_step
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = d_col
    p2 = tf.add_paragraph()
    p2.text = d_loc
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(10.5)
    p2.font.bold = True
    p2.font.color.rgb = C_WHITE
    p2.space_before = Pt(3)
    p3 = tf.add_paragraph()
    p3.text = d_desc
    p3.font.name = FONT_BODY
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = C_TEXT_LIGHT
    p3.space_before = Pt(10)

# ==============================================================================
# SLIDE 18: GRAND PRIZE CONCLUSION
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
set_slide_background(s18)

box_win = s18.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.9), Inches(11.733), Inches(5.8)
)
box_win.fill.solid()
box_win.fill.fore_color.rgb = RGBColor(16, 25, 48)
box_win.line.color.rgb = C_GOLD
box_win.line.width = Pt(2)

tb_fin = s18.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(10.9), Inches(5.2))
tf_fin = tb_fin.text_frame
tf_fin.word_wrap = True

p_f1 = tf_fin.paragraphs[0]
p_f1.text = "🏆 대상(Grand Prize) 수상의 압도적 당위성"
p_f1.font.name = FONT_HEADING
p_f1.font.size = Pt(28)
p_f1.font.bold = True
p_f1.font.color.rgb = C_GOLD

p_f2 = tf_fin.add_paragraph()
p_f2.text = "\"가장 치열한 정산의 현장에서, 가장 완벽한 AX의 실천을 증명했습니다.\""
p_f2.font.name = FONT_HEADING
p_f2.font.size = Pt(17)
p_f2.font.bold = True
p_f2.font.color.rgb = C_CYAN
p_f2.space_before = Pt(10)

reasons = [
    ("1. 아이디어가 아닌 100% 라이브 가동 중인 실전 서비스", 
     "https://ax-estimate-director.onrender.com/ 에서 내 PC가 꺼져 있어도 24시간 365일 전 세계 어디서나 즉시 구동됩니다."),
    ("2. 광고주 10대 정산 전쟁의 모든 페인포인트를 1:1로 해결한 완벽한 비즈니스 로직", 
     "실제 FAQ 86건 전수 분석을 기반으로 감성적 설득이 아닌 법적·공학적 팩트 방어 체계를 확립했습니다."),
    ("3. 비전 AI + 25.6억 실적 백데이터 + 6대 국가 표준 결합의 기술적 완성도", 
     "도면·사진 1장으로 10초 만에 공공 견적서를 산출하고, S26/폴더블 44개 키트 실적과 대조하여 오차를 검증합니다."),
    ("4. 연간 수백억 원의 제작비 정산 시간을 96% 단축하고 예산 누수를 차단하는 압도적 ROI", 
     "단 1회 사용만으로도 불합리 증액 수천만 원을 차단하고 대금 회수를 3주 단축시키는 실질적 비즈니스 파급력을 입증했습니다.")
]

for idx, (rt, rd) in enumerate(reasons):
    pr_t = tf_fin.add_paragraph()
    pr_t.text = rt
    pr_t.font.name = FONT_HEADING
    pr_t.font.size = Pt(12.5)
    pr_t.font.bold = True
    pr_t.font.color.rgb = C_WHITE
    pr_t.space_before = Pt(12)
    pr_d = tf_fin.add_paragraph()
    pr_d.text = rd
    pr_d.font.name = FONT_BODY
    pr_d.font.size = Pt(10.5)
    pr_d.font.color.rgb = C_TEXT_LIGHT
    pr_d.space_before = Pt(2)

# Save presentation
prs.save(str(OUT_PPTX))
prs.save(str(BACKUP_PPTX))

print(f"Grand Prize Presentation Deck ({len(prs.slides)} slides) generated successfully!")
print(f"Target: {OUT_PPTX}")
print(f"Backup: {BACKUP_PPTX}")
