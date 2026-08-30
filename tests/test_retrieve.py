"""检索层单元测试（标准库，无需 pytest）。

运行：python tests/test_retrieve.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dao_chong.ontology import Ontology, normalize_pinyin  # noqa: E402


def test_normalize_pinyin():
    assert normalize_pinyin("chōng qì") == "chongqi"
    assert normalize_pinyin("shū céng tiáo") == "shucengtiao"


def test_get_concept_by_id_name_pinyin():
    o = Ontology()
    assert o.get_concept("dcx:chong-qi")["name"] == "冲气"
    assert o.get_concept("冲气")["name"] == "冲气"
    assert o.get_concept("chong qi")["name"] == "冲气"
    assert o.get_concept("chongqi")["name"] == "冲气"
    assert o.get_concept("不存在") is None


def test_retrieve_top_is_chongqi():
    o = Ontology()
    hits = o.retrieve("冲气")
    assert hits, "应有结果"
    assert hits[0]["concept"]["@id"] == "dcx:chong-qi"


def test_retrieve_by_pinyin_prefix():
    o = Ontology()
    hits = o.retrieve("xiang huo")
    assert hits, "应有结果"
    assert hits[0]["concept"]["@id"] == "dcx:xiang-huo-xiang"


def test_retrieve_by_keyword():
    o = Ontology()
    hits = o.retrieve("化痰浊")
    assert any(h["concept"]["@id"] == "dcx:four-images-network" for h in hits)


def test_get_related_direction():
    o = Ontology()
    rels = o.get_related("dcx:chong-qi")
    kinds = {(r["direction"], r["type"]) for r in rels}
    assert ("out", "has_tendency") in kinds
    assert any(r["direction"] == "out" and r["type"] == "observed_via" for r in rels)


def test_summarize_contains_claims():
    o = Ontology()
    card = o.summarize("dcx:flow-as-stability")
    assert card is not None
    assert len(card["falsifiable_claims"]) >= 2


def test_all_concepts_and_relations_resolvable():
    o = Ontology()
    for c in o.concepts:
        assert o.get_concept(c["@id"]) is not None
    # 关系两端都指向合法实体（含模型自身 @id）
    valid = {c["@id"] for c in o.concepts} | {o.model_id}
    for r in o.relations:
        assert r["from"] in valid, r
        assert r["to"] in valid, r


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
