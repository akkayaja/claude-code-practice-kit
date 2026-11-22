"""미션 3: 사례 3개의 '전 → 후' 숫자를 그래프 이미지로 만든다.

- 숫자는 학습일지(15·16·17)에 적힌 확인된 숫자만 그대로 옮겨 적었다.
- 만드는 곳: 이미지/사례1.png, 사례2.png, 사례3.png
- 실행: 06번 가상환경의 파이썬(matplotlib)을 빌려 쓴다.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 창을 띄우지 않고 파일로만 저장
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"  # 맥 한글 글꼴 (안 쓰면 글자가 □□로 깨져요)
plt.rcParams["axes.unicode_minus"] = False

여기 = Path(__file__).resolve().parent
이미지폴더 = 여기 / "이미지"
이미지폴더.mkdir(exist_ok=True)

회색, 초록 = "#b0b0b0", "#2e9e6a"


def 저장(그림, 이름):
    그림.tight_layout()
    그림.savefig(이미지폴더 / 이름, dpi=150)
    plt.close(그림)
    print(f"저장: 이미지/{이름}")


# ── 사례 1: 리뷰 답글 템플릿 (15번) ─────────────────────────────
# 같은 리뷰 3개를 3번씩: 템플릿 없이 답글 1~5개·457~912자 → 템플릿 v1 항상 1개·83~104자
그림, (왼, 오) = plt.subplots(1, 2, figsize=(9, 3.6))
for 축, 제목, 단위, 전, 후 in [
    (왼, "답글 개수", "개", (1, 5), (1, 1)),
    (오, "답글 길이", "자", (457, 912), (83, 104)),
]:
    for 줄, (이름, (작은, 큰), 색) in enumerate([("템플릿 없이", 전, 회색), ("템플릿 사용", 후, 초록)]):
        축.barh(줄, max(큰 - 작은, 큰 * 0.02), left=작은, color=색, height=0.5)
        글 = f"{작은}{단위}" if 작은 == 큰 else f"{작은}~{큰}{단위}"
        축.text(큰, 줄, f"  {글}", va="center", fontsize=11)
    축.set_yticks([0, 1], ["템플릿 없이", "템플릿 사용"])
    축.invert_yaxis()
    축.set_title(f"{제목} (매번 얼마나 달라지나)")
    축.set_xlim(0, 전[1] * 1.35)
    축.spines[["top", "right"]].set_visible(False)
그림.suptitle("사례 1. 리뷰 답글 — 템플릿을 주자 결과가 한 모양으로", fontsize=13)
저장(그림, "사례1.png")

# ── 사례 2: 규정 챗봇 (16번) ──────────────────────────────────
# 9문항 채점: 처음 5/9 → 채점 기준 수정(A안) 9/9, 근거 문서 9/9 일치
그림, 축 = plt.subplots(figsize=(7, 3.6))
이름들 = ["처음 채점", "개선 후 채점", "근거 문서 일치"]
값들 = [5, 9, 9]
막대 = 축.bar(이름들, 값들, color=[회색, 초록, 초록], width=0.55)
for 하나, 값 in zip(막대, 값들):
    축.text(하나.get_x() + 하나.get_width() / 2, 값 + 0.2, f"{값} / 9", ha="center", fontsize=12)
축.set_ylim(0, 10.5)
축.set_ylabel("문항 수 (9문항 중)")
축.spines[["top", "right"]].set_visible(False)
축.set_title("사례 2. 규정 챗봇 — 테스트 9문항 채점", fontsize=13)
저장(그림, "사례2.png")

# ── 사례 3: AI 편집부 (17번) ─────────────────────────────────
# 요약.csv: 주제 5개 처리 시간(초)과 결과, 5편 비용 648원 → 1편당 약 130원
그림, 축 = plt.subplots(figsize=(8, 3.6))
주제 = ["주제 1", "주제 2", "주제 3", "주제 4", "주제 5"]
시간 = [39, 41, 48, 56, 41]
수정 = [0, 0, 0, 1, 0]
막대 = 축.bar(주제, 시간, color=초록, width=0.55)
for 하나, 초, 고침 in zip(막대, 시간, 수정):
    표시 = f"{초}초\n통과" + (" (수정 1번)" if 고침 else "")
    축.text(하나.get_x() + 하나.get_width() / 2, 초 + 1, 표시, ha="center", fontsize=10)
축.set_ylim(0, 75)
축.set_ylabel("처리 시간 (초)")
축.spines[["top", "right"]].set_visible(False)
축.set_title("사례 3. AI 편집부 — 5팀 동시 처리, 약 1분 · 1편당 약 130원 · 5편 모두 통과",
             fontsize=12)
저장(그림, "사례3.png")

print(f"\n이미지 {len(list(이미지폴더.glob('*.png')))}장 완성")
