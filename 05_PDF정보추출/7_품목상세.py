# 7_품목상세.py
# 거래명세서 PDF 8장에서 품목 한 줄 한 줄(품목·수량·단가·금액)을 뽑아
# 결과/거래명세서_목록.xlsx 에 '품목_상세' 시트로 추가해요.
# 덤으로 두 가지를 검사해요.
#   검사 ①  수량 × 단가 = 금액 인가?  (품목 줄마다)
#   검사 ②  품목 금액을 다 더하면 = 공급가액 인가?  (명세서마다)

import re
from pathlib import Path

import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

# 품목 줄 모양: "A4 복사용지 12 28,000 336,000"
#   (.+?)        품목 이름 (띄어쓰기가 있어도 OK — 뒤에서부터 숫자 3개를 먼저 찾으니까)
#   ([\d,]+) ×3  수량 / 단가 / 금액 (숫자와 쉼표로만 된 덩어리)
ITEM_LINE = re.compile(r"^(.+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)$")


def to_number(s):
    return int(s.replace(",", "").replace("원", ""))


items = []          # 모든 품목 줄을 모을 목록
problems = 0

for pdf_path in sorted(Path("invoices").glob("*.pdf")):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()

    doc_no = re.search(r"^문서번호:\s*(.+)$", text, re.MULTILINE).group(1)
    supplier = re.search(r"^공급자:\s*(.+)$", text, re.MULTILINE).group(1)
    supply = to_number(re.search(r"^공급가액:\s*(.+)$", text, re.MULTILINE).group(1))

    # '품목 수량 단가 금액' 제목 줄과 '공급가액:' 줄 사이만 잘라낸다 = 품목 표 부분
    table_part = text.split("품목 수량 단가 금액")[1].split("공급가액:")[0]

    item_sum = 0
    for line in table_part.strip().splitlines():
        m = ITEM_LINE.match(line.strip())
        if not m:
            print(f"⚠️ {doc_no}: 품목 줄로 못 읽음 → '{line}'")
            problems += 1
            continue
        name = m.group(1)
        qty, price, amount = (to_number(m.group(i)) for i in (2, 3, 4))

        if qty * price != amount:                                     # 검사 ①
            print(f"❌ {doc_no} {name}: {qty} × {price:,} = {qty * price:,} ≠ {amount:,}")
            problems += 1

        items.append([doc_no, supplier, name, qty, price, amount])
        item_sum += amount

    mark = "✅" if item_sum == supply else "❌"                        # 검사 ②
    if item_sum != supply:
        problems += 1
    print(f"{doc_no}  {supplier:<10} 품목 {sum(1 for i in items if i[0] == doc_no)}개"
          f"  품목 합 {item_sum:>10,} / 공급가액 {supply:>10,} {mark}")

print("-" * 70)
print(f"총 품목 줄: {len(items)}개 / 문제: {problems}건")

# ── 엑셀에 '품목_상세' 시트 추가 ──────────────────────────
xlsx_path = "결과/거래명세서_목록.xlsx"
wb = load_workbook(xlsx_path)
if "품목_상세" in wb.sheetnames:          # 다시 실행해도 시트가 두 개 생기지 않도록
    del wb["품목_상세"]
ws = wb.create_sheet("품목_상세")

ws.append(["문서번호", "공급자", "품목", "수량", "단가", "금액"])
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.fill = PatternFill("solid", fgColor="DDEBF7")
for row in items:
    ws.append(row)

for row in ws.iter_rows(min_row=2, min_col=4, max_col=6):
    for cell in row:
        cell.number_format = "#,##0"
for col, width in zip("ABCDEF", [15, 16, 16, 7, 10, 12]):
    ws.column_dimensions[col].width = width

wb.save(xlsx_path)
print(f"✅ {xlsx_path} 에 '품목_상세' 시트 추가 완료")
