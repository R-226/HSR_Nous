"""角色适配器：将 raw_schema.Character 转换为 sim_schema.Actor."""

from hsr_nous.raw_schema.character import Character
from hsr_nous.raw_schema.light_cone import LightCone
from hsr_nous.raw_schema.relic import Relic
from hsr_nous.sim_schema.actor import Actor, StatBlock


def adapt_character(
    character: Character,
    light_cone: LightCone | None = None,
    relics: list[Relic] | None = None,
) -> Actor:
    """将原始角色数据转换为仿真器 Actor.

    TODO: 实现完整属性计算（基础值 + 光锥 + 遗器 + 行迹）
    """
    raw = character.to_dict()
    return Actor(
        actor_id=str(character.id),
        name=character.name,
        stats=StatBlock(),
    )
