"""MCP 工具函数单元测试（需 venv python，因依赖 mcp 包）。

运行：.venv/Scripts/python.exe tests/test_mcp.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import mcp_server  # noqa: E402


def test_retrieve_returns_serializable():
    out = mcp_server.dao_chong_retrieve("冲气")
    assert isinstance(out, list) and out, "应有结果"
    assert out[0]["name"] == "冲气"
    json.dumps(out, ensure_ascii=False)  # 可 JSON 序列化


def test_get_concept_full_card():
    card = mcp_server.dao_chong_get_concept("dcx:flow-as-stability")
    assert card["name"] == "流动稳态"
    assert len(card["falsifiable_claims"]) >= 2
    json.dumps(card, ensure_ascii=False)


def test_get_concept_not_found_raises():
    try:
        mcp_server.dao_chong_get_concept("不存在")
        raise AssertionError("应抛 ValueError")
    except ValueError:
        pass


def test_get_related_direction():
    rels = mcp_server.dao_chong_get_related("dcx:chong-qi")
    kinds = {(r["direction"], r["type"]) for r in rels}
    assert ("out", "has_tendency") in kinds
    assert any(r["direction"] == "in" and r["type"] == "describes" for r in rels)
    json.dumps(rels, ensure_ascii=False)


def test_list_concepts_count():
    out = mcp_server.dao_chong_list_concepts()
    assert len(out) == 14
    assert out[0]["id"].startswith("dcx:")


def main():
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} 通过")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
