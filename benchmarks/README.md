# 道冲模型可证伪主张评测基准（L4）

把道冲模型的 `falsifiable_claims`（可证伪主张）变成第三方能一键复现的实验框架。这是工程化路线 L4——「可验证基准」。

## 核心结论（先读这个）

道冲模型有 **10 条** 可证伪主张。经对抗验证（adversarial verification），**只有 1 条当前真正可证伪**：

| 结论 | 数量 | 说明 |
|---|---|---|
| ✅ 真可证伪 | 1 | `meta:ding-shu-reduces-offtopic`（定枢减少偏题）——有天然 off 对照，判据清晰非同义反复 |
| ⚠️ 伪可证伪 | 9 | 同义反复 / 缺如型 / 异质捆绑，任何结果都能被圆过去 |

**这不是贬低，是照验替你量出的现状。** 9 条伪可证伪的主张，恰恰暴露了「把理论直觉写成可证伪命题」这个动作本身有多难——症候定义循环、停药必反弹由定义成立、解困/补益的异质捆绑，都是「理论自洽」和「可被证伪」之间的真实鸿沟。

每条的修正方案已写入 `claims.json`，是可复现实验设计的直接素材。

## 三路分派

| automation | 数量 | 运行器动作 | verdict |
|---|---|---|---|
| `automated` | 3 | `run_experiment`（实验框架就绪，等测试集） | `ready_for_test_set` |
| `needs_data` | 6 | `emit_experiment_design`（出 protocol + 判据） | `pending_data` |
| `manual` | 1 | `emit_falsification_criterion`（出证伪判据 + 量表） | `pending_manual` |

- **automated（3 条 meta 消融）**：定枢 / 照验 / 归藏，是 CQ-Agent 自身机制的 A/B 消融，纯软件可脚本化端到端跑，但需构造测试集（问题集 + 黄金标签）。
- **needs_data（6 条临床）**：冲阳症候、冲阴症候、相水困君火、解困优于补益、压制反弹、解困优于压制，需标注临床/试验数据，运行器出可复现 protocol + data_spec，数据到位即升为 automated。
- **manual（1 条概念）**：冲气无自性，证伪是「找出唯一由实体化解释导出的独立预测」，本质需人工文献/分析判读。

## 怎么跑

```bash
# 生成评测报告（校验 claims.json 与 schema 一致，按三路分派出报告）
python benchmarks/run_benchmark.py --run-id demo-001

# 产物
benchmarks/reports/demo-001/report.md     # 人类可读报告
benchmarks/reports/demo-001/results.json  # 机器可读汇总（含 claims_sha256）

# 从 schema 重新提取骨架（验证 claims.json 未被手抄错）
python benchmarks/extract_claims.py
```

## 为什么用对抗验证

普通做法是「自己给自己的主张设计实验」，这几乎必然陷入**伪可证伪**：把同义反复、必然为真、或不可测的主张包装成「可证伪」。

对抗验证的做法：先让多视角（临床方法学 / Agent 评测 / 科学哲学证伪主义 / 可复现工程）独立设计实验，再让**专门找漏洞的对抗审查员**逐条检查「这条实验真的能否证这条主张吗」，警惕六种陷阱——伪可证伪、循环论证、混淆变量、相关当因果、必然为真包装成可证伪、终点模糊到不可测。

结果就是上面的结论：10 条里 9 条没过审。**这正是评测基准存在的意义**——它不是为了证明「我们可验证」，而是为了诚实地标出「哪些真可验证、哪些还需要重做」。

## 文件

| 文件 | 作用 |
|---|---|
| `claims.json` | 评测集：10 条 claim（骨架 + 对抗裁决 + 修正方案） |
| `extract_claims.py` | 从 schema 提取骨架，校验 claims.json 一致 |
| `run_benchmark.py` | 评测运行器：加载 → 校验 → 三路分派 → 出报告 |
| `reports/` | 每次运行的报告（report.md + results.json） |

## 方法论承诺（判据预先注册）

每条 claim 的 `falsification_criterion`（证伪判据）**预先注册在 claims.json 内**，运行器只做机械对比、不做解释。修正后的方案也都加了「预承诺」条款——例如「被否证的是理论命题本身，不得以『量表没做对』为由重新定义逃避否证」——这正是对抗验证逼出来的纪律。
