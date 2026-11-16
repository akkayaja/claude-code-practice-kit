# 미션 6: 분류결과/ 폴더에 들어간 내 결과를 정답_분류표.csv와 비교해서 정확도(%)를 계산한다.

import csv
from pathlib import Path

결과폴더 = Path("분류결과")
정답파일 = Path("정답_분류표.csv")

# 1) 내 결과 읽기: 분류결과/칸이름/mail_XX.eml → {"mail_XX": "칸이름"}
내결과 = {}
for 메일파일 in 결과폴더.glob("*/*.eml"):
    내결과[메일파일.stem] = 메일파일.parent.name     # stem = 확장자(.eml)를 뺀 이름

# 2) 정답 읽기 (utf-8-sig = 맨 앞의 보이지 않는 표시(BOM)를 알아서 무시하는 방식)
정답 = {}
with open(정답파일, encoding="utf-8-sig", newline="") as f:
    for 줄 in csv.DictReader(f):
        이름 = Path(줄["파일명"].strip()).stem           # "mail_01.eml"이든 "mail_01"이든 똑같이 맞춤
        정답[이름] = 줄["분류"].strip()

# 3) 하나씩 맞춰 보기
맞은수 = 0
틀린목록 = []
print(f"{'메일':<10} {'내 답':<8} {'정답':<8} 결과")
print("-" * 40)
for 이름 in sorted(정답):
    내답 = 내결과.get(이름, "(없음)")
    if 내답 == 정답[이름]:
        맞은수 += 1
        표시 = "⭕"
    else:
        표시 = "❌"
        틀린목록.append(이름)
    print(f"{이름:<10} {내답:<8} {정답[이름]:<8} {표시}")

# 4) 정확도 = 맞은 개수 ÷ 전체 개수 × 100
정확도 = 맞은수 / len(정답) * 100
print("-" * 40)
print(f"정확도: {맞은수}/{len(정답)} = {정확도:.0f}%")
if 틀린목록:
    print("틀린 메일:", ", ".join(틀린목록))
