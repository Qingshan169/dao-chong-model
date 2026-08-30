"""MCP 端到端握手测试：模拟客户端通过 stdio 与 mcp_server.py 通信。

运行：.venv/Scripts/python.exe tests/test_stdio.py
验证 initialize → tools/list → tools/call（含错误路径）完整链路。
"""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
SERVER = str(ROOT / "mcp_server.py")


def send(proc, payload):
    proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
    proc.stdin.flush()


def recv(proc):
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("服务器无响应（进程可能已退出）")
    return json.loads(line)


def main():
    proc = subprocess.Popen(
        [PY, SERVER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )
    try:
        # 1. initialize
        send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "0"},
            },
        })
        resp = recv(proc)
        assert resp.get("id") == 1, resp
        info = resp["result"]["serverInfo"]
        print(f"initialize OK: {info['name']} v{info['version']}")

        # 2. notifications/initialized
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 3. tools/list
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        resp = recv(proc)
        names = sorted(t["name"] for t in resp["result"]["tools"])
        expected = sorted([
            "dao_chong_get_concept", "dao_chong_get_related",
            "dao_chong_list_concepts", "dao_chong_retrieve",
        ])
        print("tools/list:", names)
        assert names == expected, names

        # 4. tools/call retrieve
        send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "dao_chong_retrieve",
                               "arguments": {"query": "冲气"}}})
        resp = recv(proc)
        text = resp["result"]["content"][0]["text"]
        print("tools/call retrieve 片段:", text[:160])
        assert "冲气" in text

        # 5. tools/call get_concept 错误路径
        send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                    "params": {"name": "dao_chong_get_concept",
                               "arguments": {"ref": "不存在"}}})
        resp = recv(proc)
        assert resp["result"].get("isError") is True, resp
        print("tools/call 错误路径 isError: True")

        print("\n端到端 MCP 握手 + 工具调用 全部通过")
        return 0
    finally:
        proc.stdin.close()
        proc.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
