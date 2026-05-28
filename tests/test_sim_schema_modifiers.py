"""sim_schema Modifier 的单元测试."""

import pytest

from hsr_nous.sim_schema.modifiers import Modifier


class TestModifierDefaults:
    """测试 Modifier 默认值."""

    def test_minimal_construction(self):
        """只传必填字段，其余使用默认值."""
        m = Modifier(modifier_id="MOD_001", name="测试", modifier_type="buff")
        assert m.modifier_id == "MOD_001"
        assert m.name == "测试"
        assert m.modifier_type == "buff"
        assert m.stat_changes is None
        assert m.duration == 0
        assert m.max_stack == 1
        assert m.stack_mode == "refresh"
        assert m.dispellable is True
        assert m.buff_class == "A"
        assert m.on_apply == []
        assert m.on_turn_start == []
        assert m.on_turn_end == []
        assert m.on_expire == []
        assert m.condition is None

    def test_list_defaults_are_independent(self):
        """多次构造的列表默认值应互不影响."""
        m1 = Modifier(modifier_id="M1", name="A", modifier_type="buff")
        m2 = Modifier(modifier_id="M2", name="B", modifier_type="debuff")
        m1.on_apply.append({"effect_type": "add_stat", "stat": "atk", "value": 100})
        assert m2.on_apply == []
        assert len(m1.on_apply) == 1


class TestModifierFullConstruction:
    """测试完整构造（所有字段）."""

    def test_all_fields(self):
        """传入所有字段."""
        on_apply = [{"effect_type": "add_stat", "stat": "shield", "value": 1000}]
        on_turn_start = [{"effect_type": "deal_damage", "damage_type": "fire", "scaling": 0.5}]
        on_turn_end = [{"effect_type": "heal", "value": 200}]
        on_expire = [{"effect_type": "remove_stat", "stat": "shield"}]

        m = Modifier(
            modifier_id="MOD_FULL",
            name="完整护盾",
            modifier_type="shield",
            stat_changes={"def_pct": 0.3},
            duration=3,
            max_stack=2,
            stack_mode="independent",
            dispellable=False,
            buff_class="B",
            on_apply=on_apply,
            on_turn_start=on_turn_start,
            on_turn_end=on_turn_end,
            on_expire=on_expire,
            condition="target.hp_pct < 0.5",
        )

        assert m.modifier_id == "MOD_FULL"
        assert m.name == "完整护盾"
        assert m.modifier_type == "shield"
        assert m.stat_changes == {"def_pct": 0.3}
        assert m.duration == 3
        assert m.max_stack == 2
        assert m.stack_mode == "independent"
        assert m.dispellable is False
        assert m.buff_class == "B"
        assert m.on_apply == on_apply
        assert m.on_turn_start == on_turn_start
        assert m.on_turn_end == on_turn_end
        assert m.on_expire == on_expire
        assert m.condition == "target.hp_pct < 0.5"


class TestModifierTypeValues:
    """测试 modifier_type 合法值."""

    @pytest.mark.parametrize(
        "mtype",
        ["buff", "debuff", "dot", "shield", "heal", "control"],
    )
    def test_valid_modifier_types(self, mtype):
        """所有合法 modifier_type 都能正常构造."""
        m = Modifier(modifier_id="MOD_T", name="类型测试", modifier_type=mtype)
        assert m.modifier_type == mtype


class TestStackModeValues:
    """测试 stack_mode 合法值."""

    @pytest.mark.parametrize(
        "mode",
        ["refresh", "independent", "replace"],
    )
    def test_valid_stack_modes(self, mode):
        """所有合法 stack_mode 都能正常构造."""
        m = Modifier(
            modifier_id="MOD_S",
            name="叠加测试",
            modifier_type="buff",
            stack_mode=mode,
        )
        assert m.stack_mode == mode


class TestBuffClassValues:
    """测试 buff_class 合法值."""

    @pytest.mark.parametrize(
        "cls",
        ["A", "B"],
    )
    def test_valid_buff_classes(self, cls):
        """所有合法 buff_class 都能正常构造."""
        m = Modifier(
            modifier_id="MOD_B",
            name="类别测试",
            modifier_type="buff",
            buff_class=cls,
        )
        assert m.buff_class == cls


class TestModifierTypicalScenarios:
    """测试典型游戏场景的 Modifier 构造."""

    def test_dot_modifier(self):
        """DOT（持续伤害）场景."""
        m = Modifier(
            modifier_id="MOD_DOT_FIRE",
            name="灼烧",
            modifier_type="dot",
            duration=2,
            max_stack=3,
            stack_mode="independent",
            on_turn_start=[
                {"effect_type": "deal_damage", "damage_type": "fire", "scaling": 0.5}
            ],
        )
        assert m.modifier_type == "dot"
        assert m.max_stack == 3
        assert m.stack_mode == "independent"
        assert len(m.on_turn_start) == 1

    def test_debuff_with_condition(self):
        """带条件的 debuff."""
        m = Modifier(
            modifier_id="MOD_DEF_DOWN",
            name="防御降低",
            modifier_type="debuff",
            stat_changes={"def_reduction": 0.3},
            duration=2,
            dispellable=True,
            buff_class="B",
            on_apply=[{"effect_type": "add_stat", "stat": "def_reduction", "value": 0.3}],
            on_expire=[{"effect_type": "remove_stat", "stat": "def_reduction"}],
        )
        assert m.buff_class == "B"
        assert m.dispellable is True
        assert m.stat_changes == {"def_reduction": 0.3}

    def test_permanent_buff(self):
        """永久 buff（duration=0）."""
        m = Modifier(
            modifier_id="MOD_PERM",
            name="天赋常驻",
            modifier_type="buff",
            duration=0,
            dispellable=False,
        )
        assert m.duration == 0
        assert m.dispellable is False
