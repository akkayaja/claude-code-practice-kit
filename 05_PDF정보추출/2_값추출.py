# 2_값추출.py
# invoices 폴더의 거래명세서 PDF 8장에서
# 문서번호·거래일자·공급자·공급가액·부가세·합계 6개 값을 골라내 화면에 보여 줘요.

import re          # 글자 속에서 "규칙(패턴)"에 맞는 부분을 찾아 주는 도구
from pathlib import Path  # 폴더·파일 목록을 다루는 도구

import pdfplumber  # PDF에서 글자를 뽑아 주는 공구


def find_value(text, name):
    """'이름: 값' 줄에서 값만 꺼낸다. 예) '문서번호: INV-2026-101' → 'INV-2026-101'"""
    # ^ 줄 맨 앞 / name / 콜론(:) / 공백 / (.+) 그 뒤의 글자 전부 / $ 줄 끝
    match = re.search(rf"^{name}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def to_number(money):
    """'307,500원' → 307500 (쉼표와 '원'을 지우고 숫자로 바꾼다)"""
    return int(money.replace(",", "").replace("원", ""))


def extract(pdf_path):
    """PDF 한 장에서 6개 값을 뽑아 딕셔너리(이름표 달린 상자)로 돌려준다"""
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()

    return {
        "파일명": pdf_path.name,
        "문서번호": find_value(text, "문서번호"),
        "거래일자": find_value(text, "거래일자"),
        "공급자": find_value(text, "공급자"),
        "공급가액": to_number(find_value(text, "공급가액")),
        "부가세": to_number(find_value(text, "부가세")),
        "합계": to_number(find_value(text, "합계금액")),  # PDF에는 '합계금액'으로 적혀 있음
    }


# invoices 폴더의 PDF를 이름 순서대로 모두 가져온다
pdf_files = sorted(Path("invoices").glob("*.pdf"))

rows = [extract(p) for p in pdf_files]

# 결과를 표처럼 출력
print(f"{'파일명':<18}{'문서번호':<14}{'거래일자':<12}{'공급자':<12}{'공급가액':>10}{'부가세':>9}{'합계':>11}")
print("-" * 90)
for r in rows:
    print(f"{r['파일명']:<18}{r['문서번호']:<14}{r['거래일자']:<12}{r['공급자']:<12}"
          f"{r['공급가액']:>10,}{r['부가세']:>9,}{r['합계']:>11,}")
print("-" * 90)
print(f"✅ 총 {len(rows)}장 추출 완료")
