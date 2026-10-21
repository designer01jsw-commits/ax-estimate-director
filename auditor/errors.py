# -*- coding: utf-8 -*-
"""견적 감리관 예외 정의 모듈"""

class AuditorError(Exception):
    """견적 감리관 기본 예외 클래스"""
    pass

class ValidationError(AuditorError):
    """사용자 안내용 검증 오류 예외

    엑셀 파일 형식, 필수 시트/열 누락, 빈 데이터 등
    사용자가 직접 인지하고 해결할 수 있는 오류를 다룹니다.
    """
    def __init__(self, message: str, file_name: str = "", sheet_name: str = "", row_idx: int | None = None):
        super().__init__(message)
        self.message = message
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.row_idx = row_idx

    def __str__(self):
        return self.message
