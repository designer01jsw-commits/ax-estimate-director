# -*- coding: utf-8 -*-
from pathlib import Path

ui_path = Path("auditor/learning_ui.py")
lines = ui_path.read_text(encoding="utf-8").splitlines()

# Find line with 'with st.form("form_learn_new_case"'
start_idx = -1
for idx, line in enumerate(lines):
    if 'with st.form("form_learn_new_case"' in line:
        start_idx = idx
        break

assert start_idx != -1, "form_learn_new_case not found"
print("Found form_learn_new_case at line", start_idx + 1)

# From line start_idx + 1 until line with 'if btn_submit_learn:' (exclusive), indent by 4 spaces
# From 'if btn_submit_learn:' until end of function, indent by 4 spaces as well
new_lines = lines[:start_idx + 1]

in_form_body = True
for idx in range(start_idx + 1, len(lines)):
    line = lines[idx]
    if line.strip() == "":
        new_lines.append("")
        continue
    
    # Each line under with sub_tab_img should be properly indented:
    # with sub_tab_img has 8 spaces.
    # with st.form has 12 spaces.
    # inside with st.form has 16 spaces.
    # if btn_submit_learn has 12 spaces.
    # inside if btn_submit_learn has 16 spaces, 20 spaces, etc.
    
    if line.startswith("            f_col1, f_col2 = st.columns(2)"):
        in_form_body = True
        
    if in_form_body:
        if line.startswith("        if btn_submit_learn:"):
            in_form_body = False
            new_lines.append("            if btn_submit_learn:")
        elif line.startswith("            if btn_submit_learn:"):
            in_form_body = False
            new_lines.append("            if btn_submit_learn:")
        else:
            # Inside form: if it has 12 spaces, add 4 to make 16
            if line.startswith("            "):
                new_lines.append("    " + line)
            elif line.startswith("                "):
                new_lines.append("    " + line)
            else:
                new_lines.append("    " + line)
    else:
        # Inside if btn_submit_learn block
        if line.startswith("            "):
            new_lines.append("    " + line)
        elif line.startswith("                "):
            new_lines.append("    " + line)
        elif line.startswith("                    "):
            new_lines.append("    " + line)
        else:
            new_lines.append("    " + line)

fixed_content = "\n".join(new_lines) + "\n"
ui_path.write_text(fixed_content, encoding="utf-8")
print("Wrote fixed learning_ui.py")
