"""도전 미션: 오늘의 브리핑 파일을 내 지메일로 보내기 (나 자신에게만).

- 메일 주소와 앱 비밀번호는 이 폴더의 .env 금고에서 꺼낸다 (.gitignore로 GitHub 제외)
- 앱 비밀번호 = 구글이 주는 '메일 보내기 전용 보조 열쇠' (진짜 구글 비밀번호 아님)
- 오늘 브리핑 파일이 없으면 보내지 않는다
- 보내는 사람 = 받는 사람 = 나 (다른 사람에게는 절대 안 보냄)

실행 (14_자동실행봇 폴더에서): python3 4_메일보내기.py
"""
import os
import smtplib
from datetime import date
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEFING_FILE = os.path.join(HERE, "브리핑", f"오늘의브리핑_{date.today()}.txt")


def load_env(path):
    values = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    name, value = line.split("=", 1)
                    values[name.strip()] = value.strip()
    return values


# 1) 금고에서 주소와 보조 열쇠 꺼내기
env = load_env(os.path.join(HERE, ".env"))
address = env.get("GMAIL_ADDRESS", "")
app_password = env.get("GMAIL_APP_PASSWORD", "").replace(" ", "")   # 띄어쓰기는 빼고 16자리만
if not address or len(app_password) != 16:
    print(f"⚠️  .env 금고를 확인해 주세요 (주소 {'있음' if address else '없음'}, 앱 비밀번호 {len(app_password)}자리 / 16자리여야 해요)")
    raise SystemExit(1)

# 2) 오늘 브리핑 파일 읽기
if not os.path.exists(BRIEFING_FILE):
    print(f"⚠️  오늘 브리핑 파일이 없어요: 브리핑/{os.path.basename(BRIEFING_FILE)}")
    raise SystemExit(1)
with open(BRIEFING_FILE, encoding="utf-8") as f:
    body = f.read()

# 3) 편지 봉투 만들기 (보내는 사람 = 받는 사람 = 나)
msg = EmailMessage()
msg["Subject"] = f"📋 오늘의 브리핑 {date.today()}"
msg["From"] = address
msg["To"] = address
msg.set_content(body)

# 4) 지메일 우체국(smtp.gmail.com)에 보조 열쇠로 들어가서 부치기
stage = "우체국 연결"
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
        stage = "로그인(보조 열쇠 확인)"
        # 로그인 방식을 PLAIN 하나로 고정: 여러 방식을 차례로 시도하면 지메일이 진짜 실패 이유(535)를
        # 알려 준 뒤 전화를 끊어 버려서 'Connection unexpectedly closed'만 보이기 때문
        server.ehlo()
        server.user, server.password = address, app_password
        server.auth("PLAIN", server.auth_plain)
        stage = "편지 부치기"
        server.send_message(msg)
except smtplib.SMTPAuthenticationError:
    print("❌ 로그인 실패 (지메일 답: 535 아이디·비밀번호 불일치)")
    print("   → 앱 비밀번호를 만든 구글 계정이 .env의 GMAIL_ADDRESS와 같은지, 16자리를 정확히 붙여 넣었는지 확인해 주세요.")
    raise SystemExit(1)
except (smtplib.SMTPException, OSError) as e:
    print(f"❌ '{stage}' 단계에서 실패했어요: {type(e).__name__} {e}")
    raise SystemExit(1)

print(f"📧 보냈어요: 제목 '{msg['Subject']}' → 내 지메일 ({len(body.splitlines())}줄)")
