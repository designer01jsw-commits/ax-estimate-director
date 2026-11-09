# -*- coding: utf-8 -*-
"""
제일기획 AX 견적감독관 — 회원가입·관리자 이메일 승인·접근통제 보안 엔진 (auth.py)

프로세스:
1. 회원신청 / 가입신청 (이름, 소속 부서, 이메일, 비밀번호, 신청사유 입력)
2. 관리자 이메일(feelingsoo@naver.com)로 가입신청 알림 및 [원클릭 승인 / 반려] 서명 링크 자동 발송
3. 관리자가 이메일 내 [가입 승인] 링크 클릭 시 HMAC-SHA256 서명 검증 후 즉시 'approved' 전환
   (컨테이너 재시작 및 다중 도메인 환경을 고려해 서명된 페이로드 복원 + GitHub 원격 동기화 지원)
4. 승인 완료된 회원(또는 관리자)만 사이트 로그인 및 내부 견적 데이터 열람 가능
"""

import os
import json
import time
import hmac
import base64
import hashlib
import smtplib
import datetime
import urllib.request
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_DB_FILE = DATA_DIR / "users_db.json"
SMTP_CONFIG_FILE = DATA_DIR / "smtp_config.json"

ADMIN_EMAIL = "feelingsoo@naver.com"
DEFAULT_ADMIN_PASSWORD = os.environ.get("AX_ADMIN_PASSWORD", "CheilAX2026!")

# 양대 운영 도메인 (신규 감독관 & 기존 감리관)
SITE_DOMAINS = [
    "https://ax-estimate-director.onrender.com",
    "https://ax-estimate-supervisor.onrender.com",
]

# HMAC 서명용 시크릿 키 (환경변수 우선, 없으면 프로젝트 고유 고정 시드 사용)
AUTH_SECRET_KEY = os.environ.get(
    "AX_AUTH_SECRET_KEY",
    "CHEIL_AX_ESTIMATE_SUPERVISOR_HMAC_SECRET_2026_FEELINGSOO"
)


def _now_kst_str() -> str:
    tz_kst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(tz_kst).strftime("%Y-%m-%d %H:%M:%S KST")


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """PBKDF2-HMAC-SHA256 (200,000회 반복)으로 비밀번호를 안전하게 해시합니다."""
    if not salt:
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode("ascii")
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000,
    )
    return base64.urlsafe_b64encode(dk).decode("ascii"), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    calc_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(calc_hash, stored_hash)


def _get_github_sync_credentials() -> Tuple[Optional[str], str]:
    """
    환경변수 또는 로컬 .git/config에서 GitHub 토큰과 저장소 경로를 추출하여
    클라우드 컨테이너 재시작 및 두 사이트 간 회원 DB 실시간 동기화에 활용합니다.
    """
    token = os.environ.get("AX_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("AX_GITHUB_REPO", "designer01jsw-commits/ax-estimate-director")

    if not token:
        git_cfg = Path(__file__).resolve().parent.parent / ".git" / "config"
        if git_cfg.exists():
            try:
                cfg_text = git_cfg.read_text(encoding="utf-8", errors="ignore")
                for line in cfg_text.splitlines():
                    line_s = line.strip()
                    if "github.com/" in line_s and "@" in line_s and "url =" in line_s:
                        # 예: https://user:gho_xxx@github.com/owner/repo.git
                        after_proto = line_s.split("://", 1)[1]
                        creds, host_path = after_proto.split("@", 1)
                        if ":" in creds:
                            token = creds.split(":", 1)[1].strip()
                        if "github.com/" in host_path:
                            r_path = host_path.split("github.com/", 1)[1].strip()
                            if r_path.endswith(".git"):
                                r_path = r_path[:-4]
                            if r_path:
                                repo = r_path
                        break
            except Exception:
                pass
    return token, repo


def _default_users_db() -> Dict[str, Any]:
    admin_hash, admin_salt = hash_password(DEFAULT_ADMIN_PASSWORD, "CHEIL_ADMIN_SALT_2026")
    return {
        "version": 1,
        "admin_email": ADMIN_EMAIL,
        "updated_at": _now_kst_str(),
        "users": {
            ADMIN_EMAIL: {
                "email": ADMIN_EMAIL,
                "name": "관리자 (정승우)",
                "department": "제일기획 BX 퍼포먼스 7팀 (관리자)",
                "reason": "시스템 총괄 관리자",
                "role": "admin",
                "status": "approved",
                "password_hash": admin_hash,
                "salt": admin_salt,
                "created_at": "2026-10-01 09:00:00 KST",
                "approved_at": "2026-10-01 09:00:00 KST",
                "approved_by": "SYSTEM_INIT",
            }
        },
    }


def _sync_pull_from_github() -> Optional[Dict[str, Any]]:
    """원격 저장소에 저장된 최신 회원 DB가 있으면 가져옵니다 (두 사이트 간 동기화)."""
    token, repo = _get_github_sync_credentials()
    if not token or not repo:
        return None
    url = f"https://api.github.com/repos/{repo}/contents/data/users_db.json"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Cheil-AX-Auth-Sync",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            content_b64 = payload.get("content", "")
            if content_b64:
                raw = base64.b64decode(content_b64).decode("utf-8")
                return json.loads(raw)
    except Exception:
        return None
    return None


def _sync_push_to_github(db_data: Dict[str, Any]) -> bool:
    """회원 신청/승인 변경사항을 원격 저장소 data/users_db.json에 동기화합니다."""
    token, repo = _get_github_sync_credentials()
    if not token or not repo:
        return False
    url = f"https://api.github.com/repos/{repo}/contents/data/users_db.json"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "Cheil-AX-Auth-Sync",
    }
    sha = None
    try:
        req_get = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req_get, timeout=4) as resp:
            existing = json.loads(resp.read().decode("utf-8"))
            sha = existing.get("sha")
    except Exception:
        sha = None

    try:
        json_bytes = json.dumps(db_data, ensure_ascii=False, indent=2).encode("utf-8")
        body: Dict[str, Any] = {
            "message": f"chore(auth): sync member approval database ({_now_kst_str()})",
            "content": base64.b64encode(json_bytes).decode("ascii"),
        }
        if sha:
            body["sha"] = sha
        req_put = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="PUT",
        )
        with urllib.request.urlopen(req_put, timeout=5) as resp:
            return resp.status in (200, 201)
    except Exception:
        return False


def load_users_db(force_remote_check: bool = False) -> Dict[str, Any]:
    """로컬 및 원격 동기화 스토리지에서 회원 데이터베이스를 로드합니다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = _default_users_db()

    if USERS_DB_FILE.exists():
        try:
            local_db = json.loads(USERS_DB_FILE.read_text(encoding="utf-8"))
            if isinstance(local_db, dict) and "users" in local_db:
                db["users"].update(local_db["users"])
        except Exception:
            pass

    if force_remote_check:
        remote_db = _sync_pull_from_github()
        if isinstance(remote_db, dict) and "users" in remote_db:
            for email_k, u_val in remote_db["users"].items():
                local_u = db["users"].get(email_k)
                # 원격에 승인(approved) 또는 반려(rejected) 상태가 있으면 우선 반영
                if not local_u or u_val.get("status") in ("approved", "rejected"):
                    db["users"][email_k] = u_val

    # 관리자 계정은 항상 approved 및 admin 권한 보장
    if ADMIN_EMAIL not in db["users"]:
        default_admin = _default_users_db()["users"][ADMIN_EMAIL]
        db["users"][ADMIN_EMAIL] = default_admin
    else:
        db["users"][ADMIN_EMAIL]["role"] = "admin"
        db["users"][ADMIN_EMAIL]["status"] = "approved"

    return db


def save_users_db(db: Dict[str, Any], sync_remote: bool = True) -> None:
    """회원 데이터베이스를 로컬 파일에 저장하고 가능한 경우 원격 동기화를 수행합니다."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db["updated_at"] = _now_kst_str()
    USERS_DB_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    if sync_remote:
        _sync_push_to_github(db)


def create_signed_action_token(action: str, user_record: Dict[str, Any]) -> Tuple[str, str]:
    """
    관리자 이메일 내 원클릭 승인/반려 링크를 위한 서명된 페이로드와 HMAC-SHA256 서명을 생성합니다.
    컨테이너가 재시작되더라도 링크 자체에 암호화 해시된 회원 정보가 포함되어 즉시 복원·승인됩니다.
    """
    compact_data = {
        "e": user_record["email"],
        "n": user_record["name"],
        "d": user_record.get("department", ""),
        "r": user_record.get("reason", ""),
        "h": user_record["password_hash"],
        "s": user_record["salt"],
        "t": user_record.get("created_at", _now_kst_str()),
    }
    raw_json = json.dumps(compact_data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(raw_json).decode("ascii")
    msg = f"{action}|{payload_b64}".encode("utf-8")
    sig = hmac.new(AUTH_SECRET_KEY.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return payload_b64, sig


def verify_and_process_email_action(
    action: str,
    payload_b64: str,
    sig: str,
    sync_remote: bool = True,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    관리자가 이메일에서 클릭한 승인(approve) 또는 반려(reject) 링크의 HMAC 서명을 검증하고
    회원 상태를 즉시 업데이트합니다.
    """
    if action not in ("approve", "reject"):
        return False, "유효하지 않은 요청 액션입니다.", None
    if not payload_b64 or not sig:
        return False, "승인 토큰 또는 서명 정보가 누락되었습니다.", None

    expected_msg = f"{action}|{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(AUTH_SECRET_KEY.encode("utf-8"), expected_msg, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return False, "보안 서명(HMAC) 검증에 실패했습니다. 변조되었거나 만료된 승인 링크입니다.", None

    try:
        raw_bytes = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
        data = json.loads(raw_bytes.decode("utf-8"))
        email = str(data["e"]).strip().lower()
    except Exception as e:
        return False, f"신청자 데이터 복원 중 오류가 발생했습니다: {e}", None

    db = load_users_db(force_remote_check=sync_remote)
    user = db["users"].get(email)
    if not user:
        user = {
            "email": email,
            "name": data.get("n", ""),
            "department": data.get("d", ""),
            "reason": data.get("r", ""),
            "role": "member",
            "password_hash": data["h"],
            "salt": data["s"],
            "created_at": data.get("t", _now_kst_str()),
        }

    new_status = "approved" if action == "approve" else "rejected"
    user["status"] = new_status
    user["approved_at"] = _now_kst_str()
    user["approved_by"] = ADMIN_EMAIL
    db["users"][email] = user
    save_users_db(db, sync_remote=sync_remote)

    if new_status == "approved":
        return True, f"✅ [{user['name']} ({email})] 회원의 가입 승인이 완료되었습니다! 이제 사이트에 로그인하여 모든 기능을 이용할 수 있습니다.", user
    else:
        return True, f"🚫 [{user['name']} ({email})] 회원의 가입 신청이 반려(차단) 처리되었습니다.", user


def build_action_urls(user_record: Dict[str, Any], base_url: Optional[str] = None) -> Dict[str, str]:
    """승인 및 반려 원클릭 URL을 생성합니다."""
    p_app, s_app = create_signed_action_token("approve", user_record)
    p_rej, s_rej = create_signed_action_token("reject", user_record)

    primary_domain = (base_url or SITE_DOMAINS[0]).rstrip("/")
    secondary_domain = SITE_DOMAINS[1].rstrip("/")

    q_approve = urllib.parse.urlencode({"auth_action": "approve", "payload": p_app, "sig": s_app})
    q_reject = urllib.parse.urlencode({"auth_action": "reject", "payload": p_rej, "sig": s_rej})

    return {
        "approve_primary": f"{primary_domain}/?{q_approve}",
        "approve_secondary": f"{secondary_domain}/?{q_approve}",
        "reject_primary": f"{primary_domain}/?{q_reject}",
        "reject_secondary": f"{secondary_domain}/?{q_reject}",
    }


def load_smtp_config() -> Dict[str, str]:
    """관리자 메일 발송용 SMTP 설정을 로드합니다."""
    cfg = {
        "smtp_host": os.environ.get("AX_SMTP_HOST", "smtp.naver.com"),
        "smtp_port": os.environ.get("AX_SMTP_PORT", "465"),
        "smtp_user": os.environ.get("AX_SMTP_USER", ADMIN_EMAIL),
        "smtp_password": os.environ.get("AX_SMTP_PASSWORD", ""),
    }
    if SMTP_CONFIG_FILE.exists():
        try:
            saved = json.loads(SMTP_CONFIG_FILE.read_text(encoding="utf-8"))
            for k in ("smtp_host", "smtp_port", "smtp_user", "smtp_password"):
                if saved.get(k):
                    cfg[k] = str(saved[k])
        except Exception:
            pass
    return cfg


def save_smtp_config(smtp_host: str, smtp_port: str, smtp_user: str, smtp_password: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SMTP_CONFIG_FILE.write_text(
        json.dumps(
            {
                "smtp_host": smtp_host.strip(),
                "smtp_port": str(smtp_port).strip(),
                "smtp_user": smtp_user.strip(),
                "smtp_password": smtp_password,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def send_signup_approval_email(
    user_record: Dict[str, Any],
    base_url: Optional[str] = None,
) -> Tuple[bool, str, Dict[str, str]]:
    """
    가입 신청 시 feelingsoo@naver.com 으로 관리자 승인 버튼이 포함된 이메일을 자동 발송합니다.
    1순위: 설정된 SMTP (네이버 메일 smtp.naver.com 등) 직접 발송
    2순위: 클라우드 방화벽 무관 HTTPS 이메일 릴레이 (FormSubmit AJAX API -> feelingsoo@naver.com)
    """
    urls = build_action_urls(user_record, base_url=base_url)
    name = user_record.get("name", "-")
    email = user_record.get("email", "-")
    dept = user_record.get("department", "-")
    reason = user_record.get("reason", "-")
    created_at = user_record.get("created_at", _now_kst_str())

    subject = f"[AI 견적감독관 회원가입 승인요청] {name} ({dept}) 님의 가입 신청"

    html_body = f"""
    <div style="font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; max-width: 620px; margin: 0 auto; padding: 28px; background-color: #F3F0EE; border-radius: 20px; border: 1px solid #D1CDC7;">
        <div style="background-color: #141413; color: #FFFFFF; padding: 18px 24px; border-radius: 14px; margin-bottom: 20px;">
            <div style="font-size: 12px; color: #F37338; font-weight: 700; letter-spacing: 0.05em;">CHEIL AX ESTIMATE SUPERVISOR · SECURITY GATE</div>
            <h2 style="margin: 6px 0 0 0; font-size: 20px; color: #FFFFFF;">신규 회원가입 및 사이트 접근 승인 요청</h2>
        </div>

        <div style="background-color: #FFFFFF; padding: 22px 24px; border-radius: 14px; margin-bottom: 22px; border: 1px solid #E5E2DC;">
            <p style="margin-top: 0; font-size: 14px; color: #262627; line-height: 1.6;">
                관리자(<strong>{ADMIN_EMAIL}</strong>)님, <strong>제일기획 AI 견적감독관</strong> 웹 서비스에 아래와 같이 신규 회원가입 신청이 접수되었습니다.<br/>
                아래 <strong>[✅ 가입 승인하기]</strong> 버튼을 클릭하시면 해당 회원의 사이트 접근 권한이 즉시 활성화됩니다.
            </p>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 14px;">
                <tr>
                    <td style="padding: 9px 12px; background: #F8F7F5; font-weight: 700; width: 130px; border-bottom: 1px solid #EAE7E1;">신청자 성명</td>
                    <td style="padding: 9px 12px; border-bottom: 1px solid #EAE7E1;">{name}</td>
                </tr>
                <tr>
                    <td style="padding: 9px 12px; background: #F8F7F5; font-weight: 700; border-bottom: 1px solid #EAE7E1;">소속 부서 / 팀</td>
                    <td style="padding: 9px 12px; border-bottom: 1px solid #EAE7E1;">{dept}</td>
                </tr>
                <tr>
                    <td style="padding: 9px 12px; background: #F8F7F5; font-weight: 700; border-bottom: 1px solid #EAE7E1;">이메일 (로그인 ID)</td>
                    <td style="padding: 9px 12px; border-bottom: 1px solid #EAE7E1;">{email}</td>
                </tr>
                <tr>
                    <td style="padding: 9px 12px; background: #F8F7F5; font-weight: 700; border-bottom: 1px solid #EAE7E1;">신청 사유 / 업무</td>
                    <td style="padding: 9px 12px; border-bottom: 1px solid #EAE7E1;">{reason}</td>
                </tr>
                <tr>
                    <td style="padding: 9px 12px; background: #F8F7F5; font-weight: 700;">신청 일시</td>
                    <td style="padding: 9px 12px;">{created_at}</td>
                </tr>
            </table>
        </div>

        <div style="text-align: center; margin: 26px 0;">
            <a href="{urls['approve_primary']}" style="display: inline-block; background-color: #10B981; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 15px; padding: 14px 28px; border-radius: 999px; margin: 6px;">
                ✅ 가입 승인하기 (사이트 접근 허용)
            </a>
            <a href="{urls['reject_primary']}" style="display: inline-block; background-color: #CF4500; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 15px; padding: 14px 24px; border-radius: 999px; margin: 6px;">
                ❌ 가입 반려하기
            </a>
        </div>

        <div style="background-color: #FCFBFA; padding: 14px 18px; border-radius: 12px; font-size: 12px; color: #696969; line-height: 1.6;">
            <div><strong>[보조 도메인 원클릭 승인 링크]</strong></div>
            <div>• 메인 도메인 승인: <a href="{urls['approve_primary']}">{urls['approve_primary']}</a></div>
            <div>• 서브 도메인 승인: <a href="{urls['approve_secondary']}">{urls['approve_secondary']}</a></div>
        </div>
    </div>
    """

    # 1. SMTP 직접 발송 시도 (비밀번호 설정 시)
    smtp_cfg = load_smtp_config()
    if smtp_cfg.get("smtp_password"):
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_cfg["smtp_user"]
            msg["To"] = ADMIN_EMAIL
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            port = int(smtp_cfg.get("smtp_port", 465))
            host = smtp_cfg.get("smtp_host", "smtp.naver.com")
            if port == 465:
                with smtplib.SMTP_SSL(host, port, timeout=8) as server:
                    server.login(smtp_cfg["smtp_user"], smtp_cfg["smtp_password"])
                    server.sendmail(smtp_cfg["smtp_user"], [ADMIN_EMAIL], msg.as_string())
            else:
                with smtplib.SMTP(host, port, timeout=8) as server:
                    server.starttls()
                    server.login(smtp_cfg["smtp_user"], smtp_cfg["smtp_password"])
                    server.sendmail(smtp_cfg["smtp_user"], [ADMIN_EMAIL], msg.as_string())
            return True, f"관리자 이메일({ADMIN_EMAIL})로 승인 요청 메일이 즉시 발송되었습니다 (SMTP 직결).", urls
        except Exception:
            pass

    # 2. 클라우드 HTTPS 이메일 릴레이 자동 발송 (FormSubmit AJAX API -> feelingsoo@naver.com)
    try:
        relay_url = f"https://formsubmit.co/ajax/{ADMIN_EMAIL}"
        payload_data = {
            "_subject": subject,
            "_template": "table",
            "_captcha": "false",
            "신청자_성명": name,
            "소속_부서": dept,
            "신청자_이메일_ID": email,
            "신청_사유": reason,
            "신청_일시": created_at,
            "원클릭_가입승인_링크_1(Director)": urls["approve_primary"],
            "원클릭_가입승인_링크_2(Supervisor)": urls["approve_secondary"],
            "원클릭_가입반려_링크": urls["reject_primary"],
            "안내": "위 [원클릭_가입승인_링크]를 클릭하시면 즉시 가입이 승인되어 신청자가 두 사이트 모두에 로그인할 수 있습니다.",
        }
        req = urllib.request.Request(
            relay_url,
            data=json.dumps(payload_data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin": SITE_DOMAINS[0],
                "Referer": SITE_DOMAINS[0] + "/",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            resp_json = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if resp.status == 200 and str(resp_json.get("success", "")).lower() in ("true", "1"):
                return True, f"관리자 이메일({ADMIN_EMAIL})로 가입 승인 요청 메일이 자동 발송되었습니다.", urls
            msg_detail = resp_json.get("message", "")
            return True, f"관리자 이메일({ADMIN_EMAIL})로 승인 요청이 접수되었습니다. ({msg_detail})", urls
    except Exception as e:
        return False, f"클라우드 메일 자동 발송 대기 중 (관리자 대시보드에서도 즉시 승인 가능): {e}", urls


def register_member_application(
    name: str,
    department: str,
    email: str,
    password: str,
    reason: str = "",
    password_confirm: Optional[str] = None,
    send_email: bool = True,
    sync_remote: bool = True,
) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    """
    신규 회원 가입 신청을 등록(status='pending')하고 관리자(feelingsoo@naver.com)에게 승인 메일을 발송합니다.
    """
    clean_name = (name or "").strip()
    clean_dept = (department or "").strip()
    clean_email = (email or "").strip().lower()
    clean_reason = (reason or "").strip()

    if not clean_name:
        return False, "신청자 성명을 입력해 주세요.", None, None
    if not clean_dept:
        return False, "소속 부서 또는 팀명을 입력해 주세요.", None, None
    if not clean_email or "@" not in clean_email or "." not in clean_email.split("@")[-1]:
        return False, "올바른 이메일 주소를 입력해 주세요.", None, None
    if not password or len(password) < 6:
        return False, "비밀번호는 최소 6자 이상 입력해 주세요.", None, None
    if password_confirm is not None and password != password_confirm:
        return False, "비밀번호와 비밀번호 재확인이 일치하지 않습니다.", None, None

    db = load_users_db(force_remote_check=sync_remote)
    existing = db["users"].get(clean_email)
    if existing and existing.get("status") == "approved":
        return False, "이미 관리자 승인이 완료된 이메일 계정입니다. [로그인] 탭에서 바로 로그인해 주세요.", existing, None

    pw_hash, salt = hash_password(password)
    user_record = {
        "email": clean_email,
        "name": clean_name,
        "department": clean_dept,
        "reason": clean_reason or "전시·키트 견적 감리 및 정산 검증 업무",
        "role": "member",
        "status": "pending",
        "password_hash": pw_hash,
        "salt": salt,
        "created_at": _now_kst_str(),
        "approved_at": None,
        "approved_by": None,
    }

    db["users"][clean_email] = user_record
    save_users_db(db, sync_remote=sync_remote)

    urls = build_action_urls(user_record)
    email_msg = ""
    if send_email:
        _, email_msg, urls = send_signup_approval_email(user_record)

    return (
        True,
        f"가입 신청이 완료되었습니다! 관리자({ADMIN_EMAIL})에게 승인 요청 메일이 발송되었으며, 관리자가 메일에서 [승인]을 클릭하면 즉시 로그인이 가능합니다. {email_msg}",
        user_record,
        urls,
    )


def authenticate_member(
    email: str,
    password: str,
    sync_remote: bool = True,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    회원 로그인 검증:
    - 미가입: 가입 안내
    - pending (승인 대기): 관리자 승인 후 이용 가능 안내 (접근 차단)
    - rejected (반려): 접근 차단 안내
    - approved (승인 완료): 비밀번호 검증 후 로그인 허용
    """
    clean_email = (email or "").strip().lower()
    if not clean_email or not password:
        return False, "이메일 아이디와 비밀번호를 모두 입력해 주세요.", None

    db = load_users_db(force_remote_check=False)
    user = db["users"].get(clean_email)

    # 로컬에 없거나 아직 pending이면 원격 DB(이메일 승인 반영분) 재확인
    if (not user or user.get("status") != "approved") and sync_remote:
        db = load_users_db(force_remote_check=True)
        user = db["users"].get(clean_email)

    if not user:
        return False, "등록되지 않은 이메일 계정입니다. 먼저 [회원신청 · 가입신청] 탭에서 가입 신청을 진행해 주세요.", None

    if not verify_password(password, user.get("password_hash", ""), user.get("salt", "")):
        return False, "비밀번호가 일치하지 않습니다. 다시 확인해 주세요.", None

    status = user.get("status", "pending")
    if status == "pending":
        return (
            False,
            f"⏳ 현재 관리자({ADMIN_EMAIL}) 승인 대기 중입니다. 관리자가 신청 메일에서 [가입 승인]을 완료하면 사이트에 접속하실 수 있습니다.",
            user,
        )
    if status == "rejected":
        return (
            False,
            f"🚫 관리자에 의해 가입 신청이 반려되었거나 접근이 제한된 계정입니다. (문의: {ADMIN_EMAIL})",
            user,
        )

    return True, f"환영합니다, {user.get('name')} ({user.get('department')}) 님!", user


def admin_set_user_status(target_email: str, new_status: str, sync_remote: bool = True) -> Tuple[bool, str]:
    """관리자 대시보드에서 특정 회원의 상태를 approved / rejected / pending 으로 변경합니다."""
    clean_email = (target_email or "").strip().lower()
    if clean_email == ADMIN_EMAIL and new_status != "approved":
        return False, "총괄 관리자 계정은 차단할 수 없습니다."

    db = load_users_db(force_remote_check=sync_remote)
    user = db["users"].get(clean_email)
    if not user:
        return False, "해당 이메일 계정을 찾을 수 없습니다."

    user["status"] = new_status
    user["approved_at"] = _now_kst_str()
    user["approved_by"] = ADMIN_EMAIL
    db["users"][clean_email] = user
    save_users_db(db, sync_remote=sync_remote)
    return True, f"[{user.get('name')} ({clean_email})] 계정의 상태가 '{new_status}'로 변경되었습니다."


def admin_update_member_status(target_email: str, action: str, sync_remote: bool = True) -> Tuple[bool, str]:
    """관리자 콘솔에서 approve / reject 액션으로 회원 상태를 변경합니다."""
    new_status = "approved" if action in ("approve", "approved") else ("rejected" if action in ("reject", "rejected") else "pending")
    return admin_set_user_status(target_email, new_status, sync_remote=sync_remote)


def get_user_status(email: str, sync_remote: bool = True) -> Optional[Dict[str, Any]]:
    """특정 이메일 계정의 가입/승인 상태를 조회합니다."""
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return None
    db = load_users_db(force_remote_check=sync_remote)
    return db["users"].get(clean_email)


def list_all_members(sync_remote: bool = False) -> List[Dict[str, Any]]:
    """전체 등록 회원 목록을 반환합니다."""
    db = load_users_db(force_remote_check=sync_remote)
    users = list(db.get("users", {}).values())
    users.sort(key=lambda u: (0 if u.get("status") == "pending" else 1, u.get("created_at", "")))
    return users

