# -*- coding: utf-8 -*-
from pathlib import Path

schema_path = Path("auditor/schema.py")
content = schema_path.read_text(encoding="utf-8")

old_part = '''    # 단가
    "단가": "단가",
    "단가(원)": "단가",
    "단가(usd)": "단가",
    "단가(krw)": "단가",
    "단가원": "단가",
    "거래가격": "단가",
    "견적가": "단가",
    "견적단가": "단가",
    "unitprice": "단가",
    "price": "단가",
    
    # 금액
    "금액": "금액",
    "금액(원)": "금액",
    "합계금액": "금액",
    "금액원": "금액",
    "수정가격": "금액",
    "거래금액": "금액",
    "견적금액": "금액",
    "총금액": "금액",
    "최종금액": "금액",
    "최종수렴비용": "금액",
    "최종방향금액": "금액",
    "최종비용": "금액",
    "비용": "금액",
    "amount": "금액",
    "total": "금액",
    "소계": "금액",'''

new_part = '''    # 단가
    "단가": "단가",
    "단가(원)": "단가",
    "단가(usd)": "단가",
    "단가(krw)": "단가",
    "단가원": "단가",
    "거래가격": "단가",
    "견적가": "단가",
    "견적단가": "단가",
    "적용단가": "단가",
    "기준단가": "단가",
    "표준단가": "단가",
    "단가(vat별도)": "단가",
    "단가(vat포함)": "단가",
    "단가(부가세별도)": "단가",
    "단가(부가세포함)": "단가",
    "unitprice": "단가",
    "price": "단가",
    
    # 금액
    "금액": "금액",
    "금액(원)": "금액",
    "합계금액": "금액",
    "금액원": "금액",
    "수정가격": "금액",
    "거래금액": "금액",
    "견적금액": "금액",
    "공급가액": "금액",
    "공급가": "금액",
    "합계": "금액",
    "총액": "금액",
    "총합계": "금액",
    "금액(vat별도)": "금액",
    "금액(vat포함)": "금액",
    "금액(부가세별도)": "금액",
    "금액(부가세포함)": "금액",
    "계": "금액",
    "총금액": "금액",
    "최종금액": "금액",
    "최종수렴비용": "금액",
    "최종방향금액": "금액",
    "최종비용": "금액",
    "비용": "금액",
    "amount": "금액",
    "total": "금액",
    "소계": "금액",'''

normalized = content.replace("\r\n", "\n")
assert old_part in normalized, "old_part not found"
normalized = normalized.replace(old_part, new_part, 1)
schema_path.write_text(normalized, encoding="utf-8")
print("SUCCESS: patched schema.py with expanded price and amount aliases!")
