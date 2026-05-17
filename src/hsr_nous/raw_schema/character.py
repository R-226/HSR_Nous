"""角色相关原始数据模型（对应 StarRailRes character schema）."""

from typing import Any, Dict, List


class Character:
    """角色档案."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def tag(self) -> str:
        return self._data.get("tag", "")

    @property
    def rarity(self) -> int:
        return self._data.get("rarity", 0)

    @property
    def path(self) -> str:
        return self._data.get("path", "")

    @property
    def element(self) -> str:
        return self._data.get("element", "")

    @property
    def max_sp(self) -> float:
        return self._data.get("max_sp", 0)

    @property
    def ranks(self) -> List[str]:
        return self._data.get("ranks", [])

    @property
    def skills(self) -> List[str]:
        return self._data.get("skills", [])

    @property
    def skill_trees(self) -> List[str]:
        return self._data.get("skill_trees", [])

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    @property
    def preview(self) -> str:
        return self._data.get("preview", "")

    @property
    def portrait(self) -> str:
        return self._data.get("portrait", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
