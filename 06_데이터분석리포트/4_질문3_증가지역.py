# 미션 3-3: 질문 3 "카페가 가장 많이 늘어난 지역은?" — 표와 그래프 만들기
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

os.makedirs("결과", exist_ok=True)

df = pd.read_csv("data/지역별_카페_현황.csv", encoding="utf-8-sig")

# 1) 시작(2020년 1분기)과 끝(2025년 4분기)의 점포수 꺼내기
시작 = df[(df["연도"] == 2020) & (df["분기"] == "1분기")].set_index("시도")["영업중_점포수"]
끝 = df[(df["연도"] == 2025) & (df["분기"] == "4분기")].set_index("시도")["영업중_점포수"]

# 2) 두 가지 기준으로 '얼마나 늘었나' 계산
표 = pd.DataFrame({"2020년 1분기": 시작, "2025년 4분기": 끝})
표["증가 수(곳)"] = 표["2025년 4분기"] - 표["2020년 1분기"]
표["증가율(%)"] = (표["증가 수(곳)"] / 표["2020년 1분기"] * 100).round(1)
표 = 표.sort_values("증가 수(곳)", ascending=False)

print("=" * 55)
print("📋 질문 3. 카페가 가장 많이 늘어난 지역은?")
print("=" * 55)
print(표.to_string())

수_1등 = 표["증가 수(곳)"].idxmax()
율_1등 = 표["증가율(%)"].idxmax()
print(f"\n🥇 증가 수 기준 1등: {수_1등} (+{표.loc[수_1등, '증가 수(곳)']:,}곳)")
print(f"🥇 증가율 기준 1등: {율_1등} (+{표.loc[율_1등, '증가율(%)']}%)")
print(f"   ({율_1등}은 증가 수로는 {표.index.get_loc(율_1등) + 1}등)")

전국시작, 전국끝 = 시작.sum(), 끝.sum()
print(f"\n전국: {전국시작:,}곳 → {전국끝:,}곳 (+{전국끝 - 전국시작:,}곳, +{(전국끝 - 전국시작) / 전국시작 * 100:.1f}%)")

# 3) 표 저장
표.to_csv("결과/질문3_증가지역_표.csv", encoding="utf-8-sig")

# 4) 같은 질문, 다른 기준 → 그래프 2개 나란히
fig, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(12, 6))

수정렬 = 표.sort_values("증가 수(곳)")
왼쪽.barh(수정렬.index, 수정렬["증가 수(곳)"],
          color=["#d9534f" if s == 수_1등 else ("#f0ad4e" if s == 율_1등 else "#9aa5b1") for s in 수정렬.index])
for y, 값 in enumerate(수정렬["증가 수(곳)"]):
    왼쪽.text(값 + 100, y, f"+{값:,}", va="center", fontsize=8)
왼쪽.set_xlim(0, 수정렬["증가 수(곳)"].max() * 1.18)
왼쪽.set_title("기준 ① 증가 수 (몇 곳 늘었나)")
왼쪽.set_xlabel("늘어난 카페 수 (곳)")

율정렬 = 표.sort_values("증가율(%)")
오른쪽.barh(율정렬.index, 율정렬["증가율(%)"],
            color=["#d9534f" if s == 수_1등 else ("#f0ad4e" if s == 율_1등 else "#9aa5b1") for s in 율정렬.index])
for y, 값 in enumerate(율정렬["증가율(%)"]):
    오른쪽.text(값 + 1, y, f"+{값}%", va="center", fontsize=8)
오른쪽.set_xlim(0, 율정렬["증가율(%)"].max() * 1.18)
오른쪽.set_title("기준 ② 증가율 (처음보다 몇 % 늘었나)")
오른쪽.set_xlabel("증가율 (%)")

fig.suptitle("질문 3. 카페가 가장 많이 늘어난 지역은? (2020년 1분기 → 2025년 4분기)", fontsize=14)
plt.tight_layout()
plt.savefig("결과/질문3_증가지역.png", dpi=150)

print("\n✅ 저장 완료: 결과/질문3_증가지역_표.csv, 결과/질문3_증가지역.png")
