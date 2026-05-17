"""光锥叠影原始数据模型."""

from typing import Any, Dict, List


class LightConeRank:
    """光锥叠影."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def skill(self) -> str:
        return self._data.get("skill", "")

    @property
    def desc(self) -> str:
        return self._data.get("desc", "")

    @property
    def params(self) -> List[List[float]]:
        return self._data.get("params", [])

    @property
    def properties(self) -> List[List[Dict[str, Any]]]:
        return self._data.get("properties", [])

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
