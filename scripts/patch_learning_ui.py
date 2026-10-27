# -*- coding: utf-8 -*-
from pathlib import Path

ui_path = Path("auditor/learning_ui.py")
content = ui_path.read_text(encoding="utf-8")

# 1. Update import
old_import = """from auditor.learning_engine import (
    load_learned_cases,
    save_new_learned_case,
    find_similar_learned_cases,
    get_learning_statistics,
    IMAGES_DIR
)"""

new_import = """from auditor.learning_engine import (
    load_learned_cases,
    save_new_learned_case,
    study_and_assetize_excel_estimate,
    find_similar_learned_cases,
    get_learning_statistics,
    IMAGES_DIR
)"""

assert old_import in content, "old_import not found"
content = content.replace(old_import, new_import, 1)

# 2. Update tab_ingest to contain the XLSX study form + visual ingest form
old_ingest_block = """    # 2. 신규 실적 학습 등록
    with tab_ingest:
        st.subheader("➕ 과거 실적 데이터를 AI 에이전트에 영구 학습 등록")
        st.markdown(
            "이미 제작 완료된 프로젝트의 **사진/도면**과 **최종 정산 금액**을 입력하면, "
            "AI가 시각적 특징과 단위 단가를 벡터화하여 향후 견적 감리 및 생성에 영구 반영합니다."
        )

        with st.form("form_learn_new_case", clear_on_submit=False):"""

new_ingest_block = """    # 2. 신규 실적 학습 등록
    with tab_ingest:
        sub_tab_xlsx, sub_tab_img = st.tabs([
            "📁 클라이언트 확정 견적서(XLSX) 스터디 & 기준 DB 등록 (권장)",
            "📷 현장 사진/도면 기반 비전 AI 실적 등록"
        ])

        # A. 클라이언트 확정 견적서 XLSX 스터디 및 기준 자산 등록
        with sub_tab_xlsx:
            st.subheader("📁 클라이언트 확정 견적서(XLSX) 심층 스터디 & 기준 DB 자산화")
            st.markdown(
                "클라이언트/광고주가 최종 컨펌 완료한 견적서(XLSX)를 업로드하면, AI 에이전트가 "
                "**7대 공종별 원가 구조, 품목별 기준 단가, 투입 공수**를 정밀 스터디하여 "
                "사이드바의 **[기준 견적서 데이터셋 선택]**에 새로운 공인 기준 프로젝트로 영구 등록합니다.<br>"
                "등록된 프로젝트는 향후 협력업체나 현장에서 올라오는 **신규 견적서와의 정밀 비교·대조 기준(Baseline)**으로 즉시 사용됩니다.",
                unsafe_allow_html=True
            )

            with st.form("form_study_client_confirmed_excel", clear_on_submit=False):
                fx1, fx2 = st.columns(2)
                with fx1:
                    ex_name = st.text_input("기준 프로젝트명 *", placeholder="예: 2026 하반기 플래그십 체험존 확정 견적서", key="ex_study_name")
                    ex_client = st.text_input("발주처 / 클라이언트 *", value="삼성전자 / 제일기획", key="ex_study_client")
                with fx2:
                    ex_venue = st.text_input("설치 현장 / 베뉴", value="강남 / 홍대 / 코엑스", key="ex_study_venue")
                    ex_curr = st.selectbox("통화", ["KRW", "USD"], index=0, key="ex_study_curr")

                ex_file = st.file_uploader(
                    "클라이언트 최종 컨펌 견적서 파일 (.xlsx) *",
                    type=["xlsx"],
                    key="u_client_confirmed_xlsx",
                    help="클라이언트가 최종 승인한 엑셀 견적서 파일을 업로드하세요."
                )

                btn_study_submit = st.form_submit_button("🚀 클라이언트 확정 견적서 스터디 및 기준 자산 등록", type="primary")

            if btn_study_submit:
                if not ex_name:
                    st.error("프로젝트명을 입력해 주세요.")
                elif not ex_file:
                    st.error("클라이언트 확정 견적서 XLSX 파일을 업로드해 주세요.")
                else:
                    try:
                        file_bytes = ex_file.getvalue()
                        proj_rec, decomp, items = study_and_assetize_excel_estimate(
                            excel_bytes=file_bytes,
                            file_name=ex_file.name,
                            project_name=ex_name,
                            client=ex_client,
                            venue=ex_venue,
                            currency=ex_curr
                        )
                        st.success(
                            f"🎉 **스터디 및 자산화 완료!** 「{ex_name}」 프로젝트가 에이전트 기준 데이터베이스에 성공적으로 등록되었습니다!\\n\\n"
                            f"- **신규 프로젝트 ID:** `{proj_rec['project_id']}`\\n"
                            f"- **확정 총 예산:** `₩{proj_rec['total_budget']:,d}` ({len(items)}개 품목 스터디 완료)\\n"
                            f"- **학습 시트:** `{proj_rec['default_sheet']}`\\n\\n"
                            f"👉 **[기준 견적서 정밀 감리]** 모드로 이동하시면 '기준 데이터셋 선택' 드롭다운에서 방금 등록한 프로젝트를 즉시 선택하여 신규 견적서와 비교 감리할 수 있습니다."
                        )
                    except Exception as e:
                        st.error(f"❌ 견적서 스터디 실패: {str(e)}")

        # B. 사진/도면 기반 비전 AI 실적 등록
        with sub_tab_img:
            st.subheader("📷 현장 사진/도면 기반 과거 실적 영구 학습 등록")
            st.markdown(
                "이미 제작 완료된 프로젝트의 **사진/도면**과 **최종 정산 금액**을 입력하면, "
                "AI가 시각적 특징과 단위 단가를 벡터화하여 향후 견적 감리 및 생성에 영구 반영합니다."
            )

            with st.form("form_learn_new_case", clear_on_submit=False):"""

assert old_ingest_block in content, "old_ingest_block not found"
content = content.replace(old_ingest_block, new_ingest_block, 1)

ui_path.write_text(content, encoding="utf-8")
print("SUCCESS: auditor/learning_ui.py successfully patched with client confirmed estimate study tab!")
