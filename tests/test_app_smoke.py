# -*- coding: utf-8 -*-
"""Streamlit AppTest 스모크 테스트"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_PATH = str(ROOT_DIR / "app.py")

def test_app_smoke_p001_run():
    """앱이 오류 없이 실행되고 메트릭 카드가 정상 렌더링되는지 검증"""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    assert len(at.metric) >= 4

def test_app_smoke_no_crash():
    """예기치 않은 크래시 없이 사이드바 및 탭이 정상 로드되는지 확인"""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
