# 도전 미션 C: 키워드 규칙 대신 AI(Claude)에게 메일 분류를 맡기고,
#             정답과 비교해서 "규칙 직원 vs AI 직원" 정확도를 비교한다.
# 실행: .venv/bin/python AI분류.py   (Claude API를 부르므로 아주 적은 요금이 나와요)

import csv
from email import policy
from email.parser import BytesParser
from pathlib import Path

import anthropic                    # Claude와 대화하는 공식 도구
from dotenv import load_dotenv      # .env 비밀 쪽지를 읽는 도구

load_dotenv()                       # .env 안의 ANTHROPIC_API_KEY를 읽어 둔다 (화면엔 안 보여요)
client = anthropic.Anthropic()      # 읽어 둔 키로 Claude에 연결할 준비

# ============================================================
# ✏️ AI에게 줄 설명 — 여기만 고치면 돼요!
# ============================================================
모델 = "claude-opus-5-5"
칸목록 = ["견적요청", "청구서", "고객문의", "사내공지", "스팸"]
지시문 = """너는 회사 메일을 분류하는 직원이야.
메일을 읽고 아래 5개 중 하나로만 분류해.
- 견적요청: 가격을 알려 달라는 메일
- 청구서: 돈을 내라는 메일
- 고객문의: 고객이 묻거나 요청하는 메일
- 사내공지: 회사 안에서 직원들에게 알리는 메일
- 스팸: 원하지 않는 메일
답은 칸 이름 한 단어만 써. 설명은 쓰지 마."""
# ============================================================

INBOX = Path("inbox")


def AI에게_묻기(제목, 본문):
    """Claude에게 메일 한 통을 보여 주고, 어느 칸인지 대답을 받는다."""
    응답 = client.beta.messages.create(
        model=모델,
        max_tokens=2000,
        system=지시문,
        messages=[{"role": "user", "content": f"제목: {제목}\n\n본문:\n{본문}"}],
        output_config={"effort": "low"},             # 쉬운 일이라 "가볍게 생각해"로 설정 (요금 절약)
        betas=["server-side-fallback-2026-07-01"],   # 혹시 AI가 거절하면
        fallbacks="default",                         #   다른 모델이 자동으로 이어받게 하는 안전장치
    )
    if 응답.stop_reason == "refusal":                # AI가 대답을 거절한 경우
        return "(거절)"
    # 응답에는 여러 조각이 있을 수 있어서, 글자(text) 조각만 골라 이어 붙인다
    답 = "".join(조각.text for 조각 in 응답.content if 조각.type == "text").strip()
    return 답 if 답 in 칸목록 else f"(이상한 답: {답[:10]})"


# 1) 정답 읽기
정답 = {}
with open("정답_분류표.csv", encoding="utf-8-sig", newline="") as f:
    for 줄 in csv.DictReader(f):
        정답[Path(줄["파일명"].strip()).stem] = 줄["분류"].strip()

# 2) 규칙 직원의 답 읽기 (미션 4에서 만든 분류결과/ 폴더)
규칙답 = {p.stem: p.parent.name for p in Path("분류결과").glob("*/*.eml")}

# 3) 메일마다 AI에게 묻고 비교하기
AI맞음 = 규칙맞음 = 0
print(f"{'메일':<10} {'정답':<8} {'규칙':<8} {'AI':<8}")
print("-" * 44)

try:
    for 메일파일 in sorted(INBOX.glob("*.eml")):
        with open(메일파일, "rb") as f:
            메일 = BytesParser(policy=policy.default).parse(f)
        제목 = 메일["Subject"]
        본문 = 메일.get_body(preferencelist=("plain",)).get_content()

        이름 = 메일파일.stem
        AI답 = AI에게_묻기(제목, 본문)
        규칙 = 규칙답.get(이름, "(없음)")

        AI맞음 += AI답 == 정답[이름]
        규칙맞음 += 규칙 == 정답[이름]
        print(f"{이름:<10} {정답[이름]:<8} {규칙:<8} {AI답:<8} {'⭕' if AI답 == 정답[이름] else '❌'}")

except anthropic.AuthenticationError:
    print("\n❌ API 키가 틀렸어요. .env 파일의 키를 다시 확인해 주세요.")
    raise SystemExit
except anthropic.PermissionDeniedError:
    print("\n❌ 이 키로는 사용할 권한이 없어요. 콘솔에서 크레딧 충전·권한을 확인해 주세요.")
    raise SystemExit
except anthropic.RateLimitError:
    print("\n❌ 너무 빨리 많이 불렀어요. 1분쯤 뒤에 다시 실행해 주세요.")
    raise SystemExit
except anthropic.APIConnectionError:
    print("\n❌ 인터넷 연결을 확인해 주세요.")
    raise SystemExit

전체 = len(정답)
print("-" * 44)
print(f"🧑‍💼 규칙 직원: {규칙맞음}/{전체} = {규칙맞음 / 전체 * 100:.0f}%")
print(f"🤖 AI 직원:   {AI맞음}/{전체} = {AI맞음 / 전체 * 100:.0f}%")
