"""行动序管理：速度条与行动值计算."""

from typing import List

from hsr_nous.sim_schema.actor import Actor


class Timeline:
    """管理参战单位的行动顺序."""

    def __init__(self, actors: List[Actor]) -> None:
        self.actors = actors

    def next_actor(self) -> Actor:
        """返回下一个行动的单位.

        TODO: 实现基于速度的行动值排序
        """
        return self.actors[0]
