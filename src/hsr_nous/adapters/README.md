# Adapters 适配层

将 `raw_schema`（StarRailRes 原始数据）转换为 `sim_schema`（仿真器输入格式）。

这是数据管道与战斗模拟器之间的**唯一桥梁**。

## 文件说明

| 文件 | 职责 |
|------|------|
| `character_adapter.py` | 角色适配：`Character` + `LightCone` + `Relics` → `Actor` |
| `skill_adapter.py` | 技能适配：原始技能数据 → `Action` |
| `encounter_adapter.py` | 关卡适配：原始敌人数据 → `Encounter` |

## 设计决策

- 只 import `raw_schema` 和 `sim_schema`，不 import `sim`
- 转换逻辑是单向的：raw → sim，不允许反向
- 复杂的属性计算（如遗器最终属性）在这里完成
- 如果 StarRailRes 字段名变化，只需要改这里

## 使用方式

```python
from hsr_nous.adapters.character_adapter import adapt_character
from hsr_nous.raw_schema.character import Character
from hsr_nous.raw_schema.light_cone import LightCone

actor = adapt_character(character=char, light_cone=lc, relics=relics)
```

## 修改记录

- 初始创建：占位实现，TODO 标注待完成逻辑
