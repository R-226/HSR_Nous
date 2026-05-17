"""从 JSON 文件加载原始数据为 Python 对象."""

import json
from pathlib import Path
from typing import Any, Dict, List

from hsr_nous.raw_schema.character import Character
from hsr_nous.raw_schema.character_promotion import CharacterPromotion
from hsr_nous.raw_schema.character_rank import CharacterRank
from hsr_nous.raw_schema.character_skill import CharacterSkill
from hsr_nous.raw_schema.character_skill_tree import CharacterSkillTree
from hsr_nous.raw_schema.element import Element
from hsr_nous.raw_schema.enemy import Enemy
from hsr_nous.raw_schema.light_cone import LightCone
from hsr_nous.raw_schema.light_cone_promotion import LightConePromotion
from hsr_nous.raw_schema.light_cone_rank import LightConeRank
from hsr_nous.raw_schema.path import Path as HsrPath
from hsr_nous.raw_schema.property import Property
from hsr_nous.raw_schema.relic import Relic, RelicSet
from hsr_nous.raw_schema.relic_affix import RelicMainAffix, RelicSubAffix


def load_json(path: Path) -> List[Dict[str, Any]]:
    """加载 JSON 文件，返回 dict 列表.

    StarRailRes 的 JSON 格式为 {id: {...}, id: {...}}，需要转为 list。
    """
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return list(data.values())
    if isinstance(data, list):
        return data
    return [data]


def load_characters(path: Path) -> List[Character]:
    return [Character(d) for d in load_json(path)]


def load_character_skills(path: Path) -> List[CharacterSkill]:
    return [CharacterSkill(d) for d in load_json(path)]


def load_character_promotions(path: Path) -> List[CharacterPromotion]:
    return [CharacterPromotion(d) for d in load_json(path)]


def load_character_ranks(path: Path) -> List[CharacterRank]:
    return [CharacterRank(d) for d in load_json(path)]


def load_character_skill_trees(path: Path) -> List[CharacterSkillTree]:
    return [CharacterSkillTree(d) for d in load_json(path)]


def load_light_cones(path: Path) -> List[LightCone]:
    return [LightCone(d) for d in load_json(path)]


def load_light_cone_promotions(path: Path) -> List[LightConePromotion]:
    return [LightConePromotion(d) for d in load_json(path)]


def load_light_cone_ranks(path: Path) -> List[LightConeRank]:
    return [LightConeRank(d) for d in load_json(path)]


def load_relic_sets(path: Path) -> List[RelicSet]:
    return [RelicSet(d) for d in load_json(path)]


def load_relics(path: Path) -> List[Relic]:
    return [Relic(d) for d in load_json(path)]


def load_relic_main_affixes(path: Path) -> List[RelicMainAffix]:
    return [RelicMainAffix(d) for d in load_json(path)]


def load_relic_sub_affixes(path: Path) -> List[RelicSubAffix]:
    return [RelicSubAffix(d) for d in load_json(path)]


def load_elements(path: Path) -> List[Element]:
    return [Element(d) for d in load_json(path)]


def load_paths(path: Path) -> List[HsrPath]:
    return [HsrPath(d) for d in load_json(path)]


def load_properties(path: Path) -> List[Property]:
    return [Property(d) for d in load_json(path)]


def load_enemies(path: Path) -> List[Enemy]:
    return [Enemy(d) for d in load_json(path)]
