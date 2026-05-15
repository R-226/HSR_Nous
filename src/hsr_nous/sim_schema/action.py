"""技能/行动定义：普攻、战技、终结技、天赋等."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Action:
    action_id: str
    name: str
    action_type: str  # "basic", "skill", "ultimate", "talent", "follow_up"
    target_type: str  # "single", "blast", "aoe", "self"
    damage_type: Optional[str] = None  # "physical", "fire", etc.
    scaling: List[Dict[str, float]] = field(default_factory=list)
    energy_cost: int = 0
    energy_gain: int = 0
