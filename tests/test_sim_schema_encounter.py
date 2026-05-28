"""encounter.py 测试.

测试目标：验证关卡/遭遇战的数据结构是否正确构建和默认值是否合理。

encounter.py 定义了战斗仿真的"场景"——包括敌人波次、环境条件、
公式配置、结束条件等。这是 Encounter 作为 sim_schema 顶层容器的核心。
"""

import pytest

from hsr_nous.sim_schema.encounter import (
    Encounter,
    FormulaConfig,
    TerminationConfig,
    Wave,
)
from hsr_nous.sim_schema.policy import Policy


# ---------------------------------------------------------------------------
# Wave：波次配置
# ---------------------------------------------------------------------------


class TestWave:
    """Wave 是战斗中的一个敌人波次，包含敌人列表和转波次触发效果。"""

    def test_minimal_construction(self):
        """只提供必填字段 wave_index，其余使用默认值。"""
        wave = Wave(wave_index=1)
        assert wave.wave_index == 1
        assert wave.enemy_ids == []
        assert wave.enemy_levels == []
        assert wave.on_wave_start == []

    def test_with_enemies(self):
        """波次包含敌人时，enemy_ids 和 enemy_levels 应一一对应。"""
        wave = Wave(
            wave_index=1,
            enemy_ids=["enemy_001", "enemy_002", "enemy_003"],
            enemy_levels=[80, 80, 85],
        )
        assert len(wave.enemy_ids) == 3
        assert len(wave.enemy_levels) == 3
        assert wave.enemy_ids[0] == "enemy_001"
        assert wave.enemy_levels[2] == 85

    def test_on_wave_start_effects(self):
        """转波次时可以触发效果列表，格式与 Modifier 的 on_apply 类似。"""
        effects = [
            {"type": "add_modifier", "modifier_id": "ENV_BUFF_ATK"},
            {"type": "remove_modifier", "modifier_id": "PREV_WAVE_DEBUFF"},
        ]
        wave = Wave(wave_index=2, on_wave_start=effects)
        assert len(wave.on_wave_start) == 2
        assert wave.on_wave_start[0]["type"] == "add_modifier"

    def test_default_lists_are_independent(self):
        """验证默认列表不会在不同实例间共享（dataclass 常见陷阱）。"""
        w1 = Wave(wave_index=1)
        w2 = Wave(wave_index=2)
        w1.enemy_ids.append("enemy_001")
        assert w2.enemy_ids == []  # 不应被 w1 污染


# ---------------------------------------------------------------------------
# FormulaConfig：伤害公式配置
# ---------------------------------------------------------------------------


class TestFormulaConfig:
    """FormulaConfig 定义伤害公式表达式及其参数。

    这允许 Encounter 自定义伤害计算公式，而非硬编码在 sim 中。
    """

    def test_minimal_construction(self):
        """只有 expression 字段是必填的。"""
        fc = FormulaConfig(expression="atk * abilityMulti * dmgBoostMulti")
        assert fc.expression == "atk * abilityMulti * dmgBoostMulti"
        assert fc.parameters == []

    def test_with_parameters(self):
        """parameters 列表描述公式中各参数的来源和约束。"""
        params = [
            {"name": "abilityMulti", "source": "action.scaling", "min": 0.0},
            {"name": "dmgBoostMulti", "source": "stats.dmg_bonus", "default": 1.0},
        ]
        fc = FormulaConfig(
            expression="atk * abilityMulti * dmgBoostMulti",
            parameters=params,
        )
        assert len(fc.parameters) == 2
        assert fc.parameters[0]["name"] == "abilityMulti"


# ---------------------------------------------------------------------------
# TerminationConfig：战斗结束条件
# ---------------------------------------------------------------------------


class TestTerminationConfig:
    """TerminationConfig 定义战斗何时结束。

    四种模式：
    - fixed_av: 达到最大行动值结束（默认，适合模拟轮次测试）
    - kill_target: 击杀指定敌人结束
    - survival: 存活到一定条件
    - wipe: 全灭
    """

    def test_defaults(self):
        """默认模式是 fixed_av，最大 AV 1500，最大 50 回合。"""
        tc = TerminationConfig()
        assert tc.mode == "fixed_av"
        assert tc.max_action_value == 1500
        assert tc.target_ids == []
        assert tc.max_turns == 50
        assert tc.max_battle_duration == 10000

    def test_kill_target_mode(self):
        """kill_target 模式需要指定目标 ID。"""
        tc = TerminationConfig(
            mode="kill_target",
            target_ids=["boss_001"],
        )
        assert tc.mode == "kill_target"
        assert tc.target_ids == ["boss_001"]

    def test_survival_mode(self):
        """survival 模式下 max_turns 控制存活时长。"""
        tc = TerminationConfig(mode="survival", max_turns=20)
        assert tc.mode == "survival"
        assert tc.max_turns == 20

    def test_wipe_mode(self):
        """wipe 模式表示全灭检查。"""
        tc = TerminationConfig(mode="wipe")
        assert tc.mode == "wipe"


# ---------------------------------------------------------------------------
# Encounter：完整仿真输入
# ---------------------------------------------------------------------------


class TestEncounter:
    """Encounter 是 sim_schema 的顶层容器，组合了所有仿真输入。

    一个完整的 Encounter 包含：
    - waves: 敌人波次列表
    - actors: 参战角色（通过 adapters 从 raw_schema 转换）
    - policy: 战斗策略（LLM 生成或手动编写）
    - formula: 伤害公式配置
    - globals: 全局状态（技能点、速度阈值等）
    - termination: 结束条件
    - initial_modifiers: 战斗开始时的场地效果
    """

    def test_minimal_construction(self):
        """只有 encounter_id 和 name 是必填的。"""
        enc = Encounter(encounter_id="test_001", name="测试关卡")
        assert enc.encounter_id == "test_001"
        assert enc.name == "测试关卡"
        assert enc.waves == []
        assert enc.environment == ""
        assert enc.turn_limit == 0
        assert enc.formula == {}
        assert enc.globals == {}
        assert enc.actors == []
        assert enc.policy is None
        assert enc.initial_modifiers == []
        assert isinstance(enc.termination, TerminationConfig)

    def test_full_construction(self):
        """完整构造一个包含所有字段的 Encounter。"""
        wave = Wave(wave_index=1, enemy_ids=["e1"], enemy_levels=[80])
        policy = Policy(name="test_policy")
        term = TerminationConfig(mode="kill_target", target_ids=["e1"])

        enc = Encounter(
            encounter_id="full_001",
            name="完整测试",
            waves=[wave],
            environment="simulated_universe",
            turn_limit=30,
            formula={"basic": FormulaConfig(expression="atk * 1.0")},
            globals={"skill_points": {"max": 5, "current": 3}},
            actors=["actor_placeholder"],  # 实际应为 Actor 实例
            policy=policy,
            initial_modifiers=["mod_001"],
            termination=term,
        )

        assert len(enc.waves) == 1
        assert enc.environment == "simulated_universe"
        assert enc.turn_limit == 30
        assert "basic" in enc.formula
        assert enc.globals["skill_points"]["max"] == 5
        assert enc.policy.name == "test_policy"
        assert enc.termination.mode == "kill_target"

    def test_multiple_waves(self):
        """Encounter 支持多波次战斗。"""
        waves = [
            Wave(wave_index=1, enemy_ids=["e1", "e2"], enemy_levels=[80, 80]),
            Wave(wave_index=2, enemy_ids=["boss_1"], enemy_levels=[90]),
        ]
        enc = Encounter(encounter_id="multi_wave", name="多波次", waves=waves)
        assert len(enc.waves) == 2
        assert enc.waves[1].enemy_ids == ["boss_1"]

    def test_default_lists_are_independent(self):
        """验证默认列表不会在不同实例间共享。"""
        e1 = Encounter(encounter_id="a", name="A")
        e2 = Encounter(encounter_id="b", name="B")
        e1.actors.append("x")
        assert e2.actors == []
