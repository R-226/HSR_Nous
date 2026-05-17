"""角色行迹原始数据模型."""

from typing import Any, Dict, List


class CharacterSkillTree:
    """角色行迹节点."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def max_level(self) -> int:
        return self._data.get("max_level", 0)

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def params(self) -> List[float]:
        return self._data.get("params", [])

    @property
    def anchor(self) -> str:
        return self._data.get("anchor", "")

    @property
    def pre_points(self) -> List[str]:
        return self._data.get("pre_points", [])

    @property
    def level_up_skills(self) -> List[Dict[str, Any]]:
        return self._data.get("level_up_skills", [])

    @property
    def levels(self) -> List[Dict[str, Any]]:
        return self._data.get("levels", [])

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
