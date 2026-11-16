# 미션 2: inbox 폴더의 메일 20통을 열어서
#        제목 / 보낸사람 / 날짜 / 첨부파일을 표로 보여 주고 CSV로도 저장한다.

import csv                                  # 표(CSV) 파일을 만드는 도구
from email import policy                    # 메일 포장(base64)을 알아서 풀어 주는 설정
from email.parser import BytesParser        # .eml 파일을 읽어서 "메일 객체"로 바꿔 주는 도구
from email.utils import parsedate_to_datetime  # "Tue, 03 Nov 2026 ..." 날짜를 읽기 쉽게 바꾸는 도구
from pathlib import Path                    # 폴더·파일 경로를 다루는 도구

INBOX = Path("inbox")                       # 메일이 들어 있는 바구니(폴더)
결과파일 = Path("메일목록.csv")              # 표를 저장할 파일 이름

목록 = []                                    # 메일 정보를 하나씩 담을 빈 상자

# inbox 안의 .eml 파일을 이름 순서대로 하나씩 꺼낸다
for 메일파일 in sorted(INBOX.glob("*.eml")):
    # 봉투를 열어서 파이썬이 읽을 수 있는 메일로 바꾼다 (포장도 여기서 풀림)
    with open(메일파일, "rb") as f:
        메일 = BytesParser(policy=policy.default).parse(f)

    # 보낸사람에서 이름만 꺼낸다 (예: "이도윤 <sender01@...>" → "이도윤")
    보낸사람 = 메일["From"].addresses[0].display_name

    # 날짜를 "2026-11-03 16:00" 모양으로 바꾼다
    날짜 = parsedate_to_datetime(메일["Date"]).strftime("%Y-%m-%d %H:%M")

    # 첨부파일 이름들을 모은다 (없으면 빈 칸)
    첨부들 = [첨부.get_filename() for 첨부 in 메일.iter_attachments()]
    첨부 = ", ".join(첨부들) if 첨부들 else "-"

    목록.append({
        "파일": 메일파일.name,
        "제목": 메일["Subject"],
        "보낸사람": 보낸사람,
        "날짜": 날짜,
        "첨부파일": 첨부,
    })

# 1) 화면에 표로 출력
print(f"{'파일':<12} {'날짜':<17} {'보낸사람':<8} {'첨부파일':<16} 제목")
print("-" * 90)
for 줄 in 목록:
    print(f"{줄['파일']:<12} {줄['날짜']:<17} {줄['보낸사람']:<8} {줄['첨부파일']:<16} {줄['제목']}")

# 2) 엑셀에서도 열 수 있게 CSV로 저장 (utf-8-sig = 엑셀에서 한글이 안 깨지는 저장 방식)
with open(결과파일, "w", newline="", encoding="utf-8-sig") as f:
    쓰기 = csv.DictWriter(f, fieldnames=["파일", "제목", "보낸사람", "날짜", "첨부파일"])
    쓰기.writeheader()
    쓰기.writerows(목록)

첨부있는메일 = sum(1 for 줄 in 목록 if 줄["첨부파일"] != "-")
print("-" * 90)
print(f"메일 {len(목록)}통 / 첨부파일 있는 메일 {첨부있는메일}통 → {결과파일} 에 저장했어요.")
