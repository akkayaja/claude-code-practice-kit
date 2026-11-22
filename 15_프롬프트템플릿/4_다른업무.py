# 도전 미션: 리뷰 템플릿과 같은 틀(역할/규칙/금지사항/출력형식)로 다른 업무도 처리해 본다
# 실행 (15 폴더에서): ../03_메일분류/.venv/bin/python 4_다른업무.py

from pathlib import Path

from 공통 import 클로드에게_묻기

# (템플릿 파일, 처리할 자료, 저장할 파일) — 새 업무가 생기면 여기에 한 줄만 더하면 돼요
할일목록 = [
    ("템플릿_회의록요약.txt", "data/회의록_예시.txt", "결과/회의록_요약.txt"),
    ("템플릿_이메일답장.txt", "data/이메일_예시.txt", "결과/이메일_답장.txt"),
]

Path("결과").mkdir(exist_ok=True)
for 템플릿파일, 자료파일, 저장파일 in 할일목록:
    템플릿 = Path(템플릿파일).read_text(encoding="utf-8")
    자료 = Path(자료파일).read_text(encoding="utf-8")
    결과 = 클로드에게_묻기(자료, 지시문=템플릿)
    Path(저장파일).write_text(결과 + "\n", encoding="utf-8")

    print("=" * 60)
    print(f"템플릿: {템플릿파일}  /  자료: {자료파일}")
    print("-" * 60)
    print(결과)
    print("-" * 60)
    줄들 = 결과.splitlines()
    if "회의록" in 템플릿파일:
        구역 = None
        세기 = {"결정사항": 0, "할 일": 0, "다음 회의 안건": 0}
        for 줄 in 줄들:
            이름 = 줄.rstrip(":").strip()
            if 이름 in 세기:
                구역 = 이름
            elif 구역 and 줄.startswith("- ") and 줄 != "- 없음":
                세기[구역] += 1
        print("개수 →", ", ".join(f"{k} {v}개" for k, v in 세기.items()))
    else:
        print("[확인 필요] 표시 개수 →", 결과.count("[확인 필요"), "개")
    print(f"저장 완료 → {저장파일}")
print("=" * 60)
