# 도전 질문 B: 최근(2019년) 숫자는 믿을 만할까?
# 실행 위치: 06_데이터분석리포트 폴더 (.venv/bin/python 도전_공공데이터/3_질문B_2019안정성.py)
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

결과폴더 = "도전_공공데이터/결과"
os.makedirs(결과폴더, exist_ok=True)

df = pd.read_csv("도전_공공데이터/전국_카페_점포수.csv", encoding="cp949")
df["기준월"] = pd.to_datetime(df["기준월"])

# 1) 전 달 대비 변화율(%) 계산 — 바로 앞 달 기록이 있는 경우만 (빠진 달 건너뛰기)
df["전달대비(곳)"] = df["업소수"].diff()
df["변화율(%)"] = df["업소수"].pct_change() * 100
df["연속"] = df["기준월"].diff().dt.days.between(28, 31)
월변화 = df[df["연속"]].copy()
월변화["기간"] = 월변화["기준월"].dt.year.map(lambda y: "2019년" if y == 2019 else "2017~2018년")

# 2) 기간별로 '얼마나 들쭉날쭉한가' 비교
print("=" * 55)
print("📋 질문 B. 최근(2019년) 숫자는 믿을 만할까?")
print("=" * 55)
요약 = []
for 기간 in ["2017~2018년", "2019년"]:
    s = 월변화[월변화["기간"] == 기간]
    줄 = {
        "기간": 기간,
        "비교한 달 수": len(s),
        "줄어든 달 수": int((s["전달대비(곳)"] < 0).sum()),
        "가장 크게 오른 폭(%)": round(s["변화율(%)"].max(), 1),
        "가장 크게 내린 폭(%)": round(s["변화율(%)"].min(), 1),
        "평균 변화(곳/월)": round(s["전달대비(곳)"].mean()),
        "들쭉날쭉 지수(표준편차)": round(s["변화율(%)"].std(), 2),
    }
    요약.append(줄)
    print(f"\n[{기간}] 전 달과 비교한 달: {줄['비교한 달 수']}개")
    print(f"  줄어든 달: {줄['줄어든 달 수']}번")
    print(f"  한 달 변화 범위: {줄['가장 크게 내린 폭(%)']:+.1f}% ~ {줄['가장 크게 오른 폭(%)']:+.1f}%")
    print(f"  한 달 평균: {줄['평균 변화(곳/월)']:+,}곳")
    print(f"  들쭉날쭉 지수: {줄['들쭉날쭉 지수(표준편차)']}")

배수 = 요약[0]["들쭉날쭉 지수(표준편차)"] / 요약[1]["들쭉날쭉 지수(표준편차)"]
print(f"\n→ 2017~2018년이 2019년보다 약 {배수:.0f}배 더 들쭉날쭉해요.")

pd.DataFrame(요약).to_csv(f"{결과폴더}/질문B_2019안정성_표.csv", index=False, encoding="utf-8-sig")

# 3) 그래프: 달마다 전 달 대비 변화율 막대 (회색 = 2017~2018년, 파랑 = 2019년)
fig, ax = plt.subplots(figsize=(12, 5))
색 = ["#5b8def" if 기 == "2019년" else ("#d9534f" if 율 < 0 else "#9aa5b1")
      for 기, 율 in zip(월변화["기간"], 월변화["변화율(%)"])]
ax.bar(월변화["기준월"].dt.strftime("%y.%m"), 월변화["변화율(%)"], color=색)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylabel("전 달 대비 변화율 (%)")
ax.set_title("질문 B. 달마다 카페 수가 얼마나 변했나? (회색·빨강 = 2017~2018년, 파랑 = 2019년)")
ax.tick_params(axis="x", rotation=60, labelsize=8)
ax.text(len(월변화) - 9, 3, "2019년:\n거의 일정하게\n조금씩 증가", fontsize=10, color="#2a5bd7")
plt.tight_layout()
plt.savefig(f"{결과폴더}/질문B_2019안정성.png", dpi=150)

print(f"\n✅ 저장 완료: {결과폴더}/질문B_2019안정성_표.csv, {결과폴더}/질문B_2019안정성.png")
