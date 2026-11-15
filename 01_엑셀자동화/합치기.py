# 미션 2: data 폴더의 월별 매출 엑셀 6개를 하나로 합치는 스크립트
# 실행 방법(터미널):  .venv/bin/python 합치기.py

from pathlib import Path  # 파일·폴더 경로를 다루는 도구
import pandas as pd       # 표(엑셀) 데이터를 다루는 도구

# 1) 이 스크립트가 있는 폴더를 기준으로 경로를 정해요
#    (그래서 어느 위치에서 실행해도 같은 파일을 찾아요)
기준폴더 = Path(__file__).parent
데이터폴더 = 기준폴더 / "data"
결과폴더 = 기준폴더 / "결과"
결과폴더.mkdir(exist_ok=True)  # '결과' 폴더가 없으면 새로 만들어요

# 2) data 폴더에서 '매출_'로 시작하는 엑셀 파일을 모두 찾아 이름순으로 정렬해요
엑셀파일들 = sorted(데이터폴더.glob("매출_*.xlsx"))
print(f"찾은 파일: {len(엑셀파일들)}개")

# 3) 파일을 하나씩 읽어서 목록에 담아요
표목록 = []
for 파일 in 엑셀파일들:
    표 = pd.read_excel(파일)  # 엑셀 파일 하나를 표로 읽기
    print(f"  - {파일.name}: {len(표)}줄")
    표목록.append(표)

# 4) 목록에 담긴 표들을 위아래로 이어 붙여요
#    ignore_index=True: 줄 번호를 0부터 새로 매겨요
합친표 = pd.concat(표목록, ignore_index=True)
print(f"합친 결과: {len(합친표)}줄")

# ── 미션 3: 지점명 오타와 날짜 형식 통일 ──────────────────────

# 5) 지점명의 띄어쓰기를 모두 없애요
#    예: '광주상무 점' → '광주상무점'
#    .str.replace(" ", "") : 글자 속의 빈칸(" ")을 없는 것("")으로 바꾸기
합친표["지점"] = 합친표["지점"].str.replace(" ", "")
print("지점 종류:", 합친표["지점"].dropna().unique().tolist())

# 6) 날짜를 하나의 형식으로 통일해요
#    - 점(.)으로 적힌 '2026.01.15' 같은 글자를 '2026-01-15'로 바꾸고
#    - pd.to_datetime 으로 모든 값을 '진짜 날짜'로 변환해요
#    (글자인 값만 바꾸고, 이미 날짜인 값은 그대로 둬요)
합친표["일자"] = 합친표["일자"].apply(
    lambda 값: 값.replace(".", "-") if isinstance(값, str) else 값
)
합친표["일자"] = pd.to_datetime(합친표["일자"])
#    .dt.date : '날짜+시간'에서 시간을 떼고 '날짜'만 남겨요 (00:00:00 없애기)
합친표["일자"] = 합친표["일자"].dt.date

# ── 미션 4: 빈 행과 중복 행 지우기 ─────────────────────────
# (오타·날짜를 먼저 통일한 다음에 해야 '강남 점'과 '강남점' 같은 숨은 중복까지 잡혀요)

# 6-1) 빈 행 지우기
#      how="all" : 모든 칸이 비어 있는 줄만 지워요 (한 칸이라도 값이 있으면 남겨요)
지우기전 = len(합친표)
합친표 = 합친표.dropna(how="all")
print(f"빈 행 제거: {지우기전}줄 → {len(합친표)}줄 ({지우기전 - len(합친표)}줄 삭제)")

# 6-2) 중복 행 지우기
#      drop_duplicates() : 모든 칸이 똑같은 줄을 찾아서, 맨 처음 것 하나만 남기고 지워요
#      먼저 지워질 줄을 화면에 보여 줘서 눈으로 확인할 수 있게 해요
#      duplicated() : 앞에 똑같은 줄이 이미 있으면 True(중복), 아니면 False
중복줄 = 합친표[합친표.duplicated()]
print(f"지워질 중복 행 {len(중복줄)}줄:")
print(중복줄.to_string())
지우기전 = len(합친표)
합친표 = 합친표.drop_duplicates()
print(f"중복 제거: {지우기전}줄 → {len(합친표)}줄 ({지우기전 - len(합친표)}줄 삭제)")

# 7) 결과를 엑셀로 저장해요 (index=False: 줄 번호 열은 저장하지 않아요)
#    date_format="YYYY-MM-DD" : 엑셀에서 날짜가 '2026-01-15' 모양으로 보이게 해요
저장경로 = 결과폴더 / "6개취합.xlsx"
with pd.ExcelWriter(저장경로, date_format="YYYY-MM-DD") as 작성기:
    합친표.to_excel(작성기, index=False)
print(f"저장 완료: {저장경로}")

# ── 미션 5: 지점별·월별 매출 합계표 만들기 ───────────────────

# 8) 날짜에서 '월'만 뽑아 새 열을 만들어요 (예: 2026-03-05 → '3월')
합친표["월"] = pd.to_datetime(합친표["일자"]).dt.month.astype(str) + "월"

# 9) 가로세로 표(교차표)를 만들어요
#    pivot_table = 엑셀의 '피벗 테이블'과 같은 기능이에요
#      index="지점"      : 세로(줄)에 지점을 놓고
#      columns="월"      : 가로(열)에 월을 놓고
#      values="매출액"   : 칸 안에는 매출액을
#      aggfunc="sum"     : 더해서(합계) 넣어요
#      margins=True      : 맨 아래 줄과 맨 오른쪽 열에 '합계'를 추가해요
월순서 = [f"{m}월" for m in range(1, 13)]
요약표 = pd.pivot_table(
    합친표,
    index="지점",
    columns="월",
    values="매출액",
    aggfunc="sum",
    margins=True,
    margins_name="합계",
)
#    월 열이 '10월, 1월, 2월…'처럼 글자 순서로 섞이지 않도록 1월→12월 순서로 정렬해요
있는월 = [m for m in 월순서 if m in 요약표.columns]
요약표 = 요약표[있는월 + ["합계"]]

# 10) 화면에 보여 주고, 결과/요약.xlsx로 저장해요
print("\n[지점별·월별 매출 합계]")
print(요약표.to_string())

# 검증: 요약표의 '총합계'가 원래 매출액 전체 합과 같은지 확인해요
print(f"\n검증 - 원본 매출액 전체 합: {합친표['매출액'].sum():,.0f}원")
print(f"검증 - 요약표 총합계:       {요약표.loc['합계', '합계']:,.0f}원")

# ── 도전 미션 A: 지점별 상품 매출 TOP 3 ─────────────────────

# 11) 지점별·상품별 매출액 합계를 구해요 (6개월 전체)
#     groupby(["지점", "상품"]) : 지점과 상품이 같은 줄끼리 묶어서
#     ["매출액"].sum()          : 매출액을 더해요
상품별매출 = 합친표.groupby(["지점", "상품"])["매출액"].sum().reset_index()

# 12) 지점마다 매출액이 큰 상품 3개씩 뽑아요
#     nlargest(3, "매출액") : 매출액이 가장 큰 3줄을 골라요
TOP3목록 = {}  # {지점이름: TOP3 표} 형태로 담아 둘 상자
print("\n[지점별 상품 매출 TOP 3 (6개월 전체)]")
for 지점, 지점표 in 상품별매출.groupby("지점"):
    top3 = 지점표.nlargest(3, "매출액").reset_index(drop=True)
    top3.insert(0, "순위", [1, 2, 3])  # 맨 앞에 '순위' 열을 넣어요
    top3 = top3[["순위", "상품", "매출액"]]  # 시트에는 지점 이름이 있으니 지점 열은 빼요
    TOP3목록[지점] = top3

    # 검증: 1등과 4등을 비교해서 순위가 제대로 갈렸는지 보여 줘요
    #       (3등과 4등이 같으면 '공동 3위'라서 누구를 넣을지 정해야 해요)
    전체순위 = 지점표.sort_values("매출액", ascending=False)
    #       ※ 변수 이름은 숫자로 시작할 수 없어서 '4등매출'이 아니라 '네번째매출'로 지었어요
    네번째매출 = 전체순위["매출액"].iloc[3] if len(전체순위) > 3 else 0
    print(f"\n■ {지점} (상품 {len(지점표)}종 중 TOP 3)")
    print(top3.to_string(index=False))
    print(f"  └ 참고: 4위 매출액 {네번째매출:,.0f}원 (3위보다 작아야 정상)")

# 13) 결과/요약.xlsx 하나에 시트 여러 개로 저장해요
#     ExcelWriter를 열어 둔 채로 to_excel을 여러 번 하면 시트가 하나씩 추가돼요
요약경로 = 결과폴더 / "요약.xlsx"
with pd.ExcelWriter(요약경로) as 작성기:
    요약표.to_excel(작성기, sheet_name="지점별월별합계")  # 첫 번째 시트
    for 지점, top3 in TOP3목록.items():
        top3.to_excel(작성기, sheet_name=f"{지점}_TOP3", index=False)  # 지점마다 시트 하나

    # ── 도전 미션 B: 지점별 6개월 총매출 막대 차트 ──────────────
    # 14) 엑셀 안에 '진짜 엑셀 차트'를 그려요 (openpyxl 도구 사용)
    #     차트는 숫자를 복사해 그리는 게 아니라 '표의 칸을 가리켜서' 그려요
    #     → 그래서 표 숫자가 바뀌면 차트도 같이 바뀌어요
    from openpyxl.chart import BarChart, Reference

    시트 = 작성기.sheets["지점별월별합계"]
    지점수 = len(요약표) - 1             # 맨 아래 '합계' 줄은 차트에서 빼요
    합계열번호 = len(요약표.columns) + 1  # 맨 앞 '지점' 열이 1번이라 +1 해요

    차트 = BarChart()
    차트.title = "2026년 상반기 지점별 매출"
    차트.y_axis.title = "매출액(원)"
    차트.y_axis.numFmt = "#,##0"        # 세로축 숫자에 쉼표 넣기
    차트.y_axis.scaling.min = 0         # 세로축을 0부터 시작 (아래 설명 참고)
    차트.x_axis.delete = False          # 가로축(지점 이름) 보이게
    차트.y_axis.delete = False          # 세로축(금액) 보이게
    차트.legend = None                  # 막대 종류가 하나뿐이라 범례는 빼요

    # 막대 높이 = '합계' 열의 지점 칸들 (제목 칸 포함해서 가리키고 titles_from_data로 제목 처리)
    막대값 = Reference(시트, min_col=합계열번호, min_row=1, max_row=1 + 지점수)
    # 가로축 이름 = 'A열'의 지점 이름들
    막대이름 = Reference(시트, min_col=1, min_row=2, max_row=1 + 지점수)
    차트.add_data(막대값, titles_from_data=True)
    차트.set_categories(막대이름)

    차트.width, 차트.height = 18, 9      # 차트 크기 (cm 단위)
    시트.add_chart(차트, "J2")           # 표 오른쪽(J2 칸)에 배치
print(f"\n저장 완료: {요약경로}")

# 15) 검증: 저장된 파일을 '다시 열어서' 차트가 가리키는 칸의 숫자를 읽고,
#     요약표의 숫자와 같은지 + 지점별 비율이 맞는지 확인해요
import openpyxl
검증시트 = openpyxl.load_workbook(요약경로)["지점별월별합계"]
차트수 = len(검증시트._charts)
print(f"\n[차트 검증] 시트 안 차트 개수: {차트수}개 (1개여야 정상)")
총합 = 요약표.loc["합계", "합계"]
for 줄 in range(2, 2 + 지점수):
    지점 = 검증시트.cell(줄, 1).value
    차트값 = 검증시트.cell(줄, 합계열번호).value
    원본값 = 요약표.loc[지점, "합계"]
    표시 = "일치" if 차트값 == 원본값 else "❌ 불일치"
    막대 = "█" * round(차트값 / 총합 * 100)  # 비율만큼 막대를 글자로 그려 봐요
    print(f"  {지점:<6} {차트값:>12,.0f}원  {차트값 / 총합:6.1%}  {막대}  [{표시}]")
print("시트 목록:", ["지점별월별합계"] + [f"{지점}_TOP3" for 지점 in TOP3목록])
