"""增益/减益/特效定义."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Modifier:
    modifier_id: str
    name: str
    modifier_type: str  # "buff", "debuff", "dot", "shield", "heal"
    stat_changes: Optional[dict] = None
    duration: int = 0  # 回合数，0 表示永久
    max_stack: int = 1
