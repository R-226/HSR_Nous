"""Tests for sim_schema.action module."""

import pytest

from hsr_nous.sim_schema.action import Action
from hsr_nous.sim_schema.validator import VALID_ACTION_TYPES, VALID_TARGET_TYPES


class TestActionDefaults:
    """Action 默认构造测试."""

    def test_minimal_construction(self):
        """Action 最小构造（仅必填字段）应使用合理的默认值."""
        action = Action(
            action_id="1001_basic",
            name="寒冰之箭",
            action_type="basic",
            target_type="enemy_single",
        )

        assert action.action_id == "1001_basic"
        assert action.name == "寒冰之箭"
        assert action.action_type == "basic"
        assert action.target_type == "enemy_single"
        assert action.damage_type is None
        assert action.scaling == []
        assert action.energy_cost == 0
        assert action.energy_gain == 0
        assert action.skill_point_cost == 0
        assert action.skill_point_gain == 0
        assert action.toughness_dmg == 0
        assert action.effects == []

    def test_effects_default_is_independent_list(self):
        """不同 Action 的默认 effects 列表应互不干扰."""
        a1 = Action(action_id="a1", name="A1", action_type="basic", target_type="self")
        a2 = Action(action_id="a2", name="A2", action_type="skill", target_type="self")

        a1.effects.append({"effect_type": "deal_damage"})

        assert len(a1.effects) == 1
        assert len(a2.effects) == 0


class TestActionWithEffects:
    """Action 带 effects 字段的构造测试."""

    def test_single_damage_effect(self):
        """一个造成伤害的 effect."""
        action = Action(
            action_id="1001_basic",
            name="寒冰之箭",
            action_type="basic",
            target_type="enemy_single",
            damage_type="ice",
            energy_gain=20,
            skill_point_gain=1,
            toughness_dmg=10,
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "primary_target",
                    "effect_type": "deal_damage",
                    "formula": "damage",
                    "scaling": 0.5,
                },
            ],
        )

        assert len(action.effects) == 1
        effect = action.effects[0]
        assert effect["trigger"] == "on_cast"
        assert effect["target"] == "primary_target"
        assert effect["effect_type"] == "deal_damage"
        assert effect["formula"] == "damage"
        assert effect["scaling"] == 0.5

    def test_multi_effect_action(self):
        """一个技能同时造成伤害和施加 buff（多效果）."""
        action = Action(
            action_id="1001_ultimate",
            name="冰刻剑雨之时",
            action_type="ultimate",
            target_type="enemy_aoe",
            energy_cost=120,
            toughness_dmg=30,
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "all_enemies",
                    "effect_type": "deal_damage",
                    "formula": "damage",
                    "scaling": 1.5,
                    "damage_type": "ice",
                },
                {
                    "trigger": "on_cast",
                    "target": "random_enemy",
                    "effect_type": "apply_modifier",
                    "modifier_id": "MOD_1001_FREEZE",
                    "duration": 1,
                    "chance": 0.5,
                },
            ],
        )

        assert len(action.effects) == 2

        dmg_effect = action.effects[0]
        assert dmg_effect["effect_type"] == "deal_damage"
        assert dmg_effect["scaling"] == 1.5
        assert dmg_effect["damage_type"] == "ice"

        debuff_effect = action.effects[1]
        assert debuff_effect["effect_type"] == "apply_modifier"
        assert debuff_effect["modifier_id"] == "MOD_1001_FREEZE"
        assert debuff_effect["duration"] == 1
        assert debuff_effect["chance"] == 0.5

    def test_shield_effect(self):
        """护盾技能（施加 buff + 无伤害）."""
        action = Action(
            action_id="1001_skill",
            name="可爱即是正义",
            action_type="skill",
            target_type="ally_single",
            skill_point_cost=1,
            toughness_dmg=20,
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "primary_target",
                    "effect_type": "apply_modifier",
                    "modifier_id": "MOD_1001_SHIELD",
                    "duration": 3,
                },
            ],
        )

        assert len(action.effects) == 1
        assert action.effects[0]["effect_type"] == "apply_modifier"
        assert action.effects[0]["modifier_id"] == "MOD_1001_SHIELD"

    def test_gain_energy_effect(self):
        """回能效果."""
        action = Action(
            action_id="test_energy",
            name="回能测试",
            action_type="basic",
            target_type="self",
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "self",
                    "effect_type": "gain_energy",
                    "value": 30,
                },
            ],
        )

        assert action.effects[0]["effect_type"] == "gain_energy"
        assert action.effects[0]["value"] == 30

    def test_advance_action_effect(self):
        """拉条效果."""
        action = Action(
            action_id="test_advance",
            name="拉条测试",
            action_type="skill",
            target_type="self",
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "self",
                    "effect_type": "advance_action",
                    "value": 100,
                },
            ],
        )

        assert action.effects[0]["effect_type"] == "advance_action"
        assert action.effects[0]["value"] == 100

    def test_conditional_effect(self):
        """带触发条件的效果."""
        action = Action(
            action_id="test_cond",
            name="条件测试",
            action_type="talent",
            target_type="enemy_single",
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "primary_target",
                    "effect_type": "deal_damage",
                    "formula": "damage",
                    "scaling": 0.8,
                    "condition": "target.hp < 0.5",
                },
            ],
        )

        assert action.effects[0]["condition"] == "target.hp < 0.5"


class TestActionTypeValues:
    """action_type 合法值测试."""

    @pytest.mark.parametrize(
        "action_type",
        ["basic", "skill", "ultimate", "talent", "follow_up", "elation_damage"],
    )
    def test_valid_action_types(self, action_type):
        """所有合法 action_type 应可正常构造 Action."""
        action = Action(
            action_id=f"test_{action_type}",
            name=f"Test {action_type}",
            action_type=action_type,
            target_type="self",
        )
        assert action.action_type == action_type

    def test_action_types_match_validator(self):
        """action_type 合法值集合应与 validator 中的定义一致."""
        for at in ["basic", "skill", "ultimate", "talent", "follow_up", "elation_damage"]:
            assert at in VALID_ACTION_TYPES, f"'{at}' should be in VALID_ACTION_TYPES"


class TestTargetTypeValues:
    """target_type 合法值测试."""

    @pytest.mark.parametrize(
        "target_type",
        ["enemy_single", "enemy_blast", "enemy_aoe", "ally_single", "ally_aoe", "self"],
    )
    def test_valid_target_types(self, target_type):
        """所有合法 target_type 应可正常构造 Action."""
        action = Action(
            action_id=f"test_{target_type}",
            name=f"Test {target_type}",
            action_type="basic",
            target_type=target_type,
        )
        assert action.target_type == target_type

    def test_target_types_match_validator(self):
        """target_type 合法值集合应与 validator 中的定义一致."""
        for tt in ["enemy_single", "enemy_blast", "enemy_aoe", "ally_single", "ally_aoe", "self"]:
            assert tt in VALID_TARGET_TYPES, f"'{tt}' should be in VALID_TARGET_TYPES"


class TestActionCosts:
    """能量与战技点消耗测试."""

    def test_ultimate_energy_cost(self):
        """终结技应有能量消耗."""
        action = Action(
            action_id="test_ult",
            name="终结技",
            action_type="ultimate",
            target_type="enemy_aoe",
            energy_cost=120,
            effects=[
                {
                    "trigger": "on_cast",
                    "target": "all_enemies",
                    "effect_type": "deal_damage",
                    "formula": "damage",
                    "scaling": 2.0,
                },
            ],
        )

        assert action.energy_cost == 120
        assert action.energy_gain == 0

    def test_basic_skill_point_gain(self):
        """普攻应获取战技点."""
        action = Action(
            action_id="test_basic",
            name="普攻",
            action_type="basic",
            target_type="enemy_single",
            energy_gain=20,
            skill_point_gain=1,
            toughness_dmg=10,
        )

        assert action.skill_point_cost == 0
        assert action.skill_point_gain == 1
        assert action.energy_gain == 20
        assert action.toughness_dmg == 10

    def test_skill_point_cost(self):
        """战技应消耗战技点."""
        action = Action(
            action_id="test_skill",
            name="战技",
            action_type="skill",
            target_type="enemy_single",
            skill_point_cost=1,
            toughness_dmg=20,
        )

        assert action.skill_point_cost == 1
        assert action.skill_point_gain == 0
        assert action.toughness_dmg == 20

    def test_toughness_dmg_values(self):
        """不同技能类型的削韧值."""
        basic = Action(
            action_id="b", name="普攻", action_type="basic", target_type="enemy_single",
            toughness_dmg=10,
        )
        skill = Action(
            action_id="s", name="战技", action_type="skill", target_type="enemy_single",
            toughness_dmg=20,
        )
        ultimate = Action(
            action_id="u", name="终结技", action_type="ultimate", target_type="enemy_aoe",
            toughness_dmg=30,
        )

        assert basic.toughness_dmg == 10
        assert skill.toughness_dmg == 20
        assert ultimate.toughness_dmg == 30
