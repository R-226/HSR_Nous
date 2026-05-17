"""命途原始数据模型."""

from typing import Any, Dict


class Path:
    """命途."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    @property
    def icon_middle(self) -> str:
        return self._data.get("icon_middle", "")

    @property
    def icon_small(self) -> str:
        return self._data.get("icon_small", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
