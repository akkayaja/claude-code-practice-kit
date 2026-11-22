"""1단계: 내일 광주 기온 세 가지를 화면에 보여 주기.

- 기상청 단기예보(getVilageFcst)에서 지금 받아 볼 수 있는 가장 최근 발표분을 고른다
  (발표는 02·05·08·11·14·17·20·23시, 실제로 올라오는 건 10분쯤 뒤)
- 내일 날짜의 시간별 기온(TMP)과 강수확률(POP)을 꺼낸다
- 아침 07~09시 / 낮 12~18시 최고 / 저녁 18~23시 를 계산해서 보여 준다

실행 (내프로젝트_옷차림알림 폴더에서): python3 1_내일기온.py
"""
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
NX, NY = 58, 74  # 광주 격자 좌표
KST = timezone(timedelta(hours=9))
BASE_HOURS = [2, 5, 8, 11, 14, 17, 20, 23]  # 하루 8번 발표


def load_env(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                values[name.strip()] = value.strip()
    return values


def latest_base(now):
    """지금 받아 볼 수 있는 가장 최근 발표 시각 (발표 10분 뒤부터 받을 수 있다고 본다)."""
    ready = now - timedelta(minutes=10)
    for hour in reversed(BASE_HOURS):
        if ready.hour >= hour:
            return ready.strftime("%Y%m%d"), f"{hour:02d}00"
    # 새벽 02:10 전이면 어제 23시 발표분
    yesterday = ready - timedelta(days=1)
    return yesterday.strftime("%Y%m%d"), "2300"


def fetch_forecast(api_key, base_date, base_time):
    """예보 전체를 받아 {(날짜, 시각): {항목: 값}} 사전으로 돌려준다."""
    params = {"serviceKey": api_key, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON",
              "base_date": base_date, "base_time": base_time, "nx": NX, "ny": NY}
    try:
        with urlopen(URL + "?" + urlencode(params), timeout=15) as res:
            body = json.loads(res.read().decode("utf-8"))
    except HTTPError as e:
        raise SystemExit(f"❌ 기상청 응답 오류: 상태코드 {e.code} (키가 맞는지 확인해요)")
    except URLError:
        raise SystemExit("❌ 기상청에 연결하지 못했어요 (인터넷 연결 확인)")
    header = body["response"]["header"]
    if header["resultCode"] != "00":
        raise SystemExit(f"❌ 기상청: {header['resultCode']} {header['resultMsg']}")
    table = {}
    for it in body["response"]["body"]["items"]["item"]:
        table.setdefault((it["fcstDate"], it["fcstTime"]), {})[it["category"]] = it["fcstValue"]
    return table


def summarize(table, day):
    """내일(day, 'YYYYMMDD')의 기온 세 가지 + 강수확률 최고값을 계산한다."""
    temps, pops = {}, {}
    for (date, time), v in table.items():
        if date != day:
            continue
        hour = int(time[:2])
        if "TMP" in v:
            temps[hour] = float(v["TMP"])
        if "POP" in v:
            pops[hour] = int(v["POP"])

    def pick(hours):
        return [temps[h] for h in hours if h in temps]

    morning = pick(range(7, 10))        # 07, 08, 09시
    evening = pick(range(18, 24))       # 18 ~ 23시 (자정 전까지)
    day_hours = [h for h in range(12, 19) if h in temps]  # 12 ~ 18시
    peak_hour = max(day_hours, key=lambda h: temps[h]) if day_hours else None
    pop_hour = max(pops, key=lambda h: (pops[h], -h)) if pops else None
    return {
        "시간별": {h: (temps[h], pops.get(h)) for h in sorted(temps)},  # {시: (기온, 강수확률)}
        "아침":(min(morning), max(morning)) if morning else None,
        "낮최고": (temps[peak_hour], peak_hour) if peak_hour is not None else None,
        "저녁": (min(evening), max(evening)) if evening else None,
        "강수확률": (pops[pop_hour], pop_hour) if pop_hour is not None else None,
    }


def get_tomorrow():
    """다른 스크립트에서도 불러 쓰는 입구: (내일 날짜, 발표 시각 글자, 요약)을 돌려준다."""
    api_key = load_env(os.path.join(HERE, ".env")).get("DATA_GO_KR_KEY", "")
    if not api_key:
        raise SystemExit("⚠️  .env 파일에 DATA_GO_KR_KEY 값이 비어 있어요.")
    now = datetime.now(KST)
    base_date, base_time = latest_base(now)
    tomorrow = (now + timedelta(days=1)).strftime("%Y%m%d")
    table = fetch_forecast(api_key, base_date, base_time)
    base_label = f"{base_date[4:6]}/{base_date[6:]} {base_time[:2]}시 발표"
    return tomorrow, base_label, summarize(table, tomorrow)


def n(t):
    """기온 숫자를 보기 좋게 (15.0 → 15)."""
    return f"{t:g}"


def range_text(pair):
    low, high = pair
    return f"{n(low)}℃" if low == high else f"{n(low)}~{n(high)}℃"


if __name__ == "__main__":
    tomorrow, base_label, s = get_tomorrow()
    print(f"📅 내일 {tomorrow[4:6]}/{tomorrow[6:]} 광주 ({base_label} 기준)")
    print(f"🌅 아침 07~09시: {range_text(s['아침']) if s['아침'] else '예보 없음'}")
    if s["낮최고"]:
        print(f"☀️  낮 최고: {n(s['낮최고'][0])}℃ ({s['낮최고'][1]}시)")
    else:
        print("☀️  낮 최고: 예보 없음")
    print(f"🌙 저녁 18~23시: {range_text(s['저녁']) if s['저녁'] else '예보 없음'}")
    if s["강수확률"]:
        print(f"💧 최고 강수확률: {s['강수확률'][0]}% ({s['강수확률'][1]}시)")
