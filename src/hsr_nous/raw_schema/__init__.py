"""原始数据模型（Schema）：对应外部数据源（StarRailRes）的数据结构定义."""

from hsr_nous.raw_schema.character import Character
from hsr_nous.raw_schema.character_promotion import CharacterPromotion
from hsr_nous.raw_schema.character_rank import CharacterRank
from hsr_nous.raw_schema.character_skill import CharacterSkill
from hsr_nous.raw_schema.character_skill_tree import CharacterSkillTree
from hsr_nous.raw_schema.element import Element
from hsr_nous.raw_schema.light_cone import LightCone
from hsr_nous.raw_schema.light_cone_promotion import LightConePromotion
from hsr_nous.raw_schema.light_cone_rank import LightConeRank
from hsr_nous.raw_schema.loader import (
    load_character_promotions,
    load_character_ranks,
    load_character_skill_trees,
    load_character_skills,
    load_characters,
    load_elements,
    load_light_cone_promotions,
    load_light_cone_ranks,
    load_light_cones,
    load_paths,
    load_properties,
    load_relic_main_affixes,
    load_relic_sets,
    load_relic_sub_affixes,
    load_relics,
)
from hsr_nous.raw_schema.path import Path as HsrPath
from hsr_nous.raw_schema.property import Property
from hsr_nous.raw_schema.relic import Relic, RelicSet
from hsr_nous.raw_schema.relic_affix import RelicMainAffix, RelicSubAffix

__all__ = [
    # 模型类
    "Character",
    "CharacterSkill",
    "CharacterPromotion",
    "CharacterRank",
    "CharacterSkillTree",
    "LightCone",
    "LightConePromotion",
    "LightConeRank",
    "RelicSet",
    "Relic",
    "RelicMainAffix",
    "RelicSubAffix",
    "Element",
    "HsrPath",
    "Property",
    # 加载函数
    "load_characters",
    "load_character_skills",
    "load_character_promotions",
    "load_character_ranks",
    "load_character_skill_trees",
    "load_light_cones",
    "load_light_cone_promotions",
    "load_light_cone_ranks",
    "load_relic_sets",
    "load_relics",
    "load_relic_main_affixes",
    "load_relic_sub_affixes",
    "load_elements",
    "load_paths",
    "load_properties",
]
