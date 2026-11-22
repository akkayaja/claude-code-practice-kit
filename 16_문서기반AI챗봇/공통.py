# 공통 도구: 번호 스크립트들이 같이 쓰는 부품 모음
#  - 조각목록.json 읽기, 질문과 비슷한 조각 찾기(검색)를 여기서 한 번만 만들어 둬요

import csv
import json
import re
from pathlib import Path

여기 = Path(__file__).parent


def 조각_읽기():
    """1_청크나누기.py 가 만든 조각목록.json 을 읽어 온다."""
    return json.loads((여기 / "조각목록.json").read_text(encoding="utf-8"))


def 테스트질문_읽기():
    """테스트질문_정답.csv 를 [{'질문':..., '기대답변':..., '근거문서':...}, ...] 로 읽어 온다."""
    with open(여기 / "테스트질문_정답.csv", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def 두글자씩(글):
    """'연차가 며칠' → {'연차', '차가', '며칠'} 처럼 붙어 있는 두 글자 묶음으로 쪼갠다.
    (띄어쓰기·물음표는 빼고, 낱말 안에서만 두 글자씩 잘라요)"""
    묶음 = set()
    for 낱말 in 글.replace("?", " ").replace(",", " ").replace(".", " ").split():
        for i in range(len(낱말) - 1):
            묶음.add(낱말[i:i + 2])
    return 묶음


def 검색(질문, 개수=3):
    """질문과 '두 글자 묶음'이 많이 겹치는 조각부터 개수만큼 돌려준다.
    점수 = 질문과 조각에 함께 들어 있는 두 글자 묶음의 수"""
    질문묶음 = 두글자씩(질문)
    결과 = []
    for 조각 in 조각_읽기():
        겹침 = 질문묶음 & 두글자씩(조각["내용"])
        결과.append({**조각, "점수": len(겹침), "겹친말": sorted(겹침)})
    결과 = [c for c in 결과 if c["점수"] > 0]          # 하나도 안 겹친 조각(0점)은 빼기
    결과.sort(key=lambda c: c["점수"], reverse=True)   # 점수 높은 순으로 줄 세우기
    return 결과[:개수]


# ───────── 여기부터 미션 4: Claude에게 '조각을 근거로' 답하게 하기 ─────────

모델 = "claude-opus-5-5"
없음_문구 = "문서에 없는 내용이에요"

# 대화 내내 지킬 규칙 (알바생에게 주는 '응대 원칙')
지시문 = f"""너는 (주)연습상사의 사내 규정 안내 챗봇이야.
반드시 아래 규칙을 지켜.
1. 사용자 메시지의 [참고 조각]에 적힌 내용만 근거로 답해. 네가 원래 알던 지식이나 짐작은 쓰지 마.
2. 참고 조각에 질문의 답이 없으면 지어내지 말고 정확히 "{없음_문구}. 담당 부서에 확인해 주세요."라고만 답해.
   (단어 몇 개가 겹친다고 관련 있는 조각은 아니야. 질문이 묻는 바로 그 내용이 있어야 해.)
3. 답은 한국어 존댓말로 1~3문장, 핵심 숫자를 꼭 넣어. 터미널에 그대로 찍히니 ** 같은 꾸밈 기호는 쓰지 마."""


def 클로드에게_묻기(질문, 지시문=None):
    """Claude에게 질문 하나를 보내고 대답 글자만 돌려준다 (15번 공통.py와 같은 방식)."""
    import anthropic                    # Claude와 대화하는 공식 도구
    from dotenv import load_dotenv      # .env 금고를 여는 도구
    load_dotenv(여기.parent / "03_메일분류" / ".env")   # 03번 금고에서 API 키를 빌려 온다
    옵션 = {"system": 지시문} if 지시문 else {}
    응답 = anthropic.Anthropic().beta.messages.create(
        model=모델,
        max_tokens=1000,
        messages=[{"role": "user", "content": 질문}],
        output_config={"effort": "low"},             # 쉬운 일이라 "가볍게 생각해" (요금 절약)
        betas=["server-side-fallback-2026-07-01"],   # 혹시 AI가 거절하면
        fallbacks="default",                         #   다른 모델이 이어받게 하는 안전장치
        **옵션,
    )
    if 응답.stop_reason == "refusal":
        return "(거절)"
    글 = "".join(조각.text for 조각 in 응답.content if 조각.type == "text")
    # 가끔 답 앞뒤에 <final>, <final_answer> 같은 영어 꼬리표가 섞여 나와서 지워 줘요
    글 = re.sub(r"</?[A-Za-z_]+>", "", 글)
    return 글.strip()


def 답하기(질문):
    """RAG 한 바퀴: ① 검색 → ② 찾은 조각을 질문과 함께 건네기 → ③ Claude가 답하기
    돌려주는 것: (답, 찾은 조각 목록)"""
    찾은것 = 검색(질문, 개수=3)                                   # ① 찾기
    참고 = "\n".join(f"- {c['내용']}" for c in 찾은것) or "- (찾은 조각 없음)"
    메시지 = f"[참고 조각]\n{참고}\n\n[질문]\n{질문}"             # ② 근거 챙기기
    return 클로드에게_묻기(메시지, 지시문), 찾은것                  # ③ 답하기


# ───────── 여기부터 도전 미션: 답변마다 근거 문서 이름 표시하기 ─────────

근거_지시문 = 지시문 + """
4. 답을 다 쓴 뒤 마지막 줄에 '근거: ' 다음에 실제로 답에 쓴 조각 번호를 적어. 예) 근거: [1], [3]
   문서에 없는 내용이라 답할 수 없으면 '근거: 없음'이라고 적어."""


def 답하기_근거포함(질문):
    """답하기()와 같지만, 조각에 번호를 붙여 건네고 Claude가 '실제로 쓴' 조각 번호를 받아
    그 조각의 문서 이름으로 바꿔 준다. 돌려주는 것: (답, 근거문서 목록, 찾은 조각 목록)"""
    찾은것 = 검색(질문, 개수=3)
    참고 = "\n".join(f"[{i}] {c['내용']}" for i, c in enumerate(찾은것, start=1)) or "(찾은 조각 없음)"
    전체 = 클로드에게_묻기(f"[참고 조각]\n{참고}\n\n[질문]\n{질문}", 근거_지시문)

    답줄, 근거문서 = [], []
    for 줄 in 전체.splitlines():
        if 줄.strip().startswith("근거:"):                 # '근거: [1], [3]' 줄에서 번호만 골라내기
            for i, c in enumerate(찾은것, start=1):
                if f"[{i}]" in 줄 and c["문서"] not in 근거문서:
                    근거문서.append(c["문서"])
        else:
            답줄.append(줄)
    return "\n".join(답줄).strip(), 근거문서, 찾은것
