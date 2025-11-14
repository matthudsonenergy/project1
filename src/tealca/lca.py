"""Life cycle assessment integration helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


try:  # pragma: no cover - optional dependency
    import bw2calc  # type: ignore
    import bw2data  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    bw2calc = None
    bw2data = None


@dataclass
class LCAScenario:
    """Configuration for running an LCA scenario."""

    brightway_project: str
    database: str
    functional_unit: Dict[str, Any]
    impact_method: Dict[str, Any]


@dataclass
class LCAResult:
    """Result of an LCA run."""

    demand: Dict[str, Any]
    score: float
    unit: str
    method: tuple[str, str, str]


class LifeCycleAssessment:
    """Wrap Brightway2 calculations with a simplified API."""

    def __init__(self, scenario: LCAScenario):
        if bw2data is None or bw2calc is None:  # pragma: no cover - optional dependency
            raise ImportError(
                "Brightway2 packages are not installed. Install tealca with the 'lca' extra to enable LCA workflows."
            )
        self.scenario = scenario

    def _prepare_project(self) -> None:
        assert bw2data is not None
        bw2data.projects.set_current(self.scenario.brightway_project)

    def _resolve_functional_unit(self) -> Dict[str, Any]:
        assert bw2data is not None
        database = bw2data.Database(self.scenario.database)
        for dataset in database:
            if dataset.get("name") == self.scenario.functional_unit.get("dataset"):
                if self.scenario.functional_unit.get("reference_product"):
                    if dataset.get("reference product") != self.scenario.functional_unit.get("reference_product"):
                        continue
                return {dataset.key: self.scenario.functional_unit.get("amount", 1)}
        raise ValueError("Functional unit dataset not found in Brightway2 database")

    def run(self) -> LCAResult:
        self._prepare_project()
        functional_unit = self._resolve_functional_unit()
        assert bw2calc is not None
        method_tuple = (
            self.scenario.impact_method["name"],
            self.scenario.impact_method["category"],
            self.scenario.impact_method["indicator"],
        )
        lca = bw2calc.LCA(functional_unit, method_tuple)
        lca.lci()
        lca.lcia()
        score = float(lca.score)
        unit = lca.characterization_factors.data[0]["unit"] if lca.characterization_factors.data else "unit"
        return LCAResult(demand=functional_unit, score=score, unit=unit, method=method_tuple)


__all__ = ["LCAScenario", "LCAResult", "LifeCycleAssessment"]
