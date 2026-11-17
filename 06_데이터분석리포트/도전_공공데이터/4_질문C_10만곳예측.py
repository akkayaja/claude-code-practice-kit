# 도전 질문 C: 이 속도라면 전국 카페는 언제 10만 곳을 넘을까?
# 실행 위치: 06_데이터분석리포트 폴더 (.venv/bin/python 도전_공공데이터/4_질문C_10만곳예측.py)
import os
import numpy as np
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

# 1) 질문 B에서 '안정적'이라고 확인한 2019년 데이터만 사용
최근 = df[df["기준월"].dt.year == 2019].reset_index(drop=True)
최근["몇번째달"] = range(len(최근))          # 2019년 1월 = 0, 2월 = 1, ... 9월 = 8

# 2) 추세선(직선) 긋기: 업소수 = 기울기 × 몇번째달 + 시작값
#    np.polyfit은 점들 사이를 가장 잘 지나가는 직선을 찾아 줘요
기울기, 시작값 = np.polyfit(최근["몇번째달"], 최근["업소수"], 1)

# 3) 직선을 앞으로 늘려서 10만 곳을 처음 넘는 달 찾기
목표 = 100_000
n = 0
while 기울기 * n + 시작값 < 목표:
    n += 1
도달월 = pd.Timestamp("2019-01-01") + pd.DateOffset(months=n)
도달값 = 기울기 * n + 시작값
남은곳 = 목표 - 최근["업소수"].iloc[-1]

print("=" * 55)
print("📋 질문 C. 이 속도라면 언제 10만 곳을 넘을까?")
print("=" * 55)
print(f"  사용한 데이터: 2019년 1월 ~ 9월 ({len(최근)}개월)")
print(f"  추세선 기울기: 한 달에 약 {기울기:,.0f}곳씩 증가")
print(f"  마지막 기록: 2019년 9월 {최근['업소수'].iloc[-1]:,}곳 → 10만 곳까지 {남은곳:,}곳 남음")
print(f"\n🔮 예측: {도달월:%Y년 %m월}에 10만 곳 돌파 (그달 예상 {도달값:,.0f}곳)")
print("   ※ '2019년의 증가 속도가 그대로 이어진다면'이라는 가정이 붙은 예측이에요.")

pd.DataFrame([{
    "사용 기간": "2019-01 ~ 2019-09",
    "한 달 증가(곳)": round(기울기),
    "2019-09 업소수": 최근["업소수"].iloc[-1],
    "10만 곳 도달 예상": f"{도달월:%Y-%m}",
    "그달 예상 업소수": round(도달값),
}]).to_csv(f"{결과폴더}/질문C_10만곳예측_표.csv", index=False, encoding="utf-8-sig")

# 4) 그래프: 실제 점 + 추세선(점선으로 미래까지) + 10만 곳 기준선
미래n = np.arange(0, n + 4)
미래월 = [pd.Timestamp("2019-01-01") + pd.DateOffset(months=int(i)) for i in 미래n]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(최근["기준월"], 최근["업소수"], "o", color="#5b8def", markersize=8, label="실제 기록 (2019년)")
ax.plot(미래월, 기울기 * 미래n + 시작값, "--", color="#f0ad4e", label=f"추세선 (한 달 +{기울기:,.0f}곳)")
ax.axhline(목표, color="#d9534f", linewidth=1)
ax.text(미래월[-3], 목표 - 200, "10만 곳 기준선", color="#d9534f")
ax.plot(도달월, 도달값, "*", color="#d9534f", markersize=18, label=f"예상 돌파: {도달월:%Y년 %m월}")
ax.axvspan(pd.Timestamp("2019-09-15"), 미래월[-1], color="#f5f5f5", zorder=0)
ax.text(pd.Timestamp("2019-10-01"), 최근["업소수"].min(), "← 실제 기록 | 예측 →", color="#888")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_ylabel("카페 수 (곳)")
ax.set_title("질문 C. 이 속도라면 언제 10만 곳을 넘을까? (2019년 추세로 예측)")
ax.legend(loc="upper left")
plt.tight_layout()
plt.savefig(f"{결과폴더}/질문C_10만곳예측.png", dpi=150)

print(f"\n✅ 저장 완료: {결과폴더}/질문C_10만곳예측_표.csv, {결과폴더}/질문C_10만곳예측.png")
