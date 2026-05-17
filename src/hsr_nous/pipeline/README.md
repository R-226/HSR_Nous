# Pipeline 数据管道

从社区维护的 [Mar-7th/StarRailRes](https://github.com/Mar-7th/StarRailRes) 加载《崩坏：星穹铁道》游戏数据。

> 数据来源: [Mar-7th/StarRailRes](https://github.com/Mar-7th/StarRailRes)，上游为 Dimbreath/StarRailData

## 模块结构

```
pipeline/
├── __init__.py   # 暴露核心加载接口
├── loader.py     # 本地 JSON 加载 + 查询 + 计算辅助
├── update.py     # 从 GitHub 拉取最新数据
└── README.md     # 本文档
```

## 数据来源

数据文件存放于 `data/starrailres/index_new/en/`：

| 文件 | 内容 |
|------|------|
| `characters.json` | 91 个角色基础信息 |
| `character_skills.json` | 728 个角色技能（含 params 倍率数组） |
| `character_skill_trees.json` | 1840 个行迹节点 |
| `character_promotions.json` | 角色晋阶与等级成长数据 |
| `character_ranks.json` | 角色星魂（6 魂 × 91 角色） |
| `light_cones.json` | 161 个光锥基础信息 |
| `light_cone_promotions.json` | 光锥晋阶数据 |
| `light_cone_ranks.json` | 光锥叠影效果 |
| `relic_sets.json` | 56 个遗器套装 |
| `relics.json` | 遗器基础信息 |
| `relic_main_affixes.json` | 遗器主词条数值 |
| `relic_sub_affixes.json` | 遗器副词条数值 |
| `properties.json` | 属性类型映射表（HealRatioBase → Outgoing Healing Boost） |
| `paths.json` | 命途映射表（Knight → Preservation） |
| `elements.json` | 元素映射表（Ice → Ice） |

## Python API

### 基础加载

```python
from hsr_nous.pipeline import load_characters, load_character_skills

# 加载角色数据（自动缓存）
chars = load_characters()
# {"1001": {"id": "1001", "name": "March 7th", "element": "Ice", "path": "Knight", ...}}

# 加载技能数据
skills = load_character_skills()
# {"100101": {"id": "100101", "name": "Frigid Cold Arrow", "type_text": "Basic ATK", "params": [[0.5], [0.6], ...]}}
```

### 查询接口

```python
from hsr_nous.pipeline import (
    get_character, get_skill, get_character_full,
    get_path_name, get_element_name,
)

# 按 ID 查询角色
march = get_character("1001")
# 老版存护三月七：element="Ice", path="Knight"

# 按名称查询
march = get_character_by_name("March 7th")

# 获取技能
skill = get_skill("100101")
print(skill["desc"])  # "Deals Ice DMG equal to #1[i]% of March 7th's ATK..."
print(skill["params"][0])  # [0.5]  ← Lv.1 倍率

# 组装完整角色数据（自动解析 ID 引用）
full = get_character_full("1001")
# full["skills_detail"]   → 6 个 Skill 对象
# full["skill_trees_detail"] → 18 个 Tree 对象
# full["promotion"]       → 晋阶数据
# full["ranks_detail"]    → 6 个 Rank（星魂）对象

# 命途/元素名称映射
print(get_path_name("Knight"))      # "Preservation"
print(get_element_name("Ice"))      # "Ice"
print(get_property_name("HealRatioBase"))  # "Outgoing Healing Boost"
```

### 属性计算

```python
from hsr_nous.pipeline import calc_character_stats, calc_light_cone_stats

# 计算角色 Lv.80 基础面板
stats = calc_character_stats("1001", level=80)
# {"hp": 576.0, "atk": 278.4, "def": 312.0, "spd": 101,
#  "crit_rate": 0.05, "crit_dmg": 0.5}

# 计算光锥 Lv.80 面板
lc_stats = calc_light_cone_stats("20000", level=80)
# {"hp": 846.72, "atk": 317.52, "def": 264.6}
```

### 技能参数查询

```python
from hsr_nous.pipeline import get_skill_params

# 获取三月七普攻 Lv.10 的倍率
params = get_skill_params("100101", level=10)
# [1.4]
```

### 远程加载（fallback）

本地文件缺失时，可直接从 GitHub 拉取：

```python
from hsr_nous.pipeline import fetch_from_github

chars = fetch_from_github("characters.json")
```

## CLI 使用

```bash
# 更新英文数据（默认）
hsr-data-update

# 更新简体中文数据
hsr-data-update --lang cn

# 更新其他语言（cht=繁中, jp=日语, kr=韩语, en=英语, de=德语, es=西语, fr=法语, id=印尼语, pt=葡语, ru=俄语, th=泰语, vi=越南语）
hsr-data-update --lang jp

# 下载敌人数据（来源: theBowja/starrail-data）
hsr-data-update --enemies

# 指定数据目录
hsr-data-update --data-dir ./my_data

# 只更新指定文件
hsr-data-update --files characters.json,character_skills.json

# 使用压缩索引（index_min 体积更小）
hsr-data-update --index index_min

# 只检查，不写入（dry run）
hsr-data-update --dry-run
```

### 敌人数据

敌人数据来自 [theBowja/starrail-data](https://github.com/theBowja/starrail-data)，存放在 `data/enemies/enemies.json`。

如果 CLI 下载超时，可手动下载：

```bash
mkdir -p data/enemies
curl -L -o data/enemies/enemies.json "https://raw.githubusercontent.com/theBowja/starrail-data/main/data/CHS/enemies.json"
```

## 数据关联模型

StarRailRes 采用**分表 + ID 引用**的设计：

```
characters.json           character_skills.json
    "1001"                    "100101"
    ├── skills: ["100101",    ├── name: "Frigid Cold Arrow"
    │            "100102",    ├── type_text: "Basic ATK"
    │            ...]         ├── params: [[0.5], [0.6], ...]
    ├── skill_trees: [...]    └── ...
    ├── ranks: ["100101",     character_skill_trees.json
    │           ...]              "1001001"
    └── ...                   ├── anchor: "Point01"
                              ├── level_up_skills: [...]
                              └── levels: [{properties: [...]}, ...]
```

`get_character_full()` 会自动将这些 ID 引用解析为完整的嵌套对象。

## 与模块边界的关系

`pipeline/` **不 import 任何其他模块**（raw_schema、sim_schema、sim、agents、api）。
其他模块（如 `adapters/`）可以通过 `from hsr_nous.pipeline import load_characters` 获取原始数据，再转换为 `sim_schema` 格式。
