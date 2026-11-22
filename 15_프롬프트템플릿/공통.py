# 공통 도구: 모든 번호 스크립트가 같이 쓰는 부품 모음
#  - 03번 실습의 금고(.env)에 든 Claude API 키를 빌려 써요 (키를 새로 복사하지 않아요)
#  - 리뷰 CSV 읽기, Claude에게 묻기를 여기서 한 번만 만들어 둬요

import csv
from pathlib import Path

import anthropic                    # Claude와 대화하는 공식 도구
from dotenv import load_dotenv      # .env 금고를 여는 도구

여기 = Path(__file__).parent
load_dotenv(여기.parent / "03_메일분류" / ".env")   # 03번 금고에서 API 키를 꺼내 둔다 (화면엔 안 보여요)
client = anthropic.Anthropic()

모델 = "claude-opus-5-5"


def 리뷰_읽기():
    """data/고객리뷰.csv 를 읽어서 [{'리뷰번호':..., '별점':..., '리뷰내용':...}, ...] 로 돌려준다."""
    with open(여기 / "data" / "고객리뷰.csv", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def 클로드에게_묻기(질문, 지시문=None):
    """Claude에게 질문 하나를 보내고, 대답 글자만 돌려준다.
    지시문(system)은 '이 대화 내내 지킬 규칙'이에요. 없으면 그냥 질문만 보내요."""
    옵션 = {}
    if 지시문:
        옵션["system"] = 지시문
    응답 = client.beta.messages.create(
        model=모델,
        max_tokens=2000,
        messages=[{"role": "user", "content": 질문}],
        output_config={"effort": "low"},             # 쉬운 일이라 "가볍게 생각해" (요금 절약)
        betas=["server-side-fallback-2026-07-01"],   # 혹시 AI가 거절하면
        fallbacks="default",                         #   다른 모델이 이어받게 하는 안전장치
        **옵션,
    )
    if 응답.stop_reason == "refusal":
        return "(거절)"
    return "".join(조각.text for 조각 in 응답.content if 조각.type == "text").strip()
