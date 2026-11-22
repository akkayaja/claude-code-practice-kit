# 미션 2: 규정 문서를 '포스트잇 크기 조각(청크)'으로 자르기
#  - docs 폴더의 .md 문서를 한 줄(- 로 시작하는 항목)씩 잘라요
#  - 조각만 떼어 놓으면 무슨 얘기인지 모르니, 앞에 '문서 제목 > 소제목'을 붙여 둬요
#    예) "(주)연습상사 휴가 규정 > 경조휴가: 본인 결혼 5일, ..."
#  - 결과는 조각목록.json 에 저장해서, 다음 단계(검색)에서 꺼내 써요

import json
from pathlib import Path

여기 = Path(__file__).parent
조각목록 = []

for 문서 in sorted((여기 / "docs").glob("*.md")):      # docs 폴더의 문서를 이름순으로 하나씩
    제목 = ""
    소제목 = ""
    for 줄 in 문서.read_text(encoding="utf-8").splitlines():
        줄 = 줄.strip()
        if 줄.startswith("## "):          # ## 로 시작하면 소제목 (예: 연차, 반차)
            소제목 = 줄[3:]
        elif 줄.startswith("# "):         # # 로 시작하면 문서 제목
            제목 = 줄[2:]
        elif 줄.startswith("- "):         # - 로 시작하는 항목 한 줄 = 조각 하나
            머리말 = f"{제목} > {소제목}" if 소제목 else 제목
            조각목록.append({
                "번호": len(조각목록) + 1,
                "문서": 문서.name,
                "내용": f"{머리말}: {줄[2:]}",
            })

# 조각을 파일로 저장 (한글이 깨지지 않게 ensure_ascii=False)
(여기 / "조각목록.json").write_text(
    json.dumps(조각목록, ensure_ascii=False, indent=2), encoding="utf-8"
)

# 화면에 요약 보여 주기
print(f"✂️  문서 {len(set(c['문서'] for c in 조각목록))}개를 조각 {len(조각목록)}개로 나눴어요.\n")
for 문서이름 in sorted(set(c["문서"] for c in 조각목록)):
    개수 = sum(1 for c in 조각목록 if c["문서"] == 문서이름)
    print(f"  {문서이름}: {개수}개")
print("\n🔎 예시 조각 3개:")
for c in 조각목록[:2] + 조각목록[-1:]:
    print(f"  [{c['번호']}] {c['내용']}")
print("\n💾 조각목록.json 에 저장했어요.")
