# -*- coding: utf-8 -*-
"""auditor/export.py 단위 테스트"""

import pytest
from auditor.export import generate_csv_filename, export_to_csv_bytes

def test_generate_csv_filename():
    fname = generate_csv_filename("P001", "검토필요")
    assert fname.startswith("P001_검토필요_")
    assert fname.endswith(".csv")

def test_export_to_csv_bytes_utf8_sig():
    data = [
        {"항목코드": "E-001", "항목명": "아크릴 케이스", "차이금액": 140000, "원본_최초": "최초.xlsx / 견적 / 4행"}
    ]
    csv_bytes = export_to_csv_bytes(data)
    # utf-8-sig BOM 확인 (b'\xef\xbb\xbf')
    assert csv_bytes.startswith(b"\xef\xbb\xbf")
    # 한글 문자열 및 원본 추적 열 디코딩 확인
    decoded = csv_bytes.decode("utf-8-sig")
    assert "아크릴 케이스" in decoded
    assert "원본_최초" in decoded
    assert "최초.xlsx / 견적 / 4행" in decoded
