"""
월별 매출 요약기 (undocumented/tool.py 를 알아보기 쉽게 고친 버전)

하는 일:
    '일별·채널별 매출' CSV 파일을 읽어서, 월마다
    매출 합계 · 주문 합계 · 객단가(매출 ÷ 주문)를 계산해 새 CSV로 저장한다.
    채널 이름을 주면 그 채널만 골라서 계산한다.

사용법:
    python3 documented/월별매출요약.py  읽을_CSV  저장할_CSV  [채널이름]

예시:
    python3 documented/월별매출요약.py ../08_대시보드/data/일별_채널별_매출_2025.csv 결과/월별_전체.csv
    python3 documented/월별매출요약.py ../08_대시보드/data/일별_채널별_매출_2025.csv 결과/월별_쿠팡.csv 쿠팡

읽을 CSV에 꼭 있어야 하는 칸: 날짜(YYYY-MM-DD), 채널, 주문수, 매출액
"""

import csv
import os
import sys
from collections import defaultdict

# 읽을 파일에 꼭 있어야 하는 칸 이름
필요한_칸 = ["날짜", "채널", "주문수", "매출액"]

사용법_안내 = """사용법: python3 documented/월별매출요약.py 읽을_CSV 저장할_CSV [채널이름]
  예) python3 documented/월별매출요약.py ../08_대시보드/data/일별_채널별_매출_2025.csv 결과/월별_전체.csv
  예) python3 documented/월별매출요약.py ../08_대시보드/data/일별_채널별_매출_2025.csv 결과/월별_쿠팡.csv 쿠팡"""


def 월별로_합치기(읽을_파일, 고를_채널=None):
    """CSV를 한 줄씩 읽어 월마다 [매출 합계, 주문 합계]를 모은다.

    돌려주는 값: ({'2025-01': [매출합계, 주문합계], ...}, 파일에 있던 채널 이름 모음)
    """
    # 처음 보는 달이 나오면 [0, 0] 빈 장부를 자동으로 만들어 준다
    월별_장부 = defaultdict(lambda: [0, 0])
    파일에_있는_채널 = set()

    # utf-8-sig: 엑셀이 저장한 CSV 맨 앞의 보이지 않는 표시(BOM)를 지우고 읽는다
    with open(읽을_파일, encoding="utf-8-sig") as 파일:
        읽기 = csv.DictReader(파일)

        빠진_칸 = [칸 for 칸 in 필요한_칸 if 칸 not in (읽기.fieldnames or [])]
        if 빠진_칸:
            sys.exit(f"❌ 읽을 파일에 이 칸이 없어요: {', '.join(빠진_칸)}")

        for 한_줄 in 읽기:
            파일에_있는_채널.add(한_줄["채널"])

            # 채널을 골랐다면, 다른 채널 줄은 건너뛴다
            if 고를_채널 and 한_줄["채널"] != 고를_채널:
                continue

            # '2025-01-15' → 앞 7글자 '2025-01' 만 써서 같은 달끼리 묶는다
            월 = 한_줄["날짜"][:7]
            월별_장부[월][0] += int(한_줄["매출액"])
            월별_장부[월][1] += int(한_줄["주문수"])

    return 월별_장부, 파일에_있는_채널


def 결과_저장하기(월별_장부, 저장할_파일):
    """월별 장부를 '월, 매출, 주문, 객단가' 표로 CSV에 저장한다."""
    # 저장할 폴더가 없으면 먼저 만든다 (예: 결과/)
    폴더 = os.path.dirname(저장할_파일)
    if 폴더:
        os.makedirs(폴더, exist_ok=True)

    # utf-8-sig 로 저장해야 엑셀에서 열 때 한글이 안 깨진다
    with open(저장할_파일, "w", encoding="utf-8-sig", newline="") as 파일:
        쓰기 = csv.writer(파일)
        쓰기.writerow(["월", "매출", "주문", "객단가"])

        for 월 in sorted(월별_장부):  # 1월 → 12월 순서
            매출합계, 주문합계 = 월별_장부[월]
            # 객단가 = 매출 ÷ 주문 (원 단위 반올림). 주문이 0건이면 0으로 둔다
            객단가 = round(매출합계 / 주문합계) if 주문합계 else 0
            쓰기.writerow([월, 매출합계, 주문합계, 객단가])


def main():
    # sys.argv = [스크립트이름, 읽을_CSV, 저장할_CSV, (채널이름)]
    if len(sys.argv) < 3:
        print(사용법_안내)
        sys.exit(1)

    읽을_파일 = sys.argv[1]
    저장할_파일 = sys.argv[2]
    고를_채널 = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(읽을_파일):
        sys.exit(f"❌ 읽을 파일을 찾지 못했어요: {읽을_파일}")

    월별_장부, 파일에_있는_채널 = 월별로_합치기(읽을_파일, 고를_채널)

    # 없는 채널 이름이면 빈 파일을 만들지 않고 멈춘다
    if 고를_채널 and 고를_채널 not in 파일에_있는_채널:
        sys.exit(
            f"❌ '{고를_채널}' 채널이 파일에 없어요. "
            f"쓸 수 있는 채널: {', '.join(sorted(파일에_있는_채널))}"
        )

    결과_저장하기(월별_장부, 저장할_파일)

    대상 = 고를_채널 or "전체 채널"
    print(f"✅ 저장 완료 ({대상}, {len(월별_장부)}개월): {저장할_파일}")


if __name__ == "__main__":
    main()
