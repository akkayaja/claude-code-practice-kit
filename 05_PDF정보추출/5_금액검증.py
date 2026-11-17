# 5_금액검증.py
# 결과/거래명세서_목록.xlsx 를 읽어서, 거래명세서마다 금액 계산이 맞는지 검사해요.
#   검사 ①  공급가액 + 부가세 = 합계 인가?
#   검사 ②  부가세 = 공급가액의 10% 인가?

from openpyxl import load_workbook

ws = load_workbook("결과/거래명세서_목록.xlsx").active
rows = list(ws.iter_rows(min_row=2, values_only=True))   # 2행부터 = 데이터만

problems = 0
for 파일명, 문서번호, 거래일자, 공급자, 공급가액, 부가세, 합계 in rows:
    check1 = 공급가액 + 부가세 == 합계          # 검사 ①
    check2 = 부가세 == round(공급가액 * 0.1)    # 검사 ② (round: 반올림)

    mark1 = "✅" if check1 else "❌"
    mark2 = "✅" if check2 else "❌"
    print(f"{문서번호}  {공급가액:>10,} + {부가세:>8,} = {공급가액 + 부가세:>10,}"
          f" (합계 {합계:>10,}) {mark1}  | 부가세 10% {mark2}")

    if not (check1 and check2):
        problems += 1

print("-" * 75)
if problems == 0:
    print(f"🎉 {len(rows)}장 모두 금액 계산이 맞아요")
else:
    print(f"⚠️ {len(rows)}장 중 {problems}장에서 금액이 안 맞아요. 원본 PDF를 확인하세요")
