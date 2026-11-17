# 미션 3-1: 질문 1 "폐업률이 가장 높은 지역은?" — 표와 그래프 만들기
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")                      # 창을 띄우지 않고 그림 파일로만 저장
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"  # 맥 한글 글꼴 (안 쓰면 글자가 □□로 깨져요)
plt.rcParams["axes.unicode_minus"] = False   # 마이너스(-) 기호 깨짐 방지

os.makedirs("결과", exist_ok=True)          # 결과 폴더가 없으면 만들기

df = pd.read_csv("data/지역별_카페_현황.csv", encoding="utf-8-sig")

# 1) 분기마다 폐업률(%) 계산: 폐업 ÷ 영업중_점포수 × 100
df["폐업률"] = df["폐업"] / df["영업중_점포수"] * 100

# 2) 지역별로 24개 분기 폐업률의 평균 → 높은 순으로 정렬
표 = (
    df.groupby("시도")["폐업률"].mean()
    .sort_values(ascending=False)
    .round(2)
    .reset_index()
)
표.columns = ["시도", "평균 분기 폐업률(%)"]
표.index = range(1, len(표) + 1)            # 순위를 1부터 매기기
표.index.name = "순위"

print("=" * 40)
print("📋 질문 1. 폐업률이 가장 높은 지역은?")
print("=" * 40)
print(표.to_string())

전국평균 = df["폐업률"].mean()
print(f"\n전국 평균: {전국평균:.2f}%")
print(f"1등과 꼴찌 차이: {표.iloc[0, 1] - 표.iloc[-1, 1]:.2f}%p")

# 3) 표를 CSV로 저장 (엑셀로 열 수 있어요)
표.to_csv("결과/질문1_폐업률_표.csv", encoding="utf-8-sig")

# 4) 가로 막대그래프 그리기 (1등이 맨 위에 오도록 순서를 뒤집어요)
그래프용 = 표.iloc[::-1]
색 = ["#d9534f" if i == 0 else "#9aa5b1" for i in range(len(표))][::-1]  # 1등만 빨간색

fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(그래프용["시도"], 그래프용["평균 분기 폐업률(%)"], color=색)
ax.axvline(전국평균, color="black", linestyle="--", linewidth=1)
ax.text(전국평균, len(표) - 0.4, f" 전국 평균 {전국평균:.2f}%", fontsize=9)
ax.set_ylim(-0.6, len(표) + 0.2)            # 위쪽에 '전국 평균' 글자 자리 만들기
for y, 값 in enumerate(그래프용["평균 분기 폐업률(%)"]):
    ax.text(값 + 0.05, y, f"{값:.2f}", va="center", fontsize=8)
ax.set_xlim(9, 12)                          # 차이가 잘 보이도록 9%부터 시작
ax.set_xlabel("평균 분기 폐업률 (%)  ※ 가로축이 9%부터 시작해요")
ax.set_title("질문 1. 지역별 평균 분기 폐업률 (2020~2025)")
plt.tight_layout()
plt.savefig("결과/질문1_폐업률.png", dpi=150)

print("\n✅ 저장 완료: 결과/질문1_폐업률_표.csv, 결과/질문1_폐업률.png")
