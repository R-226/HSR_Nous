"""遗器相关原始数据模型."""

from typing import Any, Dict, List


class RelicSet:
    """遗器套装."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def desc(self) -> List[str]:
        return self._data.get("desc", [])

    @property
    def properties(self) -> List[List[Dict[str, Any]]]:
        return self._data.get("properties", [])

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class Relic:
    """遗器单件."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def set_id(self) -> str:
        return self._data.get("set_id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def rarity(self) -> int:
        return self._data.get("rarity", 0)

    @property
    def type(self) -> str:
        return self._data.get("type", "")

    @property
    def max_level(self) -> int:
        return self._data.get("max_level", 0)

    @property
    def main_affix_id(self) -> str:
        return self._data.get("main_affix_id", "")

    @property
    def sub_affix_id(self) -> str:
        return self._data.get("sub_affix_id", "")

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
