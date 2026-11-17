# 도전 미션 1: 진짜 공공데이터 살펴보기 + "이 데이터 믿어도 될까?" 점검
# 실행 위치: 06_데이터분석리포트 폴더 (.venv/bin/python 도전_공공데이터/1_데이터살펴보기.py)
import pandas as pd

# 공공데이터 CSV는 옛날 한글 방식(cp949)이라 encoding을 꼭 알려 줘야 해요
df = pd.read_csv("도전_공공데이터/전국_카페_점포수.csv", encoding="cp949")
df["기준월"] = pd.to_datetime(df["기준월"])  # 글자 "2015-12-01"을 진짜 날짜로 바꾸기

print("=" * 50)
print("📋 1. 데이터 크기와 열")
print(f"  행(줄) 수: {len(df)}줄 / 열: {', '.join(df.columns)}")
print(f"  기간: {df['기준월'].min():%Y년 %m월} ~ {df['기준월'].max():%Y년 %m월}")
print(f"  빈칸: {df.isna().sum().sum()}개")

print("\n📋 2. 처음과 마지막")
처음, 마지막 = df.iloc[0], df.iloc[-1]
print(f"  {처음['기준월']:%Y-%m}: {처음['업소수']:,}곳")
print(f"  {마지막['기준월']:%Y-%m}: {마지막['업소수']:,}곳")
증가 = 마지막["업소수"] - 처음["업소수"]
print(f"  → {증가:+,}곳 ({증가 / 처음['업소수'] * 100:+.1f}%)")

print("\n🕵️ 점검 ①: 빠진 달이 있나?")
전체달 = pd.date_range(df["기준월"].min(), df["기준월"].max(), freq="MS")  # 매달 1일
빠진달 = 전체달.difference(df["기준월"])
print(f"  있어야 할 달: {len(전체달)}개 / 실제 있는 달: {len(df)}개 / 빠진 달: {len(빠진달)}개")
print(f"  빠진 달: {', '.join(f'{d:%Y-%m}' for d in 빠진달)}")

print("\n🕵️ 점검 ②: 바로 전 달과 숫자가 똑같은 달이 있나?")
df["전달대비"] = df["업소수"].diff()
똑같은달 = df[df["전달대비"] == 0]
for _, 줄 in 똑같은달.iterrows():
    print(f"  {줄['기준월']:%Y-%m}: {줄['업소수']:,}곳 (전 달과 완전히 같음)")

print("\n🕵️ 점검 ③: 한 달 사이 크게 튄 곳 (연속된 달끼리만 비교)")
df["연속"] = df["기준월"].diff().dt.days.between(28, 31)       # 바로 다음 달인지
연속 = df[df["연속"]].copy()
연속["변화율"] = 연속["전달대비"] / (연속["업소수"] - 연속["전달대비"]) * 100
for _, 줄 in 연속.reindex(연속["변화율"].abs().sort_values(ascending=False).index).head(3).iterrows():
    print(f"  {줄['기준월']:%Y-%m}: {줄['전달대비']:+,.0f}곳 ({줄['변화율']:+.1f}%)")
print("=" * 50)
