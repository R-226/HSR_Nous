"""从 JSON 文件加载原始数据为 Python 对象."""

import json
from pathlib import Path
from typing import Any, Dict, List

from hsr_nous.raw_schema.character import Character
from hsr_nous.raw_schema.light_cone import LightCone
from hsr_nous.raw_schema.relic import Relic


def load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return [data]


def load_characters(path: Path) -> List[Character]:
    return [Character(d) for d in load_json(path)]


def load_light_cones(path: Path) -> List[LightCone]:
    return [LightCone(d) for d in load_json(path)]


def load_relics(path: Path) -> List[Relic]:
    return [Relic(d) for d in load_json(path)]
