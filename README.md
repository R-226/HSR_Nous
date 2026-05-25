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
│   ├── character.py   # 角色
│   ├── light_cone.py  # 光锥
│   ├── relic.py       # 遗器
│   ├── enemy.py       # 敌人
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

docs/                  # 战斗规则文档（模拟器"唯一事实来源"）
├── README.md          # 文档导航与使用说明
├── game_rules.md      # 战斗规则总览
└── mechanics/         # 详细机制文档
    ├── damage_formula.md    # 伤害公式
    ├── buff_system.md       # 增益/减益系统
    ├── break_system.md      # 击破机制
    ├── energy_system.md     # 能量恢复
    ├── action_sequence.md   # 行动序列
    ├── base_stats.md        # 基础属性
    ├── skill_points.md      # 战技点
    ├── follow_up_attacks.md # 追加攻击
    ├── taunt_system.md      # 嘲讽系统
    ├── special_mechanics.md # 特殊机制
    └── elation_system.md    # 欢愉命途

tests/                 # 测试目录

data/                  # 数据目录（gitignored）
├── starrailres/       # StarRailRes 索引数据（en/ cn/ 等多语言）
└── enemies/           # 敌人数据（来源: theBowja/starrail-data）
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

## 开发工具

本项目使用 **Claude Code** 作为 AI 编程助手，接入以下模型：

- **MiMo**
- **Kimi**

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

# 更新简体中文数据
hsr-data-update --lang cn

# 下载敌人数据（来源: theBowja/starrail-data）
hsr-data-update --enemies

# 使用 SSH 下载（国内网络更快，需配置 GitHub SSH key）
hsr-data-update --ssh

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

- 支持敌人数据（弱点、抗性、技能），可用于更真实的战斗模拟
- 单队伍（4 人）与单关卡
- 限定遗器套装与光锥列表
- 固定随机种子与确定性仿真
- 简化的搜索预算与启发式策略

## 下一步

- [x] 完善 `raw_schema` 模型（字段映射与验证）
- [ ] **人工检查 `sim_schema` 设计是否完备且正确**（对照 `docs/` 游戏规则文档）
- [ ] 实现 `adapters` 转换逻辑
- [ ] 实现表达式引擎（替换 eval）
- [ ] 完善 `sim.engine` 战斗循环（行动序、伤害结算、buff 管理）
- [ ] 添加 Agent 接口与评估闭环
- [ ] 构建基础 CLI 用于实验
