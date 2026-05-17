"""角色技能原始数据模型."""

from typing import Any, Dict, List


class CharacterSkill:
    """角色技能."""

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
    def element(self) -> str:
        return self._data.get("element", "")

    @property
    def type(self) -> str:
        return self._data.get("type", "")

    @property
    def type_text(self) -> str:
        return self._data.get("type_text", "")

    @property
    def effect(self) -> str:
        return self._data.get("effect", "")

    @property
    def effect_text(self) -> str:
        return self._data.get("effect_text", "")

    @property
    def simple_desc(self) -> str:
        return self._data.get("simple_desc", "")

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def params(self) -> List[List[float]]:
        return self._data.get("params", [])

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
