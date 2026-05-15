"""伤害/治疗/效果结算器."""

from typing import Dict

from hsr_nous.sim_schema.action import Action
from hsr_nous.sim_schema.actor import Actor


class DamageResolver:
    """伤害计算与结算."""

    def resolve(self, action: Action, source: Actor, target: Actor) -> Dict[str, float]:
        """计算并返回伤害数值.

        TODO: 实现倍率、防御、抗性、减伤等完整公式
        """
        return {"damage": 0.0, "is_crit": False}
