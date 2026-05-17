"""敌人原始数据模型."""

from typing import Any, Dict, List


class EnemySkill:
    """敌人技能."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> int:
        return self._data.get("Id", 0)

    @property
    def name(self) -> str:
        return self._data.get("Name", "")

    @property
    def desc(self) -> str:
        return self._data.get("SkillDesc", "")

    @property
    def type_desc(self) -> str:
        return self._data.get("SkillTypeDesc", "")

    @property
    def element_type(self) -> str:
        return self._data.get("ElementType", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class Enemy:
    """敌人."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("Id", "")

    @property
    def name(self) -> str:
        return self._data.get("Name", "")

    @property
    def introduction(self) -> str:
        return self._data.get("Introduction", "")

    @property
    def elemental_weaknesses(self) -> List[str]:
        return self._data.get("ElementalWeaknesses", [])

    @property
    def elemental_resistance(self) -> Dict[str, float]:
        return self._data.get("ElementalResistance", {})

    @property
    def skill_list(self) -> List[EnemySkill]:
        return [EnemySkill(s) for s in self._data.get("SkillList", [])]

    @property
    def version_added(self) -> str:
        return self._data.get("VersionAdded", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
