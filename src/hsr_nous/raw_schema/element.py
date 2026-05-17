"""元素原始数据模型."""

from typing import Any, Dict


class Element:
    """元素类型."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def color(self) -> str:
        return self._data.get("color", "")

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
