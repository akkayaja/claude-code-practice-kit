# 04 실습 2단계: 개인정보 동의가 '아니오'인 신청자 걸러 내기

import csv
from collections import Counter

with open("data/특강신청_응답.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 체(거름망)로 거르기: 동의 칸이 '네'인 사람만 통과, 나머지는 걸러짐
agreed = [row for row in rows if row["개인정보동의"].strip() == "네"]
not_agreed = [row for row in rows if row["개인정보동의"].strip() != "네"]

print(f"전체 {len(rows)}명 = 동의 {len(agreed)}명 + 미동의 {len(not_agreed)}명\n")

print("🚫 개인정보 미동의자 (연락하면 안 되는 사람)")
for row in not_agreed:
    print(f"  {row['이름']} | {row['신청과목']} | {row['희망일정']}")

print("\n📚 동의자만 다시 센 과목별 인원")
for subject, n in Counter(r["신청과목"] for r in agreed).most_common():
    print(f"  {subject}: {n}명")

# 동의한 사람만 새 파일로 저장 (구글 시트 연습 때도 쓸 수 있어요)
with open("data/동의자만.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(agreed)
print("\n💾 동의자만 모은 파일 저장: data/동의자만.csv")
