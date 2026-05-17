"""光锥晋阶原始数据模型."""

from typing import Any, Dict, List


class LightConePromotion:
    """光锥晋阶数据."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        return self._data.get("id", "")

    @property
    def values(self) -> List[Dict[str, Any]]:
        return self._data.get("values", [])

    @property
    def materials(self) -> List[List[Dict[str, Any]]]:
        return self._data.get("materials", [])

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
