"""可扩展的目标选择器注册表.

示例：
    @register_selector("lowest_hp")
    def select_lowest_hp(actor, candidates, context):
        return min(candidates, key=lambda a: a.stats.hp)
"""

import random
from typing import Any, Callable, Dict, List, Optional

from hsr_nous.sim_schema.actor import Actor

TargetSelectorFn = Callable[[Actor, List[Actor], Dict[str, Any]], Optional[Actor]]

# 全局注册表
_TARGET_SELECTORS: Dict[str, TargetSelectorFn] = {}


def register_selector(name: str) -> Callable[[TargetSelectorFn], TargetSelectorFn]:
    """注册一个目标选择器.

    用法：
        @register_selector("lowest_hp")
        def select_lowest_hp(actor, candidates, context):
            return min(candidates, key=lambda a: a.stats.hp)
    """

    def decorator(fn: TargetSelectorFn) -> TargetSelectorFn:
        _TARGET_SELECTORS[name] = fn
        return fn

    return decorator


def get_selector(name: str) -> Optional[TargetSelectorFn]:
    """按名称获取已注册的选择器."""
    return _TARGET_SELECTORS.get(name)


def list_selectors() -> List[str]:
    """列出所有已注册的选择器名称."""
    return list(_TARGET_SELECTORS.keys())


# ========== 内置选择器 ==========


@register_selector("primary_target")
def select_primary(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """主目标（列表第一个）."""
    return candidates[0] if candidates else None


@register_selector("self")
def select_self(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """自身."""
    return actor


@register_selector("lowest_hp")
def select_lowest_hp(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """生命值最低."""
    return min(candidates, key=lambda a: a.stats.hp) if candidates else None


@register_selector("lowest_hp_pct")
def select_lowest_hp_pct(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """生命值百分比最低."""
    return (
        min(candidates, key=lambda a: getattr(a, "max_hp", a.stats.hp) and a.stats.hp / getattr(a, "max_hp", a.stats.hp))
        if candidates
        else None
    )


@register_selector("highest_hp")
def select_highest_hp(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """生命值最高."""
    return max(candidates, key=lambda a: a.stats.hp) if candidates else None


@register_selector("highest_hp_pct")
def select_highest_hp_pct(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """生命值百分比最高."""
    return (
        max(candidates, key=lambda a: getattr(a, "max_hp", a.stats.hp) and a.stats.hp / getattr(a, "max_hp", a.stats.hp))
        if candidates
        else None
    )


@register_selector("highest_atk")
def select_highest_atk(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """攻击力最高."""
    return max(candidates, key=lambda a: a.stats.atk) if candidates else None


@register_selector("highest_spd")
def select_highest_spd(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """速度最高."""
    return max(candidates, key=lambda a: a.stats.spd) if candidates else None


@register_selector("lowest_spd")
def select_lowest_spd(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """速度最低."""
    return min(candidates, key=lambda a: a.stats.spd) if candidates else None


@register_selector("broken")
def select_broken(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """已击破韧性（ toughness == 0 ）的敌人."""
    broken = [c for c in candidates if getattr(c, "toughness", 0) == 0]
    return broken[0] if broken else (candidates[0] if candidates else None)


@register_selector("highest_break")
def select_highest_break(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """韧性最高（未击破）的敌人."""
    return max(candidates, key=lambda a: getattr(a, "toughness", 0)) if candidates else None


@register_selector("random")
def select_random(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """随机目标."""
    return random.choice(candidates) if candidates else None


@register_selector("all_enemies")
def select_all_enemies(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """全体敌人（AOE）— 返回 primary target，实际伤害由 engine 扩散处理."""
    return candidates[0] if candidates else None


@register_selector("all_allies")
def select_all_allies(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """全体队友（AOE 治疗/增益）— 返回 primary target."""
    return candidates[0] if candidates else None


@register_selector("has_modifier")
def select_has_modifier(actor: Actor, candidates: List[Actor], context: Dict[str, Any]) -> Optional[Actor]:
    """带有特定 buff 的目标.

    需要在 context 中传入 modifier_id：
        context['modifier_id'] = 'MOD_SHIELD'
    """
    modifier_id = context.get("modifier_id")
    if not modifier_id:
        return candidates[0] if candidates else None
    matched = [c for c in candidates if modifier_id in getattr(c, "active_modifiers", [])]
    return matched[0] if matched else (candidates[0] if candidates else None)


# ========== 参数化选择器解析 ==========


def _get_nested_attr(obj: Any, path: str) -> Any:
    """按点号路径获取嵌套属性，如 'stats.hp'."""
    parts = path.split(".")
    for part in parts:
        if obj is None:
            return None
        obj = getattr(obj, part, None)
    return obj


def resolve_parametric_selector(
    actor: Actor,
    candidates: List[Actor],
    context: Dict[str, Any],
    selector_config: Dict[str, Any],
) -> Optional[Actor]:
    """解析参数化选择器（字典格式），不需要预注册 Python 函数.

    支持的 type：
        - "min":      {"type": "min", "key": "stats.hp"}
        - "max":      {"type": "max", "key": "stats.atk"}
        - "filter":   {"type": "filter", "condition": "stats.hp < max_hp * 0.5"}
        - "first":    {"type": "first", "condition": "actor_type == 'monster'"}
        - "random":   {"type": "random"}
        - "has_modifier": {"type": "has_modifier", "modifier_id": "MOD_XXX"}

    Args:
        selector_config: 字典，必须包含 "type" 键
    """
    if not candidates:
        return None

    sel_type = selector_config.get("type")
    if not sel_type:
        return candidates[0]

    if sel_type == "min":
        key = selector_config.get("key", "stats.hp")
        return min(candidates, key=lambda a: _get_nested_attr(a, key) or 0)

    if sel_type == "max":
        key = selector_config.get("key", "stats.hp")
        return max(candidates, key=lambda a: _get_nested_attr(a, key) or 0)

    if sel_type == "filter":
        condition = selector_config.get("condition", "")
        # TODO: 替换为安全表达式引擎
        # 目前做简单字符串匹配占位
        if "hp <" in condition:
            threshold_str = condition.split("hp <")[-1].strip()
            try:
                threshold = float(eval(threshold_str, {"__builtins__": {}}, {}))
                matched = [c for c in candidates if c.stats.hp < threshold]
                return matched[0] if matched else candidates[0]
            except Exception:
                pass
        return candidates[0]

    if sel_type == "first":
        condition = selector_config.get("condition", "")
        # TODO: 替换为安全表达式引擎
        for c in candidates:
            if "actor_type == 'monster'" in condition and getattr(c, "actor_type", "") == "monster":
                return c
        return candidates[0]

    if sel_type == "random":
        return random.choice(candidates)

    if sel_type == "has_modifier":
        modifier_id = selector_config.get("modifier_id", "")
        matched = [c for c in candidates if modifier_id in getattr(c, "active_modifiers", [])]
        return matched[0] if matched else candidates[0]

    # 未知类型回退到主目标
    return candidates[0]
