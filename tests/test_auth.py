# -*- coding: utf-8 -*-
"""회원가입 · 관리자(feelingsoo@naver.com) 이메일 원클릭 승인 · 접근통제 테스트"""

import pytest
import auditor.auth as auth_mod


@pytest.fixture()
def isolated_users_db(tmp_path, monkeypatch):
    """테스트용 임시 users_db.json 격리 환경"""
    temp_db = tmp_path / "users_db.json"
    monkeypatch.setattr(auth_mod, "USERS_DB_FILE", temp_db)
    monkeypatch.setattr(auth_mod, "_sync_pull_from_github", lambda: None)
    monkeypatch.setattr(auth_mod, "_sync_push_to_github", lambda db: False)
    return temp_db


def test_master_admin_seeded_and_can_login(isolated_users_db):
    ok, msg, user = auth_mod.authenticate_member(
        auth_mod.ADMIN_EMAIL,
        auth_mod.DEFAULT_ADMIN_PASSWORD,
        sync_remote=False,
    )
    assert ok is True
    assert user is not None
    assert user["email"] == "feelingsoo@naver.com"
    assert user["role"] == "admin"
    assert user["status"] == "approved"


def test_signup_pending_blocks_login_until_email_approved(isolated_users_db):
    # 1. 회원신청 / 가입신청
    ok_reg, msg_reg, user_rec, urls = auth_mod.register_member_application(
        email="applicant@cheil.com",
        name="김제일 프로",
        department="BX익스피리언스팀",
        password="SecurePass123!",
        password_confirm="SecurePass123!",
        reason="전시 실행예산 감리 업무",
        send_email=False,
        sync_remote=False,
    )
    assert ok_reg is True
    assert user_rec["status"] == "pending"

    # 2. 승인 전 로그인 시도 -> 철저히 차단되어야 함
    ok_login1, msg_login1, _ = auth_mod.authenticate_member(
        "applicant@cheil.com",
        "SecurePass123!",
        sync_remote=False,
    )
    assert ok_login1 is False
    assert "승인 대기 중" in msg_login1

    # 3. 관리자(feelingsoo@naver.com) 메일 내 원클릭 [승인] 서명 토큰 생성 및 검증
    payload_b64, sig = auth_mod.create_signed_action_token("approve", user_rec)

    # 위변조된 서명은 거부되어야 함
    ok_bad, _, _ = auth_mod.verify_and_process_email_action(
        action="approve",
        payload_b64=payload_b64,
        sig="0000" + sig[4:],
        sync_remote=False,
    )
    assert ok_bad is False

    # 정상 서명 승인 링크 클릭 시 즉시 approved 전환
    ok_app, msg_app, rec = auth_mod.verify_and_process_email_action(
        action="approve",
        payload_b64=payload_b64,
        sig=sig,
        sync_remote=False,
    )
    assert ok_app is True
    assert rec["status"] == "approved"

    # 4. 승인 후 로그인 시도 -> 성공해야 함
    ok_login2, msg_login2, user2 = auth_mod.authenticate_member(
        "applicant@cheil.com",
        "SecurePass123!",
        sync_remote=False,
    )
    assert ok_login2 is True
    assert user2["status"] == "approved"


def test_stateless_email_approval_restores_after_container_reset(isolated_users_db):
    """컨테이너가 재시작되어 로컬 DB가 초기화된 상태에서도 이메일 승인 링크 클릭 시 계정이 복원·승인되는지 검증"""
    pw_hash, salt = auth_mod.hash_password("MyPass999!")
    virtual_user = {
        "email": "remote_user@cheil.com",
        "name": "박원격 프로",
        "department": "구매팀",
        "reason": "해외 전시 견적 대조",
        "password_hash": pw_hash,
        "salt": salt,
        "created_at": "2026-11-09 15:00:00 KST",
    }
    payload_b64, sig = auth_mod.create_signed_action_token("approve", virtual_user)

    ok_app, _, rec = auth_mod.verify_and_process_email_action(
        action="approve",
        payload_b64=payload_b64,
        sig=sig,
        sync_remote=False,
    )
    assert ok_app is True
    assert rec["status"] == "approved"

    # 복원 및 승인된 계정으로 즉시 로그인 가능 확인
    ok_login, _, _ = auth_mod.authenticate_member(
        "remote_user@cheil.com",
        "MyPass999!",
        sync_remote=False,
    )
    assert ok_login is True
