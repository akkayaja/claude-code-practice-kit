# 도전 미션: 데이터 점검 + 질문 A·B·C를 HTML 리포트 하나로 묶기
# 실행 위치: 06_데이터분석리포트 폴더 (.venv/bin/python 도전_공공데이터/5_리포트만들기.py)
# (2~4번 스크립트를 먼저 실행해서 도전_공공데이터/결과/ 폴더에 표와 그래프가 있어야 해요)
import base64
from datetime import date
import pandas as pd

결과폴더 = "도전_공공데이터/결과"

df = pd.read_csv("도전_공공데이터/전국_카페_점포수.csv", encoding="cp949")
df["기준월"] = pd.to_datetime(df["기준월"])


def 그림_넣기(파일):
    """PNG 그림을 글자로 바꿔 HTML 안에 직접 넣어요 → 파일 하나만 보내도 그림이 보여요."""
    with open(파일, "rb") as f:
        글자 = base64.b64encode(f.read()).decode()
    return f'<img src="data:image/png;base64,{글자}" alt="{파일}">'


def 표_넣기(파일):
    """CSV 표를 HTML 표로 바꿔요. 큰 정수에는 천 단위 쉼표를 넣어요."""
    표 = pd.read_csv(파일, encoding="utf-8-sig")
    for 열 in 표.columns:
        if 표[열].dtype.kind in "if" and 열 != "연도" and 표[열].abs().max() >= 1000:
            표[열] = 표[열].map(lambda v: "" if pd.isna(v) else f"{v:,.0f}")
    return 표.to_html(index=False, border=0, classes="표", na_rep="")


# ── 데이터 점검 결과 (파일에서 직접 계산) ──
전체달 = pd.date_range(df["기준월"].min(), df["기준월"].max(), freq="MS")
빠진달 = 전체달.difference(df["기준월"])
똑같은달 = df[df["업소수"].diff() == 0]["기준월"]
점검 = f"""
    <ul>
      <li><b>빠진 달:</b> 있어야 할 {len(전체달)}개월 중 <b>{len(빠진달)}개월</b>이 없어요
          ({', '.join(f'{d:%Y-%m}' for d in 빠진달)}). 빈칸 검사로는 0개라서, 날짜를 따로 확인해야 찾을 수 있었어요.</li>
      <li><b>전 달과 똑같은 값:</b> {', '.join(f'{d:%Y-%m}' for d in 똑같은달)}
          (전 달 숫자를 그대로 썼을 가능성 → 의심스러운 값으로 표시)</li>
      <li><b>튀는 값:</b> 2017~2018년에는 한 달에 +11.4%까지 올랐다가 바로 다음 달 내려가는 지그재그가 반복돼요
          → 한 달 단위 비교는 피하고, 같은 달끼리(12월) 비교하거나 안정적인 2019년만 사용했어요.</li>
    </ul>"""

질문들 = [
    {
        "제목": "질문 A. 해마다 카페는 얼마나 늘었고, 가장 많이 늘어난 해는?",
        "계산법": "매년 12월 기록끼리 비교해 전년 대비 증가 수와 증가율을 계산했어요.",
        "그림": 그림_넣기(f"{결과폴더}/질문A_연도별증가.png"),
        "표": 표_넣기(f"{결과폴더}/질문A_연도별증가_표.csv"),
        "주의": "2018년 증가의 약 63%가 9월(+5,884곳)과 12월(+5,989곳) 두 달에 몰려 있어요. 실제 급증인지 집계 기준 변화인지는 이 데이터만으로 알 수 없어요.",
        "결론": "12월 기준으로 전국 카페는 3년 동안 66,889곳 → 95,650곳으로 43.0% 늘었다. 2018년 증가(+18,727곳, +24.3%)가 "
                "앞선 두 해의 약 4배로 가장 컸지만, 그중 약 63%가 9월과 12월 두 달에 계단처럼 몰려 있어 실제 급증인지 "
                "집계 기준 변화인지 추가 확인이 필요하다.",
    },
    {
        "제목": "질문 B. 최근(2019년) 숫자는 믿을 만할까?",
        "계산법": "전 달 대비 변화율을 2017~2018년과 2019년으로 나눠 줄어든 달 수, 변화 범위, 들쭉날쭉 지수(표준편차)를 비교했어요.",
        "그림": 그림_넣기(f"{결과폴더}/질문B_2019안정성.png"),
        "표": 표_넣기(f"{결과폴더}/질문B_2019안정성_표.csv"),
        "주의": "2017~2018년 평균(+1,370곳/월)은 튀는 달 때문에 부풀려졌을 수 있어요. 2019년(+348곳/월)과 그대로 비교해 '증가가 느려졌다'고 단정하면 위험해요.",
        "결론": "2017~2018년은 한 달 변화가 −6.8%~+11.4%로 크게 오르내렸지만, 2019년은 0~0.7%로 줄어든 달 없이 꾸준히 늘었다"
                "(들쭉날쭉 지수 4.89 → 0.25, 약 20분의 1). 2019년 숫자는 흐름이 안정적이어서 추세를 보는 데 쓸 만하다.",
    },
    {
        "제목": "질문 C. 이 속도라면 전국 카페는 언제 10만 곳을 넘을까?",
        "계산법": "안정적인 2019년 1~9월 기록에 추세선(직선)을 그어 미래로 늘리고, 10만 곳에 닿는 달을 찾았어요.",
        "그림": 그림_넣기(f"{결과폴더}/질문C_10만곳예측.png"),
        "표": 표_넣기(f"{결과폴더}/질문C_10만곳예측_표.csv"),
        "주의": "'2019년 속도가 그대로 이어진다면'이라는 가정 위의 예측이에요. 점이 9개뿐이고, 증가 속도나 집계 기준이 바뀌면 결과도 달라져요.",
        "결론": "2019년의 안정적인 흐름(한 달 약 281곳 증가)이 그대로 이어진다면 전국 카페는 2020년 1월쯤 10만 곳을 넘는다. "
                "다만 이는 증가 속도와 집계 기준이 변하지 않는다는 가정 위의 4개월 앞 예측이라, 코로나19 같은 외부 변화가 생기면 달라질 수 있다.",
    },
]

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
<title>전국 카페 점포수 분석 리포트</title>
<style>
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", sans-serif; max-width: 960px;
         margin: 0 auto; padding: 24px 16px; color: #222; line-height: 1.6; background: #fafafa; }}
  h1 {{ margin-bottom: 4px; }}
  .부제 {{ color: #666; margin-top: 0; }}
  section, .요약 {{ background: #fff; border-radius: 12px; padding: 20px 24px; margin: 20px 0;
                   box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .점검 {{ border-left: 4px solid #f0ad4e; }}
  img {{ width: 100%; height: auto; border: 1px solid #eee; border-radius: 8px; }}
  .계산법 {{ color: #555; font-size: 0.95em; }}
  .결론 {{ background: #eef5ff; border-left: 4px solid #5b8def; padding: 12px 16px; margin: 16px 0; border-radius: 4px; }}
  .주의 {{ color: #a15c00; font-size: 0.9em; }}
  table.표 {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 0.9em; }}
  table.표 th, table.표 td {{ border-bottom: 1px solid #eee; padding: 6px 8px; text-align: right; }}
  table.표 th:first-child, table.표 td:first-child {{ text-align: left; }}
  summary {{ cursor: pointer; color: #5b8def; }}
  a {{ color: #2a5bd7; }}
  footer {{ color: #999; font-size: 0.85em; text-align: center; margin-top: 32px; }}
</style>
</head>
<body>
  <h1>☕ 전국 카페 점포수 분석 리포트 (실제 공공데이터)</h1>
  <p class="부제">출처: <a href="https://www.data.go.kr/data/15067614/fileData.do">공공데이터포털 — 소상공인시장진흥공단_전국 카페 점포수</a>
     (이용허락범위 제한 없음) · {len(df)}줄 · {df['기준월'].min():%Y년 %m월} ~ {df['기준월'].max():%Y년 %m월} 월별</p>

  <div class="요약">
    <h2>📌 한눈에 보기</h2>
    <ul>
      <li><b>증가</b>: 12월 기준 3년 동안 66,889곳 → 95,650곳(+43.0%). 2018년(+24.3%)이 가장 컸지만 두 달에 몰려 있어 확인이 필요하다.</li>
      <li><b>믿을 수 있는 구간</b>: 2017~2018년은 한 달 숫자가 크게 오르내리지만, 2019년은 꾸준하고 안정적이다.</li>
      <li><b>예측</b>: 2019년 속도(한 달 약 281곳)라면 2020년 1월쯤 10만 곳을 넘는다 — 가정이 붙은 예측이다.</li>
    </ul>
  </div>

  <section class="점검">
    <h2>🕵️ 분석 전에: 데이터 점검</h2>
    {점검}
  </section>
  {본문}
  <footer>만든 날짜: {date.today()} · Python(pandas, matplotlib, numpy)으로 자동 생성</footer>
</body>
</html>"""

저장 = f"{결과폴더}/공공데이터_카페_분석_리포트.html"
with open(저장, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 리포트 완성: {저장}")
print(f"   데이터 점검 1개 · 질문 {len(질문들)}개 · 그래프 {len(질문들)}개 · 결론 {len(질문들)}개를 담았어요.")
