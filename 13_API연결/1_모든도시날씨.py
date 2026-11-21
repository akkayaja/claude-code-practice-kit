"""미션 5: 가짜 날씨 API에서 모든 도시 날씨를 받아 표로 출력하기.

실행 (13_API연결 폴더에서): python3 1_모든도시날씨.py
먼저 서버가 켜져 있어야 해요: python3 mock_api/server.py > /dev/null 2>&1 &
"""
import json
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "http://localhost:8765"   # 주문 창구 주소 (내 컴퓨터, 8765번 창구)
API_KEY = "practice-key-123"         # 연습용 회원카드 (진짜 키 아님)


def get_json(path, params=None):
    """창구에 주문서를 보내고, 받은 JSON 상자를 열어서 돌려준다."""
    url = BASE_URL + path
    if params:
        url += "?" + urlencode(params)   # 한글을 주소용 글자로 포장
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def pad(text, width):
    """한글은 영어보다 두 칸 넓어서, 표 줄이 맞도록 빈칸을 채운다."""
    text = str(text)
    real_width = sum(2 if ord(ch) > 127 else 1 for ch in text)
    return text + " " * (width - real_width)


# 1) 도시 목록 주문
cities = get_json("/cities")["cities"]

# 2) 도시마다 날씨 주문
rows = []
for city in cities:
    weather = get_json("/weather", {"key": API_KEY, "city": city})
    rows.append(weather)

# 3) 표로 출력
print(pad("도시", 6), pad("기온(℃)", 9), pad("습도(%)", 8), "하늘")
print("-" * 36)
for w in rows:
    print(pad(w["city"], 6), pad(w["temp"], 9), pad(w["humidity"], 8), w["sky"])
print("-" * 36)
print(f"총 {len(rows)}개 도시")
