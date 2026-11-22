# 18번 실습 ③: 07번 shop.db 를 들여다보는 아주 작은 MCP 서버
#
# 비유: Claude에게 '손' 2개를 달아 주는 프로그램이에요.
#   손 ① sales_by_month   – 한 달 매출 조회
#   손 ② search_customers – 고객 검색
#   손 ③ run_select       – (도전 미션) SELECT 자유 조회, 읽기 전용 자물쇠 3개
# Claude Code가 이 파일을 뒤에서 켜 두고, 필요할 때 손을 빌려 써요.
#
# 직접 실행하면 화면에 아무것도 안 나오고 '기다리는' 상태가 돼요 (정상이에요).
# 시험은 2_서버시험.py 로 해요.

import os                          # 환경변수(SHOP_DB)를 읽는 도구
import sqlite3                     # SQLite 데이터베이스(shop.db)를 여는 도구
from datetime import date          # 오늘 날짜 → '지난달' 계산용
from pathlib import Path           # 파일 위치를 다루는 도구
from mcp.server import MCPServer   # 공식 MCP 공구 상자 (손을 만드는 틀)
from mcp.types import ToolAnnotations  # 손에 붙이는 이름표 (도전 미션: 읽기 전용 표시)

# shop.db 위치 찾기 (도전 미션 '패키징' 때문에 후보를 3개로 늘렸어요)
#   ① 환경변수 SHOP_DB 에 적힌 곳 (동료가 자기 DB 위치를 직접 알려 줄 때)
#   ② 이 파일 기준: 18 폴더 → 한 칸 위(실습키트) → 07_SQL연습/shop.db
#   ③ 지금 작업 폴더 기준: ./07_SQL연습/shop.db (플러그인으로 설치돼 다른 곳에 복사됐을 때)
후보들 = [
    os.environ.get("SHOP_DB", ""),
    Path(__file__).resolve().parent.parent / "07_SQL연습" / "shop.db",
    Path.cwd() / "07_SQL연습" / "shop.db",
]
DB파일 = next((Path(후보) for 후보 in 후보들 if 후보 and Path(후보).is_file()), Path(후보들[1]))

# 서버(손 묶음)에 이름표 붙이기. Claude Code 화면에 이 이름으로 보여요.
mcp = MCPServer("shop-db")


def DB열기():
    """shop.db 를 '읽기 전용'으로 열어서 돌려줘요.

    🔒 도전 미션: 읽기 전용 안전장치 (자물쇠 2개)
      자물쇠 ② mode=ro  : 파일을 '보기 전용'으로 열어요. 쓰려고 하면 SQLite가 거절해요.
      자물쇠 ③ query_only: 한 번 더, 이 연결로는 어떤 수정도 못 하게 잠가요.
    (자물쇠 ① 문지기는 아래 run_select 손 안에 있어요)
    """
    주소 = DB파일.as_uri() + "?mode=ro"          # file:///.../shop.db?mode=ro
    db = sqlite3.connect(주소, uri=True)
    db.execute("PRAGMA query_only = ON")
    return db


def 지난달():
    """오늘이 2026-11-22 이면 '2026-10' 을 돌려줘요."""
    오늘 = date.today()
    if 오늘.month == 1:
        return f"{오늘.year - 1}-12"
    return f"{오늘.year}-{오늘.month - 1:02d}"


# ── 손 ① 한 달 매출 조회 ─────────────────────────────────
# @mcp.tool() 한 줄 = "아래 함수를 Claude가 쓸 수 있는 손으로 등록해 줘"
# 함수 바로 아래 """설명""" 은 Claude가 읽는 '사용 설명서'예요. (언제 이 손을 쓸지 판단하는 근거)
@mcp.tool()
def sales_by_month(month: str = "") -> str:
    """shop.db 에서 한 달 동안의 매출을 조회한다.

    month: 'YYYY-MM' 형식 (예: '2026-10'). 비우면 지난달.
    기준: 상태가 '완료'인 주문만 매출로 센다 (취소·반품 제외). 매출 = 수량 × 상품 가격.
    """
    월 = month.strip() or 지난달()
    db = DB열기()
    # 완료 주문만: 매출 합계와 주문 수
    매출, 건수 = db.execute(
        """SELECT COALESCE(SUM(o.qty * p.price), 0), COUNT(*)
           FROM orders o JOIN products p ON p.id = o.product_id
           WHERE o.status = '완료' AND substr(o.ordered_at, 1, 7) = ?""",
        (월,),
    ).fetchone()
    # 상태별 주문 수 (완료·취소·반품) – 기준을 투명하게 보여 주려고
    상태별 = db.execute(
        """SELECT status, COUNT(*) FROM orders
           WHERE substr(ordered_at, 1, 7) = ? GROUP BY status""",
        (월,),
    ).fetchall()
    # 카테고리별 매출 (큰 순서)
    분류별 = db.execute(
        """SELECT p.category, SUM(o.qty * p.price) AS 금액
           FROM orders o JOIN products p ON p.id = o.product_id
           WHERE o.status = '완료' AND substr(o.ordered_at, 1, 7) = ?
           GROUP BY p.category ORDER BY 금액 DESC""",
        (월,),
    ).fetchall()
    db.close()

    if sum(n for _, n in 상태별) == 0:
        return f"{월}에는 주문이 없어요. (데이터 기간: 2025-01 ~ 2026-11)"

    줄들 = [
        f"[{월} 매출] 기준: 완료 주문만 (매출 = 수량 × 가격)",
        f"- 매출 합계: {매출:,}원",
        f"- 완료 주문: {건수}건",
        "- 상태별 주문 수: " + ", ".join(f"{상태} {n}건" for 상태, n in 상태별),
        "- 카테고리별 매출: " + ", ".join(f"{분류} {금액:,}원" for 분류, 금액 in 분류별),
    ]
    return "\n".join(줄들)


# ── 손 ② 고객 검색 ───────────────────────────────────────
@mcp.tool()
def search_customers(keyword: str) -> str:
    """shop.db 에서 고객을 검색한다.

    keyword: 이름 일부(예: '민준'), 지역(예: '서울'), 등급('VIP'/'일반') 중 하나.
    결과: 최대 20명. 고객마다 완료 주문 수와 총 구매액(완료 주문만)을 함께 보여 준다.
    """
    단어 = keyword.strip()
    if not 단어:
        return "검색어를 넣어 주세요. (이름 일부, 지역, 등급)"
    db = DB열기()
    조건 = "c.name LIKE ? OR c.region = ? OR c.grade = ?"
    값 = (f"%{단어}%", 단어, 단어)
    전체수 = db.execute(f"SELECT COUNT(*) FROM customers c WHERE {조건}", 값).fetchone()[0]
    고객들 = db.execute(
        f"""SELECT c.id, c.name, c.region, c.grade, c.joined_at,
                   COUNT(o.id), COALESCE(SUM(o.qty * p.price), 0)
            FROM customers c
            LEFT JOIN orders o ON o.customer_id = c.id AND o.status = '완료'
            LEFT JOIN products p ON p.id = o.product_id
            WHERE {조건}
            GROUP BY c.id ORDER BY c.id LIMIT 20""",
        값,
    ).fetchall()
    db.close()

    if 전체수 == 0:
        return f"'{단어}'에 맞는 고객이 없어요."
    줄들 = [f"['{단어}' 고객 검색] {전체수}명" + (" (앞 20명만 표시)" if 전체수 > 20 else "")]
    for 번호, 이름, 지역, 등급, 가입일, 주문수, 구매액 in 고객들:
        줄들.append(f"- #{번호} {이름} | {지역} | {등급} | 가입 {가입일} | 완료 주문 {주문수}건 · {구매액:,}원")
    return "\n".join(줄들)


# ── 손 ③ (도전 미션) 자유 조회 – 단, 보기만 가능 ─────────────
# 손 ①②는 정해진 질문만 해요. 손 ③은 Claude가 SQL을 직접 써서 물어볼 수 있어요.
# 자유로운 만큼 위험하니까 자물쇠를 3개 채워요.
#   자물쇠 ① 문지기   : SELECT/WITH 로 시작하는 문장 '하나'만 들여보내요
#   자물쇠 ② mode=ro  : 문지기를 속여도 파일 자체가 보기 전용이라 못 고쳐요
#   자물쇠 ③ query_only: 한 겹 더
# ToolAnnotations(readOnlyHint=True) = 손에 붙이는 "보기 전용" 이름표 (Claude Code에 알려 주는 용도)


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def run_select(sql: str) -> str:
    """shop.db 에 SELECT 문으로 자유롭게 조회한다. (읽기 전용, 최대 50줄)

    테이블: customers(id, name, region, grade, joined_at),
            products(id, name, category, price),
            orders(id, customer_id, product_id, qty, ordered_at, status)
    status 값: '완료', '취소', '반품'. 매출은 보통 status='완료' 인 주문의 qty * price.
    INSERT/UPDATE/DELETE/DROP 등 DB를 바꾸는 문장은 거절된다.
    """
    문장 = sql.strip().rstrip(";").strip()

    # 자물쇠 ① 문지기
    첫단어 = 문장.split(None, 1)[0].upper() if 문장 else ""
    if 첫단어 not in ("SELECT", "WITH"):
        return f"⛔ 거절: 읽기 전용이라 SELECT 로 시작하는 조회만 할 수 있어요. (받은 첫 단어: {첫단어 or '없음'})"
    if ";" in 문장:
        return "⛔ 거절: 문장은 한 번에 하나만 보낼 수 있어요. (; 로 여러 문장을 이어 붙이면 안 돼요)"

    db = DB열기()   # 자물쇠 ②③ 이 채워진 연결
    try:
        커서 = db.execute(문장)
        칸이름 = [칸[0] for 칸 in 커서.description] if 커서.description else []
        줄들 = 커서.fetchmany(50)
    except sqlite3.Error as 오류:
        return f"⛔ 거절: DB가 실행을 막았어요 → {오류}"
    finally:
        db.close()

    결과 = [" | ".join(칸이름)]
    결과 += [" | ".join(str(값) for 값 in 줄) for 줄 in 줄들]
    결과.append(f"({len(줄들)}줄" + (", 50줄까지만 표시" if len(줄들) == 50 else "") + ")")
    return "\n".join(결과)


# 이 파일을 직접 실행하면 서버를 켜고 Claude Code의 연락을 기다려요.
# stdio = 표준 입출력(파이프)으로 대화한다는 뜻. 그래서 print() 를 쓰면 대화가 꼬여요!
if __name__ == "__main__":
    mcp.run("stdio")
