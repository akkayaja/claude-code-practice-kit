# 미션 5: 메일에 붙어 있는 첨부파일을 꺼내서 첨부파일/ 폴더에 따로 저장한다.

import shutil
from email import policy
from email.parser import BytesParser
from pathlib import Path

INBOX = Path("inbox")
첨부폴더 = Path("첨부파일")

# 다시 실행해도 예전 파일이 섞이지 않도록 첨부파일 폴더를 비우고 새로 만든다
if 첨부폴더.exists():
    shutil.rmtree(첨부폴더)
첨부폴더.mkdir()

저장개수 = 0

for 메일파일 in sorted(INBOX.glob("*.eml")):
    with open(메일파일, "rb") as f:
        메일 = BytesParser(policy=policy.default).parse(f)

    # 메일 안의 첨부(소포)를 하나씩 꺼낸다. 첨부가 없으면 이 반복은 그냥 지나간다.
    for 첨부 in 메일.iter_attachments():
        파일이름 = 첨부.get_filename()          # 예: "견적요청서.csv" (포장도 자동으로 풀림)
        내용 = 첨부.get_payload(decode=True)    # base64 포장을 풀어서 진짜 파일 내용(바이트)을 꺼냄

        저장위치 = 첨부폴더 / 파일이름
        # 이름이 같은 첨부가 이미 있으면 덮어쓰지 않게 앞에 메일 번호를 붙인다
        if 저장위치.exists():
            저장위치 = 첨부폴더 / f"{메일파일.stem}_{파일이름}"

        저장위치.write_bytes(내용)               # 꺼낸 내용을 파일로 저장
        저장개수 += 1
        print(f"{메일파일.name} → {저장위치}  ({len(내용)} 바이트)")

print("-" * 60)
print(f"첨부파일 {저장개수}개를 {첨부폴더}/ 폴더에 저장했어요.")
