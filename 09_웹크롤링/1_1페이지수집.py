# 미션 3: 연습 쇼핑몰 1페이지에서 상품 정보 뽑기
# 실행 전: 다른 터미널 탭에서 practice_site 서버(python3 -m http.server 8080)가 켜져 있어야 해요.

import requests                    # 웹페이지를 받아 오는 도구 (브라우저 대신 주소로 접속)
from bs4 import BeautifulSoup      # 받아 온 HTML(설계도)에서 이름표로 정보를 찾는 도구

URL = "http://localhost:8080/page1.html"

# 1) 페이지 받아 오기
response = requests.get(URL)
response.encoding = "utf-8"        # 한글이 깨지지 않게
print(f"접속 결과: {response.status_code} (200이면 성공)")

# 2) HTML 읽기
soup = BeautifulSoup(response.text, "html.parser")

# 3) class="item" 상자를 전부 찾기 = 상품 하나하나
items = soup.select(".item")
print(f"찾은 상품 수: {len(items)}개\n")

products = []
for item in items:
    name = item.select_one(".name").get_text(strip=True)
    category = item.select_one(".category").get_text(strip=True)

    # 가격 "104,000원" → 숫자 104000 (쉼표와 '원' 빼기)
    price_text = item.select_one(".price").get_text(strip=True)
    price = int(price_text.replace(",", "").replace("원", ""))

    # 평점 "★ 3.3" → 숫자 3.3
    rating = float(item.select_one(".rating").get_text(strip=True).replace("★", ""))

    # 리뷰 "리뷰 457" → 숫자 457
    reviews = int(item.select_one(".reviews").get_text(strip=True).replace("리뷰", ""))

    products.append({"상품명": name, "카테고리": category, "가격": price,
                     "평점": rating, "리뷰수": reviews})

# 4) 화면에 보여 주기
for p in products:
    print(f"{p['상품명']} | {p['카테고리']} | {p['가격']:,}원 | ★{p['평점']} | 리뷰 {p['리뷰수']}")

print(f"\n1페이지 가격 합계: {sum(p['가격'] for p in products):,}원")
