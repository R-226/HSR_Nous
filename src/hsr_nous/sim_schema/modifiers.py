"""增益/减益/特效定义."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Modifier:
    """Modifier（增益/减益/特效）.

    所有持续效果都用 Modifier 表达，包括 buff、debuff、DOT、护盾、治疗、控制。
    """

    modifier_id: str
    """唯一标识符."""

    name: str
    """显示名称."""

    modifier_type: str
    """类型："buff" | "debuff" | "dot" | "shield" | "heal" | "control"."""

    stat_changes: Optional[dict] = None
    """属性变更，如 {"atk_pct": 0.2, "crit_rate": 0.1}."""

    duration: int = 0
    """持续回合数，0 表示永久."""

    max_stack: int = 1
    """最大叠层数."""

    stack_mode: str = "refresh"
    """叠加模式：
    - "refresh"：刷新持续时间（默认）
    - "independent"：独立计时
    - "replace"：替换旧实例
    """

    dispellable: bool = True
    """是否可被驱散."""

    buff_class: str = "A"
    """A/B 类判定：
    - "A"：回合开始判定 + 结算（多数增伤 buff）
    - "B"：行动进行判定，回合结束结算（部分 debuff）
    """

    on_apply: List[dict] = field(default_factory=list)
    """施加时触发的效果列表."""

    on_turn_start: List[dict] = field(default_factory=list)
    """回合开始时触发的效果列表."""

    on_turn_end: List[dict] = field(default_factory=list)
    """回合结束时触发的效果列表."""

    on_expire: List[dict] = field(default_factory=list)
    """过期时触发的效果列表."""

    condition: Optional[str] = None
    """触发条件表达式，如 "target.hp_pct < 0.5"，None 表示无条件触发."""
