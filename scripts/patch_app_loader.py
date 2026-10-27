# -*- coding: utf-8 -*-
import sys

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    is_crlf = '\r\n' in content
    line_sep = '\r\n' if is_crlf else '\n'

    old_block = line_sep.join([
        '    if data_source_mode == "광고주 컨펌 기준견적서 사용":',
        '        sample_est_str = selected_proj["sample_estimate"]',
        '        orig_path = Path(sample_est_str) if Path(sample_est_str).is_absolute() else (root_dir / "data" / sample_est_str)',
        '',
        '        sample_chg_str = selected_proj.get("sample_change")',
        '        if sample_chg_str:',
        '            rev_path = Path(sample_chg_str) if Path(sample_chg_str).is_absolute() else (root_dir / "data" / sample_chg_str)',
        '        else:',
        '            # 변경견적서가 지정되지 않은 경우 기준견적서를 자체 대조 기준으로 연결',
        '            rev_path = orig_path',
        '',
        '        if orig_path.exists():',
        '            orig_file_input = str(orig_path)',
        '            orig_file_name = orig_path.name',
        '            if rev_path.exists():',
        '                rev_file_input = str(rev_path)',
        '                rev_file_name = rev_path.name',
        '        else:',
        '            st.sidebar.error(f"파일을 찾을 수 없습니다: {orig_path}")'
    ])

    new_block = line_sep.join([
        '    if data_source_mode == "광고주 컨펌 기준견적서 사용":',
        '        sample_est_str = selected_proj.get("sample_estimate") or ""',
        '        sample_chg_str = selected_proj.get("sample_change")',
        '',
        '        # 1. 최초/기준 견적서 파일 다중 경로 탐색 (data/ 및 data/samples/ 우선 탐색)',
        '        candidate_orig = []',
        '        if sample_est_str:',
        '            if Path(sample_est_str).is_absolute():',
        '                candidate_orig.append(Path(sample_est_str))',
        '            candidate_orig.append(root_dir / "data" / sample_est_str)',
        '            candidate_orig.append(root_dir / "data" / "samples" / sample_est_str)',
        '        # 안전 fallback 샘플 파일 목록',
        '        candidate_orig.extend([',
        '            root_dir / "data" / "samples" / "전시 광고주컨펌완료 견적서 (1).xlsx",',
        '            root_dir / "data" / "samples" / "전시_광고주컨펌완료_기준견적서.xlsx",',
        '            root_dir / "data" / "samples" / "P001_최초견적.xlsx"',
        '        ])',
        '        orig_path = next((p for p in candidate_orig if p and p.exists()), None)',
        '',
        '        # 2. 변경 견적서 파일 탐색',
        '        candidate_rev = []',
        '        if sample_chg_str:',
        '            if Path(sample_chg_str).is_absolute():',
        '                candidate_rev.append(Path(sample_chg_str))',
        '            candidate_rev.append(root_dir / "data" / sample_chg_str)',
        '            candidate_rev.append(root_dir / "data" / "samples" / sample_chg_str)',
        '            candidate_rev.extend([',
        '                root_dir / "data" / "samples" / "전시_홍대점_변경내역.xlsx",',
        '                root_dir / "data" / "samples" / "P001_변경내역.xlsx"',
        '            ])',
        '        candidate_rev.append(orig_path)',
        '        rev_path = next((p for p in candidate_rev if p and p.exists()), orig_path)',
        '',
        '        if orig_path and orig_path.exists():',
        '            orig_file_input = str(orig_path)',
        '            orig_file_name = orig_path.name',
        '            if rev_path and rev_path.exists():',
        '                rev_file_input = str(rev_path)',
        '                rev_file_name = rev_path.name'
    ])

    if old_block in content:
        content = content.replace(old_block, new_block, 1)
        print("Replaced old_block with new safe loader block")
    else:
        print("Warning: old_block not found in app.py")
        sys.exit(1)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("app.py updated successfully!")

if __name__ == "__main__":
    main()
