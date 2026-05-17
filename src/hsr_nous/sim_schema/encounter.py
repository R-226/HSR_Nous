"""关卡/遭遇战定义：敌人配置、波次、环境条件."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from hsr_nous.sim_schema.policy import Policy


@dataclass
class Wave:
    """波次配置.

    波次是独立于角色和敌人的行动条节点，到达时触发转波次效果。
    """

    wave_index: int
    enemy_ids: List[str] = field(default_factory=list)
    enemy_levels: List[int] = field(default_factory=list)

    # 转波次时触发的效果（类似回合开始触发 buff）
    on_wave_start: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FormulaConfig:
    """伤害公式配置."""

    expression: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TerminationConfig:
    """战斗结束条件."""

    mode: str = "fixed_av"
    """结束模式：fixed_av | kill_target | survival | wipe"""

    max_action_value: int = 1500
    """fixed_av 模式下的最大行动值"""

    target_ids: List[str] = field(default_factory=list)
    """kill_target 模式下要击杀的敌人 ID 列表，空列表表示全部"""

    max_turns: int = 50
    """最大回合数（防止死循环）"""

    max_battle_duration: int = 10000
    """最大行动值上限"""


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

    # 结束条件
    termination: TerminationConfig = field(default_factory=TerminationConfig)
