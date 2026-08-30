"""道冲模型 MCP 服务器（L3）。

把 L2 的检索层暴露成 MCP 工具，任何接入 MCP 的 agent（Claude Code、CQ-Agent 等）
都能在需要时直接查道冲本体，而非全网搜「道冲模型」。

启动：.venv/Scripts/python.exe mcp_server.py（stdio 常驻进程）

四个工具：
- dao_chong_retrieve(query, limit)   按词/拼音检索概念
- dao_chong_get_concept(ref)         取单个概念完整卡片
- dao_chong_get_related(ref)         取概念关系邻域
- dao_chong_list_concepts()          列出全部概念
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

# MCP 服务器可能从任意 cwd 启动，先确保 src/dao_chong 可导入
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dao_chong.ontology import Ontology  # noqa: E402


mcp = MCPServer(
    "dao-chong-model",
    version="0.2.0",
    instructions=(
        "道冲阴阳和合系统模型（Dao-Chong Model）核心本体查询工具。"
        "以「冲气」为核心的生命系统解释框架：冲气无自性，是关系—过程动态；"
        "体用象道为四重观察脚手架；流动即稳定为核心命题；疾病本质是「困」（可化空间缩小）。"
        "查概念定义/本体地位/可证伪主张用 dao_chong_get_concept；"
        "按词或拼音检索概念用 dao_chong_retrieve；"
        "查概念关系邻域用 dao_chong_get_related；"
        "不知道有哪些概念时先 dao_chong_list_concepts。"
    ),
)

_onto = Ontology()


@mcp.tool()
def dao_chong_retrieve(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """按词或拼音检索道冲模型概念，返回按相关度排序的概念摘要。query 可为中文（如「冲气」）或无调拼音（如「xianghuo」）。"""
    hits = _onto.retrieve(query, limit=limit)
    return [
        {
            "id": h["concept"]["@id"],
            "name": h["concept"]["name"],
            "pinyin": h["concept"].get("pinyin", ""),
            "category": h["concept"].get("category", ""),
            "definition": h["concept"].get("definition", ""),
            "score": h["score"],
        }
        for h in hits
    ]


@mcp.tool()
def dao_chong_get_concept(ref: str) -> dict[str, Any]:
    """取单个概念的完整卡片：定义、本体地位、属性、可证伪主张、关系邻域。ref 可为 @id、中文名或无调拼音。"""
    card = _onto.summarize(ref)
    if card is None:
        raise ValueError(f"未找到概念：{ref}")
    return card


@mcp.tool()
def dao_chong_get_related(ref: str) -> list[dict[str, Any]]:
    """取概念的关系邻域（入边 + 出边，含方向、关系类型、对端概念与说明）。"""
    rels = _onto.get_related(ref)
    if not rels:
        raise ValueError(f"未找到概念或无关系：{ref}")
    return [
        {
            "direction": r["direction"],
            "type": r["type"],
            "label": r["label"],
            "other_id": (r.get("target") or r.get("source") or {}).get("@id"),
            "other_name": (r.get("target") or r.get("source") or {}).get("name"),
            "description": r["relation"].get("description", ""),
        }
        for r in rels
    ]


@mcp.tool()
def dao_chong_list_concepts() -> list[dict[str, Any]]:
    """列出道冲模型全部概念（id/名称/拼音/类别/一句话定义），供按需深查。"""
    return [
        {
            "id": c["@id"],
            "name": c["name"],
            "pinyin": c.get("pinyin", ""),
            "category": c.get("category", ""),
            "definition": c.get("definition", ""),
        }
        for c in _onto.concepts
    ]


if __name__ == "__main__":
    mcp.run()
