"""角色相关原始数据模型（对应 StarRailRes character schema）."""

from typing import Any, Dict, List


class Character:
    """角色档案."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> int:
        return self._data.get("_id", 0)

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def rarity(self) -> int:
        return self._data.get("rarity", 0)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
