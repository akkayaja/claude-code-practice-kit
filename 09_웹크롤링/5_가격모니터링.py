# 도전 미션 3: 가격이 바뀌면 알려 주는 모니터링
# 실행할 때마다: 지금 가격을 모아서 → 지난번 기록(결과/가격기록.csv)과 비교 → 바뀐 상품을 알려 주고 → 기록을 새로 저장
# 실행 전: 연습 쇼핑몰 서버(localhost:8080)가 켜져 있어야 해요.

import csv
import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

RECORD = "결과/가격기록.csv"   # 지난번 가격을 적어 두는 '장부'

# ── 1) 지금 가격 모으기 (목록 페이지만, 1초씩 쉬면서) ──
url = "http://localhost:8080/page1.html"
now_prices = {}
while url:
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    for item in soup.select(".item"):
        name = item.select_one(".name").get_text(strip=True)
        price = int(item.select_one(".price").get_text(strip=True).replace(",", "").replace("원", ""))
        now_prices[name] = price
    next_link = soup.select_one("a.next")
    url = urljoin(url, next_link["href"]) if next_link else None
    time.sleep(1)
print(f"지금 가격 확인: 상품 {len(now_prices)}개")

# ── 2) 지난번 장부와 비교하기 ──
if not os.path.exists(RECORD):
    print("📒 지난 기록이 없어요. 이번 가격을 '첫 기록'으로 저장할게요. (다음 실행부터 비교해요)")
else:
    with open(RECORD, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    old_prices = {row["상품명"]: int(row["가격"]) for row in rows}
    print(f"지난 기록과 비교: {rows[0]['확인시각']}에 저장한 가격")

    changes = []
    for name, new in now_prices.items():
        old = old_prices.get(name)
        if old is not None and old != new:
            changes.append((name, old, new))

    if not changes:
        print("✅ 가격 변동 없음")
    else:
        print(f"🔔 가격이 바뀐 상품 {len(changes)}개!")
        for name, old, new in changes:
            diff = new - old
            mark = "▲ 올랐어요" if diff > 0 else "▼ 내렸어요"
            print(f"  {name}: {old:,}원 → {new:,}원 ({diff:+,}원, {diff / old * 100:+.1f}%) {mark}")

# ── 3) 이번 가격을 장부에 새로 적기 (다음 비교의 기준이 돼요) ──
os.makedirs("결과", exist_ok=True)
checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(RECORD, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["상품명", "가격", "확인시각"])
    for name, price in now_prices.items():
        writer.writerow([name, price, checked_at])
print(f"장부 저장: {RECORD} ({checked_at})")
