# Sim Schema 仿真器输入格式

本文档定义战斗模拟器的完整输入数据结构。核心设计原则：**一切机制都抽象为"事件-响应"模型**。

## 设计哲学

- **技能、行迹、星魂、光锥、遗器**：本质都是**事件监听器**——在特定时机触发效果
- **buff/debuff**：也是事件监听器——在持续期间内响应特定事件
- **伤害公式**：参数化配置，默认使用崩铁标准公式，支持自定义
- **纯数据驱动**：所有机制用 JSON/YAML 描述，不写硬编码逻辑

---

## 数据流概览

```
Encounter（关卡配置）
├── globals（全局状态：行动值、战技点、随机种子）
├── formula（伤害公式定义）
├── actors[]（参战单位）
│   ├── base_stats（基础属性：生命、攻击、防御、速度等）
│   ├── actions[]（技能列表）
│   ├── traces[]（行迹）
│   ├── eidolons[]（星魂）
│   ├── light_cone（光锥）
│   └── relics[]（遗器 + 具体数值）
└── modifiers[]（初始 buff，如环境效果）
```

---

## 1. 伤害公式 (Formula)

公式单独定义，参数从运行时状态读取。

```yaml
formula:
  damage:
    # 崩铁标准伤害公式
    expression: "base_dmg * dmg_multiplier * (1 + dmg_bonus) * def_multiplier * res_multiplier * (1 - toughness_reduction_bonus) * crit_multiplier"
    parameters:
      - name: base_dmg
        source: skill_scaling  # 从技能倍率表读取
      - name: dmg_multiplier
        source: actor_stat_atk  # 攻击者攻击力
      - name: def_multiplier
        expression: "target_def / (target_def + 200 + 10 * attacker_level)"
      - name: res_multiplier
        expression: "1 + resistance_delta"
      - name: crit_multiplier
        expression: "1 + (is_crit ? crit_dmg : 0)"

  heal:
    expression: "heal_scaling * (1 + heal_bonus) + outgoing_heal"

  shield:
    expression: "shield_scaling * (1 + shield_bonus)"

  break_damage:
    expression: "base_break * break_level_multiplier * (1 + break_effect) * toughness_multiplier"
```

**设计意图**：
- 公式与机制解耦，想改公式只需改这里
- `expression` 用简单数学表达式，运行时求值
- `source` 指向运行时状态中的某个值
- 支持自定义新公式（如追加伤害、持续伤害等）

---

## 2. 全局状态 (Globals)

```yaml
globals:
  action_value: 10000        # 行动值上限（崩铁标准）
  skill_points:
    max: 5
    current: 3
  # 可扩展：场地效果、环境变量等
```

---

## 3. 参战单位 (Actor)

Actor 分为角色和怪物，共用同一套结构。

```yaml
actor:
  actor_id: "1001"
  name: "三月七"
  actor_type: "character"    # character | monster
  level: 80
  max_toughness: 100         # 韧性上限（怪物用）

  # ========== 基础属性（只定义变量，值由 adapter 填入）==========
  base_stats:
    hp: 1047
    atk: 564
    def: 485
    spd: 101
    crit_rate: 0.05
    crit_dmg: 0.50
    break_effect: 0.0
    effect_hit: 0.0
    effect_res: 0.0
    energy_regen: 1.0
    heal_bonus: 0.0
    shield_bonus: 0.0
    dmg_bonus: {}              # 按属性分类：{physical: 0.0, fire: 0.1, ...}
    resistance: {}             # 属性抗性
    weakness: ["ice", "wind"]  # 弱点属性

  # ========== 技能 ==========
  actions:
    - action_id: "1001_basic"
      name: "寒冰之箭"
      action_type: "basic"           # basic | skill | ultimate | talent | follow_up
      target_type: "enemy_single"    # enemy_single | enemy_blast | enemy_aoe | ally_single | ally_aoe | self
      damage_type: "ice"
      energy_gain: 20
      # 技能效果：事件响应列表
      effects:
        - trigger: "on_cast"         # 释放时触发
          target: "primary_target"
          effect_type: "deal_damage"
          formula: "damage"
          scaling: 0.5               # 倍率 50%
        - trigger: "on_cast"
          target: "self"
          effect_type: "gain_energy"
          value: 20

    - action_id: "1001_skill"
      name: "可爱即是正义"
      action_type: "skill"
      target_type: "ally_single"
      skill_point_cost: 1
      effects:
        - trigger: "on_cast"
          target: "primary_target"
          effect_type: "apply_modifier"
          modifier_id: "MOD_1001_SHIELD"
          duration: 3

    - action_id: "1001_ultimate"
      name: "冰刻剑雨之时"
      action_type: "ultimate"
      target_type: "enemy_aoe"
      energy_cost: 120
      effects:
        - trigger: "on_cast"
          target: "all_enemies"
          effect_type: "deal_damage"
          formula: "damage"
          scaling: 1.5
        - trigger: "on_cast"
          target: "random_enemy"
          effect_type: "apply_modifier"
          modifier_id: "MOD_1001_FREEZE"
          duration: 1
          chance: 0.5                  # 50% 基础概率，受效果命中影响

  # ========== 行迹（被动能力）==========
  traces:
    - trace_id: "T_1001_1"
      name: "公主殿下"
      effects:
        - trigger: "on_battle_start"
          target: "self"
          effect_type: "apply_modifier"
          modifier_id: "MOD_1001_TRACE_CRIT"
          duration: 0                   # 0 表示永久

  # ========== 星魂 ==========
  eidolons:
    - eidolon_id: "E_1001_1"
      name: "记忆中的你"
      unlocked: true
      effects:
        - trigger: "on_shield_apply"
          condition: "modifier_id == MOD_1001_SHIELD"
          target: "shielded_target"
          effect_type: "heal"
          formula: "heal"
          scaling: 0.3                  # 回合同等生命值 30%

  # ========== 光锥 ==========
  light_cone:
    light_cone_id: "20001"
    name: "余生的第一天"
    superimposition: 1
    effects:
      - trigger: "on_battle_start"
        target: "self"
        effect_type: "apply_modifier"
        modifier_id: "MOD_LC_20001_DEF"
        duration: 0
      - trigger: "on_battle_start"
        target: "all_allies"
        effect_type: "apply_modifier"
        modifier_id: "MOD_LC_20001_RES"
        duration: 0

  # ========== 遗器 ==========
  relics:
    - relic_id: "R_101_1"       # 头部
      set_id: "S_101"            # 套装编号
      slot: "head"
      main_stat: {stat: "hp", value: 705.0}
      sub_stats:
        - {stat: "atk", value: 42.0}
        - {stat: "spd", value: 4.0}
    - relic_id: "R_101_2"       # 手部
      set_id: "S_101"
      slot: "hand"
      main_stat: {stat: "atk", value: 352.0}
      sub_stats:
        - {stat: "crit_rate", value: 0.06}
        - {stat: "crit_dmg", value: 0.08}
    # ... 躯干、脚部、位面球、连结绳

  # 套装效果（由 adapter 根据套装件数自动附加）
  relic_set_effects:
    - set_id: "S_101"
      pieces: 4
      effects:
        - trigger: "on_battle_start"
          target: "self"
          effect_type: "apply_modifier"
          modifier_id: "MOD_SET_101_4P"
          duration: 0
```

---

## 4. Buff / Modifier 定义

Buff 是核心机制，所有持续效果都用它表达。

```yaml
modifier:
  modifier_id: "MOD_1001_SHIELD"
  name: "护盾"
  modifier_type: "shield"       # buff | debuff | dot | shield | heal | control
  max_stack: 1
  duration: 3                    # 持续回合数，0 为永久
  # 触发时机和效果
  on_apply:
    - effect_type: "add_stat"
      stat: "shield"
      value: "base_stats.def * 0.48 + 640"

  on_turn_start:                 # 回合开始时
    - effect_type: "none"        # 护盾回合开始时无效果

  on_expire:
    - effect_type: "remove_stat"
      stat: "shield"

  # 如果是 dot：
  on_turn_start:
    - effect_type: "deal_damage"
      formula: "damage"
      damage_type: "fire"
      scaling: 0.5

  # 如果是 debuff（减防）：
  on_apply:
    - effect_type: "add_stat"
      stat: "def_reduction"
      value: 0.3                  # 减防 30%
```

**Buff 触发时机清单**：

| 触发时机 | 说明 |
|---------|------|
| `on_battle_start` | 战斗开始时 |
| `on_turn_start` | 携带者回合开始时 |
| `on_turn_end` | 携带者回合结束时 |
| `on_before_action` | 行动前（用于增伤 buff） |
| `on_after_action` | 行动后 |
| `on_before_hit` | 造成伤害前 |
| `on_after_hit` | 造成伤害后 |
| `on_being_hit` | 受击时 |
| `on_kill` | 击杀敌人时 |
| `on_ally_kill` | 队友击杀时 |
| `on_hp_change` | 生命值变化时 |
| `on_break` | 击破韧性时 |
| `on_weakness_break` | 造成弱点击破时 |
| `on_energy_full` | 能量满时（用于自动开大） |
| `on_death` | 死亡时 |

---

## 5. 效果类型 (Effect Type)

```yaml
# 造成伤害
effect_type: "deal_damage"
formula: "damage"           # 引用 formula 中定义的公式
target: "primary_target"    # 主目标 | all_enemies | all_allies | self | random_enemy | lowest_hp_enemy
scaling: 1.0                # 技能倍率
damage_type: "ice"          # 伤害属性

# 回复生命
effect_type: "heal"
formula: "heal"
target: "ally_single"
scaling: 0.3

# 施加 buff
effect_type: "apply_modifier"
modifier_id: "MOD_XXX"
target: "self"
duration: 3
chance: 1.0                  # 基础概率，受效果命中/抵抗影响

# 移除 buff
effect_type: "remove_modifier"
modifier_id: "MOD_XXX"
target: "enemy_single"

# 修改属性（立即/持续）
effect_type: "add_stat"
stat: "spd"
value: "base_stats.spd * 0.25"   # 支持表达式

# 回复能量
effect_type: "gain_energy"
target: "self"
value: 30

# 推进/拉条
effect_type: "advance_action"
target: "self"
value: 100                     # 行动值推进 100（立即行动）

# 回复战技点
effect_type: "gain_skill_point"
value: 1

# 召唤/召唤物行动
effect_type: "summon_action"
action_id: "SUMMON_XXX"

# 直接结算（用于表达式中的复杂逻辑）
effect_type: "script"
expression: "if target.hp < target.max_hp * 0.5 then apply_modifier(MOD_CRIT_BOOST)"
```

---

## 6. 遗器数值设计

遗器数值分两部分：**主词条**（固定值，由部位决定）和**副词条**（随机数值，由强化次数决定）。

```yaml
relic_main_stats:
  head: {stat: "hp", base: 705.0}           # 固定
  hand: {stat: "atk", base: 352.0}          # 固定
  body:                                         # 可选
    candidates: ["hp_pct", "atk_pct", "def_pct", "crit_rate", "crit_dmg", "heal_bonus", "effect_hit"]
  feet:
    candidates: ["hp_pct", "atk_pct", "def_pct", "spd"]
  sphere:
    candidates: ["hp_pct", "atk_pct", "def_pct", "physical_dmg", "fire_dmg", "ice_dmg", ...]
  rope:
    candidates: ["hp_pct", "atk_pct", "def_pct", "break_effect", "energy_regen"]

relic_sub_stats:
  # 副词条每次强化增加的数值（崩铁标准）
  hp: {base: 33.87, step: 33.87}           # 小生命
  atk: {base: 16.93, step: 16.93}          # 小攻击
  def: {base: 16.93, step: 16.93}          # 小防御
  hp_pct: {base: 0.034, step: 0.034}
  atk_pct: {base: 0.034, step: 0.034}
  def_pct: {base: 0.043, step: 0.043}
  spd: {base: 2.0, step: 2.3}              # 速度有 2.0 / 2.3 两档
  crit_rate: {base: 0.026, step: 0.032}    # 2.6% / 3.2%
  crit_dmg: {base: 0.052, step: 0.064}     # 5.2% / 6.4%
  break_effect: {base: 0.052, step: 0.064}
  effect_hit: {base: 0.034, step: 0.043}
  effect_res: {base: 0.034, step: 0.043}
```

**adapter 职责**：根据遗器配置计算最终属性，合并到 `base_stats` 中。

---

## 7. 完整输入示例

```yaml
# 一份完整的仿真输入
encounter_id: "E_001"
name: "测试关卡"

formula:
  damage:
    expression: "base_dmg * dmg_multiplier * (1 + dmg_bonus) * def_multiplier * res_multiplier * crit_multiplier"

globals:
  action_value: 10000
  skill_points: {max: 5, current: 3}

actors:
  - actor_id: "1001"
    name: "三月七"
    actor_type: "character"
    level: 80
    base_stats: {hp: 2000, atk: 1000, def: 1200, spd: 101, crit_rate: 0.3, crit_dmg: 1.0}
    actions: [...]
    traces: [...]
    eidolons: [...]
    light_cone: {...}
    relics: [...]

  - actor_id: "M_8001"
    name: "测试怪物"
    actor_type: "monster"
    level: 80
    base_stats: {hp: 50000, atk: 500, def: 500, spd: 120, crit_rate: 0, crit_dmg: 0}
    max_toughness: 120
    weakness: ["ice", "fire"]
    actions:
      - action_id: "M_8001_basic"
        name: "爪击"
        action_type: "basic"
        target_type: "enemy_single"
        effects:
          - trigger: "on_cast"
            target: "primary_target"
            effect_type: "deal_damage"
            formula: "damage"
            scaling: 1.0

initial_modifiers: []   # 开局 buff，如场地效果
```

---

## 8. 与 Adapter 的交互边界

`adapters/` 负责把 `raw_schema`（StarRailRes 数据）转换成本文定义的格式：

| raw_schema 数据 | sim_schema 对应 | adapter 工作 |
|----------------|----------------|------------|
| `Character` + `LightCone` + `Relics` | `Actor.base_stats` | 计算最终白值 + 绿值 |
| `Character.skills[]` | `Actor.actions[]` | 映射倍率、目标类型、效果 |
| `Character.traces[]` | `Actor.traces[]` | 提取被动效果 |
| `Character.eidolons[]` | `Actor.eidolons[]` | 按解锁状态筛选 |
| `LightCone.effects` | `Actor.light_cone.effects` | 转换光锥特效 |
| `RelicSet.bonus` | `Actor.relic_set_effects` | 按件数组装套装效果 |

---

## FAQ

**Q: 表达式 `"base_stats.def * 0.48 + 640"` 怎么执行？**

A: 运行时维护一个 `Context`，包含当前 actor、目标、全局状态等。表达式用安全的 eval 环境求值，或者实现一个小型表达式引擎。

**Q: 复杂的条件判断（如"生命值低于 50% 时增伤"）怎么表达？**

A: 在 `effects` 里加 `condition` 字段，用表达式表示：
```yaml
effects:
  - trigger: "on_before_hit"
    condition: "target.hp / target.max_hp < 0.5"
    effect_type: "add_stat"
    stat: "dmg_bonus"
    value: 0.3
```

**Q: 多段伤害（如希儿再现）怎么处理？**

A: 每段伤害是一个独立的 `deal_damage` effect，可以设置不同的 `trigger`：
```yaml
effects:
  - trigger: "on_cast"      # 第一段
    effect_type: "deal_damage"
    scaling: 2.0
  - trigger: "on_kill"       # 击杀后再现
    effect_type: "grant_extra_turn"
  - trigger: "on_extra_turn"  # 再现段
    effect_type: "deal_damage"
    scaling: 0.8
```

**Q: 嘲讽机制怎么实现？**

A: 给目标上一个 `taunt` modifier，在 `on_being_targeted` 时改变目标选择逻辑。

---

## 9. 策略 DSL (Policy)

策略是可独立输入、可搜索优化的战斗决策逻辑。采用 **Rule-based DSL + 参数化混合** 设计。

### 设计原则

- **可执行**：模拟器直接 interpret，不需要 LLM 实时参与
- **可参数化**：关键数值（如大招阈值）抽离为可调参数，方便网格搜索/贝叶斯优化
- **LLM 友好**：结构清晰，LLM 容易生成和修改
- **维度拆分**：技能选择、目标选择、时机策略分离

### 策略结构

```yaml
policy:
  name: "三月七_default"
  version: "1.0"

  # ========== 技能选择规则（按 priority 降序匹配）==========
  action_rules:
    - condition: "energy >= ULT_THRESHOLD"
      action: "ultimate"
      priority: 100
      description: "能量满时开大"

    - condition: "skill_points > 0 && ally_without_shield"
      action: "skill"
      priority: 50
      description: "有战技点且队友没护盾时给盾"

    - condition: "true"
      action: "basic"
      priority: 0
      description: "默认普攻"

  # ========== 目标选择规则 ==========
  target_rules:
    - condition: "action_type == 'skill'"
      selector: "lowest_hp_ally"
      priority: 100

    - condition: "action_type == 'ultimate'"
      selector: "all_enemies"
      priority: 100

    - condition: "true"
      selector: "primary_target"
      priority: 0

  # ========== 时机策略（可选）==========
  timing_rules:
    - condition: "buff.stack >= 3 && !enemy.broken"
      timing: "delay"
      delay_condition: "enemy.broken == true"
      description: "buff叠满但敌人未击破，延迟到击破后再出手"

  # ========== 可调参数 ==========
  parameters:
    ULT_THRESHOLD: 120        # 大招能量阈值
    SHIELD_PRIORITY: 0.8     # 护盾优先级权重
    HP_THRESHOLD: 0.5        # 低血量阈值
```

### 规则匹配逻辑

1. **技能选择**：按 `priority` 降序遍历 `action_rules`，第一条 `condition` 为真的规则被执行
2. **目标选择**：同样按优先级匹配，决定技能打谁
3. **时机选择**：决定是否立即出手或延迟等待条件

### 表达式上下文

策略表达式中可以访问的变量：

| 变量 | 说明 |
|------|------|
| `energy` | 当前能量 |
| `skill_points` | 当前战技点 |
| `hp` / `max_hp` | 生命值 |
| `buff.<modifier_id>` | 特定 buff 的引用（如 `buff.MOD_1001_SHIELD.stack`） |
| `enemy.<attr>` | 主目标属性 |
| `allies[]` | 队友列表 |
| `enemies[]` | 敌人列表 |
| `parameters.<name>` | 策略参数 |

### 为什么不用自然语言策略

| 自然语言 | Rule-based DSL |
|---------|---------------|
| "优先使用战技" | `condition: "skill_points > 0", action: "skill"` |
| 不可精确执行 | 100% deterministic |
| 不可搜索优化 | 参数可独立调整，适合贝叶斯优化 |
| LLM 生成后需人工翻译 | LLM 直接生成可执行结构 |

### 参数优化示例

```python
# 用贝叶斯优化搜索最佳大招阈值
from hsr_nous.sim.engine import CombatEngine
from hsr_nous.sim_schema.policy import Policy

def evaluate(threshold: float) -> float:
    policy = Policy(
        action_rules=[...],
        parameters={"ULT_THRESHOLD": threshold}
    )
    engine = CombatEngine(encounter, policy=policy)
    result = engine.run()
    return result.dps

# 在 [100, 140] 区间搜索最优阈值
best_threshold = bayesian_optimize(evaluate, bounds=(100, 140))
```

### 策略与 Encounter 的关系

```yaml
encounter:
  encounter_id: "E_001"
  formula: {...}
  globals: {...}
  actors: [...]
  policy: {...}        # <-- 每个 encounter 可绑定不同策略
  initial_modifiers: []
```

同一个队伍配不同策略，可以对比不同操作手法的差异。
