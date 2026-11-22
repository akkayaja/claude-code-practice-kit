# 서브에이전트(편집장)가 쓰는 글자 수 측정기 — AI 대신 코드가 세요
#  사용법: python3 17_AI에이전트워크플로우/글자수세기.py 글파일 1500자
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from 공통 import 제목과_본문, 글자수

글 = Path(sys.argv[1]).read_text(encoding="utf-8")
목표 = int(sys.argv[2].replace("자", ""))
제목, 본문 = 제목과_본문(글)
아래, 위 = round(목표 * 0.85), round(목표 * 1.15)
본문수 = 글자수(본문)
print(f"제목 {len(제목)}자 (25자 이내: {'통과' if len(제목) <= 25 else '불통과'})")
print(f"본문 {본문수}자 (띄어쓰기 포함, 통과 범위 {아래}~{위}자) → 5번 {'통과' if 아래 <= 본문수 <= 위 else '불통과'}")
