# 4_정답비교.py
# 내가 만든 엑셀(결과/거래명세서_목록.xlsx)과 정답(정답_추출결과.csv)을
# 한 칸씩 비교해서, 틀린 칸이 있으면 어디가 틀렸는지 알려 줘요.

import csv
from openpyxl import load_workbook   # 이미 있는 엑셀 파일을 읽는 도구

# ── 1. 내 결과(엑셀) 읽기 ──────────────────────────────
ws = load_workbook("결과/거래명세서_목록.xlsx").active
my_rows = list(ws.iter_rows(values_only=True))   # 각 줄을 (값, 값, ...) 묶음으로
my_header, my_data = my_rows[0], my_rows[1:]      # 첫 줄은 제목, 나머지는 데이터

# ── 2. 정답(CSV) 읽기 ─────────────────────────────────
# utf-8-sig: 엑셀용 CSV 맨 앞에 숨어 있는 표시(BOM)를 알아서 지워 주는 읽기 방식
with open("정답_추출결과.csv", encoding="utf-8-sig") as f:
    answer_rows = list(csv.reader(f))
answer_header, answer_data = answer_rows[0], answer_rows[1:]

# ── 3. 비교 ───────────────────────────────────────────
print(f"내 결과 {len(my_data)}줄 / 정답 {len(answer_data)}줄")
if list(my_header) != answer_header:
    print(f"⚠️ 제목 줄이 달라요\n  내 것: {list(my_header)}\n  정답 : {answer_header}")

wrong = 0
total = 0
for my_row, ans_row in zip(my_data, answer_data):
    for col_name, mine, ans in zip(answer_header, my_row, ans_row):
        total += 1
        # CSV는 전부 글자로 읽히니까, 내 값도 글자로 바꿔서 비교
        if str(mine) != ans:
            wrong += 1
            print(f"❌ {ans_row[0]} / {col_name}: 내 값 '{mine}' ↔ 정답 '{ans}'")

print("-" * 40)
print(f"비교한 칸: {total}칸 / 틀린 칸: {wrong}칸")
if wrong == 0 and len(my_data) == len(answer_data):
    print("🎉 정답과 100% 일치!")
