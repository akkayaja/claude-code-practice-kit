# 미션 5: 모든 페이지의 상품을 모아 결과/상품목록.csv로 저장하기
# 실행 전: 연습 쇼핑몰 서버(localhost:8080)가 켜져 있어야 해요.

import csv                          # 표(CSV) 파일을 쓰는 도구 (파이썬 기본 도구)
import os
from collections import Counter     # 개수 세기 도구
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ── 1) 수집: 미션 4와 같아요 ──────────────────────────
url = "http://localhost:8080/page1.html"
products = []
while url:
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    for item in soup.select(".item"):
        price_text = item.select_one(".price").get_text(strip=True)
        products.append({
            "상품명": item.select_one(".name").get_text(strip=True),
            "카테고리": item.select_one(".category").get_text(strip=True),
            "가격": int(price_text.replace(",", "").replace("원", "")),
            "평점": float(item.select_one(".rating").get_text(strip=True).replace("★", "")),
            "리뷰수": int(item.select_one(".reviews").get_text(strip=True).replace("리뷰", "")),
        })
    next_link = soup.select_one("a.next")
    url = urljoin(url, next_link["href"]) if next_link else None

# ── 2) 저장: 결과 폴더를 만들고 CSV로 쓰기 ─────────────
os.makedirs("결과", exist_ok=True)   # '결과' 폴더가 없으면 만들기
save_path = "결과/상품목록.csv"

# utf-8-sig: 엑셀에서 열어도 한글이 깨지지 않게 하는 저장 방식
with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["상품명", "카테고리", "가격", "평점", "리뷰수"])
    writer.writeheader()        # 첫 줄: 제목(머리글)
    writer.writerows(products)  # 나머지 줄: 상품 45개

print(f"저장 완료: {save_path} (상품 {len(products)}개)")

# ── 3) 확인용 요약 ────────────────────────────────────
print(f"전체 가격 합계: {sum(p['가격'] for p in products):,}원")
print("카테고리별 상품 수:", dict(Counter(p["카테고리"] for p in products).most_common()))
