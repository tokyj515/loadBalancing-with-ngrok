from flask import Flask, request, Response
import requests

app = Flask(__name__)

# 로드 밸런싱할 서버 목록 (5001번, 5002번 포트의 서버)
servers = ["http://localhost:5001", "http://localhost:5002"]
current_server = 0

# 라운드 로빈 방식으로 서버 선택
def get_next_server():
    global current_server
    server = servers[current_server]
    current_server = (current_server + 1) % len(servers)
    return server

# 모든 요청을 해당 서버로 프록시 처리
@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    target_server = get_next_server()
    target_url = f"{target_server}/{path}"

    # 원본 요청 정보를 사용하여 대상 서버로 요청 전달
    if request.method == "GET":
        resp = requests.get(target_url, headers=request.headers, params=request.args)
    elif request.method == "POST":
        resp = requests.post(target_url, headers=request.headers, data=request.get_data(), params=request.args)
    elif request.method == "PUT":
        resp = requests.put(target_url, headers=request.headers, data=request.get_data(), params=request.args)
    elif request.method == "DELETE":
        resp = requests.delete(target_url, headers=request.headers, params=request.args)

    # 대상 서버의 응답을 클라이언트에게 전달
    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

if __name__ == "__main__":
    # 프록시 서버를 5000번 포트에서 실행
    app.run(host="0.0.0.0", port=5000)
