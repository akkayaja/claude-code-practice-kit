# 도전 미션 2: 간단한 웹 채팅 화면 붙이기
#  - 내 컴퓨터에 작은 서버를 켜서 http://localhost:8000 으로 채팅 화면(채팅화면.html)을 보여 줘요
#  - 화면에서 질문을 보내면 → 서버가 답하기_근거포함()으로 답과 근거 문서를 만들어 돌려줘요
#  - 비유: 알바생(챗봇)을 가게 카운터(웹 화면)에 앉히는 단계

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from 공통 import 답하기_근거포함, 여기

포트 = 8000


class 카운터(BaseHTTPRequestHandler):
    def do_GET(self):
        """브라우저가 화면을 달라고 하면 채팅화면.html 을 보내 준다."""
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        내용 = (여기 / "채팅화면.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(내용)

    def do_POST(self):
        """화면에서 질문이 오면 RAG로 답하고, {답, 근거} 를 JSON으로 돌려준다."""
        if self.path != "/ask":
            self.send_error(404)
            return
        길이 = int(self.headers.get("Content-Length", 0))
        질문 = json.loads(self.rfile.read(길이) or b"{}").get("질문", "")
        답, 근거문서, _ = 답하기_근거포함(질문)
        내용 = json.dumps({"답": 답, "근거": 근거문서}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(내용)


print(f"💬 채팅 서버를 켰어요 → http://localhost:{포트}")
ThreadingHTTPServer(("127.0.0.1", 포트), 카운터).serve_forever()
