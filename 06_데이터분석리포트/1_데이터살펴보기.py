# 미션 1: 데이터를 열어 행 수, 열, 기간을 파악한다
import pandas as pd

# CSV 파일 읽기 (엑셀에서 만든 한글 CSV라 utf-8-sig로 읽어요)
df = pd.read_csv("data/지역별_카페_현황.csv", encoding="utf-8-sig")

print("=" * 50)
print("📋 1. 데이터 크기")
print(f"  행(줄) 수: {len(df)}줄")
print(f"  열(칸) 수: {len(df.columns)}개")

print("\n📋 2. 열 이름")
for col in df.columns:
    print(f"  - {col}")

print("\n📋 3. 맨 앞 5줄 미리보기")
print(df.head().to_string(index=False))

print("\n📋 4. 기간과 지역")
print(f"  연도: {df['연도'].min()}년 ~ {df['연도'].max()}년")
print(f"  분기: {', '.join(df['분기'].unique())}")
print(f"  지역 수: {df['시도'].nunique()}개")
print(f"  지역 목록: {', '.join(df['시도'].unique())}")

print("\n📋 5. 빈칸(결측치) 확인")
빈칸 = df.isna().sum().sum()
print(f"  빈칸 개수: {빈칸}개")

print("\n📋 6. 숫자 열 요약 (최소 / 평균 / 최대)")
for col in ["영업중_점포수", "신규개업", "폐업"]:
    print(f"  {col}: 최소 {df[col].min():,} / 평균 {df[col].mean():,.0f} / 최대 {df[col].max():,}")
print("=" * 50)
