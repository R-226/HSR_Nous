# Raw Schema 原始数据模型

定义从外部数据源（StarRailRes）获取的原始数据的 Python 模型。

## 文件说明

| 文件 | 职责 |
|------|------|
| `character.py` | `Character` 类：角色档案模型（_id, name, rarity 等） |
| `light_cone.py` | `LightCone` 类：光锥（武器）档案模型 |
| `relic.py` | `Relic` 类：遗器（圣遗物）档案模型 |
| `loader.py` | 从 JSON 文件加载原始数据为 Python 对象的工具函数 |

## 设计决策

- 模型只封装数据，不做业务逻辑（如伤害计算、属性转换）
- 通过 `to_dict()` 暴露原始数据，方便 adapter 读取任意字段
- 不 import `sim_schema`、`sim`、`adapters` 等下游模块

## 使用方式

```python
from hsr_nous.raw_schema.loader import load_characters
from pathlib import Path

chars = load_characters(Path("data/starrailres/index_new/en/characters.json"))
for c in chars:
    print(c.id, c.name)
```

## 修改记录

- 初始创建：占位模型，字段待补全
