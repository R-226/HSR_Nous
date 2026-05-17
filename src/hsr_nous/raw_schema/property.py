"""属性类型原始数据模型."""

from typing import Any, Dict


class Property:
    """属性类型定义."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def type(self) -> str:
        return self._data.get("type", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def field(self) -> str:
        return self._data.get("field", "")

    @property
    def affix(self) -> bool:
        return self._data.get("affix", False)

    @property
    def ratio(self) -> bool:
        return self._data.get("ratio", False)

    @property
    def percent(self) -> bool:
        return self._data.get("percent", False)

    @property
    def order(self) -> int:
        return self._data.get("order", 0)

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
