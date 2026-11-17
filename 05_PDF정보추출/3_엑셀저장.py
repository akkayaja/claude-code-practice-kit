# 3_엑셀저장.py
# 거래명세서 PDF 8장에서 6개 값을 뽑아 `결과/거래명세서_목록.xlsx` 엑셀 파일로 저장해요.
# (값을 뽑는 부분은 2_값추출.py와 똑같고, 맨 아래 '엑셀로 저장' 부분이 새로 생겼어요.)

import re
from pathlib import Path

import pdfplumber
from openpyxl import Workbook                    # 엑셀 파일을 새로 만드는 도구
from openpyxl.styles import Font, PatternFill    # 글꼴(굵게)·칸 색칠 도구


# ── 1. PDF에서 값 뽑기 (2_값추출.py와 같음) ─────────────────────────
def find_value(text, name):
    """'이름: 값' 줄에서 값만 꺼낸다"""
    match = re.search(rf"^{name}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def to_number(money):
    """'307,500원' → 307500"""
    return int(money.replace(",", "").replace("원", ""))


def extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
    return {
        "파일명": pdf_path.name,
        "문서번호": find_value(text, "문서번호"),
        "거래일자": find_value(text, "거래일자"),
        "공급자": find_value(text, "공급자"),
        "공급가액": to_number(find_value(text, "공급가액")),
        "부가세": to_number(find_value(text, "부가세")),
        "합계": to_number(find_value(text, "합계금액")),
    }


pdf_files = sorted(Path("invoices").glob("*.pdf"))
rows = [extract(p) for p in pdf_files]


# ── 2. 엑셀로 저장 (새로 생긴 부분) ─────────────────────────────────
columns = ["파일명", "문서번호", "거래일자", "공급자", "공급가액", "부가세", "합계"]

wb = Workbook()          # 빈 엑셀 파일 하나 만들기
ws = wb.active           # 첫 번째 시트 선택
ws.title = "거래명세서_목록"

# 1행: 제목 줄 (굵은 글씨 + 연한 파란 배경)
ws.append(columns)
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.fill = PatternFill("solid", fgColor="DDEBF7")

# 2행부터: 거래명세서 한 장당 한 줄씩
for r in rows:
    ws.append([r[c] for c in columns])

# 금액 칸(E·F·G열)은 '1,234,567'처럼 쉼표가 보이게
for row in ws.iter_rows(min_row=2, min_col=5, max_col=7):
    for cell in row:
        cell.number_format = "#,##0"

# 열 너비를 보기 좋게
for col, width in zip("ABCDEFG", [18, 15, 12, 16, 13, 11, 13]):
    ws.column_dimensions[col].width = width

# 결과 폴더가 없으면 만들고 저장
out_dir = Path("결과")
out_dir.mkdir(exist_ok=True)
out_path = out_dir / "거래명세서_목록.xlsx"
wb.save(out_path)

print(f"✅ {len(rows)}장 → {out_path} 저장 완료")
print(f"   공급가액 합 {sum(r['공급가액'] for r in rows):,}원 / 합계 합 {sum(r['합계'] for r in rows):,}원")
