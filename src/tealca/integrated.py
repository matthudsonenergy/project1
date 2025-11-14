"""Combined technoeconomic and life cycle analysis workflows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .economics import CashFlowResult, EconomicInputs, TechnoEconomicModel
from .lca import LCAScenario, LifeCycleAssessment, LCAResult


@dataclass
class IntegratedResult:
    """Combined TEA and LCA outputs."""

    cash_flow: CashFlowResult
    lca: LCAResult | None
    metadata: Dict[str, Any]

    @property
    def summary(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "npv": self.cash_flow.npv,
            "irr": self.cash_flow.irr,
            "levelized_cost": self.cash_flow.levelized_cost,
        }
        if self.lca:
            data["lca_score"] = self.lca.score
            data["lca_unit"] = self.lca.unit
        return data


class IntegratedAssessment:
    """Run combined technoeconomic and life cycle assessments."""

    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata

    def run(self, economics: EconomicInputs, lca_config: Dict[str, Any] | None = None) -> IntegratedResult:
        tea_model = TechnoEconomicModel(economics)
        cash_flow = tea_model.discounted_cash_flow()
        lca_result: LCAResult | None = None
        if lca_config:
            scenario = LCAScenario(**lca_config)
            lca_runner = LifeCycleAssessment(scenario)
            lca_result = lca_runner.run()
        return IntegratedResult(cash_flow=cash_flow, lca=lca_result, metadata=self.metadata)


__all__ = ["IntegratedAssessment", "IntegratedResult"]
