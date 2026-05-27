"""技能/行动定义：普攻、战技、终结技、天赋等."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Action:
    """技能/行动."""

    action_id: str
    name: str
    action_type: str  # "basic", "skill", "ultimate", "talent", "follow_up", "elation_damage", "memosprite_skill", "memosprite_talent"
    target_type: str  # "enemy_single", "enemy_blast", "enemy_aoe", "ally_single", "ally_aoe", "self", "single", "blast", "aoe", "bounce", "all_enemies", "all_allies"
    damage_type: Optional[str] = None  # "physical", "fire", "ice", "thunder", "wind", "quantum", "imaginary"

    # 技能倍率（按等级）
    scaling: List[Dict[str, float]] = field(default_factory=list)

    # 能量
    energy_cost: int = 0      # 终结技能量消耗
    energy_gain: int = 0      # 释放后获得的能量

    # 战技点
    skill_point_cost: int = 0  # 战技点消耗（普攻=-1回复，战技=1消耗）
    skill_point_gain: int = 0  # 战技点获取（普攻默认+1）

    # 削韧值（击破系统核心参数）
    toughness_dmg: int = 0     # 削韧值（普攻10, 战技20, 终结技30）

    # 技能效果列表：描述该动作产生的所有效果（伤害、buff、回能等）
    effects: List[Dict[str, Any]] = field(default_factory=list)
