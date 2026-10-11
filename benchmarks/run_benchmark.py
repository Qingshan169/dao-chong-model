"""道冲模型可证伪主张评测运行器（L4）。

加载 claims.json，校验其与 dao-chong-schema.json 的一致性，按 automation 三路分派，
输出可复现的报告（report.md + results.json）。

三路分派：
- automated（3 条 meta 消融）：实验框架就绪，输出测试集规格，等测试集接入即一键跑
- needs_data（12 条临床）：emit_experiment_design → 实验设计（protocol + 判据）
- manual（1 条概念）：emit_falsification_criterion → 证伪判据 + 评分量表

核心纪律（来自对抗验证）：判据预先注册在 claim 内，运行器只做机械对比、不做解释；
「可验证」本身被严格检验——当前 16 条中 7 条真可证伪（核心 1 + 应用层 6），9 条伪可证伪须按修正方案重设计。

用法：python benchmarks/run_benchmark.py [--run-id <id>] [--out-dir <dir>]
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dao_chong.ontology import SCHEMA_PATH  # noqa: E402

BENCH_DIR = ROOT / "benchmarks"
CLAIMS_PATH = BENCH_DIR / "claims.json"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_claims(path: Path = CLAIMS_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_against_schema(claims_data: dict) -> list[str]:
    """校验 claims.json 的 claim 文本与 schema 的 falsifiable_claims 逐字一致。"""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_claims = [
        text for c in schema["concepts"] for text in c.get("falsifiable_claims", [])
    ]
    json_claims = [c["claim"] for c in claims_data["claims"]]
    errors = []
    if len(schema_claims) != len(json_claims):
        errors.append(
            f"数量不一致：schema {len(schema_claims)} vs claims.json {len(json_claims)}"
        )
    for s in schema_claims:
        if s not in json_claims:
            errors.append(f"schema 中的 claim 未在 claims.json 找到：{s[:30]}…")
    for j in json_claims:
        if j not in schema_claims:
            errors.append(f"claims.json 中的 claim 不在 schema：{j[:30]}…")
    return errors


def emit_experiment_design(claim: dict) -> dict:
    """needs_data：组装可复现实验设计。"""
    return {
        "claim_id": claim["id"],
        "automation": claim["automation"],
        "verdict": "pending_data",
        "verification_type": claim["verification_type"],
        "is_genuinely_falsifiable": claim["adversarial_verdict"]["is_genuinely_falsifiable"],
        "protocol": claim["method"],
        "metric": claim["metric"],
        "falsification_criterion": claim["falsification_criterion"],
        "note": "数据到位即升为 automated；判据已预注册，禁止事后修改。",
    }


def emit_falsification_criterion(claim: dict) -> dict:
    """manual：组装证伪判据 + 评分量表。"""
    return {
        "claim_id": claim["id"],
        "automation": claim["automation"],
        "verdict": "pending_manual",
        "verification_type": claim["verification_type"],
        "is_genuinely_falsifiable": claim["adversarial_verdict"]["is_genuinely_falsifiable"],
        "falsification_criterion": claim["falsification_criterion"],
        "rubric": claim["method"],
        "note": "需人工文献/分析判读；划界 gate 给不出可观察伪实例即判不可证伪。",
    }


def experiment_framework(claim: dict) -> dict:
    """automated：实验框架就绪，输出测试集规格，等测试集接入。"""
    return {
        "claim_id": claim["id"],
        "automation": claim["automation"],
        "verdict": "ready_for_test_set",
        "verification_type": claim["verification_type"],
        "is_genuinely_falsifiable": claim["adversarial_verdict"]["is_genuinely_falsifiable"],
        "experiment": claim["method"],
        "metric": claim["metric"],
        "falsification_criterion": claim["falsification_criterion"],
        "runner_step": claim["runner_step"],
        "note": "实验函数接口已定义，缺测试集 + 黄金标签，接入即一键跑。",
    }


def dispatch(claim: dict) -> dict:
    if claim["automation"] == "needs_data":
        return emit_experiment_design(claim)
    if claim["automation"] == "manual":
        return emit_falsification_criterion(claim)
    return experiment_framework(claim)


def _render_markdown(claims_data: dict, run_id: str, results_data: dict) -> str:
    s = results_data["summary"]
    lines = [
        "# 道冲模型可证伪主张评测报告",
        "",
        f"- run_id：`{run_id}`",
        f"- claims_sha256：`{results_data['claims_sha256'][:16]}…`",
        f"- schema_version：`{claims_data['schema_version']}`",
        "",
        "## 摘要",
        "",
        f"- 主张总数：**{s['total']}**",
        f"- 真正可证伪：**{s['genuinely_falsifiable']}** 条（其余为伪可证伪，须按修正方案重设计）",
        f"- automated（可跑实验）：{s['automated']} 条",
        f"- needs_data（需临床数据）：{s['needs_data']} 条",
        f"- manual（需人工判读）：{s['manual']} 条",
        "",
        f"> 核心结论：道冲模型有 {s['total']} 条可证伪主张，经对抗验证 **{s['genuinely_falsifiable']} 条当前真正可证伪**。",
        "> 核心本体 10 条中 9 条是「伪可证伪」——同义反复（症候定义循环、停药必反弹由定义成立）、",
        "> 缺如型主张（逻辑上无法否证）、或靠异质捆绑圆过去；应用层 6 条新 claim 经对抗验证全部真可证伪。",
        "",
        "## 结果（按 automation 分派）",
        "",
    ]
    for group in ("automated", "needs_data", "manual"):
        group_claims = [c for c in claims_data["claims"] if c["automation"] == group]
        title = {"automated": "可跑实验（实验框架就绪）", "needs_data": "需临床数据（实验设计已生成）", "manual": "需人工判读（证伪判据已生成）"}[group]
        lines.append(f"### {title}（{len(group_claims)} 条）")
        lines.append("")
        for c in group_claims:
            v = c["adversarial_verdict"]
            flag = "✅ 真可证伪" if v["is_genuinely_falsifiable"] else "⚠️ 伪可证伪"
            lines.append(f"#### {c['id']} — {c['concept']}  [{flag}]")
            lines.append("")
            lines.append(f"**主张**：{c['claim']}")
            lines.append("")
            lines.append(f"**为什么（对抗验证）**：{v['weakness']}")
            lines.append("")
            lines.append(f"**如何修正**：{v['suggestion']}")
            lines.append("")
            lines.append(f"**证伪判据**：{c['falsification_criterion']}")
            lines.append("")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*报告由 run_benchmark.py 机械生成；判据预先注册在 claims.json 内，运行器不做解释。*")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = list(argv) if argv is not None else sys.argv[1:]
    run_id = None
    out_dir = BENCH_DIR / "reports"
    i = 0
    while i < len(args):
        if args[i] == "--run-id" and i + 1 < len(args):
            run_id = args[i + 1]
            i += 2
        elif args[i] == "--out-dir" and i + 1 < len(args):
            out_dir = Path(args[i + 1])
            i += 2
        else:
            i += 1

    claims_data = load_claims()
    errors = validate_against_schema(claims_data)
    if errors:
        print("校验失败：claims.json 与 dao-chong-schema.json 不一致：")
        for e in errors:
            print(f"  - {e}")
        return 1

    run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
    results = [dispatch(c) for c in claims_data["claims"]]
    results_data = {
        "run_id": run_id,
        "schema_version": claims_data["schema_version"],
        "claims_sha256": _sha256(json.dumps(claims_data["claims"], ensure_ascii=False, sort_keys=True)),
        "summary": {
            "total": len(results),
            "automated": sum(1 for c in claims_data["claims"] if c["automation"] == "automated"),
            "needs_data": sum(1 for c in claims_data["claims"] if c["automation"] == "needs_data"),
            "manual": sum(1 for c in claims_data["claims"] if c["automation"] == "manual"),
            "genuinely_falsifiable": sum(
                1 for c in claims_data["claims"] if c["adversarial_verdict"]["is_genuinely_falsifiable"]
            ),
        },
        "results": results,
    }
    markdown = _render_markdown(claims_data, run_id, results_data)

    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.md").write_text(markdown, encoding="utf-8")
    (run_dir / "results.json").write_text(
        json.dumps(results_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    s = results_data["summary"]
    print(f"评测运行完成 → {run_dir}")
    print(f"  主张 {s['total']} 条：automated {s['automated']} / needs_data {s['needs_data']} / manual {s['manual']}")
    print(f"  真正可证伪：{s['genuinely_falsifiable']} / {s['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
