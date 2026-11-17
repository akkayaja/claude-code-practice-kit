# 미션 3: 채널별 매출 비중 그래프를 만든다
#   - 1년 매출을 채널별로 더하고, 전체 매출 중 몇 %인지(비중) 계산한다
#   - 터미널에 큰 순서대로 숫자표를 보여 준다
#   - 가로 막대그래프가 들어간 HTML 파일(3_채널별비중.html)을 만든다 → 브라우저로 연다
# 왜 원그래프(파이)가 아니라 막대일까? 막대는 길이를 나란히 비교하니까
# 22.3%와 22.3%처럼 비슷한 값도 눈으로 구분하기 쉽다.
# 막대는 그래프 도구 없이 HTML 상자의 "길이"로 직접 그린다 → 인터넷 없이도 보인다.

import csv

CSV_파일 = "data/일별_채널별_매출_2025.csv"
결과_파일 = "3_채널별비중.html"

# 1) CSV 읽기
with open(CSV_파일, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 2) 채널별로 매출 더하기
채널별매출 = {}
for row in rows:
    채널 = row["채널"]
    채널별매출[채널] = 채널별매출.get(채널, 0) + int(row["매출액"])

총매출 = sum(채널별매출.values())

# 3) 매출이 큰 순서대로 줄 세우기
순위 = sorted(채널별매출.items(), key=lambda x: x[1], reverse=True)

# 4) 터미널에 숫자표 보여 주기
print("===== 채널별 매출 비중 (2025년 1년, 큰 순서) =====")
for 채널, 매출 in 순위:
    비중 = 매출 / 총매출 * 100
    print(f"{채널:<8} {매출:>13,}원  {비중:5.1f}%")
print(f"{'합계':<8} {총매출:>13,}원  100.0%")

# 5) HTML 막대 만들기 (1등 채널 막대를 꽉 찬 길이로 두고, 나머지는 비율대로)
최대 = 순위[0][1]
막대_줄 = []
for 채널, 매출 in 순위:
    비중 = 매출 / 총매출 * 100
    길이 = 매출 / 최대 * 100
    막대_줄.append(f"""
    <div class="row" title="{채널}: {매출:,}원 (전체의 {비중:.1f}%)">
      <div class="name">{채널}</div>
      <div class="track"><div class="bar" style="width:{길이:.2f}%"></div></div>
      <div class="value"><b>{비중:.1f}%</b><span>{매출 / 100000000:.2f}억 원</span></div>
    </div>""")

html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>채널별 매출 비중</title>
<style>
  :root {{
    --surface: #fcfcfb; --text: #0b0b0b; --text-2: #52514e;
    --track: #efeeea; --series-1: #2a78d6; --hover: #f3f2ee;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7;
      --track: #2a2a28; --series-1: #3987e5; --hover: #242422;
    }}
  }}
  body {{ margin: 0; padding: 24px 16px; background: var(--surface); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  p.sub {{ color: var(--text-2); margin: 0 0 24px; font-size: 14px; }}
  .row {{ display: grid; grid-template-columns: 96px 1fr 120px; align-items: center;
          gap: 12px; padding: 10px 8px; border-radius: 6px; }}
  .row:hover {{ background: var(--hover); }}
  .name {{ font-size: 15px; }}
  .track {{ height: 20px; background: var(--track); border-radius: 4px; }}
  .bar {{ height: 100%; background: var(--series-1); border-radius: 4px; }}
  .value {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .value b {{ font-size: 17px; display: block; }}
  .value span {{ font-size: 12px; color: var(--text-2); }}
  .total {{ margin-top: 16px; padding: 0 8px; color: var(--text-2); font-size: 14px; }}
  @media (max-width: 480px) {{
    .row {{ grid-template-columns: 1fr auto; }}
    .track {{ grid-column: 1 / -1; grid-row: 2; }}
  }}
</style>
</head>
<body>
<main>
  <h1>2025년 채널별 매출 비중</h1>
  <p class="sub">전체 매출 중 각 채널이 차지하는 % · 매출이 큰 순서 · 막대에 마우스를 올리면 원 단위 금액이 보여요</p>
  {"".join(막대_줄)}
  <p class="total">전체 매출 {총매출:,}원 = 100%</p>
</main>
</body>
</html>
"""

with open(결과_파일, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"그래프 파일을 만들었어요 → {결과_파일}")
