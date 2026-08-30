"""道冲模型核心本体检索层（L2）。

把 dao-chong-schema.json（JSON-LD）加载为可查询对象，提供三类能力：
- retrieve(query)  按词/拼音检索概念（精确 > 名称 > 拼音 > 定义 > 属性/主张）
- get_concept(id)  取单个概念（按 @id / 中文名 / 无调拼音）
- get_related(id)  取关系邻域（入边 + 出边，含方向与对端概念）

数据量仅 14 概念，故用轻量结构化检索（无 embedding、零依赖），
比向量检索更精确、可解释；应用层全量概念接入后再升级向量检索。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "dao-chong-schema.json"

# 拼音去声调映射（ü 用 v 代，匹配输入法习惯）
_ACCENT_MAP = str.maketrans({
    "ā": "a", "á": "a", "ǎ": "a", "à": "a",
    "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
    "ē": "e", "é": "e", "ě": "e", "è": "e",
    "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
    "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
    "ǖ": "v", "ǘ": "v", "ǚ": "v", "ǜ": "v",
    "ń": "n", "ň": "n", "ǹ": "n", "ü": "v",
})


def normalize_pinyin(s: str) -> str:
    """去声调、去空格、小写，便于无调拼音检索。"""
    return s.translate(_ACCENT_MAP).replace(" ", "").lower()


class Ontology:
    """加载并查询 dao-chong-schema.json。"""

    def __init__(self, path: Path | str | None = None):
        p = Path(path) if path else SCHEMA_PATH
        with open(p, encoding="utf-8") as f:
            self.data = json.load(f)
        self.concepts: list[dict] = self.data["concepts"]
        self.relations: list[dict] = self.data["relations"]
        self.model_id: str = self.data["@id"]

        self._by_id: dict[str, dict] = {c["@id"]: c for c in self.concepts}
        self._by_name: dict[str, dict] = {c["name"]: c for c in self.concepts}
        self._by_pinyin: dict[str, dict] = {
            normalize_pinyin(c.get("pinyin", "")): c for c in self.concepts
        }

    # ---- 取单个概念 -------------------------------------------------

    def get_concept(self, ref: str) -> dict | None:
        """按 @id、中文名或（无调）拼音取单个概念。"""
        if ref in self._by_id:
            return self._by_id[ref]
        if ref in self._by_name:
            return self._by_name[ref]
        norm = normalize_pinyin(ref)
        if norm in self._by_pinyin:
            return self._by_pinyin[norm]
        return None

    def _resolve_id(self, ref: str) -> str | None:
        c = self.get_concept(ref)
        return c["@id"] if c else None

    # ---- 检索 -------------------------------------------------------

    def retrieve(self, query: str, limit: int = 5) -> list[dict]:
        """按 query 检索概念，返回按分数降序的 [{concept, score}] 列表。"""
        q = (query or "").strip()
        if not q:
            return []
        q_norm = normalize_pinyin(q)
        scored = []
        for c in self.concepts:
            s = self._score(q, q_norm, c)
            if s > 0:
                scored.append({"concept": c, "score": s})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def _score(self, q: str, q_norm: str, c: dict) -> float:
        name = c["name"]
        pinyin_norm = normalize_pinyin(c.get("pinyin", ""))
        score = 0.0

        # 精确匹配：中文名或 @id
        if q in (name, c["@id"]):
            score += 100
        # 精确匹配：无调拼音或小写 @id
        if q_norm and q_norm in (pinyin_norm, c["@id"].lower()):
            score += 100

        # 名称子串（双向）
        if q in name or name in q:
            score += 60

        # 拼音子串 / 前缀
        if q_norm and len(q_norm) >= 3 and (q_norm in pinyin_norm or pinyin_norm.startswith(q_norm)):
            score += 40

        # 定义命中
        if q in c.get("definition", ""):
            score += 25

        # 属性 / 使用语法 / 可证伪主张命中
        for attr in c.get("attributes", []):
            if q in attr:
                score += 12
        for g in c.get("usage_grammar", []):
            if q in g:
                score += 8
        for claim in c.get("falsifiable_claims", []):
            if q in claim:
                score += 8
        return score

    # ---- 关系邻域 ---------------------------------------------------

    def get_related(self, ref: str) -> list[dict]:
        """返回与某概念直接相连的关系（含方向与对端概念）。"""
        cid = self._resolve_id(ref)
        if not cid:
            return []
        out: list[dict] = []
        for r in self.relations:
            if r["from"] == cid:
                out.append({
                    "direction": "out",
                    "type": r["type"],
                    "label": r["label"],
                    "relation": r,
                    "target": self._by_id.get(r["to"]),
                })
            elif r["to"] == cid:
                out.append({
                    "direction": "in",
                    "type": r["type"],
                    "label": r["label"],
                    "relation": r,
                    "source": self._by_id.get(r["from"]),
                })
        return out

    # ---- 概念卡片（供 CLI / 下游系统） --------------------------------

    def summarize(self, ref: str) -> dict | None:
        """概念卡片：定义 + 本体地位 + 属性 + 可证伪主张 + 邻域。"""
        c = self.get_concept(ref)
        if not c:
            return None
        return {
            "id": c["@id"],
            "name": c["name"],
            "pinyin": c.get("pinyin", ""),
            "category": c.get("category", ""),
            "definition": c.get("definition", ""),
            "ontology_status": c.get("ontology_status", ""),
            "attributes": c.get("attributes", []),
            "usage_grammar": c.get("usage_grammar", []),
            "falsifiable_claims": c.get("falsifiable_claims", []),
            "relations": self.get_related(c["@id"]),
        }
