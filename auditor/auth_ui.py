# -*- coding: utf-8 -*-
"""
제일기획 AX 견적감독관 — 회원가입·관리자 이메일 승인·접근통제 UI (auth_ui.py)

워크플로우:
1. [회원신청] 사용자 정보(성명, 소속 부서/팀, 이메일, 비밀번호, 신청사유) 입력 및 보안 서약 동의
2. [가입신청] 제출 즉시 관리자(feelingsoo@naver.com)에게 가입신청 알림 및 원클릭 [가입 승인 / 반려] 링크 자동 메일 발송
3. [관리자 인증] 관리자가 수신한 이메일에서 [✅ 가입 즉시 승인] 버튼 클릭 시 즉시 승인 처리 (또는 관리자 콘솔에서 승인)
4. [사이트 이용] 승인 완료된 계정으로 로그인해야만 두 사이트 모두 내부 견적 데이터 및 AI 감리 기능 접근 가능
"""

import urllib.parse
from typing import Any, Dict, Optional
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
    # 캐시된 처리 결과가 없으면 검증 및 상태 업데이트 수행
    cache_key = f"email_action_done_{sig[:16]}_{action}"
    if cache_key not in st.session_state:
        ok, msg, record = verify_and_process_email_action(action=action, payload_b64=payload, sig=sig)
        st.session_state[cache_key] = (ok, msg, record)
    else:
        ok, msg, record = st.session_state[cache_key]

    is_approve = (action == "approve")
    badge_color = "#0E7C57" if (ok and is_approve) else ("#D92D20" if not ok else "#B54708")
    badge_bg = "rgba(14, 124, 87, 0.1)" if (ok and is_approve) else "rgba(217, 45, 32, 0.1)"
    icon_str = "✅" if (ok and is_approve) else ("🚫" if ok else "⚠️")
    title_str = (
        "관리자 이메일 원클릭 [가입 승인] 완료"
        if (ok and is_approve)
        else ("관리자 이메일 원클릭 [가입 반려] 완료" if ok else "이메일 승인 링크 검증 실패")
    )

    st.markdown(
        f"""
        <div class="mc-stadium-card" style="max-width: 760px; margin: 36px auto; padding: 40px 44px; border: 2px solid {badge_color}; background: var(--white); box-shadow: var(--shadow-cushion);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                <div class="mc-eyebrow">
                    <span class="mc-eyebrow-dot"></span>
                    <span>ADMIN EMAIL ONE-CLICK AUTHORIZATION</span>
                </div>
                <span style="background: {badge_bg}; color: {badge_color}; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 700;">
                    {icon_str} {'승인 완료 (APPROVED)' if (ok and is_approve) else ('반려 처리됨 (REJECTED)' if ok else '검증 오류')}
                </span>
            </div>
            <h2 style="margin: 0 0 12px 0; font-size: 26px; font-weight: 800; color: var(--ink-black);">
                {icon_str} {title_str}
            </h2>
            <p style="font-size: 15px; color: var(--slate-gray); line-height: 1.6; margin-bottom: 24px;">
                {msg}
            </p>
        """,
        unsafe_allow_html=True,
    )

    if record:
        st.markdown(
            f"""
            <div style="background: var(--surface-lifted); border: 1.5px solid var(--border-stone); border-radius: 18px; padding: 20px 24px; margin-bottom: 24px;">
                <div style="font-size: 13px; font-weight: 700; color: #CF4500; margin-bottom: 12px;">👤 처리된 회원 정보</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; font-size: 14px;">
                    <div><span style="color: var(--slate-gray);">성명:</span> <strong style="color: var(--ink-black); margin-left: 6px;">{record.get('name', '-')}</strong></div>
                    <div><span style="color: var(--slate-gray);">소속 부서/팀:</span> <strong style="color: var(--ink-black); margin-left: 6px;">{record.get('department', '-')}</strong></div>
                    <div><span style="color: var(--slate-gray);">이메일(ID):</span> <strong style="color: #0066CC; margin-left: 6px;">{record.get('email', '-')}</strong></div>
                    <div><span style="color: var(--slate-gray);">최종 상태:</span> <strong style="color: {badge_color}; margin-left: 6px;">{record.get('status', '').upper()}</strong></div>
                </div>
                <div style="margin-top: 12px; font-size: 12.5px; color: var(--slate-gray);">
                    • 승인 시각: {record.get('approved_at') or '-'} (승인자: {record.get('approved_by') or ADMIN_EMAIL})<br/>
                    • 이제 해당 회원은 두 사이트(<strong>ax-estimate-director</strong> 및 <strong>ax-estimate-supervisor</strong>)에서 모두 로그인하여 시스템을 이용할 수 있습니다.
                </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 로그인 및 메인 사이트로 이동", type="primary", use_container_width=True):
            _clear_query_params()
            st.rerun()


def render_sidebar_auth_Widget(user: Dict[str, Any]) -> None:
    """로그인 완료 후 좌측 사이드바 상단에 표시되는 인증 회원 정보 및 관리자 승인 콘솔입니다."""
    is_admin = (user.get("role") == "admin") or (user.get("email", "").lower() == ADMIN_EMAIL.lower())
    role_badge = "🛡️ 총괄 관리자" if is_admin else "✅ 승인 정회원"

    st.sidebar.markdown(
        f"""
        <div style="background: var(--white); border: 1.5px solid var(--border-stone); border-radius: 16px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-size: 11px; font-weight: 700; color: #0E7C57; background: rgba(14,124,87,0.1); padding: 3px 9px; border-radius: 999px;">{role_badge}</span>
                <span style="font-size: 11px; color: var(--slate-gray);">보안 인증됨 🔒</span>
            </div>
            <div style="font-size: 14.5px; font-weight: 700; color: var(--ink-black);">{user.get('name', '회원')} <span style="font-size: 12px; font-weight: 500; color: var(--slate-gray);">({user.get('department', '-')})</span></div>
            <div style="font-size: 12px; color: var(--slate-gray); margin-top: 2px;">{user.get('email', '')}</div>
        </div>
        """,
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
                        f"""
                        <div style="background:#FFF9F5; border:1px solid #F7C4A5; border-radius:10px; padding:10px 12px; margin-bottom:8px; font-size:12.5px;">
                            <strong>{pm.get('name')}</strong> ({pm.get('department')})<br/>
                            <span style="color:#0066CC;">{em}</span><br/>
                            <span style="color:#555;">사유: {pm.get('reason', '-')}</span><br/>
                            <span style="color:#888; font-size:11px;">신청: {pm.get('created_at', '-')}</span>
                        </div>
                        """,
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
    사이트 최상단 보안 게이트 함수.
    - URL 쿼리에 관리자 이메일 승인/반려 토큰(`auth_action`, `payload`, `sig`)이 있으면 즉시 처리 화면을 렌더링합니다.
    - 세션에 승인된 로그인 사용자가 있으면 사이드바 프로필을 표시하고 `True`를 반환합니다.
    - 미인증 상태면 내부 데이터를 일절 노출하지 않고 [로그인 / 회원신청·가입신청] 화면을 렌더링한 뒤 `False`를 반환합니다.
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

    # 3. 미인증 사용자: 좌측 사이드바 및 내부 UI를 완전히 숨기고 중앙 보안 로그인 게이트만 단독 노출
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapseButton"] {
                display: none !important;
            }
            .block-container {
                max-width: 960px !important;
                padding-top: 2.5rem !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 4. 중앙 메인 화면: 4단계 가입·승인 프로세스 배너 + 로그인 / 가입신청 탭
    st.markdown(
        f"""
        <div class="mc-stadium-card" style="padding: 32px 38px; margin: 16px 0 24px 0; border: 1.5px solid rgba(207, 69, 0, 0.35); background: var(--surface-lifted); box-shadow: var(--shadow-cushion);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 18px; flex-wrap: wrap; gap: 12px;">
                <div>
                    <div class="mc-eyebrow" style="margin-bottom: 4px;">
                        <span class="mc-eyebrow-dot"></span>
                        <span>ENTERPRISE ACCESS CONTROL & ADMIN EMAIL APPROVAL</span>
                    </div>
                    <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: var(--ink-black);">
                        🔒 회원제 보안 인증 및 관리자 승인 게이트
                    </h2>
                    <div style="font-size: 13.5px; color: var(--slate-gray); margin-top: 4px;">
                        두 공식 사이트(<a href="{SITE_DOMAINS[0]}" target="_blank" style="color:#0066CC; font-weight:600;">ax-estimate-director</a> · <a href="{SITE_DOMAINS[1]}" target="_blank" style="color:#0066CC; font-weight:600;">ax-estimate-supervisor</a>)는 통합 회원 인증 후 이용할 수 있습니다.
                    </div>
                </div>
                <span class="mc-pill-chip mc-chip-orange" style="font-size: 12px; font-weight: 700;">● 관리자 승인 필수</span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr)); gap: 12px; margin-top: 14px;">
                <div style="background: var(--white); border: 1px solid var(--border-stone); border-radius: 16px; padding: 14px 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #CF4500;">STEP 01 · 회원신청</div>
                    <div style="font-size: 14px; font-weight: 700; color: var(--ink-black); margin: 4px 0;">회원 정보 입력</div>
                    <div style="font-size: 12px; color: var(--slate-gray);">성명, 소속 부서/팀, 이메일, 비밀번호 및 신청 사유 작성</div>
                </div>
                <div style="background: var(--white); border: 1px solid var(--border-stone); border-radius: 16px; padding: 14px 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #CF4500;">STEP 02 · 가입신청</div>
                    <div style="font-size: 14px; font-weight: 700; color: var(--ink-black); margin: 4px 0;">관리자 메일 자동 발송</div>
                    <div style="font-size: 12px; color: var(--slate-gray);"><code>{ADMIN_EMAIL}</code>으로 승인 요청 메일 즉시 자동 전송</div>
                </div>
                <div style="background: var(--white); border: 1px solid var(--border-stone); border-radius: 16px; padding: 14px 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #CF4500;">STEP 03 · 관리자 인증</div>
                    <div style="font-size: 14px; font-weight: 700; color: var(--ink-black); margin: 4px 0;">메일 내 [가입 승인] 클릭</div>
                    <div style="font-size: 12px; color: var(--slate-gray);">관리자가 수신 메일에서 원클릭 승인 버튼 클릭 시 즉시 자격 부여</div>
                </div>
                <div style="background: var(--white); border: 1px solid var(--border-stone); border-radius: 16px; padding: 14px 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #0E7C57;">STEP 04 · 사이트 이용</div>
                    <div style="font-size: 14px; font-weight: 700; color: var(--ink-black); margin: 4px 0;">양대 사이트 즉시 접속</div>
                    <div style="font-size: 12px; color: var(--slate-gray);">승인 완료된 이메일·비밀번호로 로그인하여 전 기능 이용</div>
                </div>
            </div>
        </div>
        """,
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
            st.markdown("#### 🔐 승인 회원 / 관리자 로그인")
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
                f"""
                <div class="mc-card-20" style="background: var(--white); border: 1.5px solid var(--border-stone); padding: 24px;">
                    <div style="font-size: 13px; font-weight: 700; color: #CF4500; margin-bottom: 8px;">📌 이용 안내 및 보안 정책</div>
                    <ul style="font-size: 13px; color: var(--slate-gray); line-height: 1.7; padding-left: 18px; margin: 0;">
                        <li>아직 계정이 없으신 경우 상단 <strong>[📝 신규 회원신청 · 가입신청]</strong> 탭에서 가입을 신청해 주세요.</li>
                        <li>가입신청 즉시 총괄 관리자(<code>{ADMIN_EMAIL}</code>)에게 <strong>원클릭 승인 버튼이 포함된 이메일</strong>이 발송됩니다.</li>
                        <li>관리자가 메일에서 <strong>[✅ 가입 즉시 승인]</strong>을 클릭하면 그 즉시 로그인이 활성화됩니다.</li>
                        <li><strong>총괄 관리자 계정:</strong> <code>{ADMIN_EMAIL}</code> 로 로그인 시 좌측 사이드바에서 대기 회원 관리 및 메일 설정도 가능합니다.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_signup:
        st.markdown("#### 📝 신규 회원신청 → 가입신청서 제출")
        st.caption(
            f"아래 양식을 작성하여 제출하면 `{ADMIN_EMAIL}` 주소로 가입신청 내역과 관리자 전용 [원클릭 가입 승인] 링크가 자동 발송됩니다."
        )

        with st.form("form_member_signup", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                su_name = st.text_input("신청자 성명 *", placeholder="예: 홍길동 프로")
                su_email = st.text_input("이메일 주소 (로그인 ID) *", placeholder="예: gildong.hong@cheil.com")
                su_pw = st.text_input("사용할 비밀번호 (6자 이상) *", type="password", placeholder="6자 이상 비밀번호 입력")
            with c2:
                su_dept = st.text_input("소속 회사 / 부서(팀) *", placeholder="예: 제일기획 BX익스피리언스팀 / 구매팀")
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

        # 방금 신청한 경우 보조 메일 발송 버튼(클라우드 방화벽 대비 100% 도달 보장용) 함께 제공
        last_su = st.session_state.get("last_signup_info")
        if last_su and isinstance(last_su, dict):
            user_rec = last_su.get("user", {})
            action_urls = last_su.get("urls") or build_action_urls(user_rec)
            approve_url_dir = action_urls["approve_primary"]
            approve_url_sup = action_urls["approve_secondary"]

            mail_subj = urllib.parse.quote(
                f"[AX 견적감독관] 신규 회원가입 승인 요청 — {user_rec.get('name')} ({user_rec.get('department')})"
            )
            mail_body = urllib.parse.quote(
                f"관리자님 ({ADMIN_EMAIL}),\n\n"
                f"제일기획 AX 견적감독관 신규 회원가입 승인 요청입니다.\n\n"
                f"- 성명: {user_rec.get('name')}\n"
                f"- 소속 부서/팀: {user_rec.get('department')}\n"
                f"- 이메일(ID): {user_rec.get('email')}\n"
                f"- 신청 사유: {user_rec.get('reason')}\n"
                f"- 신청 일시: {user_rec.get('created_at')}\n\n"
                f"아래 [원클릭 가입 승인 링크]를 클릭하시면 즉시 가입이 승인되어 사이트 이용이 가능해집니다:\n\n"
                f"▶ 승인 링크 (견적감독관): {approve_url_sup}\n"
                f"▶ 승인 링크 (견적감리관): {approve_url_dir}\n"
            )
            mailto_href = f"mailto:{ADMIN_EMAIL}?subject={mail_subj}&body={mail_body}"

            st.markdown(
                f"""
                <div style="background: #F4FBF7; border: 1.5px solid #0E7C57; border-radius: 18px; padding: 20px 24px; margin-top: 14px;">
                    <div style="font-size: 15px; font-weight: 700; color: #0E7C57; margin-bottom: 6px;">
                        ✅ 가입신청 접수 완료 — 관리자({ADMIN_EMAIL}) 승인 대기 중
                    </div>
                    <div style="font-size: 13px; color: var(--ink-black); line-height: 1.6; margin-bottom: 12px;">
                        • 신청자: <strong>{user_rec.get('name')}</strong> ({user_rec.get('department')}) · <code>{user_rec.get('email')}</code><br/>
                        • 자동 메일 알림 상태: {last_su.get('email_status', '발송 요청됨')}<br/>
                        • 관리자가 수신한 이메일에서 <strong>[✅ 가입 즉시 승인]</strong> 버튼을 클릭하면 즉시 로그인하실 수 있습니다.
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <a href="{mailto_href}" style="display: inline-block; background: #03C75A; color: #FFFFFF; text-decoration: none; padding: 9px 18px; border-radius: 999px; font-size: 12.5px; font-weight: 700;">
                            📧 내 메일앱으로 관리자({ADMIN_EMAIL})에게 승인링크 직접 발송 (즉시도달 보조)
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_status:
        st.markdown("#### 🔎 내 가입신청 승인 상태 실시간 조회")
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
