# 미션 4: 지금까지 만든 것을 HTML 파일 하나(4_대시보드.html)로 합친다
#   맨 위  : KPI 카드 4장 (총매출·총주문수·객단가·전환율)  ← 미션 1
#   가운데 : 월별 매출 추이 꺾은선 그래프                    ← 미션 2
#   아래   : 채널별 매출 비중 가로 막대                      ← 미션 3
# 계산 방법은 미션 1~3과 똑같다. 그래서 숫자도 똑같이 나와야 한다.
# 꺾은선 그래프는 Chart.js(인터넷에서 불러오는 그래프 도구)로 그린다.

import csv
import json

CSV_파일 = "data/일별_채널별_매출_2025.csv"
결과_파일 = "4_대시보드.html"

# 1) CSV 읽기
with open(CSV_파일, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 2) 한 번 훑으면서 세 가지를 동시에 더한다: 전체 합계 / 월별 매출 / 채널별 매출
전체 = {"주문수": 0, "매출액": 0, "방문자수": 0}
월별매출 = {}
채널별매출 = {}
for row in rows:
    매출 = int(row["매출액"])
    전체["주문수"] += int(row["주문수"])
    전체["매출액"] += 매출
    전체["방문자수"] += int(row["방문자수"])
    월 = row["날짜"][:7]
    월별매출[월] = 월별매출.get(월, 0) + 매출
    채널별매출[row["채널"]] = 채널별매출.get(row["채널"], 0) + 매출

# 3) KPI 4개 (미션 1과 같은 계산)
총매출 = 전체["매출액"]
총주문수 = 전체["주문수"]
객단가 = 총매출 / 총주문수
전환율 = 총주문수 / 전체["방문자수"] * 100

# 4) 월별 (미션 2와 같은 계산)
월목록 = sorted(월별매출)
월라벨 = [f"{int(m[5:])}월" for m in 월목록]
월값 = [월별매출[m] for m in 월목록]

# 5) 채널 비중 (미션 3과 같은 계산), 큰 순서대로
순위 = sorted(채널별매출.items(), key=lambda x: x[1], reverse=True)

# 6) 터미널에 요약 보여 주기
print("===== 대시보드에 들어간 숫자 =====")
print(f"[KPI] 총매출 {총매출:,}원 / 총주문수 {총주문수:,}건 / 객단가 {객단가:,.0f}원 / 전환율 {전환율:.2f}%")
최고 = max(range(len(월값)), key=lambda i: 월값[i])
print(f"[월별] 12개월 합계 {sum(월값):,}원 / 최고 {월라벨[최고]} {월값[최고]:,}원")
print("[채널] " + " / ".join(f"{c} {v / 총매출 * 100:.1f}%" for c, v in 순위))

# 7) HTML 조각 만들기
카드 = [
    ("총매출", f"{총매출 / 100000000:.2f}억 원", f"{총매출:,}원"),
    ("총주문수", f"{총주문수:,}건", "1년 동안 들어온 주문"),
    ("객단가", f"{객단가:,.0f}원", "총매출 ÷ 총주문수"),
    ("전환율", f"{전환율:.2f}%", f"주문 ÷ 방문자 {전체['방문자수']:,}명"),
]
카드_html = "".join(
    f'<div class="card"><div class="label">{이름}</div><div class="big">{값}</div><div class="note">{설명}</div></div>'
    for 이름, 값, 설명 in 카드
)

최대 = 순위[0][1]
막대_html = "".join(
    f"""<div class="row" title="{c}: {v:,}원 (전체의 {v / 총매출 * 100:.1f}%)">
      <div class="name">{c}</div>
      <div class="track"><div class="bar" style="width:{v / 최대 * 100:.2f}%"></div></div>
      <div class="value"><b>{v / 총매출 * 100:.1f}%</b><span>{v / 100000000:.2f}억 원</span></div>
    </div>"""
    for c, v in 순위
)

월표_html = "".join(f"<tr><td>{l}</td><td>{v:,}원</td></tr>" for l, v in zip(월라벨, 월값))

html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2025 매출 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --page: #f4f3ef; --surface: #fcfcfb; --text: #0b0b0b; --text-2: #52514e;
    --border: #e6e5e1; --track: #efeeea; --series-1: #2a78d6; --hover: #f3f2ee;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --page: #121211; --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7;
      --border: #33322f; --track: #2a2a28; --series-1: #3987e5; --hover: #242422;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 24px 16px 40px; background: var(--page); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 1040px; margin: 0 auto; }}
  header h1 {{ font-size: 24px; margin: 0 0 4px; }}
  header p {{ color: var(--text-2); margin: 0 0 20px; font-size: 14px; }}
  .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
  .card, .panel {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; }}
  .card {{ padding: 16px; }}
  .label {{ font-size: 13px; color: var(--text-2); }}
  .big {{ font-size: 28px; font-weight: 700; margin: 6px 0 4px; font-variant-numeric: tabular-nums; }}
  .note {{ font-size: 12px; color: var(--text-2); }}
  .grid {{ display: grid; grid-template-columns: 3fr 2fr; gap: 16px; }}
  .panel {{ padding: 18px; }}
  .panel h2 {{ font-size: 16px; margin: 0 0 2px; }}
  .panel .sub {{ font-size: 12px; color: var(--text-2); margin: 0 0 14px; }}
  .chart-box {{ position: relative; height: 300px; }}
  details {{ margin-top: 12px; color: var(--text-2); font-size: 13px; }}
  table {{ border-collapse: collapse; margin-top: 6px; }}
  td {{ padding: 3px 16px 3px 0; border-bottom: 1px solid var(--border); }}
  td:last-child {{ text-align: right; color: var(--text); font-variant-numeric: tabular-nums; }}
  .row {{ display: grid; grid-template-columns: 84px 1fr 86px; align-items: center;
          gap: 10px; padding: 9px 6px; border-radius: 6px; }}
  .row:hover {{ background: var(--hover); }}
  .name {{ font-size: 14px; }}
  .track {{ height: 18px; background: var(--track); border-radius: 4px; }}
  .bar {{ height: 100%; background: var(--series-1); border-radius: 4px; }}
  .value {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .value b {{ font-size: 16px; display: block; }}
  .value span {{ font-size: 11px; color: var(--text-2); }}
  @media (max-width: 860px) {{
    .kpis {{ grid-template-columns: repeat(2, 1fr); }}
    .grid {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 420px) {{ .big {{ font-size: 22px; }} }}
</style>
</head>
<body>
<main>
  <header>
    <h1>2025년 매출 대시보드</h1>
    <p>기간 2025-01-01 ~ 2025-12-31 · 4개 채널(자사몰·스마트스토어·쿠팡·오프라인) 합계</p>
  </header>

  <section class="kpis">{카드_html}</section>

  <section class="grid">
    <div class="panel">
      <h2>월별 매출 추이</h2>
      <p class="sub">단위: 백만 원 · 점에 마우스를 올리면 정확한 금액</p>
      <div class="chart-box"><canvas id="trend"></canvas></div>
      <details><summary>숫자표로 보기</summary><table>{월표_html}</table></details>
    </div>
    <div class="panel">
      <h2>채널별 매출 비중</h2>
      <p class="sub">전체 매출 중 % · 큰 순서</p>
      {막대_html}
    </div>
  </section>
</main>
<script>
  const 월라벨 = {json.dumps(월라벨, ensure_ascii=False)};
  const 월값 = {json.dumps(월값)};
  const css = getComputedStyle(document.documentElement);
  const 색 = (이름) => css.getPropertyValue(이름).trim();

  new Chart(document.getElementById("trend"), {{
    type: "line",
    data: {{
      labels: 월라벨,
      datasets: [{{
        label: "월 매출", data: 월값,
        borderColor: 색("--series-1"), backgroundColor: 색("--series-1"),
        borderWidth: 2, pointRadius: 4, pointHoverRadius: 6, tension: 0,
      }}],
    }},
    options: {{
      maintainAspectRatio: false,
      interaction: {{ mode: "index", intersect: false }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ callbacks: {{ label: (c) => " " + c.parsed.y.toLocaleString("ko-KR") + "원" }} }},
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: 색("--text-2") }} }},
        y: {{
          beginAtZero: true, grid: {{ color: 색("--border") }},
          ticks: {{ color: 색("--text-2"), callback: (v) => (v / 1000000).toLocaleString("ko-KR") }},
        }},
      }},
    }},
  }});
</script>
</body>
</html>
"""

with open(결과_파일, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"대시보드 파일을 만들었어요 → {결과_파일}")
