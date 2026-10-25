# -*- coding: utf-8 -*-
import sys

def main():
    with open('scripts/build_grand_prize_deck.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, l in enumerate(lines):
        if 's10 = prs.slides.add_slide(blank_layout)' in l:
            start_idx = i
        if start_idx is not None and 'for idx, (f_title, f_desc) in enumerate(cloud_features):' in l:
            end_idx = i
            break

    assert start_idx is not None and end_idx is not None, f'{start_idx}, {end_idx}'

    new_s10_block = '''s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "The Live Product", "24시간 365일 어디서나 접속 가능한 엔터프라이즈 라이브 클라우드 도메인", 
           "발표자 컴퓨터 전원 OFF 상태에서도 100% 무중단 가동되는 멀티 클라우드 프로덕션 시스템", 10)

add_card(s10, 0.8, 1.85, 11.733, 1.7, RGBColor(16, 32, 65), C_GOLD, 2)
tb_conn = s10.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(11.333), Inches(1.5))
tf_conn = tb_conn.text_frame
tf_conn.word_wrap = True
p_c1 = tf_conn.paragraphs[0]
p_c1.text = "🌐 공식 상용급 클라우드 글로벌 프로덕션 듀얼 도메인 가동 현황"
p_c1.font.name = FONT_HEADING
p_c1.font.size = Pt(13)
p_c1.font.bold = True
p_c1.font.color.rgb = C_CYAN

p_c2 = tf_conn.add_paragraph()
p_c2.text = "★ 신규 도메인(견적감독관): https://ax-estimate-supervisor.onrender.com/ (총체적 종합의견 란 탑재)"
p_c2.font.name = FONT_HEADING
p_c2.font.size = Pt(14)
p_c2.font.bold = True
p_c2.font.color.rgb = C_GOLD
p_c2.space_before = Pt(3)

p_c2_sub = tf_conn.add_paragraph()
p_c2_sub.text = "★ 기존 도메인(견적감리관): https://ax-estimate-director.onrender.com/ (기존 도메인 24/7/365 유지)"
p_c2_sub.font.name = FONT_HEADING
p_c2_sub.font.size = Pt(12)
p_c2_sub.font.bold = True
p_c2_sub.font.color.rgb = C_GREEN
p_c2_sub.space_before = Pt(2)

p_c3 = tf_conn.add_paragraph()
p_c3.text = "⚡ Zero Local Dependency: 사용자 PC 전원 종료 시에도 독립 운영 | Docker 가상화 자동 복구 | SSL 보안 암호화 완비"
p_c3.font.name = FONT_BODY
p_c3.font.size = Pt(10)
p_c3.font.color.rgb = C_TEXT_LIGHT
p_c3.space_before = Pt(3)

cloud_features = [
    ("Tab 0. 견적감독관 종합진단실", "종합 리스크 등급(🔴고위험/🟡주의/🟢적정), 부적정 삭감 목표액, 4대 공종 총평 및 3대 액션 플랜"),
    ("Tab 1. 신호등 정밀 감리표", "적합/조건부/비적합 전수 판정, 공공 6대 기준 소명서 연계 및 공문서용 진단서 발행"),
    ("Tab 2. 제작비 요인 분해", "'왜 비싼가?' 원가 상승 동인을 자재비/공임/가공비 축으로 투명하게 분해"),
    ("Tab 4. 광고주 질의 대응", "협력사/발주처 FAQ 질의에 1초 만에 공식 답변서 및 소명 가이드라인 생성"),
    ("Tab 5. 비전 AI 견적 추정", "시안/렌더링 이미지 단 1장으로 5대 공종 원가 산출 및 표준 견적서(XLSX) 자동 생성"),
    ("Tab 6. 과거 실적 자산화", "25.6억 원 44종 실물 키트 원가 DB 및 43종 실제 고화질 키트 사진 전수 탑재")
]

'''

    lines = lines[:start_idx] + [new_s10_block] + lines[end_idx:]

    with open('scripts/build_grand_prize_deck.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Slide 10 in scripts/build_grand_prize_deck.py updated successfully!")

if __name__ == '__main__':
    main()
