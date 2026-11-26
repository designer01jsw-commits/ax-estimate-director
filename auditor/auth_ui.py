# -*- coding: utf-8 -*-
"""
제일기획 AX 견적감독관 — 아임웹(Imweb '상품 하나로 판매 시작') 스타일 고가시성·멀티컬러 랜딩 & 회원가입·관리자 이메일 승인 UI (auth_ui.py)

워크플로우:
1. [회원신청] 사용자 정보(성명, 직급, 소속 부서/팀, 연락처, 이메일, 비밀번호, 신청사유) 입력 및 보안 서약 동의
2. [가입신청] 제출 즉시 관리자(feelingsoo@naver.com)에게 신청인 작성 정보 표 및 원클릭 [가입 승인 / 반려] 링크 자동 메일 발송
3. [관리자 인증] 관리자가 수신한 이메일에서 [✅ 가입 승인하기] 버튼 클릭 시 즉시 승인 처리 (또는 관리자 콘솔에서 승인)
4. [사이트 이용] 승인 완료된 계정으로 로그인해야만 두 사이트 모두 내부 견적 데이터 및 AI 감리 기능 접근 가능
"""

import urllib.parse
from typing import Any, Dict
import streamlit as st

from auditor.auth import (
    ADMIN_EMAIL,
    SITE_DOMAINS,
    authenticate_member,
    register_member_application,
    verify_and_process_email_action,
    get_user_status,
    list_all_members,
    admin_update_member_status,
    load_smtp_config,
    save_smtp_config,
    send_signup_approval_email,
    build_action_urls,
)


def _clean_html(raw: str) -> str:
    """
    Markdown 파서가 4칸 이상 들여쓰기된 HTML 줄을 코드 블록(<pre><code>)으로
    오인하여 화면에 태그 문자열을 그대로 노출하는 현상을 원천 방지합니다.
    """
    return "\n".join(line.strip() for line in raw.splitlines() if line.strip())


def _get_query_param(key: str) -> str:
    """Streamlit 버전에 관계없이 URL 쿼리 파라미터를 안전하게 추출합니다."""
    try:
        val = st.query_params.get(key, "")
        if isinstance(val, list):
            return str(val[0]) if val else ""
        return str(val or "")
    except Exception:
        try:
            qp = st.experimental_get_query_params()
            vals = qp.get(key, [""])
            return str(vals[0]) if vals else ""
        except Exception:
            return ""


def _clear_query_params() -> None:
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass


def _render_email_action_screen(action: str, payload: str, sig: str) -> None:
    """
    관리자(feelingsoo@naver.com)가 가입신청 이메일 내 [가입 즉시 승인] 또는 [가입 반려]
    링크를 클릭하여 접속했을 때 실행되는 원클릭 인증 처리 화면입니다.
    """
    cache_key = f"email_action_done_{sig[:16]}_{action}"
    if cache_key not in st.session_state:
        ok, msg, record = verify_and_process_email_action(action=action, payload_b64=payload, sig=sig)
        st.session_state[cache_key] = (ok, msg, record)
    else:
        ok, msg, record = st.session_state[cache_key]

    is_approve = (action == "approve")
    badge_color = "#059669" if (ok and is_approve) else ("#E11D48" if not ok else "#D97706")
    badge_bg = "#ECFDF5" if (ok and is_approve) else "#FFF1F2"
    icon_str = "✅" if (ok and is_approve) else ("🚫" if ok else "⚠️")
    title_str = (
        "관리자 이메일 원클릭 [가입 승인] 완료"
        if (ok and is_approve)
        else ("관리자 이메일 원클릭 [가입 반려] 완료" if ok else "이메일 승인 링크 검증 실패")
    )

    detail_html = ""
    if record:
        detail_html = f"""
        <div style="background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 18px; padding: 22px 26px; margin-bottom: 24px;">
            <div style="font-size: 13px; font-weight: 800; color: #1A6DFF; margin-bottom: 12px;">👤 처리된 가입 신청인 상세 정보</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 14px;">
                <div><span style="color: #64748B;">성명 / 직급:</span> <strong style="color: #0F172A; margin-left: 6px;">{record.get('name', '-')} ({record.get('position', '프로')})</strong></div>
                <div><span style="color: #64748B;">소속 부서/팀:</span> <strong style="color: #0F172A; margin-left: 6px;">{record.get('department', '-')}</strong></div>
                <div><span style="color: #64748B;">연락처:</span> <strong style="color: #0F172A; margin-left: 6px;">{record.get('phone', '-')}</strong></div>
                <div><span style="color: #64748B;">이메일(ID):</span> <strong style="color: #1A6DFF; margin-left: 6px;">{record.get('email', '-')}</strong></div>
                <div><span style="color: #64748B;">신청 사유:</span> <strong style="color: #0F172A; margin-left: 6px;">{record.get('reason', '-')}</strong></div>
                <div><span style="color: #64748B;">최종 상태:</span> <strong style="color: {badge_color}; margin-left: 6px;">{record.get('status', '').upper()}</strong></div>
            </div>
            <div style="margin-top: 14px; font-size: 12.5px; color: #475569; line-height: 1.6;">
                • 승인 시각: {record.get('approved_at') or '-'} (승인자: {record.get('approved_by') or ADMIN_EMAIL})<br/>
                • 이제 해당 회원은 두 사이트(<strong>ax-estimate-director</strong> 및 <strong>ax-estimate-supervisor</strong>)에서 모두 로그인하여 시스템을 이용할 수 있습니다.
            </div>
        </div>
        """

    st.markdown(
        _clean_html(
            f"""
            <div style="max-width: 780px; margin: 36px auto; padding: 40px 44px; border-radius: 28px; border: 2px solid {badge_color}; background: #FFFFFF; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                    <span style="background: #EFF6FF; color: #1A6DFF; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 800; letter-spacing: 0.04em;">
                        ADMIN EMAIL ONE-CLICK AUTHORIZATION
                    </span>
                    <span style="background: {badge_bg}; color: {badge_color}; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 800;">
                        {icon_str} {'승인 완료 (APPROVED)' if (ok and is_approve) else ('반려 처리됨 (REJECTED)' if ok else '검증 오류')}
                    </span>
                </div>
                <h2 style="margin: 0 0 12px 0; font-size: 26px; font-weight: 800; color: #0F172A;">
                    {icon_str} {title_str}
                </h2>
                <p style="font-size: 15px; color: #475569; line-height: 1.6; margin-bottom: 24px;">
                    {msg}
                </p>
                {detail_html}
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 로그인 및 메인 사이트로 이동", type="primary", use_container_width=True):
            _clear_query_params()
            st.rerun()


def render_sidebar_auth_Widget(user: Dict[str, Any]) -> None:
    """로그인 완료 후 좌측 사이드바 상단에 표시되는 인증 회원 정보 및 관리자 승인 콘솔입니다."""
    is_admin = (user.get("role") == "admin") or (user.get("email", "").lower() == ADMIN_EMAIL.lower())
    role_badge = "🛡️ 총괄 관리자" if is_admin else "✅ 승인 정회원"
    badge_bg = "#EEF2FF" if is_admin else "#ECFDF5"
    badge_fg = "#4F46E5" if is_admin else "#059669"

    st.sidebar.markdown(
        _clean_html(
            f"""
            <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-top: 4px solid #1A6DFF; border-radius: 16px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 800; color: {badge_fg}; background: {badge_bg}; padding: 3px 10px; border-radius: 999px;">{role_badge}</span>
                    <span style="font-size: 11px; font-weight: 700; color: #1A6DFF;">보안 인증됨 🔒</span>
                </div>
                <div style="font-size: 15px; font-weight: 800; color: #0F172A;">{user.get('name', '회원')} <span style="font-size: 12px; font-weight: 600; color: #64748B;">({user.get('department', '-')})</span></div>
                <div style="font-size: 12px; color: #475569; margin-top: 3px;">{user.get('email', '')}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    if st.sidebar.button("🚪 로그아웃 (보안 세션 종료)", use_container_width=True, key="btn_sidebar_logout"):
        st.session_state.pop("authenticated_user", None)
        st.rerun()

    if is_admin:
        all_members = list_all_members()
        pending_list = [m for m in all_members if m.get("status") == "pending"]
        pending_badge = f" ({len(pending_list)}건 대기)" if pending_list else ""

        with st.sidebar.expander(f"🛡️ 관리자 회원 승인·메일 센터{pending_badge}", expanded=bool(pending_list)):
            st.caption(f"수신 관리자 메일: `{ADMIN_EMAIL}`")
            if pending_list:
                st.markdown(f"**⏳ 가입 승인 대기 회원 ({len(pending_list)}명)**")
                for pm in pending_list:
                    em = pm.get("email", "")
                    st.markdown(
                        _clean_html(
                            f"""
                            <div style="background:#EFF6FF; border:1.5px solid #BFDBFE; border-radius:12px; padding:10px 12px; margin-bottom:8px; font-size:12.5px;">
                                <strong style="color:#0F172A;">{pm.get('name')}</strong> <span style="color:#475569;">({pm.get('department')} / {pm.get('position', '프로')})</span><br/>
                                <span style="color:#1A6DFF; font-weight:700;">{em}</span> · 📞 {pm.get('phone', '-')}<br/>
                                <span style="color:#334155;">사유: {pm.get('reason', '-')}</span><br/>
                                <span style="color:#64748B; font-size:11px;">신청: {pm.get('created_at', '-')}</span>
                            </div>
                            """
                        ),
                        unsafe_allow_html=True,
                    )
                    c_app, c_rej = st.columns(2)
                    with c_app:
                        if st.button("✅ 승인", key=f"adm_app_{em}", type="primary", use_container_width=True):
                            ok, msg = admin_update_member_status(em, "approve")
                            if ok:
                                st.success(msg)
                                st.rerun()
                    with c_rej:
                        if st.button("❌ 반려", key=f"adm_rej_{em}", use_container_width=True):
                            ok, msg = admin_update_member_status(em, "reject")
                            if ok:
                                st.warning(msg)
                                st.rerun()
            else:
                st.info("현재 승인 대기 중인 신규 가입신청이 없습니다.")

            st.markdown("---")
            st.markdown("**📋 전체 회원 현황**")
            for m in all_members:
                em = m.get("email", "")
                st_code = m.get("status", "pending")
                st_icon = "✅" if st_code == "approved" else ("⏳" if st_code == "pending" else "❌")
                st.caption(f"{st_icon} **{m.get('name')}** ({m.get('department')}) · `{em}` [{st_code}]")
                if em.lower() != ADMIN_EMAIL.lower():
                    if st_code == "approved":
                        if st.button(f"권한 회수 ({m.get('name')})", key=f"adm_revoke_{em}", use_container_width=True):
                            admin_update_member_status(em, "reject")
                            st.rerun()
                    elif st_code == "rejected":
                        if st.button(f"재승인 ({m.get('name')})", key=f"adm_reapp_{em}", use_container_width=True):
                            admin_update_member_status(em, "approve")
                            st.rerun()

            st.markdown("---")
            st.markdown("**📧 자동 메일 발송 설정 (네이버 SMTP)**")
            st.caption(
                f"기본값으로 HTTPS 메일 릴레이(`{ADMIN_EMAIL}`)가 작동하며, "
                "네이버 메일 앱 비밀번호(또는 로그인 비밀번호)를 등록하면 네이버 공식 SMTP(`smtp.naver.com`)로 즉시 발송됩니다."
            )
            smtp_cfg = load_smtp_config()
            smtp_pw_input = st.text_input(
                "feelingsoo@naver.com SMTP 비밀번호",
                value=smtp_cfg.get("smtp_password", ""),
                type="password",
                help="네이버 메일 > 환경설정 > POP3/IMAP 설정에서 'POP3/SMTP 사용함' 활성화 후 비밀번호를 입력하면 100% 실시간 직발송됩니다.",
                key="adm_smtp_pw_input",
            )
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("💾 설정 저장", use_container_width=True, key="btn_save_smtp"):
                    save_smtp_config(
                        smtp_host="smtp.naver.com",
                        smtp_port=465,
                        smtp_user=ADMIN_EMAIL,
                        smtp_password=smtp_pw_input.strip(),
                    )
                    st.success("SMTP 설정이 저장되었습니다.")
            with col_s2:
                if st.button("📨 테스트 메일 발송", use_container_width=True, key="btn_test_email"):
                    test_rec = {
                        "email": "test_applicant@cheil.com",
                        "name": "홍길동 (테스트 신청자)",
                        "department": "제일기획 BX익스피리언스팀",
                        "position": "선임프로",
                        "phone": "010-1234-5678",
                        "reason": "관리자 승인 메일 발송 연동 테스트",
                        "password_hash": "test",
                        "salt": "test",
                        "created_at": "방금 전",
                    }
                    ok_mail, msg_mail, _ = send_signup_approval_email(test_rec)
                    if ok_mail:
                        st.success(f"발송 성공: {msg_mail}")
                    else:
                        st.warning(msg_mail)


def enforce_authentication_gate() -> bool:
    """
    사이트 최상단 보안 게이트 및 아임웹(Imweb '상품 하나로 판매 시작') 스타일 공식 홈페이지 소개 화면.
    """
    # 1. 이메일 내 원클릭 [승인 / 반려] 링크 접속 여부 확인
    auth_action = _get_query_param("auth_action")
    payload = _get_query_param("payload")
    sig = _get_query_param("sig")

    if auth_action in ("approve", "reject") and payload and sig:
        _render_email_action_screen(auth_action, payload, sig)
        return False

    # 2. 이미 로그인된 세션 확인
    auth_user = st.session_state.get("authenticated_user")
    if auth_user and isinstance(auth_user, dict) and auth_user.get("status") == "approved":
        render_sidebar_auth_Widget(auth_user)
        return True

    # 3. 미인증 사용자: 좌측 사이드바를 숨기고 아임웹 스타일 고가시성 랜딩 홈페이지 + 보안 로그인 게이트 노출
    st.markdown(
        _clean_html(
            """
            <style>
                [data-testid="stSidebar"],
                [data-testid="collapsedControl"],
                [data-testid="stSidebarCollapseButton"] {
                    display: none !important;
                }
                .block-container {
                    max-width: 1080px !important;
                    padding-top: 1.8rem !important;
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

    # 4. 상단 아임웹 스타일 플로팅 GNB 헤더
    st.markdown(
        _clean_html(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 999px; padding: 12px 26px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04); flex-wrap: wrap; gap: 10px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="background: linear-gradient(135deg, #1A6DFF 0%, #4F46E5 100%); color: #FFFFFF; width: 32px; height: 32px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 800;">⚖️</span>
                    <span style="font-size: 16px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">제일기획 AI 견적감독관</span>
                    <span style="background: #EFF6FF; color: #1A6DFF; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 999px;">AX ENTERPRISE</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 999px;">● 24/7 AI 감리 엔진 가동 중</span>
                    <span style="background: #FFF1F2; color: #E11D48; border: 1px solid #FECDD3; font-size: 12px; font-weight: 800; padding: 4px 12px; border-radius: 999px;">🔒 관리자 승인 회원 전용</span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # 5. 아임웹 '상품 하나로 판매 시작' 스타일 히어로 배너 + 컬러 포인트 벤토 그리드
    st.markdown(
        _clean_html(
            f"""
            <div style="background: #FFFFFF; border-radius: 32px; border: 1.5px solid #E2E8F0; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.06); overflow: hidden; margin-bottom: 28px;">
                <div style="height: 6px; background: linear-gradient(90deg, #1A6DFF 0%, #6366F1 35%, #10B981 70%, #FF5A36 100%);"></div>
                <div style="padding: 40px 44px 36px 44px; background: radial-gradient(circle at 95% 10%, rgba(26, 109, 255, 0.08), transparent 40%), radial-gradient(circle at 5% 90%, rgba(16, 185, 129, 0.07), transparent 40%), #FFFFFF;">
                    <div style="display: inline-flex; align-items: center; gap: 8px; background: #EFF6FF; border: 1px solid #BFDBFE; color: #1A6DFF; padding: 6px 16px; border-radius: 999px; font-size: 13px; font-weight: 800; margin-bottom: 16px;">
                        <span>✨ 견적서 파일 하나로 3초 만에 정밀 감리 시작</span>
                    </div>
                    <h1 style="margin: 0 0 14px 0; font-size: 36px; font-weight: 900; letter-spacing: -0.035em; color: #0F172A; line-height: 1.22;">
                        복잡한 실행예산과 협력사 견적서,<br/>
                        <span style="color: #1A6DFF;">AI 견적감독관</span> 하나로 완벽하게 검증하세요.
                    </h1>
                    <p style="margin: 0 0 24px 0; font-size: 15.5px; color: #334155; line-height: 1.7; max-width: 880px; font-weight: 400;">
                        프로젝트마다 제각각인 엑셀 견적서를 <strong style="color: #0F172A; font-weight: 800;">7대 표준 공종</strong>으로 자동 분해하고, <strong style="color: #1A6DFF; font-weight: 800;">정부 공인 6대 물가·노임 기준(KIDP·KOSA·시중노임·조달청 등)</strong> 및 광고주 컨펌 실적 DB와 실시간 교차 검증하여 과다 청구 리스크와 협상 소명 리포트를 즉시 도출합니다.
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px;">
                        <span style="background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 7px 15px; border-radius: 12px; font-size: 13px; font-weight: 800;">🔵 7대 표준 공종 자동분해</span>
                        <span style="background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; padding: 7px 15px; border-radius: 12px; font-size: 13px; font-weight: 800;">🟢 6대 정부 공인단가 소명</span>
                        <span style="background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; padding: 7px 15px; border-radius: 12px; font-size: 13px; font-weight: 800;">🟣 비전 AI 3D 투시도 예상견적</span>
                        <span style="background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; padding: 7px 15px; border-radius: 12px; font-size: 13px; font-weight: 800;">🟠 3단계 신호등(🟢·🟡·🔴) 리스크 진단</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 18px; margin-bottom: 28px;">
                        <div style="background: #FFFFFF; border: 1.5px solid #DBEAFE; border-top: 5px solid #1A6DFF; border-radius: 22px; padding: 24px 22px; box-shadow: 0 8px 24px rgba(26, 109, 255, 0.06);">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                <span style="background: #EFF6FF; color: #1A6DFF; width: 42px; height: 42px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 22px;">⚖️</span>
                                <span style="background: #EFF6FF; color: #1A6DFF; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px;">CORE 01 · 정밀 감리</span>
                            </div>
                            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-bottom: 8px; letter-spacing: -0.02em;">양식초월 정밀 견적 감리</div>
                            <div style="font-size: 13.5px; color: #475569; line-height: 1.6;">
                                협력사마다 다른 시트 구조와 품목명을 <strong style="color: #0F172A;">7대 표준 공종</strong>으로 자동 정규화하고, 기준 견적 대비 수량·단가·인건비 편차를 신호등으로 즉시 진단합니다.
                            </div>
                        </div>
                        <div style="background: #FFFFFF; border: 1.5px solid #A7F3D0; border-top: 5px solid #10B981; border-radius: 22px; padding: 24px 22px; box-shadow: 0 8px 24px rgba(16, 185, 129, 0.06);">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                <span style="background: #ECFDF5; color: #059669; width: 42px; height: 42px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 22px;">📷</span>
                                <span style="background: #ECFDF5; color: #059669; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px;">CORE 02 · 비전 AI</span>
                            </div>
                            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-bottom: 8px; letter-spacing: -0.02em;">비전 AI 공간 예상견적 산출</div>
                            <div style="font-size: 13.5px; color: #475569; line-height: 1.6;">
                                전시 부스·팝업스토어 <strong style="color: #0F172A;">3D 투시도 또는 현장 사진 1장</strong>만 업로드하면 비전 AI가 구조물·마감재·조명 물량을 식별해 적정 실행예산을 산출합니다.
                            </div>
                        </div>
                        <div style="background: #FFFFFF; border: 1.5px solid #C7D2FE; border-top: 5px solid #6366F1; border-radius: 22px; padding: 24px 22px; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.06);">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                <span style="background: #EEF2FF; color: #4F46E5; width: 42px; height: 42px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 22px;">🧠</span>
                                <span style="background: #EEF2FF; color: #4F46E5; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px;">CORE 03 · 자산화 DB</span>
                            </div>
                            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-bottom: 8px; letter-spacing: -0.02em;">실적 자산화 &amp; 공공기준 소명</div>
                            <div style="font-size: 13.5px; color: #475569; line-height: 1.6;">
                                광고주 컨펌 완료 견적서를 사내 표준 DB로 자산화하고, <strong style="color: #0F172A;">6대 공인 노임·물가 기준</strong>에 기반한 대외 소명 리포트와 협상 가이드를 자동 생성합니다.
                            </div>
                        </div>
                    </div>
                    <div style="background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 20px; padding: 20px 24px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
                            <div style="font-size: 15px; font-weight: 800; color: #0F172A;">
                                🛡️ 보안 접근통제 안내 — 4단계 회원가입 및 관리자 이메일 승인 절차
                            </div>
                            <span style="background: #EFF6FF; color: #1A6DFF; border: 1px solid #BFDBFE; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 800;">
                                📩 승인 요청 자동 수신처: {ADMIN_EMAIL}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                            <div style="background: #FFFFFF; border: 1.5px solid #DBEAFE; border-left: 4px solid #1A6DFF; border-radius: 14px; padding: 12px 15px;">
                                <div style="font-size: 11px; font-weight: 800; color: #1A6DFF;">STEP 01 · 회원신청</div>
                                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin: 3px 0;">신청인 정보 작성</div>
                                <div style="font-size: 12px; color: #475569;">성명·소속·직급·연락처·사유 입력</div>
                            </div>
                            <div style="background: #FFFFFF; border: 1.5px solid #C7D2FE; border-left: 4px solid #6366F1; border-radius: 14px; padding: 12px 15px;">
                                <div style="font-size: 11px; font-weight: 800; color: #6366F1;">STEP 02 · 가입신청</div>
                                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin: 3px 0;">관리자 메일 자동 발송</div>
                                <div style="font-size: 12px; color: #475569;">신청인 정보 + 승인 링크 즉시 전송</div>
                            </div>
                            <div style="background: #FFFFFF; border: 1.5px solid #FED7AA; border-left: 4px solid #FF5A36; border-radius: 14px; padding: 12px 15px;">
                                <div style="font-size: 11px; font-weight: 800; color: #EA580C;">STEP 03 · 관리자 인증</div>
                                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin: 3px 0;">메일 내 [가입 승인] 클릭</div>
                                <div style="font-size: 12px; color: #475569;">수신 메일에서 원클릭 즉시 승인</div>
                            </div>
                            <div style="background: #ECFDF5; border: 1.5px solid #6EE7B7; border-left: 4px solid #10B981; border-radius: 14px; padding: 12px 15px;">
                                <div style="font-size: 11px; font-weight: 800; color: #059669;">STEP 04 · 사이트 이용</div>
                                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin: 3px 0;">양대 사이트 로그인 접속</div>
                                <div style="font-size: 12px; color: #047857; font-weight: 600;">승인 완료 후 전 기능 즉시 활성화</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    tab_login, tab_signup, tab_status = st.tabs([
        "🔐 승인 회원 로그인",
        "📝 신규 회원신청 · 가입신청 (관리자 승인 요청)",
        "🔎 가입 승인 상태 조회",
    ])

    with tab_login:
        col_l, col_r = st.columns([1.15, 0.85], gap="large")
        with col_l:
            st.markdown("#### **🔐 승인 회원 / 관리자 보안 로그인**")
            st.caption("관리자 이메일 승인이 완료된 회원만 로그인이 허용됩니다.")
            with st.form("form_member_login", clear_on_submit=False):
                login_email = st.text_input(
                    "이메일 아이디 (Email)",
                    placeholder="예: name@cheil.com 또는 feelingsoo@naver.com",
                )
                login_pw = st.text_input(
                    "비밀번호 (Password)",
                    type="password",
                    placeholder="비밀번호를 입력하세요",
                )
                submitted_login = st.form_submit_button("🔐 보안 로그인 및 사이트 접속", type="primary", use_container_width=True)

            if submitted_login:
                ok_auth, msg_auth, user_rec = authenticate_member(login_email, login_pw)
                if ok_auth and user_rec:
                    st.session_state["authenticated_user"] = user_rec
                    st.success(msg_auth)
                    st.rerun()
                else:
                    st.error(msg_auth)

        with col_r:
            st.markdown(
                _clean_html(
                    f"""
                    <div style="background: #FFFFFF; border: 1.5px solid #E2E8F0; border-top: 4px solid #1A6DFF; border-radius: 20px; padding: 24px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);">
                        <div style="font-size: 16px; font-weight: 800; color: #0F172A; margin-bottom: 12px;">📌 회원제 이용 안내 및 보안 정책</div>
                        <ul style="font-size: 13.5px; color: #334155; line-height: 1.75; padding-left: 18px; margin: 0;">
                            <li>본 사이트는 <strong style="color: #0F172A;">대외비 실행예산 및 협력사 단가 보호</strong>를 위해 사전 승인된 회원만 접근할 수 있습니다.</li>
                            <li>신규 이용자는 상단 <strong style="color: #1A6DFF;">[📝 신규 회원신청 · 가입신청]</strong> 탭에서 신청서를 제출해 주세요.</li>
                            <li>가입신청 즉시 관리자(<code>{ADMIN_EMAIL}</code>)에게 <strong style="color: #0F172A;">신청인 작성 정보와 [✅ 가입 승인하기] 버튼이 담긴 이메일</strong>이 발송됩니다.</li>
                            <li>관리자가 메일에서 승인 버튼을 클릭하면 두 공식 도메인(<a href="{SITE_DOMAINS[0]}" target="_blank" style="color:#1A6DFF; font-weight:800;">Director</a> · <a href="{SITE_DOMAINS[1]}" target="_blank" style="color:#1A6DFF; font-weight:800;">Supervisor</a>) 모두 즉시 이용 가능합니다.</li>
                        </ul>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    with tab_signup:
        st.markdown("#### **📝 신규 회원신청 → 가입신청서 제출**")
        st.caption(
            f"아래 양식을 작성하여 제출하면 신청인이 작성한 모든 항목과 관리자 전용 [원클릭 가입 승인] 링크가 `{ADMIN_EMAIL}` 주소로 자동 발송됩니다."
        )

        with st.form("form_member_signup", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                su_name = st.text_input("신청자 성명 *", placeholder="예: 김제일 프로")
                su_pos = st.text_input("직급 / 직책 *", placeholder="예: 선임프로 / 팀장 / 매니저")
                su_email = st.text_input("이메일 주소 (로그인 ID) *", placeholder="예: gildong.hong@cheil.com")
                su_pw = st.text_input("사용할 비밀번호 (6자 이상) *", type="password", placeholder="6자 이상 비밀번호 입력")
            with c2:
                su_dept = st.text_input("소속 회사 / 부서(팀) *", placeholder="예: 제일기획 BX익스피리언스팀 / 구매팀")
                su_phone = st.text_input("연락처 (휴대폰 / 사내 내선) *", placeholder="예: 010-1234-5678")
                su_reason = st.text_input("가입 신청 사유 및 담당 프로젝트 *", placeholder="예: 2026 갤럭시 언팩 전시 견적 감리 및 단가 검증")
                su_pw_confirm = st.text_input("비밀번호 재확인 *", type="password", placeholder="비밀번호를 한 번 더 입력하세요")

            su_agree = st.checkbox(
                "[필수] 본 시스템 내 모든 프로젝트 실행예산, 협력사 단가 및 감리 리포트를 외부에 유출하지 않을 것을 서약하며 회원 가입신청서를 제출합니다.",
                value=False,
            )

            submitted_signup = st.form_submit_button(
                f"📨 회원신청 완료 및 관리자({ADMIN_EMAIL})에게 가입승인 요청 메일 발송",
                type="primary",
                use_container_width=True,
            )

        if submitted_signup:
            if not su_agree:
                st.error("보안 서약 동의 체크박스를 선택해 주세요.")
            else:
                ok_reg, msg_reg, user_rec_out, urls_out = register_member_application(
                    email=su_email,
                    name=su_name,
                    department=su_dept,
                    position=su_pos,
                    phone=su_phone,
                    password=su_pw,
                    password_confirm=su_pw_confirm,
                    reason=su_reason,
                    send_email=True,
                    sync_remote=True,
                )
                if ok_reg and user_rec_out:
                    st.session_state["last_signup_info"] = {
                        "user": user_rec_out,
                        "urls": urls_out or build_action_urls(user_rec_out),
                        "email_status": msg_reg,
                    }
                    st.success(msg_reg)
                else:
                    st.error(msg_reg)

        last_su = st.session_state.get("last_signup_info")
        if last_su and isinstance(last_su, dict):
            user_rec = last_su.get("user", {})
            action_urls = last_su.get("urls") or build_action_urls(user_rec)
            approve_url_dir = action_urls["approve_primary"]
            approve_url_sup = action_urls["approve_secondary"]

            mail_subj = urllib.parse.quote(
                f"[AX 견적감독관] 신규 회원가입 승인 요청 — {user_rec.get('name')} ({user_rec.get('department')} / {user_rec.get('position', '프로')})"
            )
            mail_body = urllib.parse.quote(
                f"관리자님 ({ADMIN_EMAIL}),\n\n"
                f"제일기획 AX 견적감독관 신규 회원가입 승인 요청입니다.\n\n"
                f"[가입 신청인이 작성한 정보]\n"
                f"1. 신청자 성명: {user_rec.get('name')}\n"
                f"2. 소속 회사/부서: {user_rec.get('department')}\n"
                f"3. 직급/직책: {user_rec.get('position', '-')}\n"
                f"4. 연락처(휴대폰/내선): {user_rec.get('phone', '-')}\n"
                f"5. 이메일(로그인 ID): {user_rec.get('email')}\n"
                f"6. 가입 신청 사유 및 담당 프로젝트: {user_rec.get('reason')}\n"
                f"7. 보안서약 동의: 동의 완료\n"
                f"8. 신청 일시: {user_rec.get('created_at')}\n\n"
                f"아래 [원클릭 가입 승인 링크]를 클릭하시면 즉시 가입이 승인되어 사이트 이용이 가능해집니다:\n\n"
                f"▶ 승인 링크 (견적감독관): {approve_url_sup}\n"
                f"▶ 승인 링크 (견적감리관): {approve_url_dir}\n"
            )
            mailto_href = f"mailto:{ADMIN_EMAIL}?subject={mail_subj}&body={mail_body}"

            st.markdown(
                _clean_html(
                    f"""
                    <div style="background: #ECFDF5; border: 1.5px solid #10B981; border-radius: 18px; padding: 20px 24px; margin-top: 14px;">
                        <div style="font-size: 15px; font-weight: 800; color: #047857; margin-bottom: 8px;">
                            ✅ 가입신청 접수 및 메일 발송 완료 — 관리자({ADMIN_EMAIL}) 승인 대기 중
                        </div>
                        <div style="font-size: 13px; color: #0F172A; line-height: 1.7; margin-bottom: 12px; background: #FFFFFF; padding: 12px 16px; border-radius: 12px; border: 1px solid #A7F3D0;">
                            <strong>[관리자 메일(<code>{ADMIN_EMAIL}</code>)로 전송된 신청인 작성 정보]</strong><br/>
                            • <strong>성명 / 직급:</strong> {user_rec.get('name')} ({user_rec.get('position', '-')})<br/>
                            • <strong>소속 부서/팀:</strong> {user_rec.get('department')}<br/>
                            • <strong>연락처:</strong> {user_rec.get('phone', '-')}<br/>
                            • <strong>이메일(로그인 ID):</strong> <code>{user_rec.get('email')}</code><br/>
                            • <strong>가입 신청 사유:</strong> {user_rec.get('reason')}<br/>
                            • <strong>신청 일시:</strong> {user_rec.get('created_at')}
                        </div>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <a href="{mailto_href}" style="display: inline-block; background: #1A6DFF; color: #FFFFFF; text-decoration: none; padding: 10px 20px; border-radius: 999px; font-size: 13px; font-weight: 800; box-shadow: 0 4px 12px rgba(26, 109, 255, 0.25);">
                                📧 내 메일앱으로 관리자({ADMIN_EMAIL})에게 승인링크 직접 발송 (즉시도달 보조)
                            </a>
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    with tab_status:
        st.markdown("#### **🔎 내 가입신청 승인 상태 실시간 조회**")
        st.caption("가입신청 시 입력한 이메일 주소를 입력하면 관리자 승인 여부를 즉시 확인할 수 있습니다.")
        chk_col1, chk_col2 = st.columns([3, 1])
        with chk_col1:
            chk_email = st.text_input("조회할 이메일 주소 입력", placeholder="예: gildong.hong@cheil.com", key="chk_status_email")
        with chk_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_chk = st.button("🔄 승인 여부 조회", type="primary", use_container_width=True)

        if btn_chk and chk_email:
            found = get_user_status(chk_email)
            if not found:
                st.warning("해당 이메일로 접수된 회원신청 내역이 없습니다. [신규 회원신청 · 가입신청] 탭에서 먼저 신청해 주세요.")
            else:
                st_val = found.get("status", "pending")
                if st_val == "approved":
                    st.success(
                        f"✅ **{found.get('name')}** ({found.get('email')}) 회원님은 **관리자 승인이 완료(APPROVED)**되었습니다! "
                        f"상단 [🔐 승인 회원 로그인] 탭에서 바로 로그인하실 수 있습니다."
                    )
                elif st_val == "pending":
                    st.info(
                        f"⏳ **{found.get('name')}** ({found.get('email')}) 회원님은 현재 **관리자(`{ADMIN_EMAIL}`) 승인 대기 중(PENDING)**입니다. "
                        f"(신청 시각: {found.get('created_at', '-')})"
                    )
                else:
                    st.error(
                        f"❌ **{found.get('name')}** ({found.get('email')}) 회원님의 가입신청이 반려(REJECTED)되었습니다. 관리자에게 문의해 주세요."
                    )

    return False
