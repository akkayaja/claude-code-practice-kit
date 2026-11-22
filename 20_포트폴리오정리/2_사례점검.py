"""미션 2: 사례 파일들이 양식대로 쓰였는지 점검한다.

- 읽는 곳: 사례/*.md
- 확인하는 것
  1) 양식의 칸 6개(한 줄 요약·문제·해결·결과·화면·배운 점)가 다 있는가
  2) '결과' 칸에 숫자가 있는가 (체크리스트: 모든 사례에 숫자로 된 효과)
  3) 공개 저장소에 올리면 안 되는 것(컴퓨터 경로·이메일·API 키)이 없는가
"""
import re
from pathlib import Path

여기 = Path(__file__).resolve().parent
칸목록 = ["## 한 줄 요약", "## 문제", "## 해결", "## 결과", "## 화면", "## 배운 점"]
위험 = {
    "컴퓨터 경로": r"/Users/",
    "이메일 주소": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "API 키": r"sk-ant-|serviceKey=",
}

파일들 = sorted((여기 / "사례").glob("*.md"))
통과 = 0
print(f"{'파일':<22} 칸   결과숫자  민감정보")
for 파일 in 파일들:
    글 = 파일.read_text(encoding="utf-8")
    있는칸 = sum(1 for 칸 in 칸목록 if 칸 in 글)
    결과칸 = 글.split("## 결과", 1)[-1].split("## 화면", 1)[0]
    숫자수 = len(re.findall(r"\d", 결과칸))
    걸린것 = [이름 for 이름, 무늬 in 위험.items() if re.search(무늬, 글)]
    ok = 있는칸 == len(칸목록) and 숫자수 > 0 and not 걸린것
    통과 += ok
    print(f"{파일.stem:<22} {있는칸}/{len(칸목록)}  {'있음' if 숫자수 else '없음':<6}  {', '.join(걸린것) or '없음'}")

print(f"\n사례 {len(파일들)}개 중 {통과}개 통과")
