# -*- coding: utf-8 -*-
"""CSV 내보내기 유틸리티 모듈"""

import datetime
from io import BytesIO
from typing import Any, Dict, List
import pandas as pd

def generate_csv_filename(project_id: str, table_name: str) -> str:
    """명세 형식 {프로젝트ID}_{표이름}_{YYYYMMDD_HHMM}.csv 에 맞는 파일명을 생성합니다."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    return f"{project_id}_{table_name}_{timestamp}.csv"

def export_to_csv_bytes(records: List[Dict[str, Any]]) -> bytes:
    """데이터 목록을 utf-8-sig 인코딩된 CSV 바이트 데이터로 변환합니다."""
    if not records:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(records)
    
    # 엑셀 한글 호환을 위해 utf-8-sig 인코딩 적용
    csv_str = df.to_csv(index=False, encoding="utf-8-sig")
    return csv_str.encode("utf-8-sig")
