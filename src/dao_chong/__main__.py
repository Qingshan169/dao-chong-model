"""CLI 入口：python -m dao_chong <command> <arg>

命令：
  retrieve <query>  按词/拼音检索概念
  concept <ref>     取单个概念完整卡片
  related <ref>     取概念的关系邻域
"""

from __future__ import annotations

import argparse
import json

from .ontology import Ontology


def _print_hit(hit: dict) -> None:
    c = hit["concept"]
    print(f"[{hit['score']:>6.1f}] {c['@id']}  {c['name']}（{c.get('category', '')}）")
    print(f"        {c.get('definition', '')[:64]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dao_chong", description="道冲模型本体检索")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_retr = sub.add_parser("retrieve", help="按词/拼音检索概念")
    p_retr.add_argument("query")
    p_retr.add_argument("-n", "--limit", type=int, default=5)

    p_get = sub.add_parser("concept", help="取单个概念完整卡片")
    p_get.add_argument("ref")

    p_rel = sub.add_parser("related", help="取概念的关系邻域")
    p_rel.add_argument("ref")

    args = parser.parse_args(argv)
    onto = Ontology()

    if args.cmd == "retrieve":
        hits = onto.retrieve(args.query, limit=args.limit)
        if not hits:
            print("无匹配。")
            return 1
        for h in hits:
            _print_hit(h)
    elif args.cmd == "concept":
        card = onto.summarize(args.ref)
        if not card:
            print(f"未找到：{args.ref}")
            return 1
        print(json.dumps(card, ensure_ascii=False, indent=2))
    elif args.cmd == "related":
        rels = onto.get_related(args.ref)
        if not rels:
            print(f"未找到或无边：{args.ref}")
            return 1
        for r in rels:
            other = r.get("target") or r.get("source") or {}
            arrow = "→" if r["direction"] == "out" else "←"
            print(f"{arrow} {r['type']:<18} {other.get('name', '?')}  [{r['label']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
