# 도전 미션 A: 청구서 칸으로 분류된 메일에서 금액만 뽑아 합계를 낸다.
# (먼저 python3 메일분류.py 를 실행해서 분류결과/청구서/ 폴더가 있어야 해요)

import re                                   # 글자 속에서 "모양"으로 찾는 도구 (정규표현식)
from email import policy
from email.parser import BytesParser
from pathlib import Path

청구서폴더 = Path("분류결과") / "청구서"

# 금액 모양: 숫자와 쉼표가 이어지다가 "원"으로 끝나는 부분 (예: 3,300,000원)
#   [\d,]+  → 숫자(\d) 또는 쉼표(,)가 1개 이상 이어진 것
#   원       → 바로 뒤에 "원" 글자
금액모양 = re.compile(r"([\d,]+)원")

합계 = 0

print(f"{'메일':<12} {'금액':>12}  제목")
print("-" * 60)

for 메일파일 in sorted(청구서폴더.glob("*.eml")):
    with open(메일파일, "rb") as f:
        메일 = BytesParser(policy=policy.default).parse(f)

    제목 = 메일["Subject"]
    본문 = 메일.get_body(preferencelist=("plain",)).get_content()

    찾음 = 금액모양.search(본문)              # 본문에서 처음 나오는 "OOO원"을 찾는다
    if 찾음:
        금액 = int(찾음.group(1).replace(",", ""))   # "3,300,000" → 쉼표 빼고 → 숫자 3300000
        합계 += 금액
        print(f"{메일파일.name:<12} {금액:>12,}원  {제목}")
    else:
        print(f"{메일파일.name:<12} {'금액 못 찾음':>12}  {제목}")

print("-" * 60)
print(f"{'합계':<12} {합계:>12,}원")
