"""参战单位定义：仿真器内部使用的角色/敌人表示."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StatBlock:
    hp: float = 0.0
    atk: float = 0.0
    def_: float = 0.0
    spd: float = 0.0
    crit_rate: float = 0.0
    crit_dmg: float = 0.0
    break_effect: float = 0.0
    effect_hit: float = 0.0
    effect_res: float = 0.0
    energy_regen: float = 1.0


@dataclass
class Actor:
    actor_id: str
    name: str
    level: int = 80
    stats: StatBlock = field(default_factory=StatBlock)
    actions: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)
