# 道冲阴阳和合系统模型（Dao-Chong Model）

> 以「冲气」为核心的完整生命系统解释框架——贯通中医临床与儒释道哲学，可工程化为可验证的 AI Agent 闭环。

## 这是什么

道冲模型不是封闭教条、不是万能理论，也不替代中医经典或现代医学。它是：

- 一套以「冲气」为核心的生命系统解释框架
- 连接中医经典与现代复杂系统思维的**转译语言**
- 辅助临床辨证、处方、反馈与修正的**思维操作系统**

核心判断一句话：**一切生命现象，都是冲气在不同层级、不同关系、不同时间、不同通道中的显现。**

## 核心概念

| 概念 | 一句定义 |
|---|---|
| **冲气** | 生命—世界关系网络中持续发生的生成、聚散、升降、开合、反馈、回返与再组织等关系—过程动态的高层操作性总称。**无自性，不是实体。** |
| **冲阳 / 冲阴** | 生命动力的两种根本趋向：冲阳外发外显（向动向温向明），冲阴内承内守（向静向润向藏）。 |
| **体用象道** | 观察冲气的四重认知脚手架：体（生命资本）、用（生命调控）、象（功能网络）、道（运行通道）。是脚手架，不是四个零件。 |
| **四象功能网络** | 把传统五脏重构为动力网络：君火象（明）、相火象（动）、肾水象（藏）、相水象（化降）。 |
| **疾病本质：困** | 疾病不是器官孤立损坏，而是可化、可转、可退、可复与未来可达空间缩小。分六类病理模式。 |
| **流动稳态** | 「不动」不是稳定是死亡；冲气的持续流动才是系统稳定性的真正保证。 |

## 三条限制声明

1. 冲气不是可被固定抓住的实体。
2. 体用象道不是生命真实存在的四个「零件」，只是认知脚手架。
3. 道冲模型不能替代现代医学诊断和治疗（尤其在肿瘤、感染、出血、血栓、梗阻、休克、器官衰竭等高风险场景）。

## 本体文件

`dao-chong-schema.json` 是道冲模型核心本体的机器可读版本（JSON-LD，W3C 语义网标准）：

- **14 个概念**、**15 条关系**，构成一张有向图，锚点是冲气。
- 每个概念含：`definition`（精确定义）、`ontology_status`（本体地位，防实体化）、`attributes`（关键属性）、`usage_grammar`（使用语法）、`falsifiable_claims`（可证伪主张）。
- `falsifiable_claims` 是可验证性的落点——把理论变成可被第三方检验的命题。

概念类别：`core_concept`（核心）/ `scaffold`（脚手架）/ `functional_network`（功能网络）/ `pathology_model`（病理模型）/ `principle`（原则）/ `operational_grammar`（操作语法）。

## 检索与调用

### 命令行检索（L2）

```bash
# 检索层零依赖（仅标准库），直接用系统 python 即可
PYTHONPATH=src python -m dao_chong retrieve "冲气"
PYTHONPATH=src python -m dao_chong concept "dcx:flow-as-stability"
PYTHONPATH=src python -m dao_chong related "dcx:chong-qi"
```

支持中文词、无调拼音（`xianghuo` → 相火象）与 `@id`（`dcx:chong-qi`）。

### MCP 接口（L3）

把道冲本体暴露成 MCP 工具，任何接入 MCP 的 agent（Claude Code、CQ-Agent 等）都能直接调用：

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e .   # 装 mcp 依赖并注册 dao-chong CLI
```

在 MCP 客户端（如 Claude Code 的 `.mcp.json`）加：

```json
{
  "mcpServers": {
    "dao-chong": {
      "command": "<本仓库路径>/.venv/Scripts/python.exe",
      "args": ["<本仓库路径>/mcp_server.py"]
    }
  }
}
```

四个工具：

| 工具 | 作用 |
|---|---|
| `dao_chong_retrieve(query, limit)` | 按词/拼音检索概念 |
| `dao_chong_get_concept(ref)` | 取单概念完整卡片（定义/本体地位/可证伪主张/关系） |
| `dao_chong_get_related(ref)` | 取概念关系邻域（in/out 方向 + 对端概念） |
| `dao_chong_list_concepts()` | 列出全部 14 个核心概念 |

## 可验证基准（L4）

`benchmarks/` 把每个概念的 `falsifiable_claims` 变成可复现实验框架。经对抗验证，10 条主张中**仅 1 条当前真正可证伪**，其余 9 条为伪可证伪（同义反复/缺如型/异质捆绑），每条附修正方案。详见 [benchmarks/](benchmarks/)。

```bash
python benchmarks/run_benchmark.py --run-id demo-001
```

## 路线图

- [x] **L1 结构化本体** — 本仓库的 `dao-chong-schema.json`
- [x] **L2 可检索知识库** — `src/dao_chong/`（轻量结构化检索 + CLI）
- [x] **L3 可调用接口** — `mcp_server.py`（MCP 工具，任何 agent 可调）
- [x] **L4 可验证基准** — `benchmarks/`（评测集 + 对抗验证 + 可复现实验框架）
- [ ] L5 应用层扩展 — 中西医结合、心学唯识、修行、养生等概念的补充结构化

## 署名

提出者：青山（llq），中医与道家哲学研究者。模型当前版本 V3（2026-08-15）。

---

*「道冲，而用之或不盈。」——《道德经》第四章*
