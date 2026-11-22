"""미션 1: 학습일지에 흩어진 '📝 포트폴리오 한 줄'을 한 파일로 모은다.

- 읽는 곳: ../학습일지/*.md (01~19 + 내프로젝트)
- 만드는 곳: 결과/1_한줄모음.md
- 각 일지에서 '포트폴리오 한 줄' 제목 아래의 문제·해결·효과 3줄만 뽑는다.
"""
from pathlib import Path

여기 = Path(__file__).resolve().parent
일지폴더 = 여기.parent / "학습일지"
결과폴더 = 여기 / "결과"
결과폴더.mkdir(exist_ok=True)


def 한줄_뽑기(글: str) -> dict:
    """일지 글에서 문제·해결·효과 줄을 찾아 돌려준다."""
    찾음 = {}
    안쪽 = False
    for 줄 in 글.splitlines():
        if 줄.startswith("## ") and "포트폴리오 한 줄" in 줄:
            안쪽 = True
            continue
        if 안쪽 and 줄.startswith("## "):  # 다음 제목이 나오면 끝
            break
        if 안쪽:
            for 칸 in ("문제", "해결", "효과"):
                머리 = f"- **{칸}:**"
                if 줄.startswith(머리):
                    찾음[칸] = 줄[len(머리):].strip()
    return 찾음


줄들 = ["# 포트폴리오 한 줄 모음", "", "학습일지에서 자동으로 모았어요. (`1_한줄모으기.py`)", ""]
성공 = 0
빠짐 = []
for 파일 in sorted(일지폴더.glob("*.md")):
    결과 = 한줄_뽑기(파일.read_text(encoding="utf-8"))
    if len(결과) == 3:
        성공 += 1
        줄들 += [f"## {파일.stem}", ""]
        줄들 += [f"- **{칸}:** {결과[칸]}" for 칸 in ("문제", "해결", "효과")]
        줄들.append("")
    else:
        빠짐.append(파일.name)

(결과폴더 / "1_한줄모음.md").write_text("\n".join(줄들), encoding="utf-8")

print(f"읽은 일지: {성공 + len(빠짐)}개")
print(f"한 줄(문제·해결·효과)을 다 찾은 일지: {성공}개")
print(f"빠진 일지: {', '.join(빠짐) if 빠짐 else '없음'}")
print("저장: 결과/1_한줄모음.md")
