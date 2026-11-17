# 미션 5: 질문 3개의 표·그래프·결론을 HTML 리포트 하나로 묶기
# (2~4번 스크립트를 먼저 실행해서 결과/ 폴더에 표와 그래프가 있어야 해요)
import base64
from datetime import date
import pandas as pd

df = pd.read_csv("data/지역별_카페_현황.csv", encoding="utf-8-sig")


def 그림_넣기(파일):
    """PNG 그림을 글자로 바꿔 HTML 안에 직접 넣어요 → 파일 하나만 보내도 그림이 보여요."""
    with open(파일, "rb") as f:
        글자 = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{글자}" alt="{파일}">'


def 표_넣기(파일, 줄수=None):
    """결과 폴더의 CSV 표를 HTML 표로 바꿔요."""
    표 = pd.read_csv(파일, encoding="utf-8-sig")
    if 줄수:
        표 = 표.head(줄수)
    # 큰 정수에는 천 단위 쉼표 넣기 (연도 열은 그대로 둬요)
    for 열 in 표.columns:
        if 표[열].dtype.kind == "i" and 열 != "연도" and 표[열].max() >= 1000:
            표[열] = 표[열].map("{:,}".format)
    return 표.to_html(index=False, border=0, classes="표")


# ── 질문별 내용 (질문 / 표 / 그래프 / 한 줄 결론) ──
질문들 = [
    {
        "제목": "질문 1. 폐업률이 가장 높은 지역은?",
        "계산법": "분기마다 폐업 ÷ 영업중_점포수 × 100을 구하고, 지역별로 24개 분기의 평균을 냈어요.",
        "표": 표_넣기("결과/질문1_폐업률_표.csv"),
        "그림": 그림_넣기("결과/질문1_폐업률.png"),
        "주의": "가로축이 9%부터 시작해서 막대 길이 차이가 실제보다 크게 보여요. 1등과 꼴찌의 차이는 1.63%p예요.",
        "결론": "대구·울산·충남의 폐업률이 분기 평균 11.5% 이상으로 가장 높지만 세 곳의 차이는 0.1%p도 안 되고, "
                "전국이 10~11%대에 몰려 있어 지역 간 차이는 크지 않다. 강원만 9.98%로 유일하게 10% 아래다.",
    },
    {
        "제목": "질문 2. 폐업이 가장 몰리는 분기는 언제인가?",
        "계산법": "1~4분기별로 17개 지역 × 6년의 폐업을 모두 더하고, 해마다 1등 분기가 같은지도 확인했어요.",
        "표": 표_넣기("결과/질문2_분기별폐업_표.csv"),
        "그림": 그림_넣기("결과/질문2_분기별폐업.png"),
        "주의": "왼쪽 막대그래프는 세로축이 0부터 시작해서 실제 차이(최대 2.6%)를 그대로 보여 줘요.",
        "결론": "6년 합계로는 4분기 폐업이 가장 많지만(25.4%) 네 분기가 모두 약 25%로 비슷하고, 해마다 1등 분기도 바뀐다. "
                "폐업은 특정 분기에 몰리지 않으며, 계절보다 해가 갈수록 늘어나는 흐름이 더 뚜렷하다.",
    },
    {
        "제목": "질문 3. 카페가 가장 많이 늘어난 지역은?",
        "계산법": "2020년 1분기와 2025년 4분기의 점포수를 비교해 증가 수(곳)와 증가율(%) 두 가지로 계산했어요.",
        "표": 표_넣기("결과/질문3_증가지역_표.csv"),
        "그림": 그림_넣기("결과/질문3_증가지역.png"),
        "주의": "증가율은 출발점이 작은 지역일수록 크게 튀어요(강원·광주). 증가 수는 원래 큰 지역이 유리해요.",
        "결론": "늘어난 카페 수로는 부산(+9,581곳), 증가율로는 강원(+79.7%)이 1등으로, 기준에 따라 답이 달라진다. "
                "강원은 출발점이 작아 비율이 크게 나왔고, 두 기준 모두 상위권인 곳은 충북(5등·2등)이다.",
    },
]

# ── 데이터 개요 숫자 (파일에서 직접 계산) ──
개요 = (
    f"{len(df)}줄 · {df['시도'].nunique()}개 시도 · "
    f"{df['연도'].min()}~{df['연도'].max()}년 분기별 · 빈칸 {df.isna().sum().sum()}개"
)

본문 = ""
for q in 질문들:
    본문 += f"""
    <section>
      <h2>{q['제목']}</h2>
      <p class="계산법">📐 {q['계산법']}</p>
      {q['그림']}
      <div class="결론">💡 <b>그래서 무엇을 알 수 있나?</b><br>{q['결론']}</div>
      <p class="주의">⚠️ {q['주의']}</p>
      <details><summary>표 보기</summary>{q['표']}</details>
    </section>"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>지역별 카페 현황 분석 리포트</title>
<style>
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; max-width: 960px;
         margin: 0 auto; padding: 24px 16px; color: #222; line-height: 1.6; background: #fafafa; }}
  h1 {{ margin-bottom: 4px; }}
  .부제 {{ color: #666; margin-top: 0; }}
  section, .요약 {{ background: #fff; border-radius: 12px; padding: 20px 24px; margin: 20px 0;
                   box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  img {{ width: 100%; height: auto; border: 1px solid #eee; border-radius: 8px; }}
  .계산법 {{ color: #555; font-size: 0.95em; }}
  .결론 {{ background: #eef5ff; border-left: 4px solid #5b8def; padding: 12px 16px; margin: 16px 0;
          border-radius: 4px; }}
  .주의 {{ color: #a15c00; font-size: 0.9em; }}
  table.표 {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 0.9em; }}
  table.표 th, table.표 td {{ border-bottom: 1px solid #eee; padding: 6px 8px; text-align: right; }}
  table.표 th:first-child, table.표 td:first-child {{ text-align: left; }}
  summary {{ cursor: pointer; color: #5b8def; }}
  footer {{ color: #999; font-size: 0.85em; text-align: center; margin-top: 32px; }}
</style>
</head>
<body>
  <h1>☕ 지역별 카페 현황 분석 리포트</h1>
  <p class="부제">데이터: data/지역별_카페_현황.csv (가상 데이터) — {개요}</p>

  <div class="요약">
    <h2>📌 한눈에 보기</h2>
    <ul>
      <li><b>폐업률</b>: 대구·울산·충남이 가장 높지만(약 11.6%) 지역 간 차이는 작다. 강원만 9.98%로 확실히 낮다.</li>
      <li><b>폐업 시기</b>: 특정 분기에 몰리지 않는다(각 분기 약 25%). 계절보다 해마다 늘어나는 흐름이 뚜렷하다.</li>
      <li><b>증가 지역</b>: 증가 수는 부산(+9,581곳), 증가율은 강원(+79.7%)이 1등. 두 기준 모두 상위권은 충북이다.</li>
      <li><b>전국</b>: 카페가 6년 동안 208,680곳 → 291,757곳으로 39.8% 늘었다.</li>
    </ul>
  </div>
  {본문}
  <footer>만든 날짜: {date.today()} · Python(pandas, matplotlib)으로 자동 생성</footer>
</body>
</html>"""

with open("결과/카페_분석_리포트.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ 리포트 완성: 결과/카페_분석_리포트.html")
print(f"   질문 {len(질문들)}개 · 그래프 {len(질문들)}개 · 결론 {len(질문들)}개를 담았어요.")
