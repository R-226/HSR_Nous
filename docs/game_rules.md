# 崩坏：星穹铁道 战斗规则

本文档记录崩铁核心战斗机制，作为战斗模拟器的**唯一事实来源**。

> 当本文档与代码实现冲突时，以本文档为准，代码需要修正。

---

## 目录

| 章节 | 说明 | 详细文档 |
|------|------|---------|
| **1. 基础属性** | 角色/敌人属性计算、技能分类、记忆命途与忆灵 | [mechanics/base_stats.md](mechanics/base_stats.md) |
| **2. 伤害公式** | 完整伤害乘区体系（增伤、易伤、防御、抗性、暴击、真实伤害等） | [mechanics/damage_formula.md](mechanics/damage_formula.md) |
| **3. 行动序** | 行动值计算、拉条/推条、速度变化、额外回合、冻结 | [mechanics/action_sequence.md](mechanics/action_sequence.md) |
| **4. 击破机制** | 韧性削减、弱点击破、击破伤害、超击破 | [mechanics/break_system.md](mechanics/break_system.md) |
| **5. 能量机制** | 能量获取、终结技释放、能量恢复效率 | [mechanics/energy_system.md](mechanics/energy_system.md) |
| **6. 战技点机制** | 战技点上限、获取与消耗规则 | [mechanics/skill_points.md](mechanics/skill_points.md) |
| **7. Buff / Debuff** | 持续时间、结算机制、层数叠加、驱散规则 | [mechanics/buff_system.md](mechanics/buff_system.md) |
| **8. 追加攻击** | 追加攻击的触发条件与优先级 | [mechanics/follow_up_attacks.md](mechanics/follow_up_attacks.md) |
| **9. 嘲讽机制** | 基础嘲讽值、受击概率计算 | [mechanics/taunt_system.md](mechanics/taunt_system.md) |
| **10. 特殊机制** | 待补充的特殊战斗机制 | [mechanics/special_mechanics.md](mechanics/special_mechanics.md) |

---

## 核心公式速查

### 基础伤害

```
伤害 = abilityMulti × dmgBoostMulti × indDmgBoostMulti × defMulti × resMulti
      × baseUniversalMulti × vulnMulti × indVulnMulti × finalDmgMulti
      × critMulti × trueDmgMulti
```

各乘区详见 [mechanics/damage_formula.md](mechanics/damage_formula.md)。

### 行动值

```
AV = 10000 / speed
```

详见 [mechanics/action_sequence.md](mechanics/action_sequence.md)。

### 削韧值

```
最终削韧 = baseToughnessDmg × breakEfficiencyMulti + fixedToughnessDmg
```

详见 [mechanics/break_system.md](mechanics/break_system.md)。

---

## 待确认事项

- [ ] 部分怪物的效果抵抗/效果命中数值需要进一步验证
- [ ] 持续伤害（DOT）的增益乘区生效情况是否覆盖所有角色
- [ ] 追加攻击的触发条件分类是否需要进一步细化
- [ ] 冻结与强烈震荡的补偿机制数值来源
- [ ] 超击破伤害公式中的等级系数具体值
- [ ] 真实伤害是否完全不受任何效果影响（包括减伤）

## 修改记录

- 2026-05-15：拆分为 `mechanics/` 目录下的独立文档，`game_rules.md` 改为总纲
- 2026-05-15：新增 1.4 记忆命途与忆灵、2.8 真实伤害、2.2 防御乘区收益特性
- 2026-05-15：新增独立增伤区、独立易伤区；修正抗性上下限为 ±100%
