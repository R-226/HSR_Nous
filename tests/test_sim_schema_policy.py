"""policy.py 测试.

测试目标：验证策略 DSL 的数据结构是否正确构建。

policy.py 定义了战斗策略的核心抽象：
- PolicyRule: 技能选择规则（条件 → 动作）
- TargetRule: 目标选择规则（条件 → 选择器）
- TimingRule: 时机策略（延迟/提前行动）
- Policy: 完整策略容器，包含参数表供规则引用

这是 LLM 生成策略 → 模拟器执行策略 的接口层。
LLM 输出 JSON，解析为 Policy 对象，模拟器通过 PolicyInterpreter 执行。
"""

import pytest

from hsr_nous.sim_schema.policy import (
    Policy,
    PolicyRule,
    TargetRule,
    TimingRule,
)


# ---------------------------------------------------------------------------
# PolicyRule：技能选择规则
# ---------------------------------------------------------------------------


class TestPolicyRule:
    """PolicyRule 表示"当条件满足时，执行某个技能动作"。

    规则按 priority 降序匹配，第一条满足的被执行。
    这是战斗 AI 的核心决策单元。
    """

    def test_minimal_construction(self):
        """condition 和 action 是必填字段。"""
        rule = PolicyRule(
            condition="energy >= 120",
            action="ultimate",
        )
        assert rule.condition == "energy >= 120"
        assert rule.action == "ultimate"
        assert rule.priority == 0
        assert rule.description == ""

    def test_full_construction(self):
        """包含优先级和描述的完整规则。"""
        rule = PolicyRule(
            condition="energy >= ULT_THRESHOLD",
            action="ultimate",
            priority=100,
            description="能量满时释放终结技",
        )
        assert rule.priority == 100
        assert rule.description == "能量满时释放终结技"

    def test_different_actions(self):
        """验证支持的各种动作类型。"""
        for action in ["ultimate", "skill", "basic", "pass"]:
            rule = PolicyRule(condition="true", action=action)
            assert rule.action == action

    def test_priority_ordering(self):
        """高优先级规则应排在前面（模拟器按 priority 降序匹配）。"""
        rules = [
            PolicyRule(condition="a", action="basic", priority=10),
            PolicyRule(condition="b", action="skill", priority=50),
            PolicyRule(condition="c", action="ultimate", priority=100),
        ]
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        assert sorted_rules[0].action == "ultimate"
        assert sorted_rules[2].action == "basic"

    def test_parameter_reference_in_condition(self):
        """condition 可以引用 Policy.parameters 中定义的参数名。"""
        rule = PolicyRule(
            condition="energy >= ULT_THRESHOLD",
            action="ultimate",
        )
        # 参数名在 condition 中以裸标识符出现，由 PolicyInterpreter 替换
        assert "ULT_THRESHOLD" in rule.condition


# ---------------------------------------------------------------------------
# TargetRule：目标选择规则
# ---------------------------------------------------------------------------


class TestTargetRule:
    """TargetRule 表示"当条件满足时，用某个选择器选目标"。

    selector 支持两种形式：
    1. 字符串：引用预注册的选择器（如 "lowest_hp"）
    2. 字典：参数化选择器（如 {"type": "min", "key": "stats.hp"}）
    """

    def test_string_selector(self):
        """使用预注册选择器名称。"""
        rule = TargetRule(
            condition="true",
            selector="lowest_hp",
        )
        assert rule.selector == "lowest_hp"
        assert rule.priority == 0

    def test_dict_selector(self):
        """使用参数化选择器，内联定义选择逻辑。"""
        selector = {"type": "min", "key": "stats.hp"}
        rule = TargetRule(
            condition="action.target_type == 'single'",
            selector=selector,
        )
        assert rule.selector["type"] == "min"
        assert rule.selector["key"] == "stats.hp"

    def test_filter_selector(self):
        """filter 类型选择器用于按条件筛选目标。"""
        selector = {"type": "filter", "condition": "stats.hp < max_hp * 0.5"}
        rule = TargetRule(
            condition="need_heal",
            selector=selector,
        )
        assert rule.selector["type"] == "filter"

    def test_has_modifier_selector(self):
        """has_modifier 选择器用于选中带特定 buff 的目标。"""
        selector = {"type": "has_modifier", "modifier_id": "MOD_SHIELD"}
        rule = TargetRule(condition="need_shield", selector=selector)
        assert rule.selector["modifier_id"] == "MOD_SHIELD"

    def test_with_priority(self):
        """目标规则也支持优先级排序。"""
        rule = TargetRule(
            condition="true",
            selector="primary_target",
            priority=10,
        )
        assert rule.priority == 10


# ---------------------------------------------------------------------------
# TimingRule：时机策略
# ---------------------------------------------------------------------------


class TestTimingRule:
    """TimingRule 控制行动时机：立即、延迟、或提前。

    - "immediate": 默认，满足条件就行动
    - "delay": 等待 delay_condition 满足后才行动（如等 buff 到期）
    - "advance": 提前行动（配合拉条机制）
    """

    def test_immediate(self):
        """默认立即行动。"""
        rule = TimingRule(
            condition="true",
            timing="immediate",
        )
        assert rule.timing == "immediate"
        assert rule.delay_condition is None

    def test_delay_with_condition(self):
        """延迟行动需要指定等待条件。"""
        rule = TimingRule(
            condition="enemy.is_broken",
            timing="delay",
            delay_condition="enemy.toughness > 0",
        )
        assert rule.timing == "delay"
        assert rule.delay_condition == "enemy.toughness > 0"

    def test_advance(self):
        """提前行动（拉条）。"""
        rule = TimingRule(
            condition="ally.hp < 0.3",
            timing="advance",
        )
        assert rule.timing == "advance"


# ---------------------------------------------------------------------------
# Policy：完整策略容器
# ---------------------------------------------------------------------------


class TestPolicy:
    """Policy 是完整的战斗策略，组合了技能选择、目标选择、时机和参数。

    典型使用流程：
    1. LLM 根据角色信息生成 Policy JSON
    2. JSON 解析为 Policy 对象
    3. PolicyInterpreter 在模拟器中执行规则
    """

    def test_defaults(self):
        """默认策略没有规则，参数为空。"""
        p = Policy()
        assert p.name == "default"
        assert p.action_rules == []
        assert p.target_rules == []
        assert p.timing_rules == []
        assert p.parameters == {}
        assert p.version == "1.0"

    def test_full_construction(self):
        """完整构造包含所有规则类型和参数。"""
        p = Policy(
            name="aggressive",
            action_rules=[
                PolicyRule(condition="energy >= 120", action="ultimate", priority=100),
                PolicyRule(condition="skill_points > 0", action="skill", priority=50),
                PolicyRule(condition="true", action="basic", priority=0),
            ],
            target_rules=[
                TargetRule(condition="true", selector="lowest_hp"),
            ],
            timing_rules=[
                TimingRule(condition="true", timing="immediate"),
            ],
            parameters={
                "ULT_THRESHOLD": 120,
                "SKILL_PRIO": 0.8,
            },
            version="2.0",
        )
        assert p.name == "aggressive"
        assert len(p.action_rules) == 3
        assert len(p.target_rules) == 1
        assert len(p.timing_rules) == 1
        assert p.parameters["ULT_THRESHOLD"] == 120
        assert p.version == "2.0"

    def test_get_parameter_existing(self):
        """get_parameter 返回已存在的参数值。"""
        p = Policy(parameters={"ULT_THRESHOLD": 120})
        assert p.get_parameter("ULT_THRESHOLD") == 120

    def test_get_parameter_missing_with_default(self):
        """get_parameter 对不存在的参数返回默认值。"""
        p = Policy()
        assert p.get_parameter("MISSING", 42) == 42

    def test_get_parameter_missing_no_default(self):
        """get_parameter 对不存在的参数且无默认值时返回 None。"""
        p = Policy()
        assert p.get_parameter("MISSING") is None

    def test_default_lists_are_independent(self):
        """验证默认列表不会在不同实例间共享。"""
        p1 = Policy(name="a")
        p2 = Policy(name="b")
        p1.action_rules.append(PolicyRule(condition="x", action="basic"))
        assert p2.action_rules == []
