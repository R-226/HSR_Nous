"""关卡/遭遇战定义：敌人配置、波次、环境条件."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from hsr_nous.sim_schema.policy import Policy


@dataclass
class Wave:
    wave_index: int
    enemy_ids: List[str] = field(default_factory=list)
    enemy_levels: List[int] = field(default_factory=list)


@dataclass
class FormulaConfig:
    """伤害公式配置."""

    expression: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Encounter:
    """完整仿真输入：关卡 + 队伍 + 策略."""

    encounter_id: str
    name: str
    waves: List[Wave] = field(default_factory=list)
    environment: str = ""
    turn_limit: int = 0

    # 仿真配置
    formula: Dict[str, FormulaConfig] = field(default_factory=dict)
    globals: Dict[str, Any] = field(default_factory=dict)
    actors: List[Any] = field(default_factory=list)
    policy: Optional[Policy] = None
    initial_modifiers: List[Any] = field(default_factory=list)
