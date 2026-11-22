"""도전 미션: 13번 날씨 기록 + 14번 할 일 브리핑을 한 번에 돌리는 '지휘자' 스크립트.

순서
  1) 13번 '4_날씨기록.py'를 실행 → 13_API연결/날씨기록.csv 에 오늘 날씨가 쌓인다
  2) 14번 '2_브리핑저장.py'를 실행 → 브리핑/오늘의브리핑_날짜.txt 가 만들어진다
  3) 날씨기록.csv 에서 '가장 최근 관측 시각'의 7개 도시 날씨를 골라
     브리핑 파일 맨 위(제목 아래)에 끼워 넣는다
  4) 이 폴더에 .env 금고가 있으면 '4_메일보내기.py'로 완성된 브리핑을 내 지메일로 보낸다

- 날씨 받기가 실패해도(인터넷 끊김 등) 할 일 브리핑은 그대로 만든다
- 자동 실행(launchd)에서도 쓸 수 있게, 모든 파일 위치를 이 파일 기준으로 찾는다

실행 (14_자동실행봇 폴더에서): python3 3_날씨브리핑.py
"""
import csv
import os
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)                                   # 실습키트 폴더
WEATHER_SCRIPT = os.path.join(KIT, "13_API연결", "4_날씨기록.py")
WEATHER_FILE = os.path.join(KIT, "13_API연결", "날씨기록.csv")
BRIEFING_SCRIPT = os.path.join(HERE, "2_브리핑저장.py")
MAIL_SCRIPT = os.path.join(HERE, "4_메일보내기.py")
BRIEFING_FILE = os.path.join(HERE, "브리핑", f"오늘의브리핑_{date.today()}.txt")


def run(script):
    """다른 파이썬 스크립트를 실행하고, 그 스크립트가 화면에 쓴 글을 돌려준다."""
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


# 1) 날씨 기록 (13번 스크립트에게 일 시키기)
code, out = run(WEATHER_SCRIPT)
print("☁️  [1/4] 날씨 기록:", "성공" if code == 0 else "실패")
print("   " + out.replace("\n", "\n   "))

# 2) 할 일 브리핑 (14번 2_브리핑저장.py에게 일 시키기)
code, out = run(BRIEFING_SCRIPT)
print("📋 [2/4] 할 일 브리핑:", "성공" if code == 0 else "실패")
print("   " + out.replace("\n", "\n   "))
if code != 0:
    raise SystemExit(1)

# 3) 날씨기록.csv에서 가장 최근 관측 시각의 줄만 고르기
weather_lines = ["🌤️ 오늘 아침 날씨"]
if os.path.exists(WEATHER_FILE):
    with open(WEATHER_FILE, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if rows:
        latest = max(r["관측일시"] for r in rows)
        weather_lines[0] += f" (기상청 실황, {latest} 관측)"
        for r in rows:
            if r["관측일시"] == latest:
                weather_lines.append(f"  - {r['도시']}: {r['기온']}℃, 습도 {r['습도']}%, 강수 {r['강수']}")
cities = len(weather_lines) - 1                               # 날씨가 들어간 도시 수
if cities == 0:
    weather_lines.append("  - (날씨 기록이 아직 없어요)")

# 4) 브리핑 파일 제목 아래(3번째 줄 '=====' 다음)에 날씨 끼워 넣기
with open(BRIEFING_FILE, encoding="utf-8") as f:
    lines = f.read().splitlines()
lines = lines[:3] + [""] + weather_lines + lines[3:]
with open(BRIEFING_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"🌤️ [3/4] 날씨 {cities}개 도시를 브리핑 맨 위에 넣었어요: 브리핑/{os.path.basename(BRIEFING_FILE)}")

# 5) 메일 보내기 (금고 .env가 있을 때만 — 없으면 건너뛰기)
if os.path.exists(os.path.join(HERE, ".env")):
    code, out = run(MAIL_SCRIPT)
    print("📧 [4/4] 메일:", "성공" if code == 0 else "실패")
    print("   " + out.replace("\n", "\n   "))
else:
    print("📧 [4/4] 메일: .env 금고가 없어서 건너뛰었어요")
