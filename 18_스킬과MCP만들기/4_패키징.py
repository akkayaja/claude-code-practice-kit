# 18번 도전 미션: 동료가 설치할 수 있게 '선물 상자(플러그인)'로 포장하기
#
# 비유: 내 책상에 흩어진 매뉴얼 2권과 손 1개를 상자(onggi-office)에 차곡차곡 담는 일이에요.
#   원본(내 책상)                               → 상자 안
#   .claude/skills/weekly-report/               → onggi-office/skills/weekly-report/
#   .claude/skills/review-reply/                → onggi-office/skills/review-reply/
#   18_스킬과MCP만들기/1_shop서버.py             → onggi-office/server/shop_server.py
# 상자의 이름표(plugin.json), 손 연결표(.mcp.json), 설명서(README.md)는 이미 만들어 뒀어요.
# 원본을 고치면 이 스크립트를 다시 돌려 '다시 포장'하면 돼요.
#
# 실행: 18 폴더에서  python3 4_패키징.py

import shutil
import subprocess
from pathlib import Path

폴더 = Path(__file__).resolve().parent        # 18 폴더
맨위 = 폴더.parent                              # 실습키트 맨 위
상자 = 폴더 / "onggi-office"

# 1) 매뉴얼(스킬) 2권 담기 – 상자 안 옛 복사본은 지우고 새로 복사
for 이름 in ["weekly-report", "review-reply"]:
    원본 = 맨위 / ".claude" / "skills" / 이름
    도착 = 상자 / "skills" / 이름
    if 도착.exists():
        shutil.rmtree(도착)
    shutil.copytree(원본, 도착)
    print(f"📘 스킬 담음: {이름}")

# 2) 손(MCP 서버) 담기 – 영어 파일 이름으로 (명령줄에서 다루기 쉽게)
(상자 / "server").mkdir(exist_ok=True)
shutil.copy2(폴더 / "1_shop서버.py", 상자 / "server" / "shop_server.py")
print("🖐 MCP 서버 담음: server/shop_server.py")

# 3) 상자에 든 파일 목록 보여 주기
print("\n📦 상자 안 파일:")
파일들 = sorted(p for p in 상자.rglob("*") if p.is_file())
for p in 파일들:
    print("   ", p.relative_to(상자))
print(f"   → 모두 {len(파일들)}개")

# 4) 검사: Claude Code의 '포장 검사기'로 상자와 가게 목록(marketplace)이 규칙에 맞는지 확인
print("\n🔍 포장 검사")
for 대상 in [상자, 맨위]:
    결과 = subprocess.run(["claude", "plugin", "validate", str(대상)], capture_output=True, text=True)
    마지막줄 = (결과.stdout.strip() or 결과.stderr.strip()).splitlines()[-1]
    print(f"   {'✅' if 결과.returncode == 0 else '❌'} {대상.relative_to(맨위.parent).as_posix()}: {마지막줄}")
