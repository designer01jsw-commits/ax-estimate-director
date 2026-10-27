# -*- coding: utf-8 -*-
"""
Apply Samsung Sharp Sans (English) and Samsung SS Head KR (Korean) font system to app.py
"""

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

samsung_font_css = """    /* ==========================================================================
       Samsung Typography System:
       - English: Samsung Sharp Sans (Bold, Medium, Regular)
       - Korean: Samsung SS Head KR (Bold, Medium, Regular, Light)
       ========================================================================== */

    /* 1. English Font: Samsung Sharp Sans */
    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Regular'), local('Samsung Sharp Sans Regular'), local('Samsung Sharp Sans'),
             url('/app/static/fonts/SamsungSharpSans-Regular.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Regular.ttf') format('truetype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Medium'), local('Samsung Sharp Sans Medium'),
             url('/app/static/fonts/SamsungSharpSans-Medium.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Medium.ttf') format('truetype');
        font-weight: 500;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSharpSans';
        src: local('SamsungSharpSans-Bold'), local('Samsung Sharp Sans Bold'),
             url('/app/static/fonts/SamsungSharpSans-Bold.ttf') format('truetype'),
             url('app/static/fonts/SamsungSharpSans-Bold.ttf') format('truetype');
        font-weight: 700;
        font-weight: 800;
        font-style: normal;
        font-display: swap;
    }

    /* 2. Korean Font: Samsung SS Head KR */
    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Light'), local('Samsung SS Head KR Light'),
             url('/app/static/fonts/SamsungSSHeadKR-Light.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Light.ttf') format('truetype');
        font-weight: 300;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Regular'), local('Samsung SS Head KR Regular'), local('Samsung SS Head KR'),
             url('/app/static/fonts/SamsungSSHeadKR-Regular.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Regular.ttf') format('truetype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Medium'), local('Samsung SS Head KR Medium'),
             url('/app/static/fonts/SamsungSSHeadKR-Medium.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Medium.ttf') format('truetype');
        font-weight: 500;
        font-style: normal;
        font-display: swap;
    }

    @font-face {
        font-family: 'SamsungSSHeadKR';
        src: local('SamsungSSHeadKR-Bold'), local('Samsung SS Head KR Bold'),
             url('/app/static/fonts/SamsungSSHeadKR-Bold.ttf') format('truetype'),
             url('app/static/fonts/SamsungSSHeadKR-Bold.ttf') format('truetype');
        font-weight: 700;
        font-weight: 800;
        font-style: normal;
        font-display: swap;
    }

    :root {
        --canvas-cream: #F3F0EE;
        --lifted-cream: #FCFBFA;
        --white: #FFFFFF;
        --soft-bone: #F4F4F4;
        --ink-black: #141413;
        --charcoal: #262627;
        --slate-gray: #696969;
        --granite: #555555;
        --dust-taupe: #D1CDC7;
        --signal-orange: #CF4500;
        --light-signal-orange: #F37338;
        --clay-brown: #9A3A0A;
        --link-blue: #3860BE;
        --semantic-success: #10B981;
        --semantic-danger: #CF4500;
        --semantic-warning: #F79E1B;
        
        --radius-pill: 999px;
        --radius-stadium: 40px;
        --radius-card: 20px;
        --radius-button: 20px;
        --radius-circle: 50%;
        
        --shadow-nav: rgba(0, 0, 0, 0.04) 0px 4px 24px 0px;
        --shadow-cushion: rgba(0, 0, 0, 0.06) 0px 18px 40px 0px;
        --shadow-card: rgba(0, 0, 0, 0.03) 0px 6px 20px 0px;
    }

    /* 1. Global Font Stack: English (SamsungSharpSans) -> Korean (SamsungSSHeadKR) */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: var(--canvas-cream) !important;
        color: var(--ink-black) !important;
        font-family: 'SamsungSharpSans', 'SamsungSSHeadKR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        font-weight: 400 !important;
        line-height: 1.45 !important;
        -webkit-font-smoothing: antialiased !important;
    }"""

# Find existing font definition block
old_font_start = content.find("    @import url('https://fonts.googleapis.com/css2?family=Sofia+Sans")
old_font_end = content.find("    /* 2. Sidebar: Lifted Cream with Subtle Border */")

if old_font_start != -1 and old_font_end != -1:
    content = content[:old_font_start] + samsung_font_css + "\n\n" + content[old_font_end:]
    print("1. Replaced font definitions with Samsung Sharp Sans & Samsung SS Head KR!")
else:
    print("WARNING: Old font block not found!")

# Replace all occurrences of Sofia Sans with SamsungSharpSans, SamsungSSHeadKR
content = content.replace("'Sofia Sans', sans-serif", "'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif")
content = content.replace("'Sofia Sans', 'Inter', Arial, sans-serif", "'SamsungSharpSans', 'SamsungSSHeadKR', sans-serif")
print("2. Replaced all font-family declarations with SamsungSharpSans and SamsungSSHeadKR!")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved app.py with Samsung Typography System successfully.")
