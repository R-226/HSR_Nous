"""validator.py 测试.

测试目标：验证输入校验逻辑是否正确捕获非法配置。

validator.py 是 sim_schema 的"守门人"——在仿真开始前检查 Encounter 配置
是否合法，避免运行时出现意外错误。校验覆盖：
- Encounter 基础字段
- 全局状态（技能点等）
- Actor 列表（角色数上限、属性合法性）
- Wave 列表（波次上限、敌人 ID/level 一致性）
- TerminationConfig（结束条件模式）
- Modifier（类型、叠层、持续时间等）

校验结果分两级：error（必须修复）和 warning（建议修复）。
"""

import pytest

from hsr_nous.sim_schema.actor import Actor, StatBlock
from hsr_nous.sim_schema.encounter import Encounter, TerminationConfig, Wave
from hsr_nous.sim_schema.modifiers import Modifier
from hsr_nous.sim_schema.validator import (
    MAX_ACTIONS_PER_ACTOR,
    MAX_ENEMIES_PER_WAVE,
    MAX_MODIFIER_STACK,
    MAX_TEAM_SIZE,
    MAX_WAVES,
    VALID_ACTOR_TYPES,
    VALID_ACTION_TYPES,
    VALID_BUFF_CLASSES,
    VALID_ELEMENT_TYPES,
    VALID_MODIFIER_TYPES,
    VALID_STACK_MODES,
    VALID_TARGET_TYPES,
    VALID_TERMINATION_MODES,
    ValidationError,
    ValidationResult,
    validate_actor,
    validate_actors,
    validate_encounter,
    validate_globals,
    validate_modifier,
    validate_stats,
    validate_termination,
    validate_wave,
    validate_waves,
)


# ---------------------------------------------------------------------------
# ValidationError & ValidationResult：验证结果容器
# ---------------------------------------------------------------------------


class TestValidationResult:
    """ValidationResult 收集验证过程中的所有 error 和 warning。

    - valid 属性：无 error 时为 True（warning 不影响）
    - add_error/add_warning：添加对应级别的问题
    - merge：合并另一个 ValidationResult（用于子组件验证汇总）
    """

    def test_empty_is_valid(self):
        """没有 error 的结果是 valid 的。"""
        r = ValidationResult()
        assert r.valid is True
        assert r.errors == []
        assert r.warnings == []

    def test_add_error_makes_invalid(self):
        """添加 error 后 valid 变为 False。"""
        r = ValidationResult()
        r.add_error("field", "不能为负数")
        assert r.valid is False
        assert len(r.errors) == 1
        assert r.errors[0].path == "field"
        assert r.errors[0].message == "不能为负数"
        assert r.errors[0].severity == "error"

    def test_add_warning_stays_valid(self):
        """只有 warning 时仍然 valid。"""
        r = ValidationResult()
        r.add_warning("name", "建议填写名称")
        assert r.valid is True
        assert len(r.warnings) == 1
        assert r.warnings[0].severity == "warning"

    def test_merge(self):
        """merge 合并两个结果的 errors 和 warnings。"""
        r1 = ValidationResult()
        r1.add_error("a", "error_a")
        r2 = ValidationResult()
        r2.add_error("b", "error_b")
        r2.add_warning("c", "warning_c")

        r1.merge(r2)
        assert len(r1.errors) == 2
        assert len(r1.warnings) == 1


class TestValidationError:
    """ValidationError 记录单个校验问题的路径和描述。"""

    def test_construction(self):
        err = ValidationError(
            path="actors[0].stats.hp",
            message="不能为负数",
            severity="error",
        )
        assert err.path == "actors[0].stats.hp"
        assert err.message == "不能为负数"
        assert err.severity == "error"


# ---------------------------------------------------------------------------
# validate_encounter：顶层验证入口
# ---------------------------------------------------------------------------


class TestValidateEncounter:
    """validate_encounter 是顶层验证函数，组合所有子验证。

    它检查 encounter_id 和 name，然后委托给子验证函数。
    """

    def test_valid_encounter(self):
        """合法的 Encounter 应通过验证。"""
        enc = Encounter(encounter_id="e1", name="测试")
        r = validate_encounter(enc)
        assert r.valid is True

    def test_empty_encounter_id_is_error(self):
        """encounter_id 为空是 error。"""
        enc = Encounter(encounter_id="", name="测试")
        r = validate_encounter(enc)
        assert r.valid is False
        assert any("encounter_id" in e.path for e in r.errors)

    def test_empty_name_is_warning(self):
        """name 为空是 warning（不影响 valid）。"""
        enc = Encounter(encounter_id="e1", name="")
        r = validate_encounter(enc)
        assert r.valid is True
        assert len(r.warnings) >= 1


# ---------------------------------------------------------------------------
# validate_globals：全局状态验证
# ---------------------------------------------------------------------------


class TestValidateGlobals:
    """validate_globals 检查全局状态配置（目前主要是技能点）。"""

    def test_empty_globals_is_valid(self):
        """空 globals 字典是合法的。"""
        r = validate_globals({})
        assert r.valid is True

    def test_valid_skill_points(self):
        """合法的技能点配置。"""
        r = validate_globals({"skill_points": {"max": 5, "current": 3}})
        assert r.valid is True

    def test_negative_max_is_error(self):
        """技能点上限为负数是 error。"""
        r = validate_globals({"skill_points": {"max": -1}})
        assert r.valid is False

    def test_current_exceeds_max_is_error(self):
        """当前技能点超过上限是 error。"""
        r = validate_globals({"skill_points": {"max": 5, "current": 6}})
        assert r.valid is False


# ---------------------------------------------------------------------------
# validate_actors / validate_actor：角色验证
# ---------------------------------------------------------------------------


def _make_actor(**kwargs) -> Actor:
    """辅助函数：创建测试用 Actor。"""
    defaults = {
        "actor_id": "char_001",
        "name": "测试角色",
        "actor_type": "character",
        "level": 80,
        "stats": StatBlock(spd=100),
    }
    defaults.update(kwargs)
    return Actor(**defaults)


class TestValidateActors:
    """validate_actors 检查角色列表的整体合法性。

    关键规则：
    - 角色（character）数量不超过 MAX_TEAM_SIZE (4)
    - 至少应有一个角色（warning）
    - 每个元素必须是 Actor 实例
    """

    def test_valid_single_character(self):
        """单个合法角色应通过。"""
        r = validate_actors([_make_actor()])
        assert r.valid is True

    def test_too_many_characters_is_error(self):
        """超过 MAX_TEAM_SIZE 个角色是 error。"""
        actors = [_make_actor(actor_id=f"c{i}") for i in range(MAX_TEAM_SIZE + 1)]
        r = validate_actors(actors)
        assert r.valid is False
        assert any("角色数量" in e.message for e in r.errors)

    def test_no_characters_is_warning(self):
        """没有角色单位是 warning（可能只有怪物的测试场景）。"""
        monster = _make_actor(actor_id="m1", actor_type="monster")
        r = validate_actors([monster])
        assert r.valid is True
        assert any("没有角色" in w.message for w in r.warnings)

    def test_non_actor_instance_is_error(self):
        """列表中包含非 Actor 实例是 error。"""
        r = validate_actors(["not_an_actor"])
        assert r.valid is False
        assert any("必须是 Actor 实例" in e.message for e in r.errors)


class TestValidateActor:
    """validate_actor 检查单个 Actor 的字段合法性。

    关键规则：
    - actor_id 不能为空
    - actor_type 必须在 VALID_ACTOR_TYPES 中
    - level 必须在 1-90 之间
    - actions 数量不超过 MAX_ACTIONS_PER_ACTOR
    """

    def test_valid_actor(self):
        """合法 Actor 应通过验证。"""
        r = validate_actor(_make_actor(), "actors[0]")
        assert r.valid is True

    def test_empty_actor_id_is_error(self):
        """actor_id 为空是 error。"""
        r = validate_actor(_make_actor(actor_id=""), "actors[0]")
        assert r.valid is False

    def test_invalid_actor_type_is_error(self):
        """非法 actor_type 是 error。"""
        r = validate_actor(_make_actor(actor_type="pet"), "actors[0]")
        assert r.valid is False

    def test_all_valid_actor_types(self):
        """VALID_ACTOR_TYPES 中的所有类型都应通过。"""
        for atype in VALID_ACTOR_TYPES:
            r = validate_actor(_make_actor(actor_type=atype), "actors[0]")
            assert r.valid is True, f"actor_type='{atype}' 应该合法"

    def test_level_out_of_range_is_error(self):
        """等级超出 1-90 范围是 error。"""
        r = validate_actor(_make_actor(level=0), "actors[0]")
        assert r.valid is False
        r = validate_actor(_make_actor(level=91), "actors[0]")
        assert r.valid is False

    def test_too_many_actions_is_error(self):
        """技能数量超过上限是 error。"""
        actor = _make_actor(actions=[f"a{i}" for i in range(MAX_ACTIONS_PER_ACTOR + 1)])
        r = validate_actor(actor, "actors[0]")
        assert r.valid is False

    def test_empty_name_is_warning(self):
        """name 为空是 warning。"""
        r = validate_actor(_make_actor(name=""), "actors[0]")
        assert r.valid is True
        assert any("name" in w.path for w in r.warnings)


# ---------------------------------------------------------------------------
# validate_stats：属性验证
# ---------------------------------------------------------------------------


class TestValidateStats:
    """validate_stats 检查 StatBlock 中各属性的数值范围。

    关键规则：
    - hp/atk/def 不能为负
    - spd 必须 > 0
    - crit_rate 通常在 0-1 之间（warning，因为可能有 buff 超出）
    - energy 不能超过 max_energy
    - toughness 不能超过 max_toughness
    """

    def test_valid_stats(self):
        """合法属性应通过。"""
        stats = StatBlock(hp=1000, atk=500, def_=300, spd=100)
        r = validate_stats(stats, "test")
        assert r.valid is True

    def test_negative_hp_is_error(self):
        """hp 为负是 error。"""
        r = validate_stats(StatBlock(hp=-1, spd=100), "test")
        assert r.valid is False

    def test_negative_atk_is_error(self):
        """atk 为负是 error。"""
        r = validate_stats(StatBlock(atk=-1, spd=100), "test")
        assert r.valid is False

    def test_zero_spd_is_error(self):
        """spd 为 0 是 error（会导致除零）。"""
        r = validate_stats(StatBlock(spd=0), "test")
        assert r.valid is False

    def test_negative_spd_is_error(self):
        """spd 为负是 error。"""
        r = validate_stats(StatBlock(spd=-1), "test")
        assert r.valid is False

    def test_crit_rate_out_of_range_is_warning(self):
        """暴击率超出 0-1 是 warning（不一定是错误，可能有 buff）。"""
        r = validate_stats(StatBlock(crit_rate=1.5, spd=100), "test")
        assert r.valid is True
        assert any("crit_rate" in w.path for w in r.warnings)

    def test_energy_exceeds_max_is_error(self):
        """当前能量超过上限是 error。"""
        r = validate_stats(StatBlock(energy=130, max_energy=120, spd=100), "test")
        assert r.valid is False

    def test_toughness_exceeds_max_is_error(self):
        """当前韧性超过上限是 error。"""
        r = validate_stats(StatBlock(toughness=100, max_toughness=80, spd=100), "test")
        assert r.valid is False

    def test_negative_crit_dmg_is_error(self):
        """暴击伤害为负是 error。"""
        r = validate_stats(StatBlock(crit_dmg=-0.5, spd=100), "test")
        assert r.valid is False


# ---------------------------------------------------------------------------
# validate_waves / validate_wave：波次验证
# ---------------------------------------------------------------------------


class TestValidateWaves:
    """validate_waves 检查波次列表的合法性。

    关键规则：
    - 波次数不超过 MAX_WAVES (10)
    - 每个元素必须是 Wave 实例
    """

    def test_valid_waves(self):
        """合法波次列表应通过。"""
        waves = [Wave(wave_index=1, enemy_ids=["e1"], enemy_levels=[80])]
        r = validate_waves(waves)
        assert r.valid is True

    def test_too_many_waves_is_error(self):
        """超过 MAX_WAVES 个波次是 error。"""
        waves = [Wave(wave_index=i + 1) for i in range(MAX_WAVES + 1)]
        r = validate_waves(waves)
        assert r.valid is False

    def test_non_wave_instance_is_error(self):
        """列表中包含非 Wave 实例是 error。"""
        r = validate_waves(["not_a_wave"])
        assert r.valid is False


class TestValidateWave:
    """validate_wave 检查单个波次的字段合法性。

    关键规则：
    - wave_index 必须 >= 1
    - 敌人数不超过 MAX_ENEMIES_PER_WAVE (10)
    - enemy_ids 和 enemy_levels 长度必须一致
    - 没有敌人是 warning
    """

    def test_valid_wave(self):
        """合法波次应通过。"""
        wave = Wave(wave_index=1, enemy_ids=["e1"], enemy_levels=[80])
        r = validate_wave(wave, "waves[0]")
        assert r.valid is True

    def test_wave_index_zero_is_error(self):
        """wave_index 为 0 是 error（必须 >= 1）。"""
        r = validate_wave(Wave(wave_index=0), "waves[0]")
        assert r.valid is False

    def test_too_many_enemies_is_error(self):
        """超过 MAX_ENEMIES_PER_WAVE 个敌人是 error。"""
        wave = Wave(
            wave_index=1,
            enemy_ids=[f"e{i}" for i in range(MAX_ENEMIES_PER_WAVE + 1)],
            enemy_levels=[80] * (MAX_ENEMIES_PER_WAVE + 1),
        )
        r = validate_wave(wave, "waves[0]")
        assert r.valid is False

    def test_empty_enemies_is_warning(self):
        """没有敌人是 warning。"""
        r = validate_wave(Wave(wave_index=1), "waves[0]")
        assert r.valid is True
        assert any("敌人" in w.message for w in r.warnings)

    def test_mismatched_lengths_is_error(self):
        """enemy_ids 和 enemy_levels 长度不一致是 error。"""
        wave = Wave(
            wave_index=1,
            enemy_ids=["e1", "e2"],
            enemy_levels=[80],
        )
        r = validate_wave(wave, "waves[0]")
        assert r.valid is False
        assert any("长度不一致" in e.message for e in r.errors)


# ---------------------------------------------------------------------------
# validate_termination：结束条件验证
# ---------------------------------------------------------------------------


class TestValidateTermination:
    """validate_termination 检查结束条件配置。

    关键规则：
    - mode 必须在 VALID_TERMINATION_MODES 中
    - max_turns 必须 >= 1
    - max_action_value 必须 >= 1
    - kill_target 模式建议指定 target_ids（warning）
    """

    def test_valid_termination(self):
        """默认 TerminationConfig 应通过验证。"""
        r = validate_termination(TerminationConfig())
        assert r.valid is True

    def test_invalid_mode_is_error(self):
        """非法 mode 是 error。"""
        r = validate_termination(TerminationConfig(mode="invalid"))
        assert r.valid is False

    def test_all_valid_modes(self):
        """VALID_TERMINATION_MODES 中的所有模式都应通过。"""
        for mode in VALID_TERMINATION_MODES:
            r = validate_termination(TerminationConfig(mode=mode))
            assert r.valid is True, f"mode='{mode}' 应该合法"

    def test_max_turns_zero_is_error(self):
        """max_turns 为 0 是 error。"""
        r = validate_termination(TerminationConfig(max_turns=0))
        assert r.valid is False

    def test_max_action_value_zero_is_error(self):
        """max_action_value 为 0 是 error。"""
        r = validate_termination(TerminationConfig(max_action_value=0))
        assert r.valid is False

    def test_kill_target_without_ids_is_warning(self):
        """kill_target 模式没有 target_ids 是 warning。"""
        r = validate_termination(TerminationConfig(mode="kill_target"))
        assert r.valid is True
        assert any("target_ids" in w.path for w in r.warnings)

    def test_kill_target_with_ids_is_valid(self):
        """kill_target 模式有 target_ids 应通过。"""
        r = validate_termination(
            TerminationConfig(mode="kill_target", target_ids=["boss_1"])
        )
        assert r.valid is True


# ---------------------------------------------------------------------------
# validate_modifier：Modifier 验证
# ---------------------------------------------------------------------------


class TestValidateModifier:
    """validate_modifier 检查 Modifier 的字段合法性。

    关键规则：
    - modifier_id 不能为空
    - modifier_type 必须在 VALID_MODIFIER_TYPES 中
    - duration 不能为负（0 表示永久）
    - max_stack 必须在 1 到 MAX_MODIFIER_STACK 之间
    - stack_mode 必须在 VALID_STACK_MODES 中
    - buff_class 必须在 VALID_BUFF_CLASSES 中
    """

    def _make_mod(self, **kwargs) -> Modifier:
        """辅助函数：创建测试用 Modifier。"""
        defaults = {
            "modifier_id": "mod_001",
            "name": "测试 buff",
            "modifier_type": "buff",
        }
        defaults.update(kwargs)
        return Modifier(**defaults)

    def test_valid_modifier(self):
        """合法 Modifier 应通过验证。"""
        r = validate_modifier(self._make_mod(), "test")
        assert r.valid is True

    def test_empty_id_is_error(self):
        """modifier_id 为空是 error。"""
        r = validate_modifier(self._make_mod(modifier_id=""), "test")
        assert r.valid is False

    def test_invalid_type_is_error(self):
        """非法 modifier_type 是 error。"""
        r = validate_modifier(self._make_mod(modifier_type="unknown"), "test")
        assert r.valid is False

    def test_all_valid_types(self):
        """VALID_MODIFIER_TYPES 中的所有类型都应通过。"""
        for mtype in VALID_MODIFIER_TYPES:
            r = validate_modifier(self._make_mod(modifier_type=mtype), "test")
            assert r.valid is True, f"modifier_type='{mtype}' 应该合法"

    def test_negative_duration_is_error(self):
        """duration 为负是 error。"""
        r = validate_modifier(self._make_mod(duration=-1), "test")
        assert r.valid is False

    def test_zero_duration_is_valid(self):
        """duration 为 0 表示永久，是合法的。"""
        r = validate_modifier(self._make_mod(duration=0), "test")
        assert r.valid is True

    def test_max_stack_zero_is_error(self):
        """max_stack 为 0 是 error。"""
        r = validate_modifier(self._make_mod(max_stack=0), "test")
        assert r.valid is False

    def test_max_stack_exceeds_limit_is_error(self):
        """max_stack 超过 MAX_MODIFIER_STACK 是 error。"""
        r = validate_modifier(self._make_mod(max_stack=MAX_MODIFIER_STACK + 1), "test")
        assert r.valid is False

    def test_all_valid_stack_modes(self):
        """VALID_STACK_MODES 中的所有模式都应通过。"""
        for mode in VALID_STACK_MODES:
            r = validate_modifier(self._make_mod(stack_mode=mode), "test")
            assert r.valid is True, f"stack_mode='{mode}' 应该合法"

    def test_invalid_stack_mode_is_error(self):
        """非法 stack_mode 是 error。"""
        r = validate_modifier(self._make_mod(stack_mode="merge"), "test")
        assert r.valid is False

    def test_all_valid_buff_classes(self):
        """VALID_BUFF_CLASSES 中的所有类别都应通过。"""
        for bc in VALID_BUFF_CLASSES:
            r = validate_modifier(self._make_mod(buff_class=bc), "test")
            assert r.valid is True, f"buff_class='{bc}' 应该合法"

    def test_invalid_buff_class_is_error(self):
        """非法 buff_class 是 error。"""
        r = validate_modifier(self._make_mod(buff_class="C"), "test")
        assert r.valid is False


# ---------------------------------------------------------------------------
# 常量完整性：确保常量集合不为空且包含预期值
# ---------------------------------------------------------------------------


class TestConstants:
    """验证常量值是否符合预期，防止意外修改。"""

    def test_max_team_size(self):
        assert MAX_TEAM_SIZE == 4

    def test_max_enemies_per_wave(self):
        assert MAX_ENEMIES_PER_WAVE == 10

    def test_max_waves(self):
        assert MAX_WAVES == 10

    def test_valid_actor_types_contains_expected(self):
        assert "character" in VALID_ACTOR_TYPES
        assert "monster" in VALID_ACTOR_TYPES
        assert "summon" in VALID_ACTOR_TYPES

    def test_valid_termination_modes_contains_expected(self):
        assert "fixed_av" in VALID_TERMINATION_MODES
        assert "kill_target" in VALID_TERMINATION_MODES
