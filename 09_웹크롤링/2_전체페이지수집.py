# 미션 4: '다음 ›' 링크를 따라가며 모든 페이지의 상품 모으기
# 실행 전: 연습 쇼핑몰 서버(localhost:8080)가 켜져 있어야 해요.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin   # "page2.html" 같은 짧은 주소를 전체 주소로 바꿔 주는 도구

url = "http://localhost:8080/page1.html"   # 출발점: 1페이지
products = []
page_no = 0

# '다음' 링크가 있는 동안 계속 반복 (없으면 마지막 페이지라는 뜻)
while url:
    page_no += 1
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select(".item")
    for item in items:
        price_text = item.select_one(".price").get_text(strip=True)
        products.append({
            "상품명": item.select_one(".name").get_text(strip=True),
            "카테고리": item.select_one(".category").get_text(strip=True),
            "가격": int(price_text.replace(",", "").replace("원", "")),
            "평점": float(item.select_one(".rating").get_text(strip=True).replace("★", "")),
            "리뷰수": int(item.select_one(".reviews").get_text(strip=True).replace("리뷰", "")),
        })
    print(f"{page_no}페이지: {len(items)}개 수집 ({url})")

    # class="next" 링크(다음 ›)를 찾아서 다음 주소로 바꾸기
    next_link = soup.select_one("a.next")
    url = urljoin(url, next_link["href"]) if next_link else None

print(f"\n총 {page_no}페이지, 상품 {len(products)}개 수집 완료")
print(f"첫 상품: {products[0]['상품명']} / 마지막 상품: {products[-1]['상품명']}")
print(f"전체 가격 합계: {sum(p['가격'] for p in products):,}원")
