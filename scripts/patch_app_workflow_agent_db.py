# -*- coding: utf-8 -*-
"""Patch app.py to align with the agent-held database philosophy:
1) Step 1: Agent Confirmed Baseline Database Selection (No manual baseline upload needed)
2) Step 2: Target Candidate Estimate Upload for Diagnosis
"""

import re
from pathlib import Path

app_path = Path("app.py")
content = app_path.read_text(encoding="utf-8")

old_sidebar_step1_and_2_pattern = re.compile(
    r"# 2\. 사이드바 - \[1단계\] 광고주 컨펌 기준가이드 선택 \(Baseline\).*?"
    r"if target_supply_mode == \"📁 대조 견적서 직접 업로드 \(기본\)\":",
    re.DOTALL
)

new_sidebar_code = """# 2. 사이드바 - [1단계] 기준 견적서 데이터셋 선택 (에이전트 보유 DB)
    root_dir = Path(__file__).resolve().parent

    st.sidebar.markdown("---")
    st.sidebar.header("📁 [1단계] 기준견적서 데이터셋 (에이전트 DB)")
    if not projects:
        st.sidebar.error("등록된 프로젝트가 없습니다.")
        return

    proj_labels = [f"[{p['project_id']}] {p['name']}" for p in projects]
    selected_idx = st.sidebar.selectbox(
        "기준 견적 데이터셋 선택 (광고주 컨펌 완료)",
        range(len(proj_labels)),
        format_func=lambda x: proj_labels[x],
        index=3 if len(proj_labels) > 3 else 0  # 기준견적서4 기본 포커스 지원
    )
    selected_proj = projects[selected_idx]

    currency = selected_proj.get("currency", "KRW")
    proj_id = selected_proj.get("project_id", "PROJ")

    sample_est_str = selected_proj.get("sample_estimate") or ""
    candidate_orig = []
    if sample_est_str:
        if Path(sample_est_str).is_absolute():
            candidate_orig.append(Path(sample_est_str))
        candidate_orig.append(root_dir / "data" / sample_est_str)
        candidate_orig.append(root_dir / "data" / "samples" / sample_est_str)
    candidate_orig.extend([
        root_dir / "data" / "기준견적서4_전시_광고주컨펌.xlsx",
        root_dir / "data" / "samples" / "기준견적서4_전시_광고주컨펌.xlsx",
        root_dir / "data" / "samples" / "전시 광고주컨펌완료 견적서 (1).xlsx",
        root_dir / "data" / "samples" / "전시_광고주컨펌완료_기준견적서.xlsx",
        root_dir / "data" / "samples" / "P001_최초견적.xlsx"
    ])
    orig_path = next((p for p in candidate_orig if p and p.exists()), None)
    orig_file_input = str(orig_path) if orig_path and orig_path.exists() else None
    orig_file_name = orig_path.name if orig_path and orig_path.exists() else ""

    with st.sidebar.expander("📌 에이전트 기준 메타데이터", expanded=False):
        st.write(f"**프로젝트 ID:** {proj_id}")
        st.write(f"**기준 파일명:** `{orig_file_name}`")
        st.write(f"**발주처:** {selected_proj.get('client', '-')}")
        st.write(f"**현장/베뉴:** {selected_proj.get('site', '-')}")
        st.write(f"**통화:** {currency}")
        st.write(f"**상태:** {selected_proj.get('status', '광고주 컨펌 완료')} ✅")
        if selected_proj.get("total_budget"):
            st.write(f"**확정 예산:** ₩{selected_proj['total_budget']:,d}")
        if selected_proj.get("item_count"):
            st.write(f"**스터디 품목수:** {selected_proj['item_count']}건")

    st.sidebar.caption("💡 새 기준견적서를 에이전트 DB에 추가하려면 상단 모드에서 **[과거 실적 자산화]**를 이용해 엑셀을 스터디하세요.")

    # 3. 사이드바 - [2단계] 대조·진단받을 견적서 공급 (사용자 업로드)
    st.sidebar.markdown("---")
    st.sidebar.header("📤 [2단계] 진단받을 견적서 공급 (Target)")

    if "use_sample_change" not in st.session_state:
        st.session_state["use_sample_change"] = False

    target_mode_options = ["📁 진단받을 견적서 직접 업로드 (기본)", "📋 내장 샘플 견적서로 빠른 체험"]
    default_target_mode_idx = 1 if st.session_state.get("use_sample_change", False) else 0

    target_supply_mode = st.sidebar.radio(
        "견적서 공급 방식",
        target_mode_options,
        index=default_target_mode_idx,
        key="target_supply_mode_radio"
    )

    rev_file_input = None
    rev_file_name = ""

    sample_options = [
        ("전시_홍대점_변경내역.xlsx", "홍대점 전시 공사 변경 내역서 (전시 샘플)"),
        ("P001_변경내역.xlsx", "국립과학관 체험전시 변경 내역서 (키트 샘플)"),
        ("P002_변경내역.xlsx", "글로벌 과학 엑스포 변경 내역서 (USD 샘플)")
    ]
    if selected_proj and selected_proj.get("sample_change"):
        sc_name = selected_proj.get("sample_change")
        if not any(s[0] == sc_name for s in sample_options):
            sample_options.insert(0, (sc_name, f"{selected_proj.get('name')} 전용 변경내역서"))

    if target_supply_mode == "📁 진단받을 견적서 직접 업로드 (기본)":"""

assert old_sidebar_step1_and_2_pattern.search(content), "Failed to match old_sidebar_step1_and_2_pattern"
content = old_sidebar_step1_and_2_pattern.sub(new_sidebar_code, content, count=1)

# Also update the uploader label in step 2
old_uploader = 'st.sidebar.file_uploader(\n            "대조·감리할 견적서 파일 (.xlsx) *",'
new_uploader = 'st.sidebar.file_uploader(\n            "진단받을 신규 견적서 파일 (.xlsx) *",'
content = content.replace(old_uploader, new_uploader, 1)

app_path.write_text(content, encoding="utf-8")
print("SUCCESS: app.py successfully patched for agent-database driven workflow!")
