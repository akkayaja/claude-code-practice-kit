"""기본 미션 1: 할 일 목록을 '오늘' 기준으로 나눠서 화면에 보여 주기.

- 이미 '완료'된 일은 빼고 센다
- 마감 지남 / 오늘 마감 / 이번 주(내일~7일 안) / 그 뒤 로 나눈다
- 각 묶음 안에서는 중요도 높은 순 → 마감 빠른 순으로 줄 세운다

실행 (14_자동실행봇 폴더에서):
    python3 1_분류.py              ← 진짜 오늘 날짜로
    python3 1_분류.py 2026-11-25   ← 다른 날이라고 가정해 보기 (연습용)
"""
import csv
import os
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
TODO_FILE = os.path.join(HERE, "data", "할일목록.csv")
RANK = {"높음": 0, "보통": 1, "낮음": 2}   # 중요도 순서 (작을수록 먼저)

# 1) 기준 날짜 정하기: 뒤에 날짜를 적으면 그 날, 아니면 진짜 오늘
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
week_end = today + timedelta(days=7)

# 2) 할 일 목록 읽기
with open(TODO_FILE, encoding="utf-8-sig", newline="") as f:
    todos = list(csv.DictReader(f))

# 3) 바구니 4개에 나눠 담기 (완료된 일은 따로 세기만)
groups = {"🔴 마감 지남": [], "🟠 오늘 마감": [], "🟡 이번 주 (내일~7일 안)": [], "⚪ 그 뒤": []}
done = 0
for t in todos:
    if t["상태"] == "완료":
        done += 1
        continue
    due = date.fromisoformat(t["마감일"])
    if due < today:
        groups["🔴 마감 지남"].append(t)
    elif due == today:
        groups["🟠 오늘 마감"].append(t)
    elif due <= week_end:
        groups["🟡 이번 주 (내일~7일 안)"].append(t)
    else:
        groups["⚪ 그 뒤"].append(t)

# 4) 화면에 보여 주기
print(f"기준 날짜: {today}  (이번 주 = {today + timedelta(days=1)} ~ {week_end})")
print(f"전체 {len(todos)}개 중 완료 {done}개는 빼고 셌어요\n")
for name, items in groups.items():
    items.sort(key=lambda t: (RANK[t["중요도"]], t["마감일"]))
    print(f"{name}: {len(items)}개")
    for t in items:
        print(f"   [{t['중요도']}] {t['할일']} (마감 {t['마감일']}, {t['상태']})")
