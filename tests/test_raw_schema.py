"""raw_schema 模型和加载函数的单元测试."""

import json
import pytest
from pathlib import Path

from hsr_nous.raw_schema import (
    Character,
    CharacterPromotion,
    CharacterRank,
    CharacterSkill,
    CharacterSkillTree,
    Element,
    LightCone,
    LightConePromotion,
    LightConeRank,
    HsrPath,
    Property,
    Relic,
    RelicSet,
    RelicMainAffix,
    RelicSubAffix,
    load_characters,
    load_character_skills,
    load_character_promotions,
    load_character_ranks,
    load_character_skill_trees,
    load_light_cones,
    load_light_cone_promotions,
    load_light_cone_ranks,
    load_relic_sets,
    load_relics,
    load_relic_main_affixes,
    load_relic_sub_affixes,
    load_elements,
    load_paths,
    load_properties,
)


DATA_DIR = Path(__file__).parent.parent / "data" / "starrailres" / "index_new" / "en"


# ---------------------------------------------------------------------------
# 模型测试
# ---------------------------------------------------------------------------


class TestCharacter:
    def test_from_dict(self):
        data = {
            "id": "1001",
            "name": "March 7th",
            "tag": "mar7th",
            "rarity": 4,
            "path": "Knight",
            "element": "Ice",
            "max_sp": 120,
            "skills": ["100101", "100102"],
            "skill_trees": ["1001001"],
            "ranks": ["100101"],
            "icon": "some_icon.png",
            "preview": "some_preview.png",
            "portrait": "some_portrait.png",
        }
        char = Character(data)

        assert char.id == "1001"
        assert char.name == "March 7th"
        assert char.tag == "mar7th"
        assert char.rarity == 4
        assert char.path == "Knight"
        assert char.element == "Ice"
        assert char.max_sp == 120
        assert char.skills == ["100101", "100102"]
        assert char.skill_trees == ["1001001"]
        assert char.ranks == ["100101"]
        assert char.icon == "some_icon.png"

    def test_missing_fields(self):
        char = Character({"id": "9999"})
        assert char.id == "9999"
        assert char.name == ""
        assert char.rarity == 0
        assert char.skills == []

    def test_to_dict(self):
        data = {"id": "1001", "name": "Test"}
        char = Character(data)
        assert char.to_dict() == data


class TestLightCone:
    def test_from_dict(self):
        data = {
            "id": "20000",
            "name": "Arrows",
            "rarity": 3,
            "path": "Rogue",
            "desc": "A basic light cone.",
            "icon": "icon.png",
            "preview": "preview.png",
            "portrait": "portrait.png",
        }
        lc = LightCone(data)

        assert lc.id == "20000"
        assert lc.name == "Arrows"
        assert lc.rarity == 3
        assert lc.path == "Rogue"
        assert lc.desc == "A basic light cone."


class TestRelicSet:
    def test_from_dict(self):
        data = {
            "id": "101",
            "name": "Passerby of Wandering Cloud",
            "desc": ["2-piece: ...", "4-piece: ..."],
            "properties": [[{"type": "HealRatioBase", "value": 0.1}]],
            "icon": "icon.png",
        }
        rs = RelicSet(data)

        assert rs.id == "101"
        assert rs.name == "Passerby of Wandering Cloud"
        assert len(rs.desc) == 2
        assert len(rs.properties) == 1


class TestRelic:
    def test_from_dict(self):
        data = {
            "id": "61011",
            "set_id": "101",
            "name": "Wandering Cloud Hat",
            "rarity": 5,
            "type": "HEAD",
            "max_level": 15,
            "main_affix_id": "1",
            "sub_affix_id": "1",
            "icon": "icon.png",
        }
        relic = Relic(data)

        assert relic.id == "61011"
        assert relic.set_id == "101"
        assert relic.type == "HEAD"
        assert relic.rarity == 5
        assert relic.max_level == 15


class TestCharacterSkill:
    def test_from_dict(self):
        data = {
            "id": "100101",
            "name": "Frigid Cold Arrow",
            "max_level": 6,
            "element": "Ice",
            "type": "Normal",
            "type_text": "Basic ATK",
            "effect": "SingleAttack",
            "effect_text": "Single Target",
            "simple_desc": "Deals Ice DMG...",
            "desc": "Deals Ice DMG equal to #1[i]%...",
            "params": [[0.5], [0.6]],
            "icon": "icon.png",
        }
        skill = CharacterSkill(data)

        assert skill.id == "100101"
        assert skill.type_text == "Basic ATK"
        assert skill.params == [[0.5], [0.6]]


class TestCharacterPromotion:
    def test_from_dict(self):
        data = {
            "id": "1001",
            "values": [
                {"hp": {"base": 100, "step": 10}, "atk": {"base": 50, "step": 5}}
            ],
            "materials": [[{"id": "1", "num": 4}]],
        }
        promo = CharacterPromotion(data)

        assert promo.id == "1001"
        assert len(promo.values) == 1
        assert promo.values[0]["hp"]["base"] == 100


class TestCharacterRank:
    def test_from_dict(self):
        data = {
            "id": "100101",
            "name": "Butterfly Flurry",
            "rank": 1,
            "desc": "When using Skill...",
            "materials": [],
            "level_up_skills": [],
            "icon": "icon.png",
        }
        rank = CharacterRank(data)

        assert rank.id == "100101"
        assert rank.rank == 1


class TestCharacterSkillTree:
    def test_from_dict(self):
        data = {
            "id": "1001001",
            "name": "ATK Boost",
            "max_level": 6,
            "desc": "ATK increases by...",
            "params": [0.02, 0.04],
            "anchor": "Point01",
            "pre_points": [],
            "level_up_skills": [],
            "levels": [],
            "icon": "icon.png",
        }
        tree = CharacterSkillTree(data)

        assert tree.id == "1001001"
        assert tree.anchor == "Point01"
        assert tree.params == [0.02, 0.04]


class TestLightConePromotion:
    def test_from_dict(self):
        data = {
            "id": "20000",
            "values": [{"hp": {"base": 50, "step": 5}, "atk": {"base": 25, "step": 3}}],
            "materials": [],
        }
        promo = LightConePromotion(data)

        assert promo.id == "20000"


class TestLightConeRank:
    def test_from_dict(self):
        data = {
            "id": "20000",
            "skill": "Arrow",
            "desc": "Increases ATK by #1[i]%",
            "params": [[0.08], [0.10]],
            "properties": [[{"type": "AttackAddedRatio", "value": 0.08}]],
        }
        rank = LightConeRank(data)

        assert rank.id == "20000"
        assert rank.skill == "Arrow"


class TestRelicAffix:
    def test_main_affix(self):
        data = {
            "id": "1",
            "affixes": {
                "1": {"affix_id": "1", "property": "HPDelta", "base": 100, "step": 50}
            },
        }
        affix = RelicMainAffix(data)

        assert affix.id == "1"
        assert "1" in affix.affixes

    def test_sub_affix(self):
        data = {
            "id": "1",
            "affixes": {
                "1": {
                    "affix_id": "1",
                    "property": "HPDelta",
                    "base": 50,
                    "step": 25,
                    "step_num": 1,
                }
            },
        }
        affix = RelicSubAffix(data)

        assert affix.id == "1"
        assert affix.affixes["1"]["step_num"] == 1


class TestElement:
    def test_from_dict(self):
        data = {
            "id": "Ice",
            "name": "Ice",
            "desc": "Freezes enemies.",
            "color": "#4FC1E9",
            "icon": "icon.png",
        }
        elem = Element(data)

        assert elem.id == "Ice"
        assert elem.color == "#4FC1E9"


class TestPath:
    def test_from_dict(self):
        data = {
            "id": "Knight",
            "text": "Preservation",
            "name": "Preservation",
            "desc": "Uses shields to protect allies.",
            "icon": "icon.png",
            "icon_middle": "mid.png",
            "icon_small": "small.png",
        }
        path = HsrPath(data)

        assert path.id == "Knight"
        assert path.text == "Preservation"


class TestProperty:
    def test_from_dict(self):
        data = {
            "type": "HPDelta",
            "name": "HP",
            "field": "hp",
            "affix": True,
            "ratio": False,
            "percent": False,
            "order": 1,
            "icon": "icon.png",
        }
        prop = Property(data)

        assert prop.type == "HPDelta"
        assert prop.affix is True
        assert prop.ratio is False


# ---------------------------------------------------------------------------
# 加载函数测试
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not DATA_DIR.exists(), reason="数据文件不存在")
class TestLoaders:
    def test_load_characters(self):
        chars = load_characters(DATA_DIR / "characters.json")
        assert len(chars) > 0
        assert all(isinstance(c, Character) for c in chars)
        assert all(c.id for c in chars)

    def test_load_character_skills(self):
        skills = load_character_skills(DATA_DIR / "character_skills.json")
        assert len(skills) > 0
        assert all(isinstance(s, CharacterSkill) for s in skills)

    def test_load_character_promotions(self):
        promos = load_character_promotions(DATA_DIR / "character_promotions.json")
        assert len(promos) > 0
        assert all(isinstance(p, CharacterPromotion) for p in promos)

    def test_load_character_ranks(self):
        ranks = load_character_ranks(DATA_DIR / "character_ranks.json")
        assert len(ranks) > 0
        assert all(isinstance(r, CharacterRank) for r in ranks)

    def test_load_character_skill_trees(self):
        trees = load_character_skill_trees(DATA_DIR / "character_skill_trees.json")
        assert len(trees) > 0
        assert all(isinstance(t, CharacterSkillTree) for t in trees)

    def test_load_light_cones(self):
        lcs = load_light_cones(DATA_DIR / "light_cones.json")
        assert len(lcs) > 0
        assert all(isinstance(lc, LightCone) for lc in lcs)

    def test_load_light_cone_promotions(self):
        promos = load_light_cone_promotions(DATA_DIR / "light_cone_promotions.json")
        assert len(promos) > 0

    def test_load_light_cone_ranks(self):
        ranks = load_light_cone_ranks(DATA_DIR / "light_cone_ranks.json")
        assert len(ranks) > 0

    def test_load_relic_sets(self):
        sets = load_relic_sets(DATA_DIR / "relic_sets.json")
        assert len(sets) > 0
        assert all(isinstance(s, RelicSet) for s in sets)

    def test_load_relics(self):
        relics = load_relics(DATA_DIR / "relics.json")
        assert len(relics) > 0
        assert all(isinstance(r, Relic) for r in relics)

    def test_load_relic_main_affixes(self):
        affixes = load_relic_main_affixes(DATA_DIR / "relic_main_affixes.json")
        assert len(affixes) > 0

    def test_load_relic_sub_affixes(self):
        affixes = load_relic_sub_affixes(DATA_DIR / "relic_sub_affixes.json")
        assert len(affixes) > 0

    def test_load_elements(self):
        elements = load_elements(DATA_DIR / "elements.json")
        assert len(elements) == 7

    def test_load_paths(self):
        paths = load_paths(DATA_DIR / "paths.json")
        assert len(paths) == 9

    def test_load_properties(self):
        props = load_properties(DATA_DIR / "properties.json")
        assert len(props) > 0

    def test_load_nonexistent_file(self):
        from hsr_nous.raw_schema.loader import load_json

        result = load_json(DATA_DIR / "nonexistent.json")
        assert result == []
