# 6_공급자별집계.py
# 결과/거래명세서_목록.xlsx 를 읽어서 공급자별로 건수·공급가액·부가세·합계를 모아 더하고,
# 같은 엑셀 파일에 '공급자별_집계' 시트를 새로 추가해요.

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

xlsx_path = "결과/거래명세서_목록.xlsx"
wb = load_workbook(xlsx_path)
ws = wb["거래명세서_목록"]

# ── 1. 공급자별로 모아 더하기 ─────────────────────────────
# summary = { "새롬오피스": {"건수": 2, "공급가액": ..., ...}, ... }
summary = {}
for 파일명, 문서번호, 거래일자, 공급자, 공급가액, 부가세, 합계 in ws.iter_rows(min_row=2, values_only=True):
    if 공급자 not in summary:   # 처음 보는 공급자면 0으로 시작하는 칸을 만든다
        summary[공급자] = {"건수": 0, "공급가액": 0, "부가세": 0, "합계": 0}
    summary[공급자]["건수"] += 1
    summary[공급자]["공급가액"] += 공급가액
    summary[공급자]["부가세"] += 부가세
    summary[공급자]["합계"] += 합계

# 합계가 큰 공급자부터 줄 세우기
ranked = sorted(summary.items(), key=lambda item: item[1]["합계"], reverse=True)

# ── 2. 화면에 출력 ────────────────────────────────────────
print(f"{'공급자':<12}{'건수':>4}{'공급가액':>13}{'부가세':>11}{'합계':>13}")
print("-" * 58)
for name, s in ranked:
    print(f"{name:<12}{s['건수']:>4}{s['공급가액']:>13,}{s['부가세']:>11,}{s['합계']:>13,}")
print("-" * 58)
total = {k: sum(s[k] for s in summary.values()) for k in ["건수", "공급가액", "부가세", "합계"]}
print(f"{'전체':<12}{total['건수']:>4}{total['공급가액']:>13,}{total['부가세']:>11,}{total['합계']:>13,}")

# ── 3. 엑셀에 새 시트로 저장 ──────────────────────────────
if "공급자별_집계" in wb.sheetnames:      # 다시 실행해도 시트가 두 개 생기지 않도록
    del wb["공급자별_집계"]
ws2 = wb.create_sheet("공급자별_집계")

ws2.append(["공급자", "건수", "공급가액", "부가세", "합계"])
for cell in ws2[1]:
    cell.font = Font(bold=True)
    cell.fill = PatternFill("solid", fgColor="DDEBF7")
for name, s in ranked:
    ws2.append([name, s["건수"], s["공급가액"], s["부가세"], s["합계"]])
ws2.append(["전체", total["건수"], total["공급가액"], total["부가세"], total["합계"]])
for cell in ws2[ws2.max_row]:             # 마지막 '전체' 줄은 굵게
    cell.font = Font(bold=True)

for row in ws2.iter_rows(min_row=2, min_col=3, max_col=5):
    for cell in row:
        cell.number_format = "#,##0"
for col, width in zip("ABCDE", [16, 8, 13, 11, 13]):
    ws2.column_dimensions[col].width = width

wb.save(xlsx_path)
print(f"\n✅ {xlsx_path} 에 '공급자별_집계' 시트 추가 완료")
