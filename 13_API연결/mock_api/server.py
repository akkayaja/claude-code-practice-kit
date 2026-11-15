"""연습용 가짜 날씨 API 서버. 실행: python3 server.py  →  http://localhost:8765/weather?city=서울"""
import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DATA = json.load(open(os.path.join(os.path.dirname(__file__), "weather.json"), encoding="utf-8"))
API_KEY = "practice-key-123"  # 연습용 키 (진짜 키 아님)

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        url = urlparse(self.path); q = parse_qs(url.query)
        if url.path == "/cities":
            return self._send(200, {"cities": list(DATA)})
        if url.path == "/weather":
            if q.get("key", [""])[0] != API_KEY:
                return self._send(401, {"error": "API 키가 없거나 틀렸습니다. ?key=practice-key-123 을 붙이세요"})
            city = q.get("city", [""])[0]
            if city not in DATA:
                return self._send(404, {"error": f"'{city}' 도시를 찾을 수 없습니다", "available": list(DATA)})
            return self._send(200, DATA[city])
        self._send(404, {"error": "없는 주소입니다. /cities 또는 /weather 를 사용하세요"})

if __name__ == "__main__":
    print("가짜 API 서버 실행 중: http://localhost:8765/cities  (종료: Ctrl+C)")
    HTTPServer(("localhost", 8765), Handler).serve_forever()
