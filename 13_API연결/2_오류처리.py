"""미션 6: 오류가 나도 멈추지 않는 날씨 표 만들기.

- 없는 도시(수원)를 일부러 섞어서 404 오류를 받아 본다
- 서버가 꺼져 있으면 빨간 에러 대신 친절한 안내를 보여 준다

실행 (13_API연결 폴더에서): python3 2_오류처리.py
"""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "http://localhost:8765"
API_KEY = "practice-key-123"
EXTRA_CITIES = ["수원"]   # 서버에 없는 도시를 일부러 하나 섞음


def get_json(path, params=None):
    """주문서를 보내고 JSON을 돌려준다. 3초 안에 답이 없으면 포기한다."""
    url = BASE_URL + path
    if params:
        url += "?" + urlencode(params)
    with urlopen(url, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def pad(text, width):
    text = str(text)
    real_width = sum(2 if ord(ch) > 127 else 1 for ch in text)
    return text + " " * (width - real_width)


# 1) 도시 목록 주문 — 여기서 서버가 꺼져 있으면 바로 안내하고 끝낸다
try:
    cities = get_json("/cities")["cities"]
except URLError:
    print("⚠️  API 서버에 연결할 수 없어요. (창구가 문을 닫았어요)")
    print("   서버를 켠 뒤 다시 실행하세요: python3 mock_api/server.py > /dev/null 2>&1 &")
    raise SystemExit(0)   # 빨간 에러 없이 조용히 종료

# 2) 도시마다 주문 — 한 도시가 실패해도 다음 도시로 넘어간다
ok, failed = [], []
for city in cities + EXTRA_CITIES:
    try:
        w = get_json("/weather", {"key": API_KEY, "city": city})
        ok.append(w)
    except HTTPError as e:   # 서버가 "안 돼요"라고 답한 경우 (401, 404 등)
        reason = json.loads(e.read().decode("utf-8")).get("error", "")
        failed.append((city, e.code, reason))
    except URLError:         # 도중에 서버가 꺼진 경우
        failed.append((city, "-", "서버에 연결할 수 없음"))

# 3) 성공한 도시는 표로
print(pad("도시", 6), pad("기온(℃)", 9), pad("습도(%)", 8), "하늘")
print("-" * 36)
for w in ok:
    print(pad(w["city"], 6), pad(w["temp"], 9), pad(w["humidity"], 8), w["sky"])
print("-" * 36)

# 4) 실패한 도시는 따로 모아서 이유와 함께
for city, code, reason in failed:
    print(f"❌ {city}: 상태코드 {code} — {reason}")
print(f"성공 {len(ok)}개 / 실패 {len(failed)}개")
