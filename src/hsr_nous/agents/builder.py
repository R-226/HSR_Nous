"""Builder Agent：配装与配队候选生成."""

from typing import Any, Dict, List

from hsr_nous.sim_schema.actor import Actor


class BuilderAgent:
    """根据目标生成候选配装与配队方案."""

    def build_candidates(
        self,
        characters: List[str],
        constraints: Dict[str, Any],
    ) -> List[List[Actor]]:
        """生成候选队伍列表.

        TODO: 实现基于角色池和约束的候选生成
        """
        return []
