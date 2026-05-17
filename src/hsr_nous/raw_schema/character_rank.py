"""角色星魂原始数据模型."""

from typing import Any, Dict, List


class CharacterRank:
    """角色星魂."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def rank(self) -> int:
        return self._data.get("rank", 0)

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def materials(self) -> List[Dict[str, Any]]:
        return self._data.get("materials", [])

    @property
    def level_up_skills(self) -> List[Dict[str, Any]]:
        return self._data.get("level_up_skills", [])

    @property
    def icon(self) -> str:
        return self._data.get("icon", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
