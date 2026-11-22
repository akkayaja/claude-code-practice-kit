"""기본 미션 2: 할 일 분류 결과를 '오늘의 브리핑' 텍스트 파일로 저장하기.

- 1_분류.py와 같은 기준 (완료 빼기 / 마감 지남·오늘·이번 주(내일~7일 안)·그 뒤 / 중요도 높은 순)
- '브리핑' 폴더 안에 날짜별로 '오늘의브리핑_2026-11-22.txt' 같은 파일을 만든다
- 같은 날 다시 실행하면 그날 파일을 새 내용으로 덮어쓴다
- 파일 맨 위에 '만든 시각'을 적어서, 자동 실행이 언제 돌았는지 알 수 있게 한다

실행 (14_자동실행봇 폴더에서):
    python3 2_브리핑저장.py              ← 진짜 오늘 날짜로
    python3 2_브리핑저장.py 2026-11-25   ← 다른 날이라고 가정해 보기 (연습용)
"""
import csv
import os
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))   # 어디서 실행해도 이 폴더 기준으로 파일을 찾기
TODO_FILE = os.path.join(HERE, "data", "할일목록.csv")
OUT_DIR = os.path.join(HERE, "브리핑")
RANK = {"높음": 0, "보통": 1, "낮음": 2}
WEEKDAY = "월화수목금토일"

# 1) 기준 날짜 정하기
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
week_end = today + timedelta(days=7)

# 2) 할 일 읽고 바구니에 나누기 (1_분류.py와 같은 방법)
with open(TODO_FILE, encoding="utf-8-sig", newline="") as f:
    todos = list(csv.DictReader(f))

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

# 3) 브리핑 글 만들기 (줄 하나하나를 lines 목록에 모은다)
lines = [
    f"📋 오늘의 브리핑 — {today} ({WEEKDAY[today.weekday()]})",
    f"만든 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "=" * 40,
    "",
]
for name, items in groups.items():
    if name == "⚪ 그 뒤":          # 브리핑에는 급한 것만 자세히, '그 뒤'는 개수만
        continue
    items.sort(key=lambda t: (RANK[t["중요도"]], t["마감일"]))
    lines.append(f"{name}: {len(items)}개")
    for t in items:
        days = (date.fromisoformat(t["마감일"]) - today).days
        when = f"{-days}일 지남" if days < 0 else ("오늘" if days == 0 else f"D-{days}")
        lines.append(f"  - [{t['중요도']}] {t['할일']} ({when}, {t['상태']})")
    lines.append("")
lines.append(f"⚪ 그 뒤: {len(groups['⚪ 그 뒤'])}개 / ✅ 완료: {done}개")

# 4) 파일로 저장하기
os.makedirs(OUT_DIR, exist_ok=True)          # '브리핑' 폴더가 없으면 만들기
out_path = os.path.join(OUT_DIR, f"오늘의브리핑_{today}.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"✅ 저장했어요: 브리핑/{os.path.basename(out_path)}")
print(f"   마감 지남 {len(groups['🔴 마감 지남'])} / 오늘 {len(groups['🟠 오늘 마감'])} / "
      f"이번 주 {len(groups['🟡 이번 주 (내일~7일 안)'])} / 그 뒤 {len(groups['⚪ 그 뒤'])} / 완료 {done}")
