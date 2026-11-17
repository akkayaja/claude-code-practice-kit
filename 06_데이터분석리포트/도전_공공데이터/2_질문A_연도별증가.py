# 도전 질문 A: 해마다 카페는 얼마나 늘었고, 가장 많이 늘어난 해는 언제일까?
# 실행 위치: 06_데이터분석리포트 폴더 (.venv/bin/python 도전_공공데이터/2_질문A_연도별증가.py)
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

# 1) 매년 12월 기록만 골라서 비교 (같은 달끼리 비교해야 공평해요)
십이월 = df[df["기준월"].dt.month == 12].copy()
십이월["연도"] = 십이월["기준월"].dt.year
십이월["전년 대비 증가(곳)"] = 십이월["업소수"].diff()
십이월["증가율(%)"] = (십이월["업소수"].pct_change() * 100).round(1)
표 = 십이월[["연도", "업소수", "전년 대비 증가(곳)", "증가율(%)"]]

print("=" * 50)
print("📋 질문 A. 해마다 카페는 얼마나 늘었나? (매년 12월 기준)")
print("=" * 50)
for _, 줄 in 표.iterrows():
    if pd.isna(줄["전년 대비 증가(곳)"]):
        print(f"  {int(줄['연도'])}년 12월: {int(줄['업소수']):>7,}곳  (출발점)")
    else:
        print(f"  {int(줄['연도'])}년 12월: {int(줄['업소수']):>7,}곳  "
              f"{줄['전년 대비 증가(곳)']:+,.0f}곳 ({줄['증가율(%)']:+.1f}%)")

최고 = 표.loc[표["전년 대비 증가(곳)"].idxmax()]
print(f"\n🥇 가장 많이 늘어난 해: {int(최고['연도'])}년 "
      f"({최고['전년 대비 증가(곳)']:+,.0f}곳, {최고['증가율(%)']:+.1f}%)")
print(f"   2015년 12월 → 2018년 12월, 3년 동안: "
      f"{표['업소수'].iloc[-1] - 표['업소수'].iloc[0]:+,}곳 "
      f"({(표['업소수'].iloc[-1] / 표['업소수'].iloc[0] - 1) * 100:+.1f}%)")

표.to_csv(f"{결과폴더}/질문A_연도별증가_표.csv", index=False, encoding="utf-8-sig")

# 2) 그래프 2개
fig, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(12, 5))

# 왼쪽: 전체 월별 흐름 (빠진 달은 선이 끊기게) + 12월 점 강조
매달 = df.set_index("기준월").reindex(
    pd.date_range(df["기준월"].min(), df["기준월"].max(), freq="MS"))
왼쪽.plot(매달.index, 매달["업소수"], color="#9aa5b1", marker=".", label="월별 기록 (빈 곳 = 빠진 달)")
왼쪽.scatter(십이월["기준월"], 십이월["업소수"], color="#d9534f", s=60, zorder=3, label="매년 12월")
왼쪽.set_xticks(pd.to_datetime(["2016-01-01", "2017-01-01", "2018-01-01", "2019-01-01"]))
왼쪽.set_xticklabels(["2016년", "2017년", "2018년", "2019년"])  # 날짜 글자 겹침 방지
왼쪽.set_title("전국 카페 수 월별 흐름")
왼쪽.set_ylabel("카페 수 (곳)")
왼쪽.legend(fontsize=9)

# 오른쪽: 해마다 늘어난 카페 수 막대
증가표 = 표.dropna()
색 = ["#d9534f" if 연 == 최고["연도"] else "#5b8def" for 연 in 증가표["연도"]]
막대 = 오른쪽.bar(증가표["연도"].astype(str) + "년", 증가표["전년 대비 증가(곳)"], color=색)
for 막, 수, 율 in zip(막대, 증가표["전년 대비 증가(곳)"], 증가표["증가율(%)"]):
    오른쪽.text(막.get_x() + 막.get_width() / 2, 수 + 300, f"+{수:,.0f}곳\n(+{율}%)", ha="center", fontsize=9)
오른쪽.set_ylim(0, 증가표["전년 대비 증가(곳)"].max() * 1.25)
오른쪽.set_title("해마다 늘어난 카페 수 (전년 12월 → 올해 12월)")
오른쪽.set_ylabel("늘어난 카페 수 (곳)")

fig.suptitle("질문 A. 해마다 카페는 얼마나 늘었나? (소상공인시장진흥공단 실제 데이터)", fontsize=14)
plt.tight_layout()
plt.savefig(f"{결과폴더}/질문A_연도별증가.png", dpi=150)

print(f"\n✅ 저장 완료: {결과폴더}/질문A_연도별증가_표.csv, {결과폴더}/질문A_연도별증가.png")
