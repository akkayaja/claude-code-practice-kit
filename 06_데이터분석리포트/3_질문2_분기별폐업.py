# 미션 3-2: 질문 2 "폐업이 가장 몰리는 분기는 언제인가?" — 표와 그래프 만들기
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

os.makedirs("결과", exist_ok=True)

df = pd.read_csv("data/지역별_카페_현황.csv", encoding="utf-8-sig")

# 1) 분기별 폐업 합계 (17개 지역 × 6년을 모두 더함)
분기합계 = df.groupby("분기")["폐업"].sum()
전체 = 분기합계.sum()

print("=" * 45)
print("📋 질문 2. 폐업이 가장 몰리는 분기는 언제인가?")
print("=" * 45)
print("\n[표 1] 분기별 폐업 합계 (2020~2025, 전국)")
for 분기, 값 in 분기합계.items():
    print(f"  {분기}: {값:>8,}곳  (전체의 {값 / 전체 * 100:.1f}%)")
print(f"  → 가장 많은 분기: {분기합계.idxmax()} / 가장 적은 분기: {분기합계.idxmin()}")
print(f"  → 1등과 꼴찌 차이: {분기합계.max() - 분기합계.min():,}곳")

# 2) 해마다 어느 분기가 1등인지 (같은 분기가 매년 1등인가?)
연도별 = df.pivot_table(index="연도", columns="분기", values="폐업", aggfunc="sum")
연도별["1등 분기"] = 연도별.idxmax(axis=1)
print("\n[표 2] 연도별·분기별 폐업 합계")
print(연도별.to_string())
print("\n  1등 분기 횟수:", 연도별["1등 분기"].value_counts().to_dict())

# 3) 표 저장
연도별.to_csv("결과/질문2_분기별폐업_표.csv", encoding="utf-8-sig")

# 4) 그래프 2개를 나란히 그리기
fig, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(12, 5))

# 왼쪽: 분기별 합계 막대 (세로축을 0부터 시작해 '진짜 차이'를 보여 줌)
왼쪽.bar(분기합계.index, 분기합계.values, color="#5b8def")
for x, 값 in enumerate(분기합계.values):
    왼쪽.text(x, 값 + 2000, f"{값:,}", ha="center", fontsize=9)
왼쪽.set_ylim(0, 분기합계.max() * 1.15)
왼쪽.set_title("분기별 폐업 합계 (2020~2025)")
왼쪽.set_ylabel("폐업 수 (곳)")

# 오른쪽: 연도마다 분기별 폐업 꺾은선 (해마다 1등 분기가 같은지 보기)
for 분기 in ["1분기", "2분기", "3분기", "4분기"]:
    오른쪽.plot(연도별.index, 연도별[분기], marker="o", label=분기)
오른쪽.set_title("연도별로 본 분기별 폐업")
오른쪽.set_xlabel("연도")
오른쪽.set_ylabel("폐업 수 (곳)")
오른쪽.legend()

fig.suptitle("질문 2. 폐업이 가장 몰리는 분기는?", fontsize=14)
plt.tight_layout()
plt.savefig("결과/질문2_분기별폐업.png", dpi=150)

print("\n✅ 저장 완료: 결과/질문2_분기별폐업_표.csv, 결과/질문2_분기별폐업.png")
