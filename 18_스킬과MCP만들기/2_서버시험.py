# 18번 실습 ③: MCP 서버 시험하기
#
# 비유: Claude Code 대신 '시험관'이 되어 서버에 손을 빌려 보는 프로그램이에요.
#   1) 1_shop서버.py 를 뒤에서 켜고
#   2) "손이 몇 개 있어?" 물어본 뒤 (도구 목록)
#   3) 손 ① 매출 조회, 손 ② 고객 검색을 한 번씩 빌려 써요.
# 실행: 18 폴더에서  .venv/bin/python 2_서버시험.py

import asyncio                                   # '기다렸다가 답 받기'를 하는 도구
import sys                                       # 지금 쓰는 파이썬 위치를 알아내는 도구
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

서버파일 = Path(__file__).resolve().parent / "1_shop서버.py"


async def 시험():
    # 서버를 켜는 방법: "지금 이 파이썬으로 1_shop서버.py 를 실행해"
    켜는법 = StdioServerParameters(command=sys.executable, args=[str(서버파일)])

    async with stdio_client(켜는법) as (읽기, 쓰기):          # 서버와 전화 연결
        async with ClientSession(읽기, 쓰기) as 세션:          # 대화 시작
            await 세션.initialize()                          # 첫인사

            목록 = await 세션.list_tools()                    # "손이 몇 개 있어?"
            print(f"🖐 서버에 달린 손: {len(목록.tools)}개")
            for 도구 in 목록.tools:
                print(f"  - {도구.name}: {도구.description.splitlines()[0]}")
            print()

            # 손 ① 빌리기: month 를 비우면 '지난달'
            결과 = await 세션.call_tool("sales_by_month", {})
            print(결과.content[0].text, "\n")

            # 손 ② 빌리기: '민준'이 이름에 들어간 고객
            결과 = await 세션.call_tool("search_customers", {"keyword": "민준"})
            print(결과.content[0].text)


asyncio.run(시험())
