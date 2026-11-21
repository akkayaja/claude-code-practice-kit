"""도전 미션: 진짜 날씨를 받아 '날씨기록.csv'에 한 줄씩 쌓기 (일기장처럼).

- 실행할 때마다 7개 도시의 최신 관측값을 파일 맨 아래에 덧붙인다
- 같은 관측 시각·같은 도시가 이미 적혀 있으면 두 번 적지 않는다 (중복 방지)
- 매일 자동으로 돌리는 건 14번 실습(스케줄 자동화)에서 연결해요

실행 (13_API연결 폴더에서): python3 4_날씨기록.py
"""
import csv
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "날씨기록.csv")
URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
GRID = {
    "서울": (60, 127), "부산": (98, 76), "대구": (89, 90), "인천": (55, 124),
    "광주": (58, 74), "대전": (67, 100), "제주": (52, 38),
}
RAIN = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림"}
COLUMNS = ["관측일시", "도시", "기온", "습도", "강수", "저장한때"]
KST = timezone(timedelta(hours=9))


def load_env(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                values[name.strip()] = value.strip()
    return values


def fetch(api_key, base_date, base_time, nx, ny):
    """한 도시의 실황을 받아 {기온, 습도, 강수}를 돌려준다. 실패하면 오류 이유(문자열)를 돌려준다."""
    params = {"serviceKey": api_key, "pageNo": 1, "numOfRows": 100, "dataType": "JSON",
              "base_date": base_date, "base_time": base_time, "nx": nx, "ny": ny}
    try:
        with urlopen(URL + "?" + urlencode(params), timeout=10) as res:
            body = json.loads(res.read().decode("utf-8"))
    except HTTPError as e:
        return f"상태코드 {e.code}"
    except URLError:
        return "연결 실패"
    except json.JSONDecodeError:
        return "인증키 오류 또는 알 수 없는 응답"
    header = body["response"]["header"]
    if header["resultCode"] != "00":
        return f"{header['resultCode']} {header['resultMsg']}"
    v = {it["category"]: it["obsrValue"] for it in body["response"]["body"]["items"]["item"]}
    return {"기온": v.get("T1H"), "습도": v.get("REH"), "강수": RAIN.get(v.get("PTY"), v.get("PTY"))}


# 1) 키 꺼내기 + 관측 시각 정하기
API_KEY = load_env(os.path.join(HERE, ".env")).get("DATA_GO_KR_KEY", "")
if not API_KEY:
    print("⚠️  .env 파일에 DATA_GO_KR_KEY 값이 비어 있어요.")
    raise SystemExit(0)
now = datetime.now(KST)
obs = now - timedelta(hours=1) if now.minute < 45 else now
base_date, base_time = obs.strftime("%Y%m%d"), obs.strftime("%H00")
obs_label = obs.strftime("%Y-%m-%d %H:00")

# 2) 이미 적힌 기록 읽기 (파일이 없으면 빈 상태로 시작)
already = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            already.add((row["관측일시"], row["도시"]))

# 3) 도시마다 받아서, 새 기록만 모으기
new_rows, skipped, failed = [], 0, []
for city, (nx, ny) in GRID.items():
    if (obs_label, city) in already:
        skipped += 1
        continue
    result = fetch(API_KEY, base_date, base_time, nx, ny)
    if isinstance(result, str):
        failed.append((city, result))
        continue
    new_rows.append({"관측일시": obs_label, "도시": city, **result,
                     "저장한때": now.strftime("%Y-%m-%d %H:%M")})

# 4) 파일 맨 아래에 덧붙이기 (처음이면 제목 줄부터)
is_new_file = not os.path.exists(LOG_FILE)
with open(LOG_FILE, "a", encoding="utf-8-sig" if is_new_file else "utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMNS)
    if is_new_file:
        writer.writeheader()
    writer.writerows(new_rows)

# 5) 결과 보고
total = len(already) + len(new_rows)
print(f"관측 시각: {obs_label}")
print(f"새로 적음 {len(new_rows)}줄 / 이미 있어서 건너뜀 {skipped}줄 / 실패 {len(failed)}줄")
for city, reason in failed:
    print(f"❌ {city}: {reason}")
print(f"📒 날씨기록.csv 전체 기록: {total}줄 (제목 줄 빼고)")
