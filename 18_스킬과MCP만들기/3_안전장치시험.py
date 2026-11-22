# 18번 도전 미션: 읽기 전용 안전장치 시험하기
#
# 비유: '도둑 역할'을 맡은 시험관이 손 ③(run_select)에 나쁜 명령을 넣어 봐요.
#   자물쇠가 제대로 걸려 있으면 → 전부 ⛔ 거절, shop.db 는 한 글자도 안 바뀌어요.
# 확인 방법: 시험 전후로 shop.db 파일의 '지문'(해시)과 주문 수를 비교해요.
# 실행: 18 폴더에서  .venv/bin/python 3_안전장치시험.py

import asyncio
import hashlib                                   # 파일 지문(해시)을 만드는 도구
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

폴더 = Path(__file__).resolve().parent
서버파일 = 폴더 / "1_shop서버.py"
DB파일 = 폴더.parent / "07_SQL연습" / "shop.db"


def 지문():
    """파일 내용으로 만든 짧은 지문. 한 글자라도 바뀌면 완전히 달라져요."""
    return hashlib.sha256(DB파일.read_bytes()).hexdigest()[:12]


시험목록 = [
    ("정상 조회", "SELECT COUNT(*) AS 주문수 FROM orders"),
    ("삭제 시도", "DELETE FROM orders"),
    ("수정 시도", "UPDATE products SET price = 0"),
    ("테이블 삭제 시도", "DROP TABLE customers"),
    ("끼워 넣기 시도", "SELECT 1; DELETE FROM orders"),
    ("문지기 속이기 시도", "WITH x AS (SELECT 1) DELETE FROM orders"),
]


async def 시험():
    전지문 = 지문()
    print(f"🔎 시험 전 shop.db 지문: {전지문}\n")

    켜는법 = StdioServerParameters(command=sys.executable, args=[str(서버파일)])
    async with stdio_client(켜는법) as (읽기, 쓰기):
        async with ClientSession(읽기, 쓰기) as 세션:
            await 세션.initialize()

            목록 = await 세션.list_tools()
            이름들 = ", ".join(도구.name for 도구 in 목록.tools)
            print(f"🖐 서버에 달린 손: {len(목록.tools)}개 ({이름들})\n")

            거절수 = 0
            for 번호, (제목, sql) in enumerate(시험목록, 1):
                결과 = await 세션.call_tool("run_select", {"sql": sql})
                답 = 결과.content[0].text
                if 답.startswith("⛔"):
                    거절수 += 1
                print(f"[{번호}] {제목}: {sql}")
                print("    → " + 답.replace("\n", "\n      ") + "\n")

            # 시험이 끝난 뒤 주문 수 다시 세기
            결과 = await 세션.call_tool("run_select", {"sql": "SELECT COUNT(*) FROM orders"})
            주문수 = 결과.content[0].text.splitlines()[1]

    후지문 = 지문()
    print("=" * 50)
    print(f"나쁜 명령 {len(시험목록) - 1}개 중 거절: {거절수}개")
    print(f"시험 후 주문 수: {주문수}건")
    print(f"시험 후 shop.db 지문: {후지문} → {'✅ 그대로예요' if 전지문 == 후지문 else '❌ 바뀌었어요!'}")


asyncio.run(시험())
