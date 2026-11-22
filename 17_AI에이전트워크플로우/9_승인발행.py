# 도전 미션 2: 발행 전 사람(사장님) 승인 단계 넣기 — B안
#  미션 5에서 만든 완성본 5편을 하나씩 보여 주고 y(승인) / n(반려) / q(그만)을 물어요
#  반려하면: 사장님이 적은 이유 → 작가가 고침 → 편집장 재검수(되돌이 고리) → 다시 사장님께
#  승인한 글만 결과/발행/ 에 들어가요. 결정 기록은 결과/승인/승인기록.csv
import csv
import re
import shutil
from 공통 import 주제_읽기, 결과폴더, 검수루프, 사장님_요청_반영, 제목과_본문, 글자수

최대반려 = 2                                  # 사장님 반려도 2번까지 → 그다음은 '보류'
승인폴더, 발행폴더 = 결과폴더 / "승인", 결과폴더 / "발행"
shutil.rmtree(승인폴더, ignore_errors=True)
shutil.rmtree(발행폴더, ignore_errors=True)
발행폴더.mkdir(parents=True)
승인폴더.mkdir(parents=True)          # 반려가 하나도 없어도 승인기록.csv 를 둘 자리
한글키 = {"ㅛ": "y", "ㅜ": "n", "ㅂ": "q"}  # 한글 자판으로 눌러도 알아듣기


def 미리보기(글):
    """제목, 글자 수, 첫 문단, 마지막 문단만 보여 준다 (전체는 파일에서)."""
    제목, 본문 = 제목과_본문(글)
    문단 = [p.strip() for p in re.split(r"\n\s*\n", 본문) if p.strip() and not p.strip().startswith("#")]
    print(f"   📰 제목: {제목} ({len(제목)}자) / 본문 {글자수(본문)}자")
    print(f"   ▶ 첫 문단: {문단[0]}")
    print(f"   ▶ 마지막 문단: {문단[-1]}")


기록 = []
그만 = False
for 주제 in 주제_읽기():
    번호 = 주제["번호"]
    완성본파일 = 결과폴더 / "전체" / f"주제{번호}" / "5_완성본.md"
    글 = 완성본파일.read_text(encoding="utf-8")
    반려이유 = []
    결정 = "보류"
    while not 그만:
        print("\n" + "─" * 60)
        print(f"📋 주제 {번호}: {주제['주제']}" + (f"  (반려 후 {len(반려이유)}번째 수정본)" if 반려이유 else ""))
        미리보기(글)
        답 = input("👉 발행할까요? (y=승인 / n=반려 / q=그만): ").strip().lower()
        답 = 한글키.get(답, 답)
        if 답 == "y":
            결정 = "승인"
            (발행폴더 / f"주제{번호}.md").write_text(글, encoding="utf-8")
            print(f"   ✅ 승인! → 결과/발행/주제{번호}.md")
            break
        if 답 == "q":
            그만 = True
            break
        if 답 != "n":
            print("   (y, n, q 중 하나만 눌러 주세요)")
            continue
        if len(반려이유) >= 최대반려:
            print(f"   ⏸ 반려 {최대반려}번을 다 썼어요 → '보류'로 두고 다음 글로 넘어가요")
            break
        이유 = input("✏️  반려 이유(고칠 점)를 적어 주세요: ").strip() or "전체적으로 더 읽기 쉽게 다듬어 주세요"
        반려이유.append(이유)
        작업폴더 = 승인폴더 / f"주제{번호}" / f"반려{len(반려이유)}차"
        작업폴더.mkdir(parents=True, exist_ok=True)
        print("   ④ 작가: 사장님 요청대로 고치는 중...")
        글 = 사장님_요청_반영(주제, 글, 이유)
        (작업폴더 / "4_사장님요청_수정본.md").write_text(글, encoding="utf-8")
        글, _ = 검수루프(주제, 글, 작업폴더, 꼭지킬것=" / ".join(반려이유))   # 고친 글도 편집장이 재검수 (사장님 요청은 유지)
    기록.append([번호, 제목과_본문(글)[0], 결정, len(반려이유), " / ".join(반려이유)])

with open(승인폴더 / "승인기록.csv", "w", encoding="utf-8-sig", newline="") as f:
    쓰기 = csv.writer(f)
    쓰기.writerow(["번호", "제목", "결정", "반려횟수", "반려이유"])
    쓰기.writerows(기록)

print("\n" + "=" * 60)
for 번호, 제목, 결정, 횟수, _ in 기록:
    표시 = {"승인": "✅", "보류": "⏸"}[결정]
    print(f"{표시} 주제{번호} {결정} (반려 {횟수}번)  {제목}")
print(f"🎉 승인 {sum(줄[2] == '승인' for 줄 in 기록)}편 → 결과/발행/  |  기록: 결과/승인/승인기록.csv")
