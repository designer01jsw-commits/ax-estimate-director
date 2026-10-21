# -*- coding: utf-8 -*-
"""프로젝트 목록 관리 모듈"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

DEFAULT_PROJECTS_FILE = Path(__file__).resolve().parent.parent / "data" / "projects.json"

def load_projects(file_path: Path | str = DEFAULT_PROJECTS_FILE) -> Tuple[List[Dict[str, Any]], List[str]]:
    """프로젝트 목록을 로드하고 (프로젝트 리스트, 경고 메시지 목록) 튜플을 반환합니다.
    파일이 없거나 JSON 오류가 발생해도 예외를 발생시키지 않고 안내 문구를 반환합니다.
    """
    path = Path(file_path)
    warnings = []
    
    if not path.exists():
        warnings.append(f"프로젝트 목록 파일({path.name})을 찾을 수 없습니다. 기본 프로젝트 모드로 동작합니다.")
        return [], warnings

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            if not isinstance(data, list):
                warnings.append(f"프로젝트 목록 형식 오류: JSON 루트가 배열이어야 합니다.")
                return [], warnings
            return data, warnings
    except json.JSONDecodeError as e:
        warnings.append(f"프로젝트 목록({path.name}) 형식이 올바르지 않습니다: {e.msg}")
        return [], warnings
    except Exception as e:
        warnings.append(f"프로젝트 목록을 읽는 중 문제가 발생했습니다: {str(e)}")
        return [], warnings

