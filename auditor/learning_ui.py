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
    find_similar_learned_cases,
    get_learning_statistics,
    IMAGES_DIR
)
from auditor.vision_estimator import generate_preset_sample_image

def render_learning_studio_ui(currency: str = "KRW"):
    """과거 실적 학습 및 자산화 스튜디오 화면을 렌더링합니다."""
    st.markdown("### 🧠 과거 실적 자산화 & AI 학습 스튜디오 (AI Learning Studio)")
    st.markdown(
        "기존에 성공적으로 제작 및 정산이 완료된 **전시 부스 및 키트 실적(현장 사진, 최종 계약금액, 세부 사양)**을 "
        "에이전트에 직접 학습시켜 **제일기획 고유의 견적 인텔리전스(Data Flywheel)**를 구축합니다. "
        "학습된 실적은 신규 견적 산출 시 **'과거 유사건 대비 단가 차이(FAQ 03)'를 소명하는 강력한 객관적 근거**로 자동 활용됩니다."
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
        "➕ 새 프로젝트 실적 학습시키기 (이미지 + 금액 + 스펙 등록)"
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
                            f"🎉 **스터디 및 자산화 완료!** 「{ex_name}」 프로젝트가 에이전트 기준 데이터베이스에 성공적으로 등록되었습니다!\n\n"
                            f"- **신규 프로젝트 ID:** `{proj_rec['project_id']}`\n"
                            f"- **확정 총 예산:** `₩{proj_rec['total_budget']:,d}` ({len(items)}개 품목 스터디 완료)\n"
                            f"- **학습 시트:** `{proj_rec['default_sheet']}`\n\n"
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
                        preset_img_key=preset_key
                    )

                    st.success(
                        f"🎉 **학습 성공!** 「{in_name}」 실적이 AI 견적감독관의 영구 지식베이스에 안전하게 등록되었습니다!\n\n"
                        f"- **등록 ID:** `{saved['case_id']}`\n"
                        f"- **단위당 산출 단가:** `₩{saved['unit_cost']:,d} ({saved['unit_label']})`\n"
                        f"- **효과:** 앞으로 신규 이미지 견적 산출 및 감리 시, 본 프로젝트가 '유사 실적 벤치마크'로 자동 인용됩니다."
                    )
                    st.rerun()
