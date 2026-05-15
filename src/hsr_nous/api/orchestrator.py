"""编排器：协调多 Agent 完成 ReAct 决策闭环."""

from typing import Any, Dict

from hsr_nous.agents.builder import BuilderAgent
from hsr_nous.agents.evaluator import EvaluatorAgent
from hsr_nous.agents.explainer import ExplainerAgent
from hsr_nous.agents.planner import PlannerAgent
from hsr_nous.agents.search import SearchAgent


class Orchestrator:
    """ReAct 风格多 Agent 编排器.

    1) 解析：Planner 拆解目标
    2) 生成：Builder 提出候选
    3) 搜索：Search 细调参数
    4) 仿真：Evaluator 运行评估
    5) 对比：Explainer 生成报告
    6) 迭代：在预算内收敛最优解
    """

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.builder = BuilderAgent()
        self.search = SearchAgent()
        self.evaluator = EvaluatorAgent()
        self.explainer = ExplainerAgent()

    def run(self, goal: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整决策闭环.

        TODO: 实现 ReAct 循环与中间状态管理
        """
        return {"goal": goal, "best": None, "report": ""}
