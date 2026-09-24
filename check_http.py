"""check_http.py：起服务、按脚本发请求，打印验收面（无头可跑）。"""
import json
import os
import sys
import threading
import urllib.error
import urllib.request

from server import serve


def call(method, url, body=None, headers=None):
    request = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers), response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read().decode()


def main() -> int:
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "sample/sequence.json", encoding="utf-8"))
    server = serve(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:%d" % server.server_port
    statuses = []
    etags = []
    conflicts = 0
    for step in spec["steps"]:
        if step["op"] == "get":
            status, headers, body = call("GET", base + "/kv/" + step["key"])
        else:
            headers = {"Content-Type": "application/json"}
            if step.get("if_match"):
                headers["If-Match"] = etags[-1] if etags else step["if_match"]
            status, resp_headers, body = call("PUT", base + "/kv/" + step["key"],
                                              json.dumps({"value": step["value"]}).encode(), headers)
            etags.append(resp_headers.get("ETag", ""))
            if status == 409:
                conflicts += 1
        statuses.append(status)
    print("状态码序列 =", statuses)
    print("冲突条数 =", conflicts)
    print("最终版本 =", json.loads(call("GET", base + "/kv/" + spec["steps"][-1]["key"])[2]))
    print("无 If-Match 的覆盖仍生效 =", spec["legacy_overwrite"])
    print("步骤数 =", len(spec["steps"]))
    print("ETag 非空条数 =", sum(1 for item in etags if item))
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
