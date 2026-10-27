# -*- coding: utf-8 -*-
"""Patch app.py to implement reference baseline + manual upload workflow and remove approval sheet banner."""

import re
from pathlib import Path

app_path = Path("app.py")
content = app_path.read_text(encoding="utf-8")

# 1. Target block for data loading (from "# 2. 사이드바 프로젝트 선택" to "if not orig_file_input or not rev_file_input: ... return")
old_data_load_pattern = re.compile(
    r"# 2\. 사이드바 프로젝트 선택.*?"
    r"if not orig_file_input or not rev_file_input:.*?"
    r"return\n",
    re.DOTALL
)

new_data_load_code = """# 2. 사이드바 - [1단계] 광고주 컨펌 기준가이드 선택 (Baseline)
    root_dir = Path(__file__).resolve().parent

    st.sidebar.markdown("---")
    st.sidebar.header("📁 [1단계] 광고주 컨펌 기준가이드 (Baseline)")
    if not projects:
        st.sidebar.error("등록된 프로젝트가 없습니다.")
        return

    base_guide_source = st.sidebar.radio(
        "기준가이드 지정 방식",
        ["광고주 컨펌 완료 데이터셋 (기본)", "내 기준견적서 직접 업로드"],
        index=0,
        key="base_guide_source_radio"
    )

    orig_file_input = None
    orig_file_name = ""
    selected_proj = None

    if base_guide_source == "광고주 컨펌 완료 데이터셋 (기본)":
        proj_labels = [f"[{p['project_id']}] {p['name']}" for p in projects]
        selected_idx = st.sidebar.selectbox(
            "기준견적서 데이터셋 선택",
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
        if orig_path and orig_path.exists():
            orig_file_input = str(orig_path)
            orig_file_name = orig_path.name

        with st.sidebar.expander("📌 기준가이드 메타데이터", expanded=False):
            st.write(f"**프로젝트 ID:** {proj_id}")
            st.write(f"**기준 파일명:** `{orig_file_name}`")
            st.write(f"**발주처:** {selected_proj.get('client', '-')}")
            st.write(f"**현장/베뉴:** {selected_proj.get('site', '-')}")
            st.write(f"**통화:** {currency}")
            st.write(f"**상태:** {selected_proj.get('status', '광고주 컨펌 완료')}")
    else:
        # 사용자 기준견적서 직접 업로드
        selected_proj = {
            "project_id": "CUSTOM_BASE",
            "name": "사용자 직접 업로드 기준견적서",
            "client": "직접 업로드",
            "site": "현장 미정",
            "currency": "KRW",
            "status": "사용자 지정"
        }
        currency = "KRW"
        proj_id = "CUSTOM_BASE"
        uploaded_base = st.sidebar.file_uploader(
            "기준 견적서 파일 업로드 (.xlsx)",
            type=["xlsx"],
            key="u_custom_base_file"
        )
        if uploaded_base:
            orig_file_input = uploaded_base
            orig_file_name = uploaded_base.name

    # 3. 사이드바 - [2단계] 대조·감리할 견적서 공급 (Target)
    st.sidebar.markdown("---")
    st.sidebar.header("📤 [2단계] 대조 견적서 공급 (Target)")

    if "use_sample_change" not in st.session_state:
        st.session_state["use_sample_change"] = False

    target_mode_options = ["📁 대조 견적서 직접 업로드 (기본)", "📋 내장 샘플 견적서로 빠른 체험"]
    default_target_mode_idx = 1 if st.session_state.get("use_sample_change", False) else 0

    target_supply_mode = st.sidebar.radio(
        "대조 견적서 공급 방식",
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

    if target_supply_mode == "📁 대조 견적서 직접 업로드 (기본)":
        st.session_state["use_sample_change"] = False
        rev_uploaded = st.sidebar.file_uploader(
            "대조·감리할 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_target_rev_file",
            help="선택된 광고주 컨펌 기준가이드와 비교 감리할 견적서 엑셀 파일을 업로드하세요."
        )
        if rev_uploaded:
            rev_file_input = rev_uploaded
            rev_file_name = rev_uploaded.name
    else:
        st.session_state["use_sample_change"] = True
        chosen_sample_idx = st.sidebar.selectbox(
            "체험할 샘플 변경 내역서 선택",
            range(len(sample_options)),
            format_func=lambda i: sample_options[i][1],
            key="chosen_sample_selectbox"
        )
        chosen_sample_fname = sample_options[chosen_sample_idx][0]
        candidate_sample = [
            root_dir / "data" / chosen_sample_fname,
            root_dir / "data" / "samples" / chosen_sample_fname,
            root_dir / "data" / "samples" / "전시_홍대점_변경내역.xlsx",
            root_dir / "data" / "samples" / "P001_변경내역.xlsx"
        ]
        sample_path = next((p for p in candidate_sample if p and p.exists()), None)
        if sample_path and sample_path.exists():
            rev_file_input = str(sample_path)
            rev_file_name = sample_path.name

    # 기준 파일 검증
    if not orig_file_input:
        st.info("💡 사이드바 [1단계]에서 기준견적서 프로젝트를 선택하거나 기준 견적서 XLSX를 업로드해 주세요.")
        return

    # 대조 파일 미공급 시 메인 가이드 카드 안내
    if not rev_file_input:
        st.markdown(f\"\"\"
        <div class="mc-card" style="padding: 32px 36px; margin: 24px 0; border: 2px dashed var(--signal-orange); background: var(--surface-lifted); box-shadow: 0 4px 24px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 26px;">⚖️</span>
                    <div>
                        <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: var(--ink-black);">
                            광고주 컨펌 기준가이드 준비 완료
                        </h3>
                        <div style="font-size: 13px; color: var(--slate-gray); margin-top: 2px;">
                            대조·감리할 견적서를 공급하시면 실시간 9대 정밀 진단실 및 단가·인건비 대조가 즉시 시작됩니다.
                        </div>
                    </div>
                </div>
                <span class="mc-pill-chip mc-chip-orange" style="font-size: 12px; font-weight: 600;">● 기준가이드 장착됨</span>
            </div>

            <div style="background: var(--canvas-stone); border: 1px solid var(--border-stone); border-radius: 16px; padding: 16px 20px; margin-bottom: 24px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 13px;">
                    <div><span style="color: var(--slate-gray);">기준 프로젝트:</span> <strong style="color: var(--ink-black);">{selected_proj.get('name', '기준견적서')}</strong></div>
                    <div><span style="color: var(--slate-gray);">기준 파일명:</span> <code style="background: var(--surface-lifted); padding: 2px 6px; border-radius: 6px; color: var(--ink-black);">{orig_file_name}</code></div>
                    <div><span style="color: var(--slate-gray);">발주처 / 베뉴:</span> <strong style="color: var(--ink-black);">{selected_proj.get('client', '-')} / {selected_proj.get('site', '-')}</strong></div>
                    <div><span style="color: var(--slate-gray);">통화 / 상태:</span> <strong style="color: var(--ink-black);">{currency}</strong> · <span style="color: #2E7D32; font-weight: 700;">광고주 컨펌 완료 ✅</span></div>
                </div>
            </div>

            <div style="font-size: 14px; color: var(--ink-black); line-height: 1.6; margin-bottom: 20px;">
                <strong>💡 대조 방법 안내:</strong> 좌측 사이드바 <strong>[2단계]</strong> 또는 아래 영역에서 감리하고자 하는 견적서(<strong>.xlsx</strong>)를 업로드해 주세요.<br>
                양쪽 파일의 시트명을 1:1 자동 감지하여 동일 시트 간 단가·수량·인건비 정밀 대조 및 6대 공공기준 소명 진단을 수행합니다.
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)

        col_main_up, col_main_demo = st.columns([1.2, 1])
        with col_main_up:
            main_direct_upload = st.file_uploader(
                "📥 대조·감리할 견적서 파일 바로 업로드 (.xlsx)",
                type=["xlsx"],
                key="u_main_drag_drop_rev",
                help="기준 가이드와 비교 감리할 엑셀 파일을 업로드하세요."
            )
            if main_direct_upload:
                rev_file_input = main_direct_upload
                rev_file_name = main_direct_upload.name
                st.rerun()

        with col_main_demo:
            st.markdown(\"\"\"
            <div style="padding: 16px 20px; border-radius: 16px; background: var(--canvas-stone); border: 1px solid var(--border-stone); height: 100%;">
                <div style="font-size: 13px; font-weight: 600; color: var(--ink-black); margin-bottom: 6px;">
                    📋 테스트용 견적서 파일이 없으신가요?
                </div>
                <div style="font-size: 12px; color: var(--slate-gray); margin-bottom: 14px;">
                    사전에 준비된 실제 홍대점 전시 변경 내역서 샘플을 즉시 불러와 9대 진단실과 신호등 감리를 체험해 보세요.
                </div>
            \"\"\", unsafe_allow_html=True)
            if st.button("⚡ 샘플 견적서로 지금 즉시 감리 체험하기", use_container_width=True, type="primary"):
                st.session_state["use_sample_change"] = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if not rev_file_input:
            return
"""

assert old_data_load_pattern.search(content), "Failed to match old_data_load_pattern"
content = old_data_load_pattern.sub(new_data_load_code, content, count=1)

# 2. Target block for approval sheet warning banner (lines 839-843)
old_approval_pattern = re.compile(
    r'elif "변경승인" in wb_rev\.sheetnames:\s*'
    r'approval_records, appr_warn = read_approval_sheet\(wb_rev\["변경승인"\], rev_file_name, "변경승인"\)\s*'
    r'else:\s*'
    r'st\.info\("ℹ️ ‘변경승인’ 시트가 감지되지 않아 변경 항목의 승인 여부가 기본 \'미확인\'으로 표시됩니다\."\)',
    re.DOTALL
)

new_approval_code = """elif "변경승인" in wb_rev.sheetnames:
            try:
                approval_records, appr_warn = read_approval_sheet(wb_rev["변경승인"], rev_file_name, "변경승인")
            except Exception:
                approval_records = []"""

assert old_approval_pattern.search(content), "Failed to match old_approval_pattern"
content = old_approval_pattern.sub(new_approval_code, content, count=1)

# 3. Target block for sheet matching announcement on line 870
old_sheet_banner = 'st.markdown(f"**현재 대조 시트:** `{orig_file_name}` [`{sheet_orig_selected}`] ⟷ `{rev_file_name}` [`{sheet_rev_selected}`]")'
new_sheet_banner = """st.markdown(f\"\"\"
        <div style="display: flex; align-items: center; justify-content: space-between; background: var(--surface-lifted); border: 1px solid var(--border-stone); border-radius: 20px; padding: 12px 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span style="font-size: 16px;">📑</span>
                <span style="font-size: 13px; font-weight: 700; color: var(--ink-black);">대조 감리 매칭</span>
                <span class="mc-pill-chip mc-chip-black" style="font-size: 12px;">기준 가이드: {orig_file_name} ❯ <strong>{sheet_orig_selected}</strong></span>
                <span style="color: var(--signal-orange); font-weight: 700; font-size: 14px;">⟷</span>
                <span class="mc-pill-chip mc-chip-orange" style="font-size: 12px;">대조 대상: {rev_file_name} ❯ <strong>{sheet_rev_selected}</strong></span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 12px; color: var(--slate-gray);">실시간 1:1 대조 감리 중</span>
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #2E7D32;"></span>
            </div>
        </div>
        \"\"\", unsafe_allow_html=True)"""

assert old_sheet_banner in content, "Failed to match old_sheet_banner"
content = content.replace(old_sheet_banner, new_sheet_banner, 1)

app_path.write_text(content, encoding="utf-8")
print("SUCCESS: app.py successfully patched!")
