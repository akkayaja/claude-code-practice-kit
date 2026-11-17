# 04 실습 3단계: 같은 사람이 중복 신청했는지 확인하기
# 이름만 같다고 같은 사람일까? → 연락처·이메일(사람마다 하나뿐인 '주민번호' 같은 것)로 다시 확인해요.

import csv
from collections import defaultdict

with open("data/특강신청_응답.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))


def find_duplicates(column):
    """column(칸) 값이 같은 신청서끼리 묶어서, 2장 이상인 묶음만 돌려줘요."""
    groups = defaultdict(list)  # 이름표 붙은 바구니들
    for line_no, row in enumerate(rows, start=2):  # 시트에서 1행은 제목이라 2행부터
        groups[row[column]].append((line_no, row))
    return {key: items for key, items in groups.items() if len(items) > 1}


# 1) 이름으로만 비교
by_name = find_duplicates("이름")
print(f"① 이름이 겹치는 경우: {len(by_name)}개 이름")
for name, items in by_name.items():
    print(f"  {name} ({len(items)}번)")
    for line_no, row in items:
        print(f"     {line_no}행 | {row['연락처']} | {row['이메일']} | {row['신청과목']}")

# 2) 연락처·이메일로 비교 (진짜 같은 사람인지)
by_phone = find_duplicates("연락처")
by_email = find_duplicates("이메일")
print(f"\n② 연락처가 겹치는 경우: {len(by_phone)}건")
print(f"③ 이메일이 겹치는 경우: {len(by_email)}건")

if not by_phone and not by_email:
    print("\n✅ 결론: 이름이 같은 사람은 있지만, 연락처·이메일이 모두 달라요.")
    print("   → 동명이인(이름만 같은 다른 사람)이고, 진짜 중복 신청은 0건이에요.")
else:
    print("\n⚠️ 결론: 연락처나 이메일이 같은 신청서가 있어요. 진짜 중복일 수 있어요!")
