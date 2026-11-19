# 모니터링 연습용: 가게 주인이 되어 연습 쇼핑몰의 가격 2개를 바꿔요.
#   연습상품 03: 40,000원 → 35,000원 (할인)
#   연습상품 20: 18,000원 → 21,000원 (인상)
# 원래대로 되돌리기: git restore practice_site

CHANGES = [
    # (목록 파일, 상세 파일, 원래 가격, 바꿀 가격)
    ("practice_site/page1.html", "practice_site/detail_03.html", "40,000원", "35,000원"),
    ("practice_site/page2.html", "practice_site/detail_20.html", "18,000원", "21,000원"),
]
IDS = ["3", "20"]

for (list_file, detail_file, old, new), item_id in zip(CHANGES, IDS):
    # 1) 목록 페이지: 해당 상품 상자 안의 가격만 바꾸기
    with open(list_file, encoding="utf-8") as f:
        html = f.read()
    start = html.index(f'data-id="{item_id}"')
    end = html.index("</div>", start)
    box = html[start:end]
    if old not in box:
        print(f"이미 바뀌어 있어요: {list_file} (상품 {item_id})")
        continue
    html = html[:start] + box.replace(old, new) + html[end:]
    with open(list_file, "w", encoding="utf-8") as f:
        f.write(html)

    # 2) 상세 페이지 가격도 똑같이 바꾸기
    with open(detail_file, encoding="utf-8") as f:
        detail = f.read()
    with open(detail_file, "w", encoding="utf-8") as f:
        f.write(detail.replace(old, new))

    print(f"가격 변경: 상품 {item_id.zfill(2)}  {old} → {new}")
