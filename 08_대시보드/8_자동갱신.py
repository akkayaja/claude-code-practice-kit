# 도전 미션 3: CSV 파일만 바꾸면 대시보드가 자동으로 새로 만들어지게 한다
#   → 8_자동대시보드.html
#
# 지금까지(1~7번) 스크립트는 "2025년", "12월", "12개월"처럼 이번 CSV에 맞춘 값을
# 코드 안에 적어 두었다. 그래서 다른 CSV를 넣으면 제목이나 계산이 틀어진다.
# 이 스크립트는 그런 값을 하나도 적어 두지 않고 CSV를 읽어서 스스로 알아낸다.
#   - 어떤 CSV?  → data 폴더 안에서 "가장 최근에 넣은(수정된)" CSV 파일
#   - 기간       → CSV의 첫 날짜 ~ 마지막 날짜
#   - 월 목록    → CSV에 있는 달만 (6개월치면 6칸, 2년치면 24칸)
#   - 채널 목록  → CSV에 있는 채널만 (새 채널이 생기면 버튼도 자동으로 생김)
#   - 최근 달    → CSV의 마지막 달
# 만든 뒤에는 브라우저로 자동으로 열어 준다.
# 화면 구성은 도전 1(6번)과 같다: 채널 필터 + KPI 카드 + 월별 추이 + 채널 비중 + 전월 대비 표

import csv
import glob
import json
import os
import pathlib
import subprocess
import sys
import webbrowser

DATA_폴더 = "data"
결과_파일 = "8_자동대시보드.html"


# ---------------------------------------------------------------
# 1) data 폴더에서 가장 최근에 넣은 CSV 찾기
# ---------------------------------------------------------------
def 최신_csv_찾기():
    후보 = glob.glob(os.path.join(DATA_폴더, "*.csv"))
    if not 후보:
        sys.exit(f"'{DATA_폴더}' 폴더에 CSV 파일이 없어요.")
    return max(후보, key=os.path.getmtime)  # 수정 시각이 가장 늦은 파일


# ---------------------------------------------------------------
# 2) CSV 읽어서 "채널 × 월" 합계 만들기
# ---------------------------------------------------------------
def 읽고_모으기(csv_경로):
    with open(csv_경로, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("CSV에 데이터 줄이 없어요.")

    데이터 = {}
    for row in rows:
        월 = row["날짜"][:7]
        칸 = 데이터.setdefault(row["채널"], {}).setdefault(월, {"주문수": 0, "매출액": 0, "방문자수": 0})
        for 항목 in ["주문수", "매출액", "방문자수"]:
            칸[항목] += int(row[항목])

    날짜목록 = sorted(row["날짜"] for row in rows)
    월목록 = sorted({row["날짜"][:7] for row in rows})
    # 어떤 채널에 어떤 달 데이터가 없으면 0으로 채운다
    for 채널 in 데이터:
        for 월 in 월목록:
            데이터[채널].setdefault(월, {"주문수": 0, "매출액": 0, "방문자수": 0})
    # 채널은 매출이 큰 순서로
    채널목록 = sorted(데이터, key=lambda c: sum(데이터[c][m]["매출액"] for m in 월목록), reverse=True)
    return rows, 데이터, 날짜목록[0], 날짜목록[-1], 월목록, 채널목록


def 월라벨_만들기(월목록):
    여러해 = len({m[:4] for m in 월목록}) > 1
    # 한 해 안이면 "3월", 여러 해에 걸치면 "25년 3월"
    return [f"{m[2:4]}년 {int(m[5:])}월" if 여러해 else f"{int(m[5:])}월" for m in 월목록]


# ---------------------------------------------------------------
# 3) 실행
# ---------------------------------------------------------------
csv_경로 = 최신_csv_찾기()
rows, 데이터, 시작일, 종료일, 월목록, 채널목록 = 읽고_모으기(csv_경로)
월라벨 = 월라벨_만들기(월목록)
개월수 = len(월목록)

js_데이터 = {
    c: {항목: [데이터[c][m][항목] for m in 월목록] for 항목 in ["주문수", "매출액", "방문자수"]}
    for c in 채널목록
}

# 터미널에 "무엇을 읽어서 무엇을 알아냈는지" 보여 주기
총매출 = sum(sum(v["매출액"]) for v in js_데이터.values())
총주문 = sum(sum(v["주문수"]) for v in js_데이터.values())
총방문 = sum(sum(v["방문자수"]) for v in js_데이터.values())
전체월별 = [sum(js_데이터[c]["매출액"][i] for c in 채널목록) for i in range(개월수)]

print(f"읽은 파일 : {csv_경로}")
print(f"데이터    : {len(rows):,}줄")
print(f"기간      : {시작일} ~ {종료일} ({개월수}개월)")
print(f"채널      : {len(채널목록)}개 → {', '.join(채널목록)}")
print()
print("===== 전체 KPI =====")
print(f"총매출 {총매출:,}원 / 총주문수 {총주문:,}건 / 객단가 {총매출 / 총주문:,.0f}원 / 전환율 {총주문 / 총방문 * 100:.2f}%")
if 개월수 >= 2:
    끝 = 개월수 - 1
    증감 = (전체월별[끝] - 전체월별[끝 - 1]) / 전체월별[끝 - 1] * 100
    부호 = "▲ +" if 증감 >= 0 else "▼ "
    print(f"최근 달 {월라벨[끝]} {전체월별[끝]:,}원 · 전월({월라벨[끝 - 1]}) 대비 {부호}{증감:.1f}%")

# 제목에 쓸 기간 글자: 한 해 안이면 "2025년", 아니면 "2025-01 ~ 2026-06"
연도들 = sorted({m[:4] for m in 월목록})
제목기간 = f"{연도들[0]}년" if len(연도들) == 1 else f"{월목록[0]} ~ {월목록[-1]}"

버튼_html = '<button data-ch="전체" aria-pressed="true">전체</button>' + "".join(
    f'<button data-ch="{c}" aria-pressed="false">{c}</button>' for c in 채널목록
)

# ---------------------------------------------------------------
# 4) HTML 만들기 (도전 1의 화면과 같음. 고정된 값 대신 위에서 알아낸 값을 넣음)
# ---------------------------------------------------------------
html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{제목기간} 매출 대시보드</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --page: #f4f3ef; --surface: #fcfcfb; --text: #0b0b0b; --text-2: #52514e;
    --border: #e6e5e1; --track: #efeeea; --series-1: #2a78d6; --muted-bar: #c9c8c2;
    --hover: #f3f2ee; --on-accent: #ffffff; --up: #0ca30c; --down: #d03b3b;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --page: #121211; --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7;
      --border: #33322f; --track: #2a2a28; --series-1: #3987e5; --muted-bar: #4a4945;
      --hover: #242422;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 24px 16px 40px; background: var(--page); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 1040px; margin: 0 auto; }}
  header h1 {{ font-size: 24px; margin: 0 0 4px; }}
  header p {{ color: var(--text-2); margin: 0 0 16px; font-size: 14px; line-height: 1.5; }}
  .filter {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 16px; }}
  .filter span {{ font-size: 13px; color: var(--text-2); margin-right: 4px; }}
  .filter button {{ font: inherit; font-size: 14px; padding: 7px 14px; border-radius: 999px;
                    border: 1px solid var(--border); background: var(--surface); color: var(--text); cursor: pointer; }}
  .filter button:hover {{ background: var(--hover); }}
  .filter button[aria-pressed="true"] {{ background: var(--series-1); border-color: var(--series-1); color: var(--on-accent); }}
  .headline {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
               padding: 14px 18px; margin-bottom: 16px; font-size: 15px; }}
  .chg {{ font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .chg i {{ font-style: normal; margin-right: 3px; }}
  .chg.up i {{ color: var(--up); }}
  .chg.down i {{ color: var(--down); }}
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
  .row {{ display: grid; grid-template-columns: 84px 1fr 86px; align-items: center; gap: 10px; padding: 9px 6px; border-radius: 6px; }}
  .row:hover {{ background: var(--hover); }}
  .row.dim .name, .row.dim .value b {{ color: var(--text-2); font-weight: 400; }}
  .name {{ font-size: 14px; }}
  .track {{ height: 18px; background: var(--track); border-radius: 4px; }}
  .bar {{ height: 100%; background: var(--series-1); border-radius: 4px; }}
  .row.dim .bar {{ background: var(--muted-bar); }}
  .value {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .value b {{ font-size: 16px; display: block; }}
  .value span {{ font-size: 11px; color: var(--text-2); }}
  .mom {{ margin-top: 16px; }}
  .mom table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  .mom th {{ text-align: right; font-weight: 400; color: var(--text-2); font-size: 12px; padding: 6px 8px; border-bottom: 1px solid var(--border); }}
  .mom th:first-child, .mom td:first-child {{ text-align: left; }}
  .mom td {{ text-align: right; padding: 7px 8px; border-bottom: 1px solid var(--border); font-variant-numeric: tabular-nums; }}
  .mom tr.big-move td {{ background: var(--hover); }}
  .mom .none {{ color: var(--text-2); font-size: 12px; }}
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
    <h1>{제목기간} 매출 대시보드</h1>
    <p>기간 {시작일} ~ {종료일} ({개월수}개월) · 지금 보는 범위: <b id="scope"></b><br>
    데이터 파일: {os.path.basename(csv_경로)}</p>
  </header>

  <nav class="filter" aria-label="채널 필터"><span>채널</span>{버튼_html}</nav>
  <div class="headline" id="headline"></div>

  <section class="kpis">
    <div class="card"><div class="label">총매출</div><div class="big" id="k-sales"></div><div class="note" id="k-sales-n"></div></div>
    <div class="card"><div class="label">총주문수</div><div class="big" id="k-orders"></div><div class="note">기간 동안 들어온 주문</div></div>
    <div class="card"><div class="label">객단가</div><div class="big" id="k-aov"></div><div class="note">총매출 ÷ 총주문수</div></div>
    <div class="card"><div class="label">전환율</div><div class="big" id="k-cvr"></div><div class="note" id="k-cvr-n"></div></div>
  </section>

  <section class="grid">
    <div class="panel">
      <h2 id="trend-title">월별 매출 추이</h2>
      <p class="sub">단위: 백만 원 · 점에 마우스를 올리면 금액과 전월 대비</p>
      <div class="chart-box"><canvas id="trend"></canvas></div>
    </div>
    <div class="panel">
      <h2>채널별 매출 비중</h2>
      <p class="sub">전체 매출 중 % · 고른 채널은 파란색</p>
      <div id="bars"></div>
    </div>
  </section>

  <section class="panel mom">
    <h2 id="mom-title">월별 전월 대비 증감률</h2>
    <p class="sub">(이번 달 - 지난달) ÷ 지난달 × 100 · 10% 넘게 움직인 달은 배경 강조</p>
    <table>
      <thead><tr><th>월</th><th>매출</th><th>전월 대비</th></tr></thead>
      <tbody id="mom-body"></tbody>
    </table>
  </section>
</main>
<script>
  const 월라벨 = {json.dumps(월라벨, ensure_ascii=False)};
  const 채널목록 = {json.dumps(채널목록, ensure_ascii=False)};
  const 데이터 = {json.dumps(js_데이터, ensure_ascii=False)};

  const 원 = (n) => Math.round(n).toLocaleString("ko-KR");
  const 합 = (배열) => 배열.reduce((a, b) => a + b, 0);
  const css = getComputedStyle(document.documentElement);
  const 색 = (이름) => css.getPropertyValue(이름).trim();
  const 모으기 = (채널들, 항목) => 월라벨.map((_, i) => 합(채널들.map((c) => 데이터[c][항목][i])));
  const 증감률 = (월매출) => 월매출.map((v, i) => (i === 0 || 월매출[i - 1] === 0 ? null : (v - 월매출[i - 1]) / 월매출[i - 1] * 100));
  function 증감표시(p) {{
    if (p === null) return '<span class="none">비교할 전달 없음</span>';
    const 위로 = p >= 0;
    return `<span class="chg ${{위로 ? "up" : "down"}}"><i>${{위로 ? "▲" : "▼"}}</i>${{위로 ? "+" : ""}}${{p.toFixed(1)}}%</span>`;
  }}
  let 지금증감 = [];

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
        tooltip: {{ callbacks: {{
          label: (c) => " " + 원(c.parsed.y) + "원",
          afterLabel: (c) => {{
            const p = 지금증감[c.dataIndex];
            return p === null ? " 전월 대비: 비교할 전달 없음" : " 전월 대비: " + (p >= 0 ? "▲ +" : "▼ ") + p.toFixed(1) + "%";
          }},
        }} }},
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: 색("--text-2") }} }},
        y: {{ beginAtZero: true, grid: {{ color: 색("--border") }},
              ticks: {{ color: 색("--text-2"), callback: (v) => (v / 1000000).toLocaleString("ko-KR") }} }},
      }},
    }},
  }});

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

  function 보여주기(선택) {{
    const 채널들 = 선택 === "전체" ? 채널목록 : [선택];
    const 월매출 = 모으기(채널들, "매출액");
    const 매출 = 합(월매출);
    const 주문 = 합(모으기(채널들, "주문수"));
    const 방문 = 합(모으기(채널들, "방문자수"));
    const 이름 = 선택 === "전체" ? `${{채널목록.length}}개 채널 전체` : 선택;

    document.getElementById("k-sales").textContent = (매출 / 1e8).toFixed(2) + "억 원";
    document.getElementById("k-sales-n").textContent = 원(매출) + "원";
    document.getElementById("k-orders").textContent = 원(주문) + "건";
    document.getElementById("k-aov").textContent = 원(매출 / 주문) + "원";
    document.getElementById("k-cvr").textContent = (주문 / 방문 * 100).toFixed(2) + "%";
    document.getElementById("k-cvr-n").textContent = "주문 ÷ 방문자 " + 원(방문) + "명";
    document.getElementById("scope").textContent = 이름;
    document.getElementById("trend-title").textContent = "월별 매출 추이 · " + 이름;

    지금증감 = 증감률(월매출);
    const 끝 = 월매출.length - 1;
    document.getElementById("headline").innerHTML = 끝 < 1
      ? `최근 달 <b>${{월라벨[끝]}}</b> 매출 <b>${{원(월매출[끝])}}원</b> · 비교할 전달이 없어요`
      : `최근 달 <b>${{월라벨[끝]}}</b> 매출 <b>${{원(월매출[끝])}}원</b> · 전월(${{월라벨[끝 - 1]}} ${{원(월매출[끝 - 1])}}원) 대비 ${{증감표시(지금증감[끝])}}`;
    document.getElementById("mom-title").textContent = "월별 전월 대비 증감률 · " + 이름;
    document.getElementById("mom-body").innerHTML = 월라벨.map((m, i) => {{
      const 강조 = 지금증감[i] !== null && Math.abs(지금증감[i]) >= 10 ? ' class="big-move"' : "";
      return `<tr${{강조}}><td>${{m}}</td><td>${{원(월매출[i])}}원</td><td>${{증감표시(지금증감[i])}}</td></tr>`;
    }}).join("");

    그래프.data.datasets[0].data = 월매출;
    그래프.update();
    막대그리기(선택);
    document.querySelectorAll(".filter button").forEach((b) =>
      b.setAttribute("aria-pressed", b.dataset.ch === 선택 ? "true" : "false"));
  }}

  document.querySelectorAll(".filter button").forEach((b) => b.addEventListener("click", () => 보여주기(b.dataset.ch)));
  보여주기("전체");
</script>
</body>
</html>
"""

with open(결과_파일, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"대시보드를 새로 만들었어요 → {결과_파일}")

# 5) 브라우저로 자동으로 열기 (끝에 --no-open 을 붙이면 열지 않음)
#    맥에서는 터미널의 open 명령을 그대로 부른다 (한글·띄어쓰기 경로도 문제없음)
if "--no-open" not in sys.argv:
    if sys.platform == "darwin":
        성공 = subprocess.run(["open", 결과_파일]).returncode == 0
    else:
        성공 = webbrowser.open(pathlib.Path(결과_파일).resolve().as_uri())
    print("브라우저에서 열었어요." if 성공 else f"자동으로 못 열었어요. 직접 열어 주세요: open {결과_파일}")
