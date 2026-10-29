# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
app_file = ROOT_DIR / "app.py"

with open(app_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Target is line 885: '    if not rev_file_input:\n'
target_idx = None
for i, line in enumerate(lines):
    if line.strip() == "if not rev_file_input:" and i > 850:
        target_idx = i
        break

if target_idx is None:
    print("Could not find target line!")
    sys.exit(1)

# Find the end of the stadium card markdown: '</div>""", unsafe_allow_html=True)\n'
end_idx = None
for j in range(target_idx, target_idx + 35):
    if '</div>""", unsafe_allow_html=True)' in lines[j]:
        end_idx = j
        break

if end_idx is None:
    print("Could not find end of card!")
    sys.exit(1)

new_code = '''    if not rev_file_input:
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
'''

# Replace lines from target_idx to end_idx + 1
new_lines = lines[:target_idx] + [new_code] + lines[end_idx + 1:]
with open(app_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Updated center screen card in app.py successfully!")
