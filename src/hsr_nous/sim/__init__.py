"""战斗模拟器：纯仿真核心，只依赖 sim_data."""

from hsr_nous.sim.engine import CombatEngine, PolicyInterpreter
from hsr_nous.sim.selectors import (
    get_selector,
    list_selectors,
    register_selector,
)

__all__ = [
    "CombatEngine",
    "PolicyInterpreter",
    "get_selector",
    "list_selectors",
    "register_selector",
]
