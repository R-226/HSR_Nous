"""遗器相关原始数据模型."""

from typing import Any, Dict


class Relic:
    """遗器（圣遗物）档案."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> int:
        return self._data.get("_id", 0)

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
