# 기본 미션 4: 리뷰 15개 전부를 템플릿으로 처리해서 CSV(엑셀로 열리는 표)로 저장한다
# 실행 (15 폴더에서):
#   ../03_메일분류/.venv/bin/python 3_전체처리.py                 ← 템플릿_v1 → 결과/리뷰_답글.csv
#   ../03_메일분류/.venv/bin/python 3_전체처리.py 템플릿_v2.txt   ← 템플릿_v2 → 결과/리뷰_답글_v2.csv

import csv
import sys
from collections import Counter
from pathlib import Path

from 공통 import 리뷰_읽기, 클로드에게_묻기

# 1) 어떤 템플릿을 쓸지 정하기 (명령 뒤에 파일 이름을 붙이면 그걸 쓴다)
템플릿파일 = sys.argv[1] if len(sys.argv) > 1 else "템플릿_v1.txt"
템플릿 = Path(템플릿파일).read_text(encoding="utf-8")
버전 = Path(템플릿파일).stem.removeprefix("템플릿_")             # "템플릿_v2" → "v2"
저장파일 = Path("결과") / ("리뷰_답글.csv" if 버전 == "v1" else f"리뷰_답글_{버전}.csv")


def 칸_꺼내기(결과, 이름):
    """AI 대답에서 '이름: 내용' 줄을 찾아 내용만 돌려준다. 없으면 '(빠짐)'."""
    for 줄 in 결과.splitlines():
        if 줄.startswith(f"{이름}:"):
            return 줄.removeprefix(f"{이름}:").strip()
    return "(빠짐)"


# 2) 리뷰마다 AI에게 묻고, 대답을 칸별로 나눠 담기
칸목록 = ["감정", "답글", "내부조치"]
if "긴급도:" in 템플릿:                                          # 템플릿에 긴급도 칸이 있으면 같이 받는다
    칸목록.append("긴급도")

표 = []
print(f"사용한 템플릿: {템플릿파일}")
for 리뷰 in 리뷰_읽기():
    질문 = f"별점: {리뷰['별점']}점\n리뷰: {리뷰['리뷰내용']}"
    결과 = 클로드에게_묻기(질문, 지시문=템플릿)
    줄 = dict(리뷰)
    for 이름 in 칸목록:
        줄[이름] = 칸_꺼내기(결과, 이름)
    표.append(줄)
    print(f"  {리뷰['리뷰번호']:>2}번 (별점 {리뷰['별점']}) → {줄['감정']}"
          + (f" / {줄['긴급도']}" if "긴급도" in 줄 else ""))

# 3) CSV로 저장 (utf-8-sig: 엑셀에서 열어도 한글이 안 깨지게)
저장파일.parent.mkdir(exist_ok=True)
with open(저장파일, "w", encoding="utf-8-sig", newline="") as f:
    쓰기 = csv.DictWriter(f, fieldnames=list(표[0].keys()))
    쓰기.writeheader()
    쓰기.writerows(표)

# 4) 요약
세기 = Counter(줄["감정"] for 줄 in 표)
print("-" * 40)
print("감정별 개수:", ", ".join(f"{k} {세기[k]}개" for k in ["긍정", "중립", "부정"]),
      f"(합계 {sum(세기.values())}개)")
if "긴급도" in 칸목록:
    print("긴급 대응 필요:", sum(줄["긴급도"].startswith("긴급") for 줄 in 표), "개")
print("답글 최대 길이:", max(len(줄["답글"]) for 줄 in 표), "자")
print(f"저장 완료 → {저장파일}")
