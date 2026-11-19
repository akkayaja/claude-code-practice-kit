# 도전 미션 1+2: 상세 페이지까지 들어가 판매자·재고 모으기 + 요청 사이 1초씩 쉬기
# 실행 전: 연습 쇼핑몰 서버(localhost:8080)가 켜져 있어야 해요.
# 걸리는 시간: 약 50초 (목록 3번 + 상세 45번, 매번 1초씩 쉬기 때문)

import csv
import os
import time                         # 시간 도구 (잠깐 쉬기)
from collections import Counter
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

WAIT = 1   # 요청 사이에 쉬는 시간(초) — 서버에 부담 주지 않는 '예의'


def get_soup(url):
    """주소를 받아서 HTML을 읽고, 1초 쉬고 돌려주기"""
    response = requests.get(url)
    response.encoding = "utf-8"
    time.sleep(WAIT)
    return BeautifulSoup(response.text, "html.parser")


def to_int(text):
    return int(text.replace(",", "").replace("원", "").replace("리뷰", "").strip())


# ── 1) 목록 페이지 돌면서 상품 + 상세 페이지 주소 모으기 ──
url = "http://localhost:8080/page1.html"
products = []
while url:
    soup = get_soup(url)
    for item in soup.select(".item"):
        link = item.select_one(".name a")
        products.append({
            "상품명": link.get_text(strip=True),
            "카테고리": item.select_one(".category").get_text(strip=True),
            "가격": to_int(item.select_one(".price").get_text()),
            "평점": float(item.select_one(".rating").get_text(strip=True).replace("★", "")),
            "리뷰수": to_int(item.select_one(".reviews").get_text()),
            "상세주소": urljoin(url, link["href"]),
        })
    next_link = soup.select_one("a.next")
    url = urljoin(url, next_link["href"]) if next_link else None
print(f"목록에서 상품 {len(products)}개 찾음. 이제 상세 페이지에 하나씩 들어가요 (1초씩 쉬면서)...")

# ── 2) 상품마다 상세 페이지에 들어가 판매자·재고 가져오기 ──
start = time.time()
for i, p in enumerate(products, start=1):
    detail = get_soup(p["상세주소"])
    p["판매자"] = detail.select_one(".seller").get_text(strip=True)
    p["재고"] = to_int(detail.select_one(".stock").get_text())
    if i % 15 == 0:
        print(f"  {i}/{len(products)}개 완료 ({time.time() - start:.0f}초 지남)")

# ── 3) 저장 ──
os.makedirs("결과", exist_ok=True)
save_path = "결과/상품목록_상세.csv"
columns = ["상품명", "카테고리", "가격", "평점", "리뷰수", "판매자", "재고"]
with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")  # 상세주소 칸은 빼고 저장
    writer.writeheader()
    writer.writerows(products)

# ── 4) 확인용 요약 ──
print(f"\n저장 완료: {save_path} (상품 {len(products)}개)")
print(f"판매자 수: {len(set(p['판매자'] for p in products))}곳")
print("판매자별 상품 수:", dict(Counter(p["판매자"] for p in products).most_common()))
print(f"전체 재고 합계: {sum(p['재고'] for p in products):,}개")
low = [p for p in products if p["재고"] < 30]
print(f"재고 30개 미만 상품: {len(low)}개 →", ", ".join(f"{p['상품명']}({p['재고']})" for p in low))
