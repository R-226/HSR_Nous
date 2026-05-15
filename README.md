# HSR_Nous：博识尊驱动战斗分析与配装优化

本项目面向《崩坏：星穹铁道》的配装与配队优化，采用 ReAct 风格的多 Agent 闭环，将目标转化为可验证、可复现的决策结果。

## 目标

- 用数据与仿真替代纯经验型配装决策
- 系统性比较遗器、光锥、配速与队伍构成
- 输出可解释结论与清晰的方案权衡

## 项目结构

```
src/hsr_nous/
├── pipeline/          # 数据管道：从 StarRailRes 加载游戏数据
│   ├── loader.py      # JSON 数据加载器
│   ├── update.py      # 从 GitHub 更新数据
│   └── README.md      # pipeline 模块详细文档
│
├── raw_schema/        # 原始数据模型（对应 StarRailRes schema）
│   ├── character.py
│   ├── light_cone.py
│   ├── relic.py
│   └── loader.py      # 原始数据 -> Python 对象
│
├── sim_schema/        # 仿真器输入格式（sim 的唯一输入）
│   ├── README.md      # 完整数据格式设计文档（含公式、buff、策略 DSL）
│   ├── actor.py       # 参战单位（角色/敌人）
│   ├── action.py      # 技能/普攻/终结技
│   ├── encounter.py   # 关卡/波次配置
│   ├── modifiers.py   # 增益/减益/特效
│   └── policy.py      # 策略 DSL（Rule-based + 参数化）
│
├── adapters/          # 适配层：raw_schema -> sim_schema
│   ├── character_adapter.py
│   ├── skill_adapter.py
│   └── encounter_adapter.py
│
├── sim/               # 战斗模拟器（纯仿真核心，只依赖 sim_schema）
│   ├── engine.py      # 回合制战斗循环 + PolicyInterpreter
│   ├── timeline.py    # 行动序管理
│   └── resolver.py    # 伤害/治疗/效果结算
│
├── agents/            # ReAct 风格多 Agent
│   ├── planner.py     # 目标拆解与评估计划
│   ├── builder.py     # 配装与配队候选生成
│   ├── search.py      # 参数空间搜索
│   ├── evaluator.py   # 仿真运行与指标计算
│   └── explainer.py   # 对比结论与可解释分析
│
└── api/               # 编排层
    └── orchestrator.py  # 多 Agent 协作闭环

tests/                 # 测试目录

data/                  # 数据目录（gitignored）
└── starrailres/       # StarRailRes 索引数据
```

## 模块边界

| 模块 | 可以 import | 不能 import |
|------|------------|------------|
| `pipeline/` | 无（纯工具） | `raw_schema`, `sim_schema`, `sim` |
| `raw_schema/` | 无（纯数据结构） | `sim_schema`, `sim` |
| `adapters/` | `raw_schema` | `sim`（只输出 sim_schema，不调用 sim） |
| `sim/` | `sim_schema` | `raw_schema`, `pipeline`, `adapters` |
| `agents/` | `adapters`, `sim` | `pipeline` |

数据管道与战斗模拟器完全解耦：

```
StarRailRes (JSON) ──[pipeline.loader]──→ Python 对象
                                              │
                                              ▼
                                         [adapters]
                                              │
                                              ▼
                                    sim_schema (Actor/Action...)
                                              │
                                              ▼
                                    [sim.engine] ──→ 仿真结果
```

## 核心设计亮点

### 事件-响应模型

技能、行迹、星魂、光锥、遗器本质都是**事件监听器**。所有持续效果通过 `Modifier` 表达，触发时机包括 `on_battle_start`、`on_turn_start`、`on_before_hit`、`on_kill` 等。

详见 [`sim_schema/README.md`](src/hsr_nous/sim_schema/README.md)。

### 策略 DSL

战斗策略采用 **Rule-based + 参数化混合** 设计：

```yaml
policy:
  action_rules:
    - condition: "energy >= ULT_THRESHOLD"
      action: "ultimate"
      priority: 100
    - condition: "skill_points > 0"
      action: "skill"
      priority: 50
    - condition: "true"
      action: "basic"
      priority: 0
  parameters:
    ULT_THRESHOLD: 120
```

- 模拟器直接 interpret，100% deterministic
- 参数（如 `ULT_THRESHOLD`）可独立调优，适合贝叶斯优化
- LLM 容易生成结构化的规则而非自然语言

详见 [`sim_schema/README.md`](src/hsr_nous/sim_schema/README.md) 第 9 节。

## 安装

使用 `uv`：

```bash
uv venv
uv pip install -e ".[dev]"
```

## CLI 命令

```bash
# 更新游戏数据（从 StarRailRes GitHub 拉取）
hsr-data-update

# 指定数据目录
hsr-data-update --data-dir ./my_data
```

## 运行测试

```bash
pytest tests/ -v
```

## 决策闭环（ReAct）

1. **解析**：Planner 拆解目标与约束
2. **生成**：Builder 提出候选配装与队伍
3. **搜索**：Search 在参数空间细调（副词条/配速/策略参数）
4. **仿真**：Evaluator 运行战斗模拟并聚合指标
5. **对比**：Explainer 基于指标排序生成可解释报告
6. **迭代**：在预算内收敛到最优解

## 关键指标

- DPS 与伤害分布
- 生存率 / 存活时间
- 能量循环与终结技覆盖率
- 行动序稳定性 / 配速可行性
- RNG 敏感性（方差、最差情况）

## MVP 范围

- 单队伍（4 人）与单关卡
- 限定遗器套装与光锥列表
- 固定随机种子与确定性仿真
- 简化的搜索预算与启发式策略

## 下一步

- [ ] 完善 `raw_schema` 模型（字段映射与验证）
- [ ] 实现 `adapters` 转换逻辑
- [ ] 实现表达式引擎（替换 eval）
- [ ] 完善 `sim.engine` 战斗循环（行动序、伤害结算、buff 管理）
- [ ] 添加 Agent 接口与评估闭环
- [ ] 构建基础 CLI 用于实验
