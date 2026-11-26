# -*- coding: utf-8 -*-
"""
제일기획 AX 견적감독관 — MOGAM(https://www.mogam.re.kr/) 스타일 코퍼레이트 랜딩 & 회원가입·관리자 이메일 승인 UI (auth_ui.py)

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
from auditor.mogam_theme import (
    clean_html as _clean_html,
    render_mogam_full_landing_sections,
    render_mogam_footer,
)


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
    badge_color = "#002C5F" if (ok and is_approve) else ("#DC2626" if not ok else "#B45309")
    badge_bg = "#EBF3FA" if (ok and is_approve) else "#FEF2F2"
    icon_str = "✅" if (ok and is_approve) else ("🚫" if ok else "⚠️")
    title_str = (
        "관리자 이메일 원클릭 [가입 승인] 완료"
        if (ok and is_approve)
        else ("관리자 이메일 원클릭 [가입 반려] 완료" if ok else "이메일 승인 링크 검증 실패")
    )

    detail_html = ""
    if record:
        detail_html = f"""
        <div style="background: #F8F9FB; border-top: 2px solid #002C5F; border-bottom: 1px solid #E5E8EB; padding: 24px 28px; margin-bottom: 28px;">
            <div style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 700; letter-spacing: 0.12em; color: #0052CC; margin-bottom: 14px;">
                APPLICANT PROFILE &amp; AUTHORIZATION RECORD
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 14px;">
                <div><span style="color: #6B7280;">성명 / 직급:</span> <strong style="color: #111827; margin-left: 6px;">{record.get('name', '-')} ({record.get('position', '프로')})</strong></div>
                <div><span style="color: #6B7280;">소속 부서/팀:</span> <strong style="color: #111827; margin-left: 6px;">{record.get('department', '-')}</strong></div>
                <div><span style="color: #6B7280;">연락처:</span> <strong style="color: #111827; margin-left: 6px;">{record.get('phone', '-')}</strong></div>
                <div><span style="color: #6B7280;">이메일(ID):</span> <strong style="color: #0052CC; margin-left: 6px;">{record.get('email', '-')}</strong></div>
                <div><span style="color: #6B7280;">신청 사유:</span> <strong style="color: #111827; margin-left: 6px;">{record.get('reason', '-')}</strong></div>
                <div><span style="color: #6B7280;">최종 상태:</span> <strong style="color: {badge_color}; margin-left: 6px;">{record.get('status', '').upper()}</strong></div>
            </div>
            <div style="margin-top: 16px; font-size: 12.5px; color: #4B5563; line-height: 1.65;">
                • 승인 시각: {record.get('approved_at') or '-'} (승인자: {record.get('approved_by') or ADMIN_EMAIL})<br/>
                • 이제 해당 회원은 두 공식 사이트(<strong>ax-estimate-director</strong> 및 <strong>ax-estimate-supervisor</strong>)에서 모두 로그인하여 시스템을 이용할 수 있습니다.
            </div>
        </div>
        """

    st.markdown(
        _clean_html(
            f"""
            <div style="max-width: 820px; margin: 48px auto; padding: 48px 52px; border: 1px solid #E5E8EB; border-top: 4px solid {badge_color}; background: #FFFFFF;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
                    <span style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 700; letter-spacing: 0.14em; color: #0052CC;">
                        ADMIN EMAIL ONE-CLICK AUTHORIZATION
                    </span>
                    <span style="background: {badge_bg}; color: {badge_color}; padding: 5px 14px; font-size: 12px; font-weight: 700;">
                        {icon_str} {'승인 완료 (APPROVED)' if (ok and is_approve) else ('반려 처리됨 (REJECTED)' if ok else '검증 오류')}
                    </span>
                </div>
                <h2 style="margin: 0 0 14px 0; font-size: 28px; font-weight: 800; color: #111827; letter-spacing: -0.03em;">
                    {title_str}
                </h2>
                <p style="font-size: 15px; color: #374151; line-height: 1.68; margin-bottom: 28px;">
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
        if st.button("로그인 및 메인 워크스페이스로 이동 →", type="primary", use_container_width=True):
            _clear_query_params()
            st.rerun()


def render_sidebar_auth_Widget(user: Dict[str, Any]) -> None:
    """로그인 완료 후 좌측 사이드바 상단에 표시되는 인증 회원 정보 및 관리자 승인 콘솔입니다."""
    is_admin = (user.get("role") == "admin") or (user.get("email", "").lower() == ADMIN_EMAIL.lower())
    role_badge = "ADMIN GOVERNANCE" if is_admin else "VERIFIED MEMBER"

    st.sidebar.markdown(
        _clean_html(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E5E8EB; border-top: 3px solid #002C5F; padding: 16px 18px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-family: 'Inter', sans-serif; font-size: 10.5px; font-weight: 800; letter-spacing: 0.1em; color: #002C5F; background: #EBF3FA; padding: 3px 9px;">{role_badge}</span>
                    <span style="font-family: 'Inter', sans-serif; font-size: 10.5px; font-weight: 700; color: #0052CC;">● ACTIVE</span>
                </div>
                <div style="font-size: 15px; font-weight: 800; color: #111827;">{user.get('name', '회원')} <span style="font-size: 12px; font-weight: 500; color: #6B7280;">({user.get('department', '-')})</span></div>
                <div style="font-size: 12px; color: #4B5563; margin-top: 3px;">{user.get('email', '')}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    if st.sidebar.button("로그아웃 (보안 세션 종료)", use_container_width=True, key="btn_sidebar_logout"):
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
                            <div style="background:#F8F9FB; border:1px solid #CBD5E1; border-left:3px solid #002C5F; padding:10px 12px; margin-bottom:8px; font-size:12.5px;">
                                <strong style="color:#111827;">{pm.get('name')}</strong> <span style="color:#4B5563;">({pm.get('department')} / {pm.get('position', '프로')})</span><br/>
                                <span style="color:#0052CC; font-weight:700;">{em}</span> · {pm.get('phone', '-')}<br/>
                                <span style="color:#374151;">사유: {pm.get('reason', '-')}</span><br/>
                                <span style="color:#6B7280; font-size:11px;">신청: {pm.get('created_at', '-')}</span>
                            </div>
                            """
                        ),
                        unsafe_allow_html=True,
                    )
                    c_app, c_rej = st.columns(2)
                    with c_app:
                        if st.button("승인", key=f"adm_app_{em}", type="primary", use_container_width=True):
                            ok, msg = admin_update_member_status(em, "approve")
                            if ok:
                                st.success(msg)
                                st.rerun()
                    with c_rej:
                        if st.button("반려", key=f"adm_rej_{em}", use_container_width=True):
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
                if st.button("설정 저장", use_container_width=True, key="btn_save_smtp"):
                    save_smtp_config(
                        smtp_host="smtp.naver.com",
                        smtp_port=465,
                        smtp_user=ADMIN_EMAIL,
                        smtp_password=smtp_pw_input.strip(),
                    )
                    st.success("SMTP 설정이 저장되었습니다.")
            with col_s2:
                if st.button("테스트 메일 발송", use_container_width=True, key="btn_test_email"):
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
    사이트 최상단 보안 게이트 및 MOGAM 레퍼런스 기반 6대 섹션 공식 홈페이지 화면.
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

    # 3. 미인증 사용자: 좌측 사이드바를 숨기고 MOGAM 1440px 풀와이드 코퍼레이트 랜딩 페이지 노출
    st.markdown(
        _clean_html(
            """
            <style>
                [data-testid="stSidebar"],
                [data-testid="collapsedControl"],
                [data-testid="stSidebarCollapseButton"] {
                    display: none !important;
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

    # 4. MOGAM 스타일 6대 메인 섹션 (HEADER + SECTION 01 HERO ~ SECTION 06 FINAL CTA) 렌더링
    render_mogam_full_landing_sections(admin_email=ADMIN_EMAIL, is_authenticated=False)

    # 5. 회원 인증 및 가입신청 워크스페이스 (SECTION 06 CTA 하단 직결)
    tab_login, tab_signup, tab_status = st.tabs([
        "01 · 승인 회원 로그인 (MEMBER SIGN IN)",
        "02 · 신규 회원신청 · 가입신청 (MEMBERSHIP APPLICATION)",
        "03 · 가입 승인 상태 조회 (APPLICATION STATUS)",
    ])

    with tab_login:
        col_l, col_r = st.columns([1.15, 0.85], gap="large")
        with col_l:
            st.markdown("#### **승인 정회원 / 관리자 보안 로그인**")
            st.caption("관리자 이메일 승인이 완료된 회원만 워크스페이스 접근이 허용됩니다.")
            with st.form("form_member_login", clear_on_submit=False):
                login_email = st.text_input(
                    "이메일 아이디 (Corporate Email ID)",
                    placeholder="예: name@cheil.com 또는 feelingsoo@naver.com",
                )
                login_pw = st.text_input(
                    "비밀번호 (Password)",
                    type="password",
                    placeholder="비밀번호를 입력하세요",
                )
                submitted_login = st.form_submit_button("보안 로그인 및 워크스페이스 접속 →", type="primary", use_container_width=True)

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
                    <div style="background: #F8F9FB; border-top: 2px solid #002C5F; border-bottom: 1px solid #E5E8EB; padding: 28px 30px;">
                        <div style="font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; letter-spacing: 0.14em; color: #0052CC; margin-bottom: 10px;">
                            SECURITY GOVERNANCE POLICY
                        </div>
                        <div style="font-size: 17px; font-weight: 800; color: #111827; margin-bottom: 14px;">회원제 접근통제 및 승인 정책</div>
                        <ul style="font-size: 13.5px; color: #374151; line-height: 1.8; padding-left: 18px; margin: 0;">
                            <li>본 플랫폼은 <strong>대외비 실행예산 및 협력사 단가 보호</strong>를 위해 사전 승인된 회원만 이용할 수 있습니다.</li>
                            <li>신규 이용자는 상단 <strong>[02 · 신규 회원신청 · 가입신청]</strong> 탭에서 신청서를 작성해 주십시오.</li>
                            <li>제출 즉시 총괄 관리자(<code>{ADMIN_EMAIL}</code>)에게 <strong>신청인 상세 정보와 원클릭 [가입 승인] 링크가 포함된 이메일</strong>이 자동 발송됩니다.</li>
                            <li>관리자가 수신 메일에서 승인 링크를 클릭하면 양대 공식 도메인(<a href="{SITE_DOMAINS[0]}" target="_blank" style="color:#0052CC; font-weight:700;">Director</a> · <a href="{SITE_DOMAINS[1]}" target="_blank" style="color:#0052CC; font-weight:700;">Supervisor</a>) 모두 즉시 접속이 활성화됩니다.</li>
                        </ul>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    with tab_signup:
        st.markdown("#### **신규 회원신청 및 관리자 승인 요청서 제출**")
        st.caption(
            f"아래 신청인이 작성한 8대 상세 항목과 원클릭 승인 링크가 총괄 관리자(`{ADMIN_EMAIL}`) 이메일로 즉시 발송됩니다."
        )

        with st.form("form_member_signup", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                su_name = st.text_input("1. 신청자 성명 *", placeholder="예: 김제일 프로")
                su_pos = st.text_input("3. 직급 / 직책 *", placeholder="예: 선임프로 / 팀장 / 매니저")
                su_email = st.text_input("5. 이메일 주소 (로그인 ID) *", placeholder="예: gildong.hong@cheil.com")
                su_pw = st.text_input("7. 사용할 비밀번호 (6자 이상) *", type="password", placeholder="6자 이상 비밀번호 입력")
            with c2:
                su_dept = st.text_input("2. 소속 회사 / 부서(팀) *", placeholder="예: 제일기획 BX익스피리언스팀 / 구매팀")
                su_phone = st.text_input("4. 연락처 (휴대폰 / 내선번호) *", placeholder="예: 010-1234-5678")
                su_reason = st.text_input("6. 가입 신청 사유 및 담당 프로젝트 *", placeholder="예: 2026 갤럭시 언팩 전시 실행예산 감리 및 단가 검증")
                su_pw_confirm = st.text_input("8. 비밀번호 재확인 *", type="password", placeholder="비밀번호를 한 번 더 입력하세요")

            su_agree = st.checkbox(
                "[필수 보안서약] 본 플랫폼 내 모든 프로젝트 실행예산, 협력사 단가 및 감리 리포트를 외부에 유출하지 않을 것을 서약합니다.",
                value=False,
            )

            submitted_signup = st.form_submit_button(
                f"회원신청 제출 및 관리자({ADMIN_EMAIL}) 승인 요청 메일 발송 →",
                type="primary",
                use_container_width=True,
            )

        if submitted_signup:
            if not su_agree:
                st.error("필수 보안서약 동의 체크박스를 선택해 주세요.")
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
                    <div style="background: #F8F9FB; border: 1px solid #CBD5E1; border-top: 3px solid #002C5F; padding: 24px 28px; margin-top: 16px;">
                        <div style="font-size: 16px; font-weight: 800; color: #002C5F; margin-bottom: 10px;">
                            가입신청 접수 및 메일 발송 완료 — 관리자({ADMIN_EMAIL}) 승인 대기 중
                        </div>
                        <div style="font-size: 13.5px; color: #111827; line-height: 1.75; margin-bottom: 16px; background: #FFFFFF; padding: 16px 20px; border: 1px solid #E5E8EB;">
                            <strong>[관리자 메일(<code>{ADMIN_EMAIL}</code>)로 전송된 신청인 작성 정보]</strong><br/>
                            • <strong>성명 / 직급:</strong> {user_rec.get('name')} ({user_rec.get('position', '-')})<br/>
                            • <strong>소속 부서/팀:</strong> {user_rec.get('department')}<br/>
                            • <strong>연락처:</strong> {user_rec.get('phone', '-')}<br/>
                            • <strong>이메일(로그인 ID):</strong> <code>{user_rec.get('email')}</code><br/>
                            • <strong>가입 신청 사유:</strong> {user_rec.get('reason')}<br/>
                            • <strong>신청 일시:</strong> {user_rec.get('created_at')}
                        </div>
                        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                            <a href="{mailto_href}" style="display: inline-block; background: #002C5F; color: #FFFFFF !important; text-decoration: none; padding: 11px 24px; font-size: 13px; font-weight: 700;">
                                내 메일앱으로 관리자({ADMIN_EMAIL})에게 승인링크 직접 발송 (즉시도달 보조) →
                            </a>
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    with tab_status:
        st.markdown("#### **가입신청 승인 상태 실시간 조회**")
        st.caption("가입신청 시 입력한 이메일 주소를 입력하면 관리자 승인 여부를 즉시 확인할 수 있습니다.")
        chk_col1, chk_col2 = st.columns([3, 1])
        with chk_col1:
            chk_email = st.text_input("조회할 이메일 주소 입력", placeholder="예: gildong.hong@cheil.com", key="chk_status_email")
        with chk_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_chk = st.button("승인 상태 조회 →", type="primary", use_container_width=True)

        if btn_chk and chk_email:
            found = get_user_status(chk_email)
            if not found:
                st.warning("해당 이메일로 접수된 회원신청 내역이 없습니다. [02 · 신규 회원신청 · 가입신청] 탭에서 먼저 신청해 주세요.")
            else:
                st_val = found.get("status", "pending")
                if st_val == "approved":
                    st.success(
                        f"✅ **{found.get('name')}** ({found.get('email')}) 회원님은 **관리자 승인이 완료(APPROVED)**되었습니다! "
                        f"상단 [01 · 승인 회원 로그인] 탭에서 바로 로그인하실 수 있습니다."
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

    # 6. MOGAM 코퍼레이트 푸터
    render_mogam_footer()

    return False
