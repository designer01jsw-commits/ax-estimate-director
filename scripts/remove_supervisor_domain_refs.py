# -*- coding: utf-8 -*-
"""
Remove all references to the new supervisor domain in app.py, leaving only the official director domain.
"""

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Hero Domain Pill
old_pill = """        <div class="mc-domain-pill">
            <span style="color: var(--ink-black); font-weight: 500;">🌐 배포 도메인:</span>
            <span>신규 견적감독관: <a href="https://ax-estimate-supervisor.onrender.com" target="_blank">ax-estimate-supervisor.onrender.com</a></span>
            <span style="color: #D1CDC7;">|</span>
            <span>기존 견적감리관: <a href="https://ax-estimate-director.onrender.com" target="_blank">ax-estimate-director.onrender.com</a></span>
            <span class="mc-satellite-arrow" style="margin-left: 6px;">↗</span>
        </div>"""

new_pill = """        <div class="mc-domain-pill">
            <span style="color: var(--ink-black); font-weight: 500;">🌐 공식 서비스 도메인:</span>
            <a href="https://ax-estimate-director.onrender.com" target="_blank">https://ax-estimate-director.onrender.com</a>
            <span class="mc-satellite-arrow" style="margin-left: 6px;">↗</span>
        </div>"""

# 2. Update Footer Link
old_footer = """            <div style="display: flex; gap: 20px;">
                <a href="https://ax-estimate-supervisor.onrender.com" target="_blank" style="color: #BBBBBB;">신규 감독관 도메인 ↗</a>
                <a href="https://ax-estimate-director.onrender.com" target="_blank" style="color: #BBBBBB;">기존 감리관 도메인 ↗</a>
            </div>"""

new_footer = """            <div>
                <a href="https://ax-estimate-director.onrender.com" target="_blank" style="color: #BBBBBB;">공식 도메인 (24/7 무중단 가동) ↗</a>
            </div>"""

content_norm = content.replace("\r\n", "\n")
old_pill_norm = old_pill.replace("\r\n", "\n")
old_footer_norm = old_footer.replace("\r\n", "\n")

if old_pill_norm in content_norm:
    content_norm = content_norm.replace(old_pill_norm, new_pill)
    print("1. Hero domain pill updated!")
else:
    print("WARNING: Hero domain pill not found!")

if old_footer_norm in content_norm:
    content_norm = content_norm.replace(old_footer_norm, new_footer)
    print("2. Footer links updated!")
else:
    print("WARNING: Footer links not found!")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content_norm)

print("Saved app.py cleanly without supervisor domain.")
