# 미션 2: 월별 매출 추이 그래프를 만든다
#   - CSV의 하루하루 매출을 "월"별로 모아서 더한다 (4개 채널 모두 합친 값)
#   - 터미널에 12개월 숫자표를 보여 준다
#   - 꺾은선 그래프가 들어간 HTML 파일(2_월별추이.html)을 만든다 → 브라우저로 연다
# 그래프는 Chart.js(웹에서 그래프를 그려 주는 무료 도구)를 인터넷에서 불러와 그린다.
# 추가 설치 없이 맥에 기본으로 있는 파이썬(python3)만으로 돌아간다.

import csv
import json

CSV_파일 = "data/일별_채널별_매출_2025.csv"
결과_파일 = "2_월별추이.html"

# 1) CSV 읽기
with open(CSV_파일, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 2) 월별로 매출 더하기  ("2025-03-15" → 앞 7글자 "2025-03"이 같은 줄끼리 더함)
월별매출 = {}
for row in rows:
    월 = row["날짜"][:7]
    월별매출[월] = 월별매출.get(월, 0) + int(row["매출액"])

월목록 = sorted(월별매출)                      # ["2025-01", ..., "2025-12"]
라벨 = [f"{int(m[5:])}월" for m in 월목록]     # ["1월", ..., "12월"]
값 = [월별매출[m] for m in 월목록]

# 3) 터미널에 숫자표 보여 주기
print("===== 월별 매출 (4개 채널 합계) =====")
for 이름, 매출 in zip(라벨, 값):
    print(f"{이름:>4} : {매출:>13,}원")
print(f"합계 : {sum(값):>13,}원")
최고 = max(range(12), key=lambda i: 값[i])
최저 = min(range(12), key=lambda i: 값[i])
print(f"가장 많이 판 달: {라벨[최고]} ({값[최고]:,}원)")
print(f"가장 적게 판 달: {라벨[최저]} ({값[최저]:,}원)")

# 4) 표(그래프 아래에 붙일 숫자표) 만들기
표_줄 = "\n".join(
    f"<tr><td>{이름}</td><td>{매출:,}원</td></tr>" for 이름, 매출 in zip(라벨, 값)
)

# 5) HTML 파일 만들기 (파이썬 숫자를 json으로 바꿔 자바스크립트에 넘김)
html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>월별 매출 추이</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --surface: #fcfcfb; --text: #0b0b0b; --text-2: #52514e;
    --grid: #e6e5e1; --series-1: #2a78d6;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7;
      --grid: #33322f; --series-1: #3987e5;
    }}
  }}
  body {{ margin: 0; padding: 24px 16px; background: var(--surface); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  p.sub {{ color: var(--text-2); margin: 0 0 20px; font-size: 14px; }}
  .chart-box {{ position: relative; height: 360px; }}
  details {{ margin-top: 20px; color: var(--text-2); }}
  table {{ border-collapse: collapse; margin-top: 8px; }}
  td {{ padding: 4px 16px 4px 0; border-bottom: 1px solid var(--grid); }}
  td:last-child {{ text-align: right; color: var(--text); font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
<main>
  <h1>2025년 월별 매출 추이</h1>
  <p class="sub">4개 채널(자사몰·스마트스토어·쿠팡·오프라인) 합계 · 단위: 백만 원 · 점에 마우스를 올리면 정확한 금액이 보여요</p>
  <div class="chart-box"><canvas id="chart"></canvas></div>
  <details>
    <summary>숫자표로 보기</summary>
    <table>{표_줄}</table>
  </details>
</main>
<script>
  const 라벨 = {json.dumps(라벨, ensure_ascii=False)};
  const 값 = {json.dumps(값)};
  const css = getComputedStyle(document.documentElement);
  const 색 = (이름) => css.getPropertyValue(이름).trim();

  new Chart(document.getElementById("chart"), {{
    type: "line",
    data: {{
      labels: 라벨,
      datasets: [{{
        label: "월 매출",
        data: 값,
        borderColor: 색("--series-1"),
        backgroundColor: 색("--series-1"),
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0,
      }}],
    }},
    options: {{
      maintainAspectRatio: false,
      interaction: {{ mode: "index", intersect: false }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{ label: (c) => " " + c.parsed.y.toLocaleString("ko-KR") + "원" }},
        }},
      }},
      scales: {{
        x: {{ grid: {{ display: false }}, ticks: {{ color: 색("--text-2") }} }},
        y: {{
          beginAtZero: true,
          grid: {{ color: 색("--grid") }},
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
print(f"그래프 파일을 만들었어요 → {결과_파일}")
