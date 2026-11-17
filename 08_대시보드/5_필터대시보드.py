# 미션 5: 채널을 고르면 숫자가 바뀌는 필터를 넣는다 → 5_필터대시보드.html
#   - 위쪽에 [전체] [쿠팡] [자사몰] [오프라인] [스마트스토어] 버튼을 둔다
#   - 버튼을 누르면 KPI 카드 4장과 월별 그래프가 그 채널 숫자로 바뀐다
#   - 채널 비중 막대는 4개를 그대로 두고, 고른 채널만 파란색으로 강조한다
#
# 어떻게 바뀌게 하나?
#   파이썬이 "채널 × 월"별 합계(4 × 12 = 48칸)를 미리 계산해서 HTML 안에 넣어 둔다.
#   버튼을 누르면 브라우저 안의 자바스크립트가 그중 고른 채널 칸만 다시 더해서 화면을 고친다.
#   (파이썬 = 재료 손질, 자바스크립트 = 손님이 고른 메뉴로 그 자리에서 담아 주기)

import csv
import json

CSV_파일 = "data/일별_채널별_매출_2025.csv"
결과_파일 = "5_필터대시보드.html"

# 1) CSV 읽기
with open(CSV_파일, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 2) "채널 × 월"별로 주문수·매출액·방문자수 더하기
#    결과 모양: 데이터["쿠팡"]["2025-03"] = {"주문수": .., "매출액": .., "방문자수": ..}
데이터 = {}
for row in rows:
    채널 = row["채널"]
    월 = row["날짜"][:7]
    칸 = 데이터.setdefault(채널, {}).setdefault(월, {"주문수": 0, "매출액": 0, "방문자수": 0})
    for 항목 in ["주문수", "매출액", "방문자수"]:
        칸[항목] += int(row[항목])

월목록 = sorted({row["날짜"][:7] for row in rows})
# 채널은 1년 매출이 큰 순서로 (버튼 순서 = 막대 순서)
채널목록 = sorted(데이터, key=lambda c: sum(데이터[c][m]["매출액"] for m in 월목록), reverse=True)

# 3) 자바스크립트에 넘기기 쉬운 모양으로 바꾸기: 채널마다 12개월 숫자 목록
js_데이터 = {
    c: {
        "주문수": [데이터[c][m]["주문수"] for m in 월목록],
        "매출액": [데이터[c][m]["매출액"] for m in 월목록],
        "방문자수": [데이터[c][m]["방문자수"] for m in 월목록],
    }
    for c in 채널목록
}
월라벨 = [f"{int(m[5:])}월" for m in 월목록]


# 4) 터미널에 "버튼별로 화면에 나와야 할 숫자" 미리 보여 주기 (정답 확인용)
def kpi(채널들):
    주문 = sum(sum(js_데이터[c]["주문수"]) for c in 채널들)
    매출 = sum(sum(js_데이터[c]["매출액"]) for c in 채널들)
    방문 = sum(sum(js_데이터[c]["방문자수"]) for c in 채널들)
    월별 = [sum(js_데이터[c]["매출액"][i] for c in 채널들) for i in range(12)]
    최고 = max(range(12), key=lambda i: 월별[i])
    return 매출, 주문, 매출 / 주문, 주문 / 방문 * 100, 월라벨[최고], 월별[최고]


print("===== 버튼을 눌렀을 때 나와야 할 숫자 =====")
print(f"{'버튼':<8}{'총매출(원)':>16}{'주문수':>9}{'객단가':>9}{'전환율':>8}   최고 달")
for 이름, 채널들 in [("전체", 채널목록)] + [(c, [c]) for c in 채널목록]:
    매출, 주문, 객단, 전환, 최고월, 최고값 = kpi(채널들)
    print(f"{이름:<8}{매출:>16,}{주문:>9,}{객단:>9,.0f}{전환:>7.2f}%   {최고월} {최고값:,}원")

# 5) HTML 만들기
버튼_html = '<button data-ch="전체" aria-pressed="true">전체</button>' + "".join(
    f'<button data-ch="{c}" aria-pressed="false">{c}</button>' for c in 채널목록
)

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
    --border: #e6e5e1; --track: #efeeea; --series-1: #2a78d6; --muted-bar: #c9c8c2;
    --hover: #f3f2ee; --on-accent: #ffffff;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --page: #121211; --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7;
      --border: #33322f; --track: #2a2a28; --series-1: #3987e5; --muted-bar: #4a4945;
      --hover: #242422; --on-accent: #ffffff;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 24px 16px 40px; background: var(--page); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 1040px; margin: 0 auto; }}
  header h1 {{ font-size: 24px; margin: 0 0 4px; }}
  header p {{ color: var(--text-2); margin: 0 0 16px; font-size: 14px; }}
  .filter {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 16px; }}
  .filter span {{ font-size: 13px; color: var(--text-2); margin-right: 4px; }}
  .filter button {{ font: inherit; font-size: 14px; padding: 7px 14px; border-radius: 999px;
                    border: 1px solid var(--border); background: var(--surface); color: var(--text);
                    cursor: pointer; }}
  .filter button:hover {{ background: var(--hover); }}
  .filter button[aria-pressed="true"] {{ background: var(--series-1); border-color: var(--series-1);
                                         color: var(--on-accent); }}
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
  .row {{ display: grid; grid-template-columns: 84px 1fr 86px; align-items: center;
          gap: 10px; padding: 9px 6px; border-radius: 6px; }}
  .row:hover {{ background: var(--hover); }}
  .row.dim .name, .row.dim .value b {{ color: var(--text-2); font-weight: 400; }}
  .name {{ font-size: 14px; }}
  .track {{ height: 18px; background: var(--track); border-radius: 4px; }}
  .bar {{ height: 100%; background: var(--series-1); border-radius: 4px; }}
  .row.dim .bar {{ background: var(--muted-bar); }}
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
    <p>기간 2025-01-01 ~ 2025-12-31 · 지금 보는 범위: <b id="scope">4개 채널 전체</b></p>
  </header>

  <nav class="filter" aria-label="채널 필터"><span>채널</span>{버튼_html}</nav>

  <section class="kpis">
    <div class="card"><div class="label">총매출</div><div class="big" id="k-sales"></div><div class="note" id="k-sales-n"></div></div>
    <div class="card"><div class="label">총주문수</div><div class="big" id="k-orders"></div><div class="note">1년 동안 들어온 주문</div></div>
    <div class="card"><div class="label">객단가</div><div class="big" id="k-aov"></div><div class="note">총매출 ÷ 총주문수</div></div>
    <div class="card"><div class="label">전환율</div><div class="big" id="k-cvr"></div><div class="note" id="k-cvr-n"></div></div>
  </section>

  <section class="grid">
    <div class="panel">
      <h2 id="trend-title">월별 매출 추이</h2>
      <p class="sub">단위: 백만 원 · 점에 마우스를 올리면 정확한 금액</p>
      <div class="chart-box"><canvas id="trend"></canvas></div>
    </div>
    <div class="panel">
      <h2>채널별 매출 비중</h2>
      <p class="sub">전체 매출 중 % · 고른 채널은 파란색</p>
      <div id="bars"></div>
    </div>
  </section>
</main>
<script>
  // ---- 파이썬이 미리 계산해 넣어 둔 재료 ----
  const 월라벨 = {json.dumps(월라벨, ensure_ascii=False)};
  const 채널목록 = {json.dumps(채널목록, ensure_ascii=False)};
  const 데이터 = {json.dumps(js_데이터, ensure_ascii=False)};

  const 원 = (n) => Math.round(n).toLocaleString("ko-KR");
  const 합 = (배열) => 배열.reduce((a, b) => a + b, 0);
  const css = getComputedStyle(document.documentElement);
  const 색 = (이름) => css.getPropertyValue(이름).trim();

  // 고른 채널들의 12개월 숫자를 칸별로 더한다
  function 모으기(채널들, 항목) {{
    return 월라벨.map((_, i) => 합(채널들.map((c) => 데이터[c][항목][i])));
  }}

  // ---- 월별 꺾은선 그래프 (처음 한 번 만들고, 버튼 누를 때 숫자만 바꿈) ----
  const 그래프 = new Chart(document.getElementById("trend"), {{
    type: "line",
    data: {{ labels: 월라벨, datasets: [{{
      label: "월 매출", data: [],
      borderColor: 색("--series-1"), backgroundColor: 색("--series-1"),
      borderWidth: 2, pointRadius: 4, pointHoverRadius: 6, tension: 0,
    }}] }},
    options: {{
      maintainAspectRatio: false,
      interaction: {{ mode: "index", intersect: false }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{ callbacks: {{ label: (c) => " " + 원(c.parsed.y) + "원" }} }},
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: 색("--text-2") }} }},
        y: {{ beginAtZero: true, grid: {{ color: 색("--border") }},
              ticks: {{ color: 색("--text-2"), callback: (v) => (v / 1000000).toLocaleString("ko-KR") }} }},
      }},
    }},
  }});

  // ---- 채널 비중 막대 (4개는 늘 그대로, 고른 채널만 강조) ----
  const 채널매출 = Object.fromEntries(채널목록.map((c) => [c, 합(데이터[c].매출액)]));
  const 전체매출 = 합(Object.values(채널매출));
  const 최대 = Math.max(...Object.values(채널매출));

  function 막대그리기(선택) {{
    document.getElementById("bars").innerHTML = 채널목록.map((c) => {{
      const 비중 = (채널매출[c] / 전체매출 * 100).toFixed(1);
      const 흐리게 = 선택 !== "전체" && 선택 !== c ? " dim" : "";
      return `<div class="row${{흐리게}}" title="${{c}}: ${{원(채널매출[c])}}원 (전체의 ${{비중}}%)">
        <div class="name">${{c}}</div>
        <div class="track"><div class="bar" style="width:${{(채널매출[c] / 최대 * 100).toFixed(2)}}%"></div></div>
        <div class="value"><b>${{비중}}%</b><span>${{(채널매출[c] / 1e8).toFixed(2)}}억 원</span></div>
      </div>`;
    }}).join("");
  }}

  // ---- 버튼을 눌렀을 때 화면 전체를 고치는 함수 ----
  function 보여주기(선택) {{
    const 채널들 = 선택 === "전체" ? 채널목록 : [선택];
    const 월매출 = 모으기(채널들, "매출액");
    const 매출 = 합(월매출);
    const 주문 = 합(모으기(채널들, "주문수"));
    const 방문 = 합(모으기(채널들, "방문자수"));

    document.getElementById("k-sales").textContent = (매출 / 1e8).toFixed(2) + "억 원";
    document.getElementById("k-sales-n").textContent = 원(매출) + "원";
    document.getElementById("k-orders").textContent = 원(주문) + "건";
    document.getElementById("k-aov").textContent = 원(매출 / 주문) + "원";
    document.getElementById("k-cvr").textContent = (주문 / 방문 * 100).toFixed(2) + "%";
    document.getElementById("k-cvr-n").textContent = "주문 ÷ 방문자 " + 원(방문) + "명";

    const 이름 = 선택 === "전체" ? "4개 채널 전체" : 선택;
    document.getElementById("scope").textContent = 이름;
    document.getElementById("trend-title").textContent = "월별 매출 추이 · " + 이름;

    그래프.data.datasets[0].data = 월매출;
    그래프.update();
    막대그리기(선택);

    document.querySelectorAll(".filter button").forEach((b) =>
      b.setAttribute("aria-pressed", b.dataset.ch === 선택 ? "true" : "false"));
  }}

  document.querySelectorAll(".filter button").forEach((b) =>
    b.addEventListener("click", () => 보여주기(b.dataset.ch)));

  보여주기("전체");  // 처음 열면 전체 보기
</script>
</body>
</html>
"""

with open(결과_파일, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"필터 대시보드 파일을 만들었어요 → {결과_파일}")
