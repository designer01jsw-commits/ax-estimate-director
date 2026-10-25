# -*- coding: utf-8 -*-
import sys

def main():
    with open('scripts/build_grand_prize_deck.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Slide 10 URL box
    target_s10_urls = '''p_c2 = tf_conn.add_paragraph()
p_c2.text = "URL: https://ax-estimate-director.onrender.com/  (24시간 365일 무중단 가동)"
p_c2.font.name = FONT_HEADING
p_c2.font.size = Pt(17)
p_c2.font.bold = True
p_c2.font.color.rgb = C_GOLD
p_c2.space_before = Pt(5)'''

    repl_s10_urls = '''p_c2 = tf_conn.add_paragraph()
p_c2.text = "★ 신규 견적감독관: https://ax-estimate-supervisor.onrender.com/ (총체적 종합의견 란 탑재)"
p_c2.font.name = FONT_HEADING
p_c2.font.size = Pt(14)
p_c2.font.bold = True
p_c2.font.color.rgb = C_GOLD
p_c2.space_before = Pt(3)

p_c2_sub = tf_conn.add_paragraph()
p_c2_sub.text = "★ 기존 견적감리관: https://ax-estimate-director.onrender.com/ (기존 도메인 24/7 유지)"
p_c2_sub.font.name = FONT_HEADING
p_c2_sub.font.size = Pt(12)
p_c2_sub.font.bold = True
p_c2_sub.font.color.rgb = C_CYAN
p_c2_sub.space_before = Pt(2)'''

    # Handle CRLF if present
    if target_s10_urls not in content and target_s10_urls.replace('\n', '\r\n') in content:
        content = content.replace(target_s10_urls.replace('\n', '\r\n'), repl_s10_urls.replace('\n', '\r\n'), 1)
        print("Updated Slide 10 URLs with CRLF")
    elif target_s10_urls in content:
        content = content.replace(target_s10_urls, repl_s10_urls, 1)
        print("Updated Slide 10 URLs with LF")
    else:
        print("Warning: target_s10_urls not found")

    # 2. Update Feature Tab 0 description
    target_tab0 = '("Tab 0. 견적 감리·진단실", "적합/조건부/비적합 자동판정, 공공 6대 기준 소명서 연계, 시정명령서 발행")'
    repl_tab0 = '("Tab 0. 견적감독관 종합진단실", "종합 리스크 등급(🔴고위험/🟡주의/🟢적정), 부적정 삭감 목표액, 4대 공종 총평 & 3대 액션 플랜")'

    if target_tab0 in content:
        content = content.replace(target_tab0, repl_tab0, 1)
        print("Updated Tab 0 title & desc")
    else:
        print("Warning: target_tab0 not found")

    with open('scripts/build_grand_prize_deck.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done patching scripts/build_grand_prize_deck.py!")

if __name__ == '__main__':
    main()
