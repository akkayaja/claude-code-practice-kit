# 04 실습 1단계: 과목별·일정별 신청 인원 집계
# 별도 설치 없이 파이썬 기본 도구(csv, collections)만 사용해요.

import csv
from collections import Counter

# 1) CSV 파일 열기 (utf-8-sig: 파일 맨 앞의 숨은 표시(BOM)를 지워 줘요)
with open("data/특강신청_응답.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))  # 한 줄 = 신청서 한 장

print(f"전체 신청 건수: {len(rows)}건\n")

# 2) 과목별로 세기 (Counter = 표에 바를 정(正) 자 긋는 계수기)
subject_count = Counter(row["신청과목"] for row in rows)
print("📚 과목별 신청 인원")
for subject, n in subject_count.most_common():
    print(f"  {subject}: {n}명")
print(f"  (합계 {sum(subject_count.values())}명)\n")

# 3) 일정별로 세기
schedule_count = Counter(row["희망일정"] for row in rows)
print("📅 일정별 신청 인원")
for schedule, n in sorted(schedule_count.items()):
    print(f"  {schedule}: {n}명")
print(f"  (합계 {sum(schedule_count.values())}명)")
