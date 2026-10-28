# -*- coding: utf-8 -*-
"""
견적감독관 과거 실적 학습 및 자산화 스튜디오 Streamlit UI
"""

import io
import streamlit as st
import pandas as pd
from PIL import Image

from auditor.learning_engine import (
    load_learned_cases,
    save_new_learned_case,
    study_and_assetize_excel_estimate,
    preview_excel_estimate,
    find_similar_learned_cases,
    get_learning_statistics,
    IMAGES_DIR
)
from auditor.vision_estimator import generate_preset_sample_image

def render_learning_studio_ui(currency: str = "KRW"):
    """과거 실적 학습 및 자산화 스튜디오 화면을 렌더링합니다."""
    st.markdown("### 🧠 과거 실적 자산화 & AI 학습 스튜디오 (AI Learning Studio)")
    st.markdown(
        "기존에 성공적으로 제작 및 정산이 완료된 **전시 부스 및 키트 실적(확정견적서 XLSX, 현장 사진, 최종 계약금액, 세부 사양)**을 "
        "에이전트에 직접 학습시켜 **제일기획 고유의 견적 인텔리전스(Data Flywheel)**를 구축합니다.<br>"
        "학습된 실적은 좌측 사이드바의 **[1단계: 기준 견적서 데이터셋 선택]**에 새로운 공인 기준으로 영구 등록되어 "
        "신규 견적서와의 정밀 비교·감리에 즉시 활용됩니다.",
        unsafe_allow_html=True
    )

    stats = get_learning_statistics()

    # 상단 학습 현황 메트릭
    st.markdown("##### 📈 현재 AI 학습 자산 통계")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 누적 학습 실적 수", f"{stats['total_cases']}개 프로젝트")
    c2.metric("💰 누적 학습 정산 금액", f"₩{stats['total_learned_budget']:,d}")
    c3.metric("🎯 단가 예측 신뢰 지수", stats["model_confidence"])
    c4.metric("🔍 검색 알고리즘", "다차원 코사인 RAG 가동")

    st.markdown("---")

    # 탭 1: 학습 라이브러리 갤러리 / 탭 2: 신규 실적 학습 등록
    tab_gallery, tab_ingest = st.tabs([
        f"📚 AI가 학습한 실적 라이브러리 ({stats['total_cases']}건)",
        "➕ 새 프로젝트 실적 학습시키기 (확정견적서 분석 & DB 등록)"
    ])

    # 1. 학습 실적 라이브러리 갤러리
    with tab_gallery:
        st.subheader("📚 현재 AI 지식베이스에 영구 학습된 실적 목록")
        st.caption("신규 견적서 작성 및 비전 AI 산출 시, 아래 과거 실적들과의 유사도를 자동 비교하여 적정가를 제시합니다.")

        cases = load_learned_cases()
        for idx, c in enumerate(cases):
            with st.expander(f"📁 [{c.get('project_type', '전시/키트')}] {c['name']} (정산액: ₩{c['settled_amount']:,d})", expanded=(idx < 2)):
                col_img, col_info = st.columns([1, 2])
                
                with col_img:
                    # 이미지 렌더링
                    img_file = c.get("image_file")
                    img_path = IMAGES_DIR / img_file if img_file else None
                    if img_path and img_path.exists():
                        st.image(str(img_path), caption=c["name"], use_container_width=True)
                    else:
                        preset_key = c.get("preset_img_key", "S26_KIT")
                        p_bytes = generate_preset_sample_image(preset_key)
                        st.image(p_bytes, caption=f"학습 청사진: {c['name']}", use_container_width=True)

                with col_info:
                    st.markdown(f"**발주처/광고주:** `{c.get('client', '제일기획')}` | **등록일자:** `{c.get('created_at', '-')}`")
                    st.markdown(f"**총 정산 금액:** :blue[**₩{c['settled_amount']:,d}**] (VAT 별도)")
                    st.markdown(f"**단위당 제작 단가:** **₩{c.get('unit_cost', 0):,d}** ({c.get('unit_label', '단위당')})")
                    st.markdown(f"**규모 및 사양:** `{c.get('scale', '-')}` | `{c.get('tier', '-')}` | **투입 인력:** `{c.get('labor_md', 0)} M/D`")
                    st.markdown(f"**적용 주요 자재:** {', '.join(c.get('materials', []))}")
                    st.markdown(f"**핵심 사양 내역:** {c.get('key_specs', '-')}")
                    st.markdown(f"**공공 기준 연계:** `{c.get('benchmark_cites', '-')}`")

    # 2. 신규 실적 학습 등록
    with tab_ingest:
        sub_tab_xlsx, sub_tab_img = st.tabs([
            "📁 클라이언트 확정 견적서(XLSX) 자동 분석 & 기준 DB 등록 (권장)",
            "📷 현장 사진/도면 기반 비전 AI 실적 등록"
        ])

        # A. 클라이언트 확정 견적서 XLSX 스터디 및 기준 자산 등록
        with sub_tab_xlsx:
            st.subheader("📁 클라이언트 확정 견적서(XLSX) 심층 스터디 & 기준 DB 자산화")
            st.markdown(
                "클라이언트/광고주가 최종 컨펌 완료한 견적서(XLSX)를 업로드하면, AI 에이전트가 "
                "**7대 공종별 원가 구조, 품목별 기준 단가, 투입 공수**를 정밀 스터디하여 "
                "사이드바의 **[1단계: 기준 견적서 데이터셋 선택]**에 새로운 공인 기준 프로젝트로 영구 등록합니다.<br>"
                "등록된 프로젝트는 향후 협력업체나 현장에서 올라오는 **신규 견적서와의 정밀 비교·대조 기준(Baseline)**으로 즉시 사용됩니다.",
                unsafe_allow_html=True
            )

            # 업로드 즉시 AI 실시간 분석 리포트 연출
            ex_file = st.file_uploader(
                "클라이언트 최종 컨펌 확정견적서 파일 (.xlsx, .xls) *",
                type=["xlsx", "xls"],
                key="u_client_confirmed_xlsx",
                help="광고주/클라이언트가 최종 승인한 엑셀 견적서 파일을 업로드하세요."
            )

            preview_data = None
            default_proj_name = ""
            selected_sheet_override = None

            if ex_file is not None:
                cache_key = f"prev_cache_{ex_file.name}_{ex_file.size}"
                if cache_key not in st.session_state:
                    with st.spinner("AI가 확정 견적서를 정밀 분석 중입니다..."):
                        try:
                            file_bytes = ex_file.getvalue()
                            st.session_state[cache_key] = preview_excel_estimate(file_bytes, ex_file.name)
                        except Exception as ex_prev:
                            st.warning(f"견적서 사전 분석 중 참고 알림: {str(ex_prev)}")
                            st.session_state[cache_key] = None

                preview_data = st.session_state.get(cache_key)
                clean_title = ex_file.name.replace(".xlsx", "").replace(".xls", "").replace("_", " ")
                default_proj_name = f"{clean_title}"

                if preview_data:
                    # AI 실시간 분석 리포트 카드 (Mastercard Editorial Stadium Card)
                    st.markdown(f"""<div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone); padding: 20px 24px; margin: 16px 0;">
<div class="mc-eyebrow" style="margin-bottom: 6px;"><span class="mc-eyebrow-dot"></span><span>AI ESTIMATE AUTO-ANALYSIS REPORT</span></div>
<div style="font-size: 16px; font-weight: 700; color: var(--ink-black); margin-bottom: 8px;">📊 업로드 견적서 실시간 자동 분석 완료</div>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 10px;">
<div style="background: var(--bg-putty); padding: 12px; border-radius: 8px;">
<div style="font-size: 11px; color: var(--slate-gray); font-weight: 600;">총 확정 예산</div>
<div style="font-size: 17px; font-weight: 800; color: var(--accent-orange);">₩{preview_data['total_budget']:,d}</div>
</div>
<div style="background: var(--bg-putty); padding: 12px; border-radius: 8px;">
<div style="font-size: 11px; color: var(--slate-gray); font-weight: 600;">분석 품목 수</div>
<div style="font-size: 17px; font-weight: 800; color: var(--ink-black);">{preview_data['item_count']}개 항목</div>
</div>
<div style="background: var(--bg-putty); padding: 12px; border-radius: 8px;">
<div style="font-size: 11px; color: var(--slate-gray); font-weight: 600;">분석 대상 시트</div>
<div style="font-size: 15px; font-weight: 700; color: #1E40AF;">{preview_data['selected_sheet']}</div>
</div>
</div>
<div style="font-size: 12.5px; color: var(--slate-gray); margin-top: 10px;">
<strong>감지된 주요 자재:</strong> {', '.join(preview_data['materials'])}
</div>
</div>""", unsafe_allow_html=True)

                    if len(preview_data["sheets"]) > 1:
                        selected_sheet_override = st.selectbox(
                            "학습할 시트 선택 (자동 감지된 최적 시트 기본값)",
                            preview_data["sheets"],
                            index=preview_data["sheets"].index(preview_data["selected_sheet"]) if preview_data["selected_sheet"] in preview_data["sheets"] else 0,
                            key="sb_study_sheet_choice"
                        )
                    else:
                        selected_sheet_override = preview_data["selected_sheet"]

            with st.form("form_study_client_confirmed_excel", clear_on_submit=False):
                fx1, fx2 = st.columns(2)
                with fx1:
                    ex_name = st.text_input("기준 프로젝트명 *", value=default_proj_name or "2026 하반기 플래그십 체험존 확정 견적서", key="ex_study_name")
                    ex_client = st.text_input("발주처 / 클라이언트 *", value="삼성전자 / 제일기획", key="ex_study_client")
                with fx2:
                    ex_venue = st.text_input("설치 현장 / 베뉴", value="강남 / 홍대 / 코엑스", key="ex_study_venue")
                    ex_curr = st.selectbox("통화", ["KRW", "USD"], index=0, key="ex_study_curr")

                ex_img = st.file_uploader(
                    "📷 (선택) 현장 사진 또는 3D 도면 이미지 첨부",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="u_study_confirmed_img"
                )

                btn_study_submit = st.form_submit_button("🚀 AI 에이전트에 실적 학습 및 지식베이스 업데이트", type="primary")

            if btn_study_submit:
                if not ex_file:
                    st.error("클라이언트 확정 견적서 XLSX 파일을 먼저 업로드해 주세요.")
                elif not ex_name:
                    st.error("프로젝트명을 입력해 주세요.")
                else:
                    try:
                        file_bytes = ex_file.getvalue()
                        img_bytes = ex_img.getvalue() if ex_img else None
                        proj_rec, decomp, items = study_and_assetize_excel_estimate(
                            excel_bytes=file_bytes,
                            file_name=ex_file.name,
                            project_name=ex_name,
                            client=ex_client,
                            venue=ex_venue,
                            currency=ex_curr,
                            sheet_name=selected_sheet_override,
                            image_bytes=img_bytes
                        )
                        st.session_state["selected_proj_id"] = proj_rec["project_id"]
                        st.session_state["latest_studied_proj"] = proj_rec

                        st.success(
                            f"🎉 **학습 성공!** 「{ex_name}」 실적이 AI 견적감독관의 공인 기준 데이터셋에 성공적으로 등록되었습니다!\n\n"
                            f"- **신규 프로젝트 ID:** `{proj_rec['project_id']}`\n"
                            f"- **확정 총 예산:** `₩{proj_rec['total_budget']:,d}` ({len(items)}개 품목 스터디 완료)\n"
                            f"- **학습 시트:** `{proj_rec['default_sheet']}`\n\n"
                            f"좌측 사이드바 **[1단계] 기준 견적서 데이터셋 선택** 목록에 1순위로 즉시 등록 및 자동 선택되었습니다."
                        )

                    except Exception as e:
                        st.error(f"❌ 견적서 스터디 실패: {str(e)}")

            # 바로가기 버튼 제공
            if st.session_state.get("selected_proj_id") and st.session_state.get("latest_studied_proj"):
                p_cur = st.session_state["latest_studied_proj"]
                st.markdown("---")
                st.info(f"💡 방금 등록된 기준 프로젝트: **{p_cur.get('name')}** (예산: ₩{p_cur.get('total_budget', 0):,d})")
                if st.button("⚖️ [1단계] 방금 학습한 기준견적서로 신규 견적 비교·감리 시작하기", type="primary", use_container_width=True, key="btn_jump_to_audit_mode"):
                    st.session_state["app_main_mode"] = "⚖️ 기준 견적서 정밀 감리 & 진단"
                    st.session_state["selected_proj_id"] = p_cur["project_id"]
                    st.rerun()

        # B. 사진/도면 기반 비전 AI 실적 등록
        with sub_tab_img:
            st.subheader("📷 현장 사진/도면 기반 과거 실적 영구 학습 등록")
            st.markdown(
                "이미 제작 완료된 프로젝트의 **사진/도면**과 **최종 정산 금액**을 입력하면, "
                "AI가 시각적 특징과 단위 단가를 벡터화하여 향후 견적 감리 및 생성에 영구 반영하며, "
                "사이드바의 **[기준 견적서 데이터셋 선택]**에도 즉시 등록됩니다."
            )

            with st.form("form_learn_new_case", clear_on_submit=False):
                f_col1, f_col2 = st.columns(2)

                with f_col1:
                    in_name = st.text_input("프로젝트명 *", placeholder="예: 갤럭시 S25 체험존 팝업스토어 집기제작", key="in_name")
                    in_client = st.text_input("발주처 / 광고주", value="삼성전자 / 제일기획", key="in_client")
                    in_type = st.selectbox(
                        "프로젝트 유형 *",
                        [
                            "스마트 체험 키트 / 원형 개발",
                            "팝업스토어 / 전시 부스",
                            "상설 쇼케이스 / 체험 테이블",
                            "대형 행사 / 베뉴 전시"
                        ],
                        key="in_type"
                    )
                    in_amount = st.number_input("최종 계약/정산 금액 (원, VAT별도) *", min_value=1000000, value=35000000, step=1000000, key="in_amount")
                    in_scale = st.selectbox(
                        "규모 설정",
                        [
                            "소형 (1~3평 / 단일 키트 1~2대)",
                            "중형 (5~15평 / 키트 3~5대)",
                            "대형 (20평 이상 / 다중 키트 8대 이상)"
                        ],
                        key="in_scale"
                    )

                with f_col2:
                    in_count = st.number_input("수량 (평수 또는 키트 대수) *", min_value=1, value=3, step=1, key="in_count")
                    in_unit_lbl = st.selectbox("단위 레이블", ["대당 제작비", "평당 시공비", "SET당 단가", "부스당 단가"], key="in_unit_lbl")
                    in_tier = st.selectbox("사양 등급", ["표준형 (Standard)", "고급형 (Premium)", "실속형 (Budget)"], key="in_tier")
                    in_md = st.number_input("총 투입 인력 공수 (M/D)", min_value=1.0, value=10.5, step=0.5, key="in_md")
                    in_materials = st.text_input("주요 자재 (쉼표로 구분)", value="갈바 EGI 스틸, 우레탄 도장, 조광아크릴, LED 조명", key="in_materials")

                in_specs = st.text_area(
                    "핵심 사양 및 특이사항 요약 (FAQ 소명용)",
                    value="현장 1:1 맞춤 제작, 레이저 가공 갈바 프레임, 15W 무선충전기 매립, 야간 시공 포함",
                    key="in_specs"
                )

                in_uploaded_img = st.file_uploader(
                    "프로젝트 현장 사진 또는 3D 렌더링 이미지 업로드",
                    type=["png", "jpg", "jpeg", "webp"],
                    key="in_uploaded_img"
                )

                btn_submit_learn = st.form_submit_button("🚀 AI 에이전트에 실적 학습 및 지식베이스 업데이트", type="primary")

            if btn_submit_learn:
                if not in_name:
                    st.error("프로젝트명을 입력해 주세요.")
                else:
                    mats_list = [m.strip() for m in in_materials.split(",") if m.strip()]
                    img_bytes = in_uploaded_img.getvalue() if in_uploaded_img else None
                    preset_key = "S26_KIT" if "키트" in in_type else "GALAXY_POPUP"

                    saved = save_new_learned_case(
                        image_bytes=img_bytes,
                        name=in_name,
                        client=in_client,
                        project_type=in_type,
                        settled_amount=in_amount,
                        scale=in_scale,
                        unit_count=in_count,
                        unit_label=in_unit_lbl,
                        tier=in_tier,
                        materials=mats_list,
                        labor_md=in_md,
                        key_specs=in_specs,
                        benchmark_cites="KIDP·KOSA·KBIZ 기준 및 사내 실적 정합",
                        preset_img_key=preset_key,
                        register_to_projects=True
                    )
                    st.session_state["selected_proj_id"] = saved.get("project_id", saved["case_id"])
                    st.session_state["latest_studied_proj"] = {
                        "project_id": saved.get("project_id", saved["case_id"]),
                        "name": f"⭐ [공인실적] {in_name}",
                        "total_budget": in_amount
                    }

                    st.success(
                        f"🎉 **학습 성공!** 「{in_name}」 실적이 AI 견적감독관의 영구 지식베이스 및 기준 데이터셋에 등록되었습니다!\n\n"
                        f"- **등록 ID:** `{saved.get('project_id', saved['case_id'])}`\n"
                        f"- **확정 총 예산:** `₩{saved['settled_amount']:,d}` (단위 단가: `₩{saved['unit_cost']:,d}`)\n"
                        f"- **효과:** 사이드바 **[1단계] 기준 견적서 데이터셋 선택** 목록에 즉시 추가되었습니다."
                    )

            if st.session_state.get("selected_proj_id") and st.session_state.get("latest_studied_proj"):
                p_cur = st.session_state["latest_studied_proj"]
                st.markdown("---")
                st.info(f"💡 방금 등록된 기준 프로젝트: **{p_cur.get('name')}** (예산: ₩{p_cur.get('total_budget', 0):,d})")
                if st.button("⚖️ [1단계] 방금 학습한 기준견적서로 신규 견적 비교·감리 시작하기", type="primary", use_container_width=True, key="btn_jump_to_audit_from_img"):
                    st.session_state["app_main_mode"] = "⚖️ 기준 견적서 정밀 감리 & 진단"
                    st.session_state["selected_proj_id"] = p_cur["project_id"]
                    st.rerun()
