"""从 dao-chong-schema.json 自动提取全部 falsifiable_claims，生成评测集骨架。

这是「可复现」的第一环：评测集的原始数据不手抄，而是从本体文件确定性生成，
schema 一变，评测集骨架随之更新。

输出每条 claim 的骨架字段（本体固有信息）：
- id / concept_id / concept / category / claim / source
验证方案字段（method / metric / falsification_criterion / automation）由 L4 合成结果另行填入。

用法：python benchmarks/extract_claims.py [--out 输出文件]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dao_chong.ontology import Ontology  # noqa: E402


def slugify(concept_id: str) -> str:
    """dcx:chong-qi -> chong-qi"""
    return concept_id.replace("dcx:", "")


def extract() -> list[dict]:
    o = Ontology()
    claims = []
    for c in o.concepts:
        for i, text in enumerate(c.get("falsifiable_claims", []), start=1):
            claims.append({
                "id": f"{slugify(c['@id'])}:{i}",
                "concept_id": c["@id"],
                "concept": c["name"],
                "category": c.get("category", ""),
                "claim": text,
                "source": c.get("source", ""),
            })
    return claims


def main() -> int:
    claims = extract()
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else str(
        ROOT / "benchmarks" / "claims.skeleton.json"
    )
    Path(out).write_text(
        json.dumps({"claims": claims}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"提取 {len(claims)} 条 falsifiable_claims → {out}")
    for cl in claims:
        print(f"  {cl['id']:<45} {cl['concept']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
