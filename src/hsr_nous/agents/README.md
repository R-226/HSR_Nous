# Agents ReAct 多 Agent

ReAct 风格五 Agent 协作系统。每个 Agent 负责决策闭环中的一个环节。

## 文件说明

| 文件 | 职责 |
|------|------|
| `planner.py` | `PlannerAgent`：目标拆解与评估计划 |
| `builder.py` | `BuilderAgent`：配装与配队候选生成 |
| `search.py` | `SearchAgent`：参数空间搜索（副词条/配速/策略参数） |
| `evaluator.py` | `EvaluatorAgent`：仿真运行与指标计算 |
| `explainer.py` | `ExplainerAgent`：对比结论与可解释分析 |

## 设计决策

- Agent 之间通过结构化数据传递，不直接调用彼此的方法
- `EvaluatorAgent` 是唯一能调用 `sim` 的 Agent
- `BuilderAgent` 和 `SearchAgent` 通过 `adapters` 使用原始数据
- 策略参数（如 `ULT_THRESHOLD`）是 `SearchAgent` 的搜索空间

## 决策闭环

1. `Planner` 拆解目标 → 2. `Builder` 生成候选 → 3. `Search` 细调参数 → 4. `Evaluator` 运行仿真 → 5. `Explainer` 生成报告 → 6. 迭代优化

## 修改记录

- 初始创建：占位类，方法待实现
