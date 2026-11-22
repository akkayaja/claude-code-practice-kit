"""4단계: 내일 옷차림 알림을 내 지메일로 보내기. (매일 20:00 자동 실행할 바로 그 파일)

- 2_옷차림.py 의 make_report()로 제목과 본문을 만든다
- 보내는 주소·앱 비밀번호·받는 주소는 이 폴더의 .env 금고에서 꺼낸다 (.gitignore로 GitHub 제외)
- 실행할 때마다 시각과 결과를 한 줄씩 출력한다 (자동 실행 때는 이 줄이 실행기록.log에 쌓임)

실행 (내프로젝트_옷차림알림 폴더에서): python3 3_메일보내기.py
"""
import importlib.util
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))

_spec = importlib.util.spec_from_file_location("outfit", os.path.join(HERE, "2_옷차림.py"))
outfit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(outfit)


def stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# 1) 금고에서 주소와 보조 열쇠 꺼내기
env = outfit.forecast.load_env(os.path.join(HERE, ".env"))
address = env.get("GMAIL_ADDRESS", "")
mail_to = env.get("MAIL_TO", "") or address
app_password = env.get("GMAIL_APP_PASSWORD", "").replace(" ", "")  # 띄어쓰기 빼고 16자리
if not address or len(app_password) != 16:
    print(f"[{stamp()}] ⚠️  .env 금고를 확인해 주세요 (보내는 주소 {'있음' if address else '없음'}, "
          f"앱 비밀번호 {len(app_password)}자리 / 16자리여야 해요)")
    raise SystemExit(1)

# 2) 내일 예보 + 옷차림으로 편지 내용 만들기
subject, body = outfit.make_report()

# 3) 편지 봉투 만들기
msg = EmailMessage()
msg["Subject"] = subject
msg["From"] = address
msg["To"] = mail_to
msg.set_content(body)

# 4) 지메일 우체국(smtp.gmail.com)에 보조 열쇠로 들어가서 부치기
stage = "우체국 연결"
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=20) as server:
        stage = "로그인(보조 열쇠 확인)"
        # 로그인 방식을 PLAIN 하나로 고정: 여러 방식을 차례로 시도하면 지메일이 진짜 실패 이유(535)를
        # 알려 준 뒤 연결을 끊어서 'Connection unexpectedly closed'만 보이기 때문
        server.ehlo()
        server.user, server.password = address, app_password
        server.auth("PLAIN", server.auth_plain)
        stage = "편지 부치기"
        server.send_message(msg)
except smtplib.SMTPAuthenticationError:
    print(f"[{stamp()}] ❌ 로그인 실패 (535: 아이디·앱 비밀번호 불일치)")
    print("   → 앱 비밀번호를 만든 구글 계정이 .env의 GMAIL_ADDRESS와 같은지 확인해 주세요.")
    raise SystemExit(1)
except (smtplib.SMTPException, OSError) as e:
    print(f"[{stamp()}] ❌ '{stage}' 단계에서 실패했어요: {type(e).__name__} {e}")
    raise SystemExit(1)

print(f"[{stamp()}] 📧 보냈어요: '{subject}' ({len(body.splitlines())}줄)")
