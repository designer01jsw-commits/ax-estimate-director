# -*- coding: utf-8 -*-
"""
app.py에 기준 견적서 + 비교 견적서 듀얼 직접 업로드 기능 추가 패치
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
app_file = ROOT_DIR / "app.py"

with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# Target block to replace: lines ~649 to ~786
old_block_start = """    # 2. 사이드바 - [1단계] 기준 견적서 데이터셋 선택 (에이전트 보유 DB)
    root_dir = Path(__file__).resolve().parent

    st.sidebar.markdown("---")
    st.sidebar.header("📁 [1단계] 기준견적서 데이터셋 (에이전트 DB)")"""

new_block = """    # 2. 사이드바 - [1단계] 기준 견적서 데이터셋 (에이전트 DB 또는 직접 업로드)
    root_dir = Path(__file__).resolve().parent

    is_dual_mode = (st.session_state.get("target_supply_mode_radio") == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드")

    st.sidebar.markdown("---")
    st.sidebar.header("📁 [1단계] 기준견적서 데이터셋")

    orig_file_input = None
    orig_file_name = ""
    selected_proj = None
    currency = "KRW"
    proj_id = "PROJ"

    if is_dual_mode:
        st.sidebar.info("💡 **[듀얼 직접 업로드] 모드 활성화됨**\\n\\n아래 **[2단계]**에서 기준 견적서와 비교 견적서 2개 파일을 모두 직접 업로드합니다.")
    else:
        sb_source_options = ["📚 에이전트 DB에서 선택", "📁 기준 견적서 직접 업로드 (.xlsx)"]
        baseline_source_mode = st.sidebar.radio(
            "기준 견적 공급 출처",
            sb_source_options,
            index=0,
            key="sb_baseline_source_mode"
        )

        if baseline_source_mode == "📚 에이전트 DB에서 선택":
            if not projects:
                st.sidebar.error("등록된 프로젝트가 없습니다.")
                return

            target_idx = 0
            if "selected_proj_id" in st.session_state:
                for idx, p in enumerate(projects):
                    if p.get("project_id") == st.session_state["selected_proj_id"]:
                        target_idx = idx
                        break
            else:
                has_studied = any(p.get("is_studied_asset") for p in projects)
                target_idx = 0 if has_studied else (3 if len(projects) > 3 else 0)

            target_idx = max(0, min(target_idx, len(projects) - 1))

            proj_labels = [f"[{p['project_id']}] {p['name']}" for p in projects]
            selected_idx = st.sidebar.selectbox(
                "기준 견적 데이터셋 선택 (광고주 컨펌 완료)",
                range(len(proj_labels)),
                format_func=lambda x: proj_labels[x],
                index=target_idx,
                key=f"sb_baseline_proj_select_{len(proj_labels)}"
            )
            selected_proj = projects[selected_idx]
            st.session_state["selected_proj_id"] = selected_proj.get("project_id")

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

            st.sidebar.caption("💡 새 기준견적서를 에이전트 DB에 영구 등록하려면 상단 모드에서 **[과거 실적 자산화]**를 이용하세요.")
        else:
            u_step1_orig = st.sidebar.file_uploader(
                "기준(확정) 견적서 파일 (.xlsx) *",
                type=["xlsx"],
                key="u_step1_direct_baseline",
                help="비교의 기준(확정/공인)으로 삼을 엑셀 견적서를 업로드하세요."
            )
            if u_step1_orig:
                orig_file_input = u_step1_orig
                orig_file_name = u_step1_orig.name
                clean_title = orig_file_name.replace(".xlsx", "").replace(".xls", "").replace("_", " ")
                proj_id = "P_CUSTOM_BASELINE"
                currency = "KRW"
                selected_proj = {
                    "project_id": proj_id,
                    "name": f"직접 업로드 기준: {clean_title}",
                    "client": "사용자 직접 공급",
                    "site": "현장 미정",
                    "currency": currency,
                    "status": "사용자 확정 기준",
                    "default_sheet": None
                }
                st.sidebar.success(f"기준 견적서 장착: {orig_file_name}")

    # 3. 사이드바 - [2단계] 대조·진단받을 견적서 공급 (사용자 업로드)
    st.sidebar.markdown("---")
    st.sidebar.header("📤 [2단계] 진단받을 견적서 공급")

    if "use_sample_change" not in st.session_state:
        st.session_state["use_sample_change"] = False

    target_mode_options = [
        "📁 신규 비교 견적서 직접 업로드 (1단계 기준과 대조)",
        "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드",
        "⚡ 준비된 실적 샘플로 빠른 체험"
    ]
    default_target_mode_idx = 2 if st.session_state.get("use_sample_change", False) else 0

    target_supply_mode = st.sidebar.radio(
        "견적서 공급 방식",
        target_mode_options,
        index=default_target_mode_idx,
        key="target_supply_mode_radio"
    )

    rev_file_input = None
    rev_file_name = ""

    if target_supply_mode == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드":
        st.session_state["use_sample_change"] = False
        st.sidebar.markdown("##### 1️⃣ 기준(확정) 견적서")
        u_dual_baseline = st.sidebar.file_uploader(
            "기준 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_dual_baseline_file",
            help="비교의 기준(확정/공인)이 될 엑셀 견적서 파일을 업로드하세요."
        )
        if u_dual_baseline:
            orig_file_input = u_dual_baseline
            orig_file_name = u_dual_baseline.name
            clean_b_name = orig_file_name.replace(".xlsx", "").replace(".xls", "").replace("_", " ")
            proj_id = "P_CUSTOM_DUAL_BASE"
            currency = "KRW"
            selected_proj = {
                "project_id": proj_id,
                "name": f"직접 업로드 기준: {clean_b_name}",
                "client": "사용자 직접 공급",
                "site": "사용자 지정 현장",
                "currency": currency,
                "status": "사용자 확정 기준",
                "default_sheet": None
            }
            st.sidebar.success(f"1️⃣ 기준 견적서 공급됨: `{orig_file_name}`")

        st.sidebar.markdown("##### 2️⃣ 비교(진단받을) 견적서")
        u_dual_target = st.sidebar.file_uploader(
            "비교 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_dual_target_file",
            help="기준 견적서와 대조하여 감리·진단받을 신규 견적서 파일입니다."
        )
        if u_dual_target:
            rev_file_input = u_dual_target
            rev_file_name = u_dual_target.name
            st.sidebar.success(f"2️⃣ 비교 견적서 공급됨: `{rev_file_name}`")

    elif target_supply_mode == "📁 신규 비교 견적서 직접 업로드 (1단계 기준과 대조)":
        st.session_state["use_sample_change"] = False
        rev_uploaded = st.sidebar.file_uploader(
            "진단받을 신규 견적서 파일 (.xlsx) *",
            type=["xlsx"],
            key="u_target_rev_file",
            help="선택된 광고주 컨펌 기준가이드와 비교 감리할 견적서 엑셀 파일을 업로드하세요."
        )
        if rev_uploaded:
            rev_file_input = rev_uploaded
            rev_file_name = rev_uploaded.name
            st.sidebar.success(f"신규 파일 공급됨: {rev_file_name}")
    else:
        st.session_state["use_sample_change"] = True
        sample_options = [
            ("전시_홍대점_변경내역.xlsx", "홍대점 전시 공사 변경 내역서 (전시 샘플)"),
            ("P001_변경내역.xlsx", "국립과학관 체험전시 변경 내역서 (키트 샘플)"),
            ("P002_변경내역.xlsx", "글로벌 과학 엑스포 변경 내역서 (USD 샘플)")
        ]
        if selected_proj and selected_proj.get("sample_change"):
            sc_name = selected_proj.get("sample_change")
            if not any(s[0] == sc_name for s in sample_options):
                sample_options.insert(0, (sc_name, f"{selected_proj.get('name')} 전용 변경내역서"))

        chosen_sample_idx = st.sidebar.selectbox(
            "체험할 실적 샘플 내역서 선택",
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
        if target_supply_mode == "📂 [듀얼 직접 업로드] 기준 견적서 & 비교 견적서 2개 모두 직접 업로드":
            st.markdown('''<div class="mc-stadium-card" style="padding: 32px 36px; margin: 18px 0 28px 0; border: 1.5px solid rgba(207, 69, 0, 0.4); background: var(--surface-lifted); box-shadow: var(--shadow-cushion);">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
<div style="display: flex; align-items: center; gap: 14px;">
<span style="font-size: 32px;">📂</span>
<div>
<div class="mc-eyebrow" style="margin-bottom: 4px;"><span class="mc-eyebrow-dot"></span><span>DUAL ESTIMATE UPLOAD MODE</span></div>
<h3 style="margin: 0; font-size: 20px; font-weight: 700; color: var(--ink-black);">기준 견적서 & 비교 견적서 듀얼 업로드 대기</h3>
<div style="font-size: 13.5px; color: var(--slate-gray); margin-top: 3px;">좌측 사이드바 [2단계]에서 <strong>1️⃣ 기준 견적서</strong>와 <strong>2️⃣ 비교 견적서</strong> 엑셀 파일 2개를 모두 업로드해 주세요.</div>
</div>
</div>
<span class="mc-pill-chip mc-chip-orange" style="font-size: 12px; font-weight: 600;">● 파일 공급 대기 중</span>
</div>
</div>''', unsafe_allow_html=True)
        else:
            st.info("💡 사이드바 [1단계]에서 기준견적서 프로젝트를 선택하거나 기준 견적서 XLSX를 업로드해 주세요.")
        return"""

# End anchor to find in old app.py
old_block_end_anchor = """    # 기준 파일 검증
    if not orig_file_input:
        st.info("💡 사이드바 [1단계]에서 기준견적서 프로젝트를 선택하거나 기준 견적서 XLSX를 업로드해 주세요.")
        return"""

start_pos = content.find(old_block_start)
end_pos = content.find(old_block_end_anchor)

if start_pos != -1 and end_pos != -1:
    end_pos += len(old_block_end_anchor)
    content = content[:start_pos] + new_block + content[end_pos:]
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("app.py successfully patched for dual upload mode!")
else:
    print(f"Error: anchors not found! start_pos={start_pos}, end_pos={end_pos}")
    sys.exit(1)
