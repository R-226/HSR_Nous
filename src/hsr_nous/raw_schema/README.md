# Raw Schema 原始数据模型

定义从外部数据源（StarRailRes）获取的原始数据的 Python 模型。

## 文件说明

| 文件 | 类 | 说明 |
|------|-----|------|
| `character.py` | `Character` | 角色档案（id, name, tag, rarity, path, element, max_sp, ranks, skills, skill_trees, icon, preview, portrait） |
| `character_skill.py` | `CharacterSkill` | 角色技能（id, name, max_level, element, type, type_text, effect, effect_text, simple_desc, desc, params, icon） |
| `character_promotion.py` | `CharacterPromotion` | 角色晋阶（id, values, materials） |
| `character_rank.py` | `CharacterRank` | 角色星魂（id, name, rank, desc, materials, level_up_skills, icon） |
| `character_skill_tree.py` | `CharacterSkillTree` | 角色行迹（id, name, max_level, desc, params, anchor, pre_points, level_up_skills, levels, icon） |
| `light_cone.py` | `LightCone` | 光锥档案（id, name, rarity, path, desc, icon, preview, portrait） |
| `light_cone_promotion.py` | `LightConePromotion` | 光锥晋阶（id, values, materials） |
| `light_cone_rank.py` | `LightConeRank` | 光锥叠影（id, skill, desc, params, properties） |
| `relic.py` | `RelicSet`, `Relic` | 遗器套装（id, name, desc, properties, icon）和单件（id, set_id, name, rarity, type, max_level, main_affix_id, sub_affix_id, icon） |
| `relic_affix.py` | `RelicMainAffix`, `RelicSubAffix` | 遗器主/副词条（id, affixes） |
| `element.py` | `Element` | 元素类型（id, name, desc, color, icon） |
| `path.py` | `Path` | 命途（id, text, name, desc, icon, icon_middle, icon_small） |
| `property.py` | `Property` | 属性类型定义（type, name, field, affix, ratio, percent, order, icon） |
| `loader.py` | - | 从 JSON 文件加载原始数据为 Python 对象的工具函数 |

## 设计决策

- 模型只封装数据，不做业务逻辑（如伤害计算、属性转换）
- 通过 `to_dict()` 暴露原始数据，方便 adapter 读取任意字段
- 不 import `sim_schema`、`sim`、`adapters` 等下游模块
- StarRailRes JSON 格式为 `{id: {...}}`，loader 自动转为 list

## 使用方式

```python
from pathlib import Path
from hsr_nous.raw_schema import load_characters, load_character_skills

data_dir = Path("data/starrailres/index_new/en")

# 加载角色
chars = load_characters(data_dir / "characters.json")
for c in chars[:3]:
    print(f"{c.id} {c.name} ({c.element}/{c.path}) ★{c.rarity}")

# 加载技能
skills = load_character_skills(data_dir / "character_skills.json")
for s in skills[:3]:
    print(f"{s.id} {s.name} [{s.type_text}]")
```

## 修改记录

- 初始创建：占位模型
- 完善：补全所有字段，新增 10 个模型，修复 `id` 字段读取
