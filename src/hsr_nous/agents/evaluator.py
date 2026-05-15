"""Evaluator Agent：仿真运行与指标计算."""

from typing import Any, Dict, List

from hsr_nous.sim.engine import CombatEngine
from hsr_nous.sim_schema.encounter import Encounter


class EvaluatorAgent:
    """运行战斗仿真并计算评估指标."""

    def evaluate(
        self,
        team: List[Any],
        encounter: Encounter,
        iterations: int = 10,
    ) -> Dict[str, float]:
        """评估队伍在指定关卡中的表现.

        TODO: 实现多次仿真聚合统计（DPS、生存率、方差等）
        """
        return {"dps": 0.0, "survival_rate": 0.0}
