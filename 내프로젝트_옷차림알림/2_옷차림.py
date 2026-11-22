"""2단계: 내일 시간별 기온 전부 + 하루 기온 범위에 드는 옷차림 칸 모두 + 우산 알림.

- 1_내일기온.py 의 get_tomorrow()로 예보를 받아 온다
- 00~23시 기온(강수확률)을 한 줄씩 보여 준다
- 하루 최저~최고 기온이 걸친 옷차림표 칸을 모두 보여 준다 (옷은 내가 고름)
- 내일 강수확률이 60% 이상인 시간이 있으면 ☔ 줄을 붙인다

실행 (내프로젝트_옷차림알림 폴더에서): python3 2_옷차림.py
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# 파일 이름이 숫자로 시작해서 import 대신 이 방법으로 불러온다
_spec = importlib.util.spec_from_file_location("forecast", os.path.join(HERE, "1_내일기온.py"))
forecast = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(forecast)

UMBRELLA_POP = 60  # 이 % 이상이면 우산 알림

# 기온별 옷차림표: (이 기온 이상부터, 칸 이름, 옷차림) — 높은 칸부터
CLOTHES = [
    (28, "28℃ 이상", "민소매, 반팔, 반바지, 원피스"),
    (23, "23~27℃", "반팔, 얇은 셔츠, 반바지, 면바지"),
    (20, "20~22℃", "얇은 가디건, 긴팔, 면바지, 청바지"),
    (17, "17~19℃", "얇은 니트, 맨투맨, 가디건, 청바지"),
    (12, "12~16℃", "자켓, 가디건, 야상, 스타킹, 청바지, 면바지"),
    (9, "9~11℃", "자켓, 트렌치코트, 야상, 니트, 청바지, 스타킹"),
    (5, "5~8℃", "코트, 가죽자켓, 히트텍, 니트, 레깅스"),
    (-999, "4℃ 이하", "패딩, 두꺼운 코트, 목도리, 기모제품"),
]


def band_index(t):
    """기온 t가 옷차림표 몇 번째 칸인지 (0 = 가장 더운 칸)."""
    for i, (low, _, _) in enumerate(CLOTHES):
        if t >= low:
            return i
    return len(CLOTHES) - 1


def clothes_lines(low, high):
    """low~high 범위가 걸친 칸을 추운 칸 → 더운 칸 순서로 돌려준다."""
    hot, cold = band_index(high), band_index(low)
    return [f"   · {CLOTHES[i][1]}: {CLOTHES[i][2]}" for i in range(cold, hot - 1, -1)]


def make_report():
    """(제목, 본문) 을 만들어 돌려준다. 3단계 메일에서도 이 함수를 그대로 쓴다."""
    tomorrow, base_label, s = forecast.get_tomorrow()
    n, range_text = forecast.n, forecast.range_text
    md = f"{int(tomorrow[4:6])}/{int(tomorrow[6:])}"
    hourly = s["시간별"]
    if not hourly:
        raise SystemExit("❌ 내일 시간별 예보가 비어 있어요.")
    temps = [t for t, _ in hourly.values()]
    low, high = min(temps), max(temps)

    lines = [f"📅 내일 {md} 광주 ({base_label} 기준)",
             f"🌡️ 하루 기온: {range_text((low, high))}", "",
             "⏰ 시간별 기온 (강수확률)"]
    for hour, (t, pop) in hourly.items():
        pop_text = f"  💧{pop}%" if pop is not None else ""
        lines.append(f"   {hour:02d}시  {n(t):>3}℃{pop_text}")

    lines += ["", f"👕 옷차림 ({range_text((low, high))} 범위에 드는 칸 모두)"]
    lines += clothes_lines(low, high)

    umbrella = s["강수확률"] and s["강수확률"][0] >= UMBRELLA_POP
    if umbrella:
        pop, hour = s["강수확률"]
        lines += ["", f"☔ 우산 챙기세요 (최고 강수확률 {pop}%, {hour}시)"]

    subject = f"[옷차림] 내일 {md} 광주 {range_text((low, high))}" + (" ☔" if umbrella else "")
    return subject, "\n".join(lines)


if __name__ == "__main__":
    subject, body = make_report()
    print(f"제목: {subject}")
    print("-" * 40)
    print(body)
