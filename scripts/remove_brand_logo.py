# -*- coding: utf-8 -*-
"""
Remove brand logo (overlapping red/yellow circles) from app.py
"""

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove CSS rules for mc-brand-mark, mc-circle-red, mc-circle-yellow
css_target = """    .mc-brand-mark {
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
    }"""

# 2. Update floating nav bar
nav_target = """        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="mc-brand-mark">
                <span class="mc-circle-red"></span>
                <span class="mc-circle-yellow"></span>
            </div>
            <span style="font-size: 16px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>
        </div>"""

nav_replacement = """        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">⚖️</span>
            <span style="font-size: 16px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>
        </div>"""

# 3. Update footer
footer_target = """            <div style="display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.08); padding: 8px 20px; border-radius: 999px;">
                <div class="mc-brand-mark">
                    <span class="mc-circle-red"></span>
                    <span class="mc-circle-yellow"></span>
                </div>
                <span style="font-size: 13px; font-weight: 500; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>
            </div>"""

footer_replacement = """            <div style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.08); padding: 8px 20px; border-radius: 999px;">
                <span style="font-size: 16px;">🏛️</span>
                <span style="font-size: 13px; font-weight: 500; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>
            </div>"""

# Normalize line endings
content_norm = content.replace("\r\n", "\n")
css_target_norm = css_target.replace("\r\n", "\n")
nav_target_norm = nav_target.replace("\r\n", "\n")
footer_target_norm = footer_target.replace("\r\n", "\n")

if css_target_norm in content_norm:
    content_norm = content_norm.replace(css_target_norm, "")
    print("1. CSS logo rules removed!")
else:
    print("WARNING: CSS logo rules target not found!")

if nav_target_norm in content_norm:
    content_norm = content_norm.replace(nav_target_norm, nav_replacement)
    print("2. Nav bar logo replaced!")
else:
    print("WARNING: Nav bar logo target not found!")

if footer_target_norm in content_norm:
    content_norm = content_norm.replace(footer_target_norm, footer_replacement)
    print("3. Footer logo replaced!")
else:
    print("WARNING: Footer logo target not found!")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content_norm)

print("Saved app.py without brand logo successfully.")
