# 도전 미션: SQL로 꺼낸 결과를 그래프 3장 + 표 1개짜리 HTML 리포트로 만들기
# 실행: .venv/bin/python 5_그래프리포트.py   →   결과/ 폴더에 PNG 3장 + 쇼핑몰_분석_리포트.html
import base64
import os
import sqlite3
from datetime import date

import matplotlib
matplotlib.use("Agg")  # 창을 띄우지 않고 파일로만 그리기
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"  # 맥 한글 글꼴 (안 쓰면 글자가 □□로 깨져요)
plt.rcParams["axes.unicode_minus"] = False   # 마이너스(-) 기호 깨짐 방지

os.makedirs("결과", exist_ok=True)
db = sqlite3.connect("shop.db")


def sql(질문):
    """SQL 질문을 DB에 보내고, 답을 pandas 표로 받아요."""
    return pd.read_sql_query(질문, db)


# ───────────────────────── 그래프 1. 2025년 월별 매출 (문제 11번) ─────────────────────────
월별 = sql("""
    SELECT substr(o.ordered_at, 6, 2) AS 월, SUM(o.qty * p.price) AS 매출
    FROM orders AS o JOIN products AS p ON o.product_id = p.id
    WHERE o.status = '완료' AND o.ordered_at LIKE '2025%'
    GROUP BY 월 ORDER BY 월
""")
월별["월"] = 월별["월"].astype(int)
월별["매출_만원"] = 월별["매출"] / 10000

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(월별["월"], 월별["매출_만원"], marker="o", color="#5b8def", linewidth=2)
ax.set_ylim(0, 월별["매출_만원"].max() * 1.15)  # 세로축을 0부터 → 차이를 과장하지 않기
ax.set_xticks(range(1, 13))
ax.set_xticklabels([f"{m}월" for m in range(1, 13)])
ax.set_ylabel("매출 (만 원)")
ax.set_title("2025년 월별 매출 (완료 주문)")
ax.grid(axis="y", alpha=0.3)
for 월, 값 in zip(월별["월"], 월별["매출_만원"]):
    ax.text(월, 값 + 25, f"{값:,.0f}", ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("결과/그래프1_월별매출.png", dpi=150)
plt.close(fig)

최고 = 월별.loc[월별["매출"].idxmax(), ["월", "매출"]].astype(int)  # 정수로 (5.0월 → 5월)
최저 = 월별.loc[월별["매출"].idxmin(), ["월", "매출"]].astype(int)

# ──────────────── 그래프 2. 등급별 총구매금액 vs 1인당 구매금액 (문제 10번 + 한 걸음 더) ────────────────
등급 = sql("""
    SELECT c.grade AS 등급,
           (SELECT COUNT(*) FROM customers AS x WHERE x.grade = c.grade) AS 인원,
           SUM(o.qty * p.price) AS 총구매금액
    FROM orders AS o
    JOIN customers AS c ON o.customer_id = c.id
    JOIN products  AS p ON o.product_id  = p.id
    WHERE o.status = '완료'
    GROUP BY c.grade
""")
등급["1인당"] = (등급["총구매금액"] / 등급["인원"]).round().astype(int)
등급 = 등급.set_index("등급").loc[["VIP", "골드", "실버", "일반"]].reset_index()

fig, (왼쪽, 오른쪽) = plt.subplots(1, 2, figsize=(10, 4.5))
왼쪽.bar(등급["등급"], 등급["총구매금액"] / 10000, color="#c7d7f5")
왼쪽.set_title("① 등급별 총구매금액 (만 원)")
for i, 값 in enumerate(등급["총구매금액"] / 10000):
    왼쪽.text(i, 값, f"{값:,.0f}", ha="center", va="bottom", fontsize=9)
오른쪽.bar(등급["등급"], 등급["1인당"] / 10000, color="#5b8def")
오른쪽.set_title("② 등급별 1인당 구매금액 (만 원)")
for i, 값 in enumerate(등급["1인당"] / 10000):
    오른쪽.text(i, 값, f"{값:,.1f}", ha="center", va="bottom", fontsize=9)
for ax in (왼쪽, 오른쪽):
    ax.grid(axis="y", alpha=0.3)
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{g}\n({n}명)" for g, n in zip(등급["등급"], 등급["인원"])])
fig.tight_layout()
fig.savefig("결과/그래프2_등급별구매.png", dpi=150)
plt.close(fig)

# ───────────────────────── 그래프 3. 상품별 반품률 (문제 14번) ─────────────────────────
반품 = sql("""
    SELECT p.name AS 상품, COUNT(*) AS 전체주문,
           SUM(CASE WHEN o.status = '반품' THEN 1 ELSE 0 END) AS 반품,
           ROUND(100.0 * SUM(CASE WHEN o.status = '반품' THEN 1 ELSE 0 END) / COUNT(*), 1) AS 반품률
    FROM orders AS o JOIN products AS p ON o.product_id = p.id
    GROUP BY p.id
""")
반품 = 반품.sort_values("반품률")
전체반품률 = round(100 * 반품["반품"].sum() / 반품["전체주문"].sum(), 1)

fig, ax = plt.subplots(figsize=(9, 5))
색 = ["#e8746a" if r > 전체반품률 else "#9bb7ee" for r in 반품["반품률"]]
ax.barh(반품["상품"], 반품["반품률"], color=색)
ax.axvline(전체반품률, color="#555", linestyle="--", linewidth=1)
ax.text(전체반품률, -0.9, f" 전체 평균 {전체반품률}%", fontsize=9)
for y, 값 in enumerate(반품["반품률"]):
    ax.text(값 + 0.1, y, f"{값}%", va="center", fontsize=8)
ax.set_xlabel("반품률 (%) = 반품 ÷ 전체 주문")
ax.set_title("상품별 반품률 (빨강 = 평균보다 높음)")
ax.set_xlim(0, 반품["반품률"].max() + 2)
fig.tight_layout()
fig.savefig("결과/그래프3_반품률.png", dpi=150)
plt.close(fig)

# ───────────────────────── 표. 지역별 1등 상품 (문제 15번) ─────────────────────────
지역 = sql("""
    WITH 지역상품 AS (
        SELECT c.region AS 지역, p.name AS 상품, SUM(o.qty) AS 수량,
               RANK() OVER (PARTITION BY c.region ORDER BY SUM(o.qty) DESC) AS 순위
        FROM orders AS o
        JOIN customers AS c ON o.customer_id = c.id
        JOIN products  AS p ON o.product_id  = p.id
        WHERE o.status = '완료'
        GROUP BY c.region, p.name
    )
    SELECT 지역, 상품 AS "1등 상품", 수량 AS "판매 수량" FROM 지역상품 WHERE 순위 = 1 ORDER BY 수량 DESC
""")
db.close()


# ───────────────────────── HTML 리포트로 묶기 ─────────────────────────
def 그림(파일):
    """PNG를 글자로 바꿔 HTML 안에 넣어요 → 파일 하나만 보내도 그림이 보여요."""
    with open(파일, "rb") as f:
        return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" alt="{파일}">'


VIP = 등급.set_index("등급").loc["VIP"]
골드 = 등급.set_index("등급").loc["골드"]
반품1등 = 반품.iloc[-1]
반품꼴찌 = 반품.iloc[0]
연매출 = int(월별["매출"].sum())

섹션들 = [
    ("1. 2025년 월별 매출은 어떻게 움직였나? (문제 11)",
     그림("결과/그래프1_월별매출.png"),
     f"2025년 매출은 총 {연매출:,}원이다. 최고는 {최고['월']}월({최고['매출']:,}원), "
     f"최저는 {최저['월']}월({최저['매출']:,}원)로 약 {최고['매출'] / 최저['매출']:.1f}배 차이가 난다. "
     "꾸준히 오르거나 내리는 흐름 없이 달마다 오르내린다.",
     "세로축을 0부터 시작해서 차이를 부풀리지 않았어요."),
    ("2. VIP 고객이 정말 돈을 더 쓰나? (문제 10 + 한 걸음 더)",
     그림("결과/그래프2_등급별구매.png"),
     f"총액(①)으로 보면 VIP가 꼴찌지만, 이는 VIP가 {VIP['인원']}명뿐이기 때문이다. "
     f"1인당(②)으로 다시 보면 VIP는 {VIP['1인당']:,}원으로 골드({골드['1인당']:,}원)와 일반보다 낮다. "
     "지금의 등급이 실제 구매력을 잘 반영하지 못하고 있어, 등급 기준을 다시 살펴볼 필요가 있다.",
     "1인당 = 완료 주문 총액 ÷ 그 등급의 전체 고객 수(주문 안 한 고객 0명)."),
    ("3. 어떤 상품이 많이 반품되나? (문제 14)",
     그림("결과/그래프3_반품률.png"),
     f"전체 반품률은 {전체반품률}%다. {반품1등['상품']}({반품1등['반품률']}%)이 가장 높고 "
     f"{반품꼴찌['상품']}({반품꼴찌['반품률']}%)이 가장 낮아 약 2배 차이가 난다. "
     "상위 2개(볼펜 세트·노트북 거치대)는 차이가 0.1%p뿐이라 함께 점검 대상으로 보는 게 맞다.",
     "상품마다 주문이 112~150건이라, 반품 1~2건으로도 반품률이 1%p쯤 움직여요."),
]

본문 = ""
for 제목, 그래프, 결론, 주의 in 섹션들:
    본문 += f"""
  <section>
    <h2>{제목}</h2>
    {그래프}
    <div class="결론">💡 <b>그래서 무엇을 알 수 있나?</b><br>{결론}</div>
    <p class="주의">⚠️ {주의}</p>
  </section>"""

본문 += f"""
  <section>
    <h2>4. 지역마다 가장 많이 팔린 상품은? (문제 15)</h2>
    {지역.to_html(index=False, border=0, classes="표")}
    <div class="결론">💡 <b>그래서 무엇을 알 수 있나?</b><br>
    9개 지역 중 1등 상품이 겹치는 곳은 가습기(경기·광주), A4 복사용지(대전·세종), 포스트잇(부산·인천)뿐이다.
    지역마다 잘 팔리는 상품이 달라서, 지역별로 광고 상품을 다르게 고르는 근거가 된다.</div>
  </section>"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>쇼핑몰 주문 분석 리포트</title>
<style>
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; max-width: 960px;
         margin: 0 auto; padding: 24px 16px; color: #222; line-height: 1.6; background: #fafafa; }}
  .부제 {{ color: #666; margin-top: 0; }}
  section, .요약 {{ background: #fff; border-radius: 12px; padding: 20px 24px; margin: 20px 0;
                   box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  img {{ width: 100%; height: auto; border: 1px solid #eee; border-radius: 8px; }}
  .결론 {{ background: #eef5ff; border-left: 4px solid #5b8def; padding: 12px 16px; margin: 16px 0; border-radius: 4px; }}
  .주의 {{ color: #a15c00; font-size: 0.9em; }}
  table.표 {{ border-collapse: collapse; width: 100%; font-size: 0.95em; }}
  table.표 th, table.표 td {{ border-bottom: 1px solid #eee; padding: 6px 8px; text-align: left; }}
  footer {{ color: #999; font-size: 0.85em; text-align: center; margin-top: 32px; }}
</style>
</head>
<body>
  <h1>🛒 쇼핑몰 주문 분석 리포트</h1>
  <p class="부제">데이터: shop.db (가상 데이터) — 고객 200명 · 상품 12개 · 주문 1,500건 · SQL로 조회</p>
  <div class="요약">
    <h2>📌 한눈에 보기</h2>
    <ul>
      <li><b>매출</b>: 2025년 총 {연매출:,}원. {최고['월']}월이 최고, {최저['월']}월이 최저(약 {최고['매출'] / 최저['매출']:.1f}배 차이).</li>
      <li><b>등급</b>: VIP의 1인당 구매금액({VIP['1인당']:,}원)이 골드·일반보다 낮다 → 등급 기준 재검토 필요.</li>
      <li><b>반품</b>: 전체 {전체반품률}%. {반품1등['상품']}({반품1등['반품률']}%)·노트북 거치대가 가장 높다.</li>
      <li><b>지역</b>: 지역마다 1등 상품이 달라 지역 맞춤 광고가 가능하다.</li>
    </ul>
  </div>
  {본문}
  <footer>만든 날짜: {date.today()} · Python(sqlite3, pandas, matplotlib)으로 자동 생성</footer>
</body>
</html>"""

with open("결과/쇼핑몰_분석_리포트.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ 리포트를 만들었어요: 결과/쇼핑몰_분석_리포트.html")
print(f"   2025년 매출 {연매출:,}원 / 최고 {최고['월']}월 {최고['매출']:,}원 / 최저 {최저['월']}월 {최저['매출']:,}원")
print(f"   VIP 1인당 {VIP['1인당']:,}원 / 골드 1인당 {골드['1인당']:,}원")
print(f"   전체 반품률 {전체반품률}% / 1등 {반품1등['상품']} {반품1등['반품률']}%")
