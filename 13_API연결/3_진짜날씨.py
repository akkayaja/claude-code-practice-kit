"""도전 미션: 기상청 '초단기실황' API로 7개 도시의 진짜 현재 날씨를 받아 표로 출력하기.

- 인증키는 코드에 쓰지 않고 .env 금고 파일에서 꺼내 온다
- 기본 미션의 가짜 서버와 똑같은 흐름: 키 붙여서 요청 → JSON 응답 → 표

실행 (13_API연결 폴더에서): python3 3_진짜날씨.py
"""
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

# 기상청은 위도·경도 대신 전국을 5km 바둑판으로 나눈 칸 번호(nx, ny)를 써요
GRID = {
    "서울": (60, 127), "부산": (98, 76), "대구": (89, 90), "인천": (55, 124),
    "광주": (58, 74), "대전": (67, 100), "제주": (52, 38),
}
# 강수형태(PTY) 번호 → 말
RAIN = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림"}


def load_env(path):
    """.env 금고 파일을 읽어서 {이름: 값} 사전으로 돌려준다. (# 줄과 빈 줄은 건너뜀)"""
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                values[name.strip()] = value.strip()
    return values


def base_time_now():
    """가장 최근에 발표된 관측 시각을 고른다.
    매시 정각 관측값이 약 40분 뒤에 올라오므로, 45분 전이면 한 시간 전 것을 쓴다."""
    now = datetime.now(timezone(timedelta(hours=9)))   # 한국 시간
    if now.minute < 45:
        now -= timedelta(hours=1)
    return now.strftime("%Y%m%d"), now.strftime("%H00")


def pad(text, width):
    text = str(text)
    real_width = sum(2 if ord(ch) > 127 else 1 for ch in text)
    return text + " " * (width - real_width)


# 1) 금고에서 키 꺼내기
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
API_KEY = load_env(env_path).get("DATA_GO_KR_KEY", "")
if not API_KEY:
    print("⚠️  .env 파일에 DATA_GO_KR_KEY 값이 비어 있어요. 인증키를 넣고 저장해 주세요.")
    raise SystemExit(0)

base_date, base_time = base_time_now()
print(f"기준: 기상청 초단기실황, {base_date[:4]}-{base_date[4:6]}-{base_date[6:]} {base_time[:2]}:00 관측값\n")

# 2) 도시마다 주문 — 실패해도 다음 도시로
ok, failed = [], []
for city, (nx, ny) in GRID.items():
    params = {"serviceKey": API_KEY, "pageNo": 1, "numOfRows": 100, "dataType": "JSON",
              "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny}
    try:
        with urlopen(URL + "?" + urlencode(params), timeout=10) as res:
            text = res.read().decode("utf-8")
    except HTTPError as e:
        failed.append((city, f"상태코드 {e.code}"))
        continue
    except URLError:
        failed.append((city, "인터넷 또는 기상청 서버에 연결할 수 없음"))
        continue

    try:
        body = json.loads(text)
    except json.JSONDecodeError:   # 키 문제일 땐 JSON이 아니라 XML 오류가 와요
        reason = "인증키 오류 (아직 활성화 전일 수 있어요)" if "SERVICE_KEY" in text else "알 수 없는 응답"
        failed.append((city, reason))
        continue

    header = body["response"]["header"]
    if header["resultCode"] != "00":
        failed.append((city, f"{header['resultCode']} {header['resultMsg']}"))
        continue

    items = body["response"]["body"]["items"]["item"]
    values = {it["category"]: it["obsrValue"] for it in items}
    ok.append({"city": city, "temp": values.get("T1H"), "humidity": values.get("REH"),
               "rain": RAIN.get(values.get("PTY"), values.get("PTY"))})

# 3) 표로 출력
print(pad("도시", 6), pad("기온(℃)", 9), pad("습도(%)", 8), "강수")
print("-" * 36)
for w in ok:
    print(pad(w["city"], 6), pad(w["temp"], 9), pad(w["humidity"], 8), w["rain"])
print("-" * 36)
for city, reason in failed:
    print(f"❌ {city}: {reason}")
print(f"성공 {len(ok)}개 / 실패 {len(failed)}개")
