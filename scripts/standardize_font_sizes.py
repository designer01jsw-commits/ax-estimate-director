# -*- coding: utf-8 -*-
"""
Standardize all font sizes across app.py into a clean 5-tier typographic scale:
1. Hero Display: 38px
2. Major Headings: 22px
3. Card/Subhead Titles: 16px
4. Base Body & Interactive Controls: 14px ~ 15px
5. Captions, Chips & Eyebrows: 12px ~ 13px
"""

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS typography definitions
css_replacements = [
    # Sidebar headings
    ("color: var(--slate-gray) !important;\n        font-size: 13px !important;\n        font-weight: 700 !important;",
     "color: var(--slate-gray) !important;\n        font-size: 12px !important;\n        font-weight: 700 !important;"),
    
    # H2 and H3
    ("h2 {\n        font-size: 28px !important;\n        margin-top: 36px !important;\n        margin-bottom: 16px !important;\n    }\n    h3 {\n        font-size: 22px !important;\n    }",
     "h2 {\n        font-size: 22px !important;\n        font-weight: 600 !important;\n        margin-top: 32px !important;\n        margin-bottom: 14px !important;\n    }\n    h3 {\n        font-size: 18px !important;\n        font-weight: 600 !important;\n    }"),
     
    # Primary button
    ("font-size: 16px !important;\n        font-weight: 500 !important;\n        letter-spacing: -0.32px !important;\n        border: 1.5px solid var(--ink-black) !important;",
     "font-size: 14px !important;\n        font-weight: 500 !important;\n        letter-spacing: -0.2px !important;\n        border: 1.5px solid var(--ink-black) !important;"),
     
    # Secondary button
    ("font-size: 16px !important;\n        font-weight: 450 !important;\n        letter-spacing: -0.32px !important;\n        border: 1.5px solid var(--ink-black) !important;",
     "font-size: 14px !important;\n        font-weight: 500 !important;\n        letter-spacing: -0.2px !important;\n        border: 1.5px solid var(--ink-black) !important;"),
     
    # Metric Label & Value
    ("font-size: 13px !important;\n        font-weight: 700 !important;\n        letter-spacing: 0.04em !important;\n        color: var(--slate-gray) !important;\n        text-transform: uppercase !important;\n        margin-bottom: 6px !important;\n    }\n    div[data-testid=\"stMetricValue\"] {\n        font-size: 32px !important;",
     "font-size: 12px !important;\n        font-weight: 700 !important;\n        letter-spacing: 0.04em !important;\n        color: var(--slate-gray) !important;\n        text-transform: uppercase !important;\n        margin-bottom: 6px !important;\n    }\n    div[data-testid=\"stMetricValue\"] {\n        font-size: 26px !important;"),
     
    # Metric Delta
    ("div[data-testid=\"stMetricDelta\"] {\n        font-size: 13px !important;",
     "div[data-testid=\"stMetricDelta\"] {\n        font-size: 12px !important;"),
     
    # Inputs & Textareas
    ("input, textarea {\n        background-color: var(--white) !important;\n        border: 1.5px solid rgba(20, 20, 19, 0.15) !important;\n        color: var(--ink-black) !important;\n        border-radius: 20px !important;\n        font-size: 15px !important;",
     "input, textarea {\n        background-color: var(--white) !important;\n        border: 1.5px solid rgba(20, 20, 19, 0.15) !important;\n        color: var(--ink-black) !important;\n        border-radius: 20px !important;\n        font-size: 14px !important;"),
     
    # Expander summary
    ("div[data-testid=\"stExpander\"] summary {\n        font-size: 15px !important;",
     "div[data-testid=\"stExpander\"] summary {\n        font-size: 14px !important;"),
     
    # Eyebrow
    ("mc-eyebrow {\n        font-size: 13px !important;",
     "mc-eyebrow {\n        font-size: 12px !important;"),
     
    # Hero Title (from 52px to clean 38px)
    (".mc-hero-title {\n        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;\n        font-size: 52px !important;\n        font-weight: 500 !important;\n        line-height: 1.05 !important;\n        letter-spacing: -0.02em !important;\n        color: var(--ink-black) !important;\n        margin: 0 0 14px 0 !important;\n    }\n    .mc-hero-subhead {\n        font-size: 18px !important;",
     ".mc-hero-title {\n        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;\n        font-size: 38px !important;\n        font-weight: 700 !important;\n        line-height: 1.15 !important;\n        letter-spacing: -0.02em !important;\n        color: var(--ink-black) !important;\n        margin: 0 0 10px 0 !important;\n    }\n    .mc-hero-subhead {\n        font-size: 15px !important;"),
     
    # Domain pill font size
    ("padding: 8px 22px;\n        font-size: 14px;",
     "padding: 6px 18px;\n        font-size: 13px;"),
     
    # Pill chip font size
    ("padding: 5px 16px;\n        font-size: 13px;",
     "padding: 4px 14px;\n        font-size: 12px;"),
     
    # Satellite badge font size
    ("padding: 6px 18px;\n        box-shadow: var(--shadow-card);\n        border: 1px solid rgba(20, 20, 19, 0.08);\n        font-size: 13px;",
     "padding: 6px 16px;\n        box-shadow: var(--shadow-card);\n        border: 1px solid rgba(20, 20, 19, 0.08);\n        font-size: 12px;"),
     
    # Footer title
    (".mc-footer-title {\n        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;\n        font-size: 32px !important;",
     ".mc-footer-title {\n        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif !important;\n        font-size: 22px !important;")
]

for old, new in css_replacements:
    if old in content:
        content = content.replace(old, new)
        print("CSS rule updated successfully.")
    else:
        print("WARNING: CSS rule not matched directly:", old[:40])

# 2. Update HTML components font sizes in main()
html_replacements = [
    # Nav bar title font size
    ('<span style="font-size: 16px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>',
     '<span style="font-size: 15px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink-black);">CHEIL AX · ESTIMATE SUPERVISOR</span>'),
     
    # Nav bar engine tag
    ('<span style="font-size: 13px; font-weight: 500; color: var(--slate-gray);">• 정밀 감리 엔진 v2.0</span>',
     '<span style="font-size: 12px; font-weight: 500; color: var(--slate-gray);">• 정밀 감리 엔진 v2.0</span>'),
     
    # Verdict title (from 26px to 22px)
    ('<div style="font-size: 26px; font-weight: 500; letter-spacing: -0.02em; color: var(--ink-black);">\n                            🏛️ 견적감독관 총체적 종합 진단 소견\n                        </div>',
     '<div style="font-size: 22px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink-black);">\n                            🏛️ 견적감독관 총체적 종합 진단 소견\n                        </div>'),
     
    # Verdict recommendation text (from 16px to 15px)
    ('<div style="font-size: 16px; font-weight: 450; color: var(--ink-black); line-height: 1.55;',
     '<div style="font-size: 15px; font-weight: 400; color: var(--ink-black); line-height: 1.5;'),
     
    # Pillars titles (from 17px to 16px)
    ('<div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p1[\'title\']}</div>',
     '<div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p1[\'title\']}</div>'),
    ('<div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p2[\'title\']}</div>',
     '<div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p2[\'title\']}</div>'),
    ('<div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p3[\'title\']}</div>',
     '<div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p3[\'title\']}</div>'),
    ('<div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{p4[\'title\']}</div>',
     '<div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{p4[\'title\']}</div>'),
     
    # Action item title (from 16px to 15px)
    ('<div style="font-size: 16px; font-weight: 500; color: var(--ink-black); margin-bottom: 6px; letter-spacing: -0.02em;">{act[\'title\']}</div>',
     '<div style="font-size: 15px; font-weight: 600; color: var(--ink-black); margin-bottom: 6px; letter-spacing: -0.01em;">{act[\'title\']}</div>'),
    ('<div style="font-size: 16px; font-weight: 700; color: var(--signal-orange); margin-bottom: 8px;">{act[\'amount\']}</div>',
     '<div style="font-size: 15px; font-weight: 700; color: var(--signal-orange); margin-bottom: 6px;">{act[\'amount\']}</div>'),
     
    # Problem item title (from 17px to 16px)
    ('<div style="font-size: 17px; font-weight: 500; color: var(--ink-black); letter-spacing: -0.02em;">{it[\'항목명\']}</div>',
     '<div style="font-size: 16px; font-weight: 600; color: var(--ink-black); letter-spacing: -0.01em;">{it[\'항목명\']}</div>'),
     
    # Footer meta
    ('<span style="font-size: 13px; font-weight: 500; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>',
     '<span style="font-size: 12px; font-weight: 600; color: #FFFFFF;">CHEIL AX ESTIMATE SUPERVISOR</span>')
]

for old, new in html_replacements:
    if old in content:
        content = content.replace(old, new)
        print("HTML component font updated successfully.")
    else:
        print("WARNING: HTML component not matched directly:", old[:40])

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app.py with standardized font scale successfully.")
