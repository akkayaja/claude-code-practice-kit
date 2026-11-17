# 도전 미션 2: 요일별 매출 패턴 히트맵 → 7_요일히트맵.html
#   히트맵 = 칸마다 색의 진하기로 숫자 크기를 보여 주는 표 (날씨 지도의 기온 색칠과 비슷)
#   - 세로: 전체 + 채널 4개,  가로: 월~일
#   - 칸 숫자: 그 요일의 "하루 평균 매출"
#   - 칸 색:   그 채널의 평소(7개 요일 평균)보다 몇 % 높은지/낮은지
#              파란색 = 평소보다 높음, 빨간색 = 평소보다 낮음, 회색 = 평소와 비슷
#
# 왜 "합계"가 아니라 "하루 평균"일까?
#   2025년은 수요일로 시작해서 수요일만 53번, 나머지 요일은 52번 있다.
#   합계로 비교하면 수요일이 하루치 더 많아 억울하게 유리해진다 → 평균으로 맞춘다.
# 왜 채널마다 "평소 대비 %"로 색칠할까?
#   쿠팡은 원래 하루 매출이 커서 금액 그대로 칠하면 쿠팡 줄만 온통 진해진다.
#   채널마다 자기 평소와 비교해야 "어느 요일에 잘 팔리나" 패턴이 보인다.

import csv
import datetime

CSV_파일 = "data/일별_채널별_매출_2025.csv"
결과_파일 = "7_요일히트맵.html"
요일이름 = ["월", "화", "수", "목", "금", "토", "일"]

# 1) CSV 읽기
with open(CSV_파일, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# 2) (채널, 요일)별로 매출 합계와 날짜 수 세기.  "전체"에도 같이 더한다
합계 = {}
날짜들 = {}
for row in rows:
    날짜 = datetime.date.fromisoformat(row["날짜"])
    요일 = 날짜.weekday()  # 월요일=0, 화요일=1, ... 일요일=6
    for 채널 in (row["채널"], "전체"):
        합계[(채널, 요일)] = 합계.get((채널, 요일), 0) + int(row["매출액"])
        날짜들.setdefault((채널, 요일), set()).add(날짜)

채널순서 = ["전체", "쿠팡", "자사몰", "오프라인", "스마트스토어"]

# 3) 하루 평균 매출과 "평소 대비 %" 계산
표 = {}
for 채널 in 채널순서:
    평균들 = [합계[(채널, w)] / len(날짜들[(채널, w)]) for w in range(7)]
    평소 = sum(평균들) / 7  # 7개 요일 평균의 평균 = 그 채널의 "평소 하루"
    표[채널] = [(평균, (평균 / 평소 - 1) * 100) for 평균 in 평균들]

# 4) 터미널에 보여 주기
print("요일별 날짜 수:", " ".join(f"{요일이름[w]}{len(날짜들[('전체', w)])}" for w in range(7)))
print()
print("===== 요일별 하루 평균 매출 (단위: 백만 원) / 평소 대비 % =====")
print("채널        " + "".join(f"{d:>13}" for d in 요일이름))
for 채널 in 채널순서:
    칸 = "".join(f"{평균 / 1e6:>6.2f}({차이:+5.1f}%)" for 평균, 차이 in 표[채널])
    print(f"{채널:<8}{칸}")
print()
for 채널 in 채널순서:
    최고 = max(range(7), key=lambda w: 표[채널][w][0])
    최저 = min(range(7), key=lambda w: 표[채널][w][0])
    print(f"{채널:<8} 가장 잘 팔리는 요일: {요일이름[최고]}요일 ({표[채널][최고][1]:+.1f}%)"
          f"  /  가장 덜 팔리는 요일: {요일이름[최저]}요일 ({표[채널][최저][1]:+.1f}%)")

# 5) HTML 만들기
#    색 진하기: 평소 대비 ±20%를 가장 진한 색으로 두고, 그 사이는 비율대로 섞는다
최대폭 = 20


def 칸_html(채널, w):
    평균, 차이 = 표[채널][w]
    세기 = min(abs(차이) / 최대폭, 1) * 100  # 0~100 (%)
    방향 = "var(--pos)" if 차이 >= 0 else "var(--neg)"
    글자 = "light" if 세기 >= 55 else ""
    부호 = "+" if 차이 >= 0 else ""
    return (
        f'<td class="{글자}" style="background: color-mix(in oklab, {방향} {세기:.0f}%, var(--mid))" '
        f'title="{채널} {요일이름[w]}요일: 하루 평균 {평균:,.0f}원 (평소 대비 {부호}{차이:.1f}%)">'
        f"<b>{부호}{차이:.1f}%</b><span>{평균 / 1e6:.2f}백만</span></td>"
    )


줄들 = "".join(
    f'<tr{" class=total" if 채널 == "전체" else ""}><th>{채널}</th>'
    + "".join(칸_html(채널, w) for w in range(7))
    + "</tr>"
    for 채널 in 채널순서
)

html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>요일별 매출 히트맵</title>
<style>
  :root {{
    --page: #f4f3ef; --surface: #fcfcfb; --text: #0b0b0b; --text-2: #52514e; --border: #e6e5e1;
    --pos: #1c5cab; --neg: #c0392b; --mid: #f0efec;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --page: #121211; --surface: #1a1a19; --text: #f0efec; --text-2: #c3c2b7; --border: #33322f;
      --pos: #3987e5; --neg: #e66767; --mid: #383835;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 24px 16px 40px; background: var(--page); color: var(--text);
         font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; }}
  main {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  p.sub {{ color: var(--text-2); margin: 0 0 18px; font-size: 14px; line-height: 1.5; }}
  .panel {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
            padding: 18px; overflow-x: auto; }}
  table {{ border-collapse: separate; border-spacing: 2px; width: 100%; min-width: 560px; }}
  thead th {{ font-size: 13px; color: var(--text-2); font-weight: 400; padding: 4px 0 8px; }}
  tbody th {{ text-align: left; font-size: 14px; font-weight: 400; padding-right: 10px; white-space: nowrap; }}
  tr.total th {{ font-weight: 700; }}
  td {{ text-align: center; padding: 12px 4px; border-radius: 4px; color: var(--text);
        font-variant-numeric: tabular-nums; cursor: default; }}
  td b {{ display: block; font-size: 15px; }}
  td span {{ display: block; font-size: 11px; opacity: .8; margin-top: 2px; }}
  td.light {{ color: #ffffff; }}
  tr.total td {{ padding: 16px 4px; }}
  .legend {{ display: flex; align-items: center; gap: 8px; margin-top: 14px; font-size: 12px; color: var(--text-2); }}
  .legend .ramp {{ width: 220px; height: 12px; border-radius: 3px;
                   background: linear-gradient(90deg, var(--neg), var(--mid), var(--pos)); }}
</style>
</head>
<body>
<main>
  <h1>2025년 요일별 매출 패턴</h1>
  <p class="sub">칸의 큰 숫자 = 그 채널의 <b>평소 하루(7개 요일 평균) 대비</b> 몇 % 높은지·낮은지 · 작은 숫자 = 그 요일의 하루 평균 매출(백만 원)<br>
  파란색일수록 평소보다 잘 팔리고, 빨간색일수록 덜 팔려요 · 칸에 마우스를 올리면 원 단위 금액</p>
  <div class="panel">
    <table>
      <thead><tr><th></th>{"".join(f"<th>{d}</th>" for d in 요일이름)}</tr></thead>
      <tbody>{줄들}</tbody>
    </table>
    <div class="legend"><span>평소보다 낮음 −{최대폭}%</span><div class="ramp"></div><span>+{최대폭}% 평소보다 높음</span></div>
  </div>
</main>
</body>
</html>
"""

with open(결과_파일, "w", encoding="utf-8") as f:
    f.write(html)

print()
print(f"히트맵 파일을 만들었어요 → {결과_파일}")
