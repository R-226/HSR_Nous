"""遗器词条原始数据模型."""

from typing import Any, Dict


class RelicMainAffix:
    """遗器主词条."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def affixes(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get("affixes", {})

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


class RelicSubAffix:
    """遗器副词条."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def affixes(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get("affixes", {})

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
