"""技能适配器：将 raw_schema 技能数据转换为 sim_schema.Action."""

from typing import Any, Dict

from hsr_nous.sim_schema.action import Action


def adapt_skill(skill_data: Dict[str, Any]) -> Action:
    """将原始技能数据转换为仿真器 Action.

    TODO: 实现倍率、目标类型、能量等字段映射
    """
    return Action(
        action_id=str(skill_data.get("_id", "")),
        name=skill_data.get("name", ""),
        action_type="basic",
        target_type="single",
    )
