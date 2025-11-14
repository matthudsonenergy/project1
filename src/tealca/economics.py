"""Technoeconomic models and helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import math


@dataclass
class EconomicInputs:
    """Input parameters for technoeconomic analysis."""

    discount_rate: float
    project_lifetime: int
    tax_rate: float
    depreciation_years: int
    capacity_factor: float
    production_rate_kg_per_hr: float
    product_price_per_kg: float
    capital_expenditures: List[Dict[str, float]]
    operating_costs: Dict[str, Iterable[Dict[str, float]]]
    additional_revenue_streams: Iterable[Dict[str, float]] | None = None


@dataclass
class CashFlowResult:
    """Results from the discounted cash flow model."""

    annual_revenue: List[float]
    annual_costs: List[float]
    depreciation: List[float]
    taxable_income: List[float]
    cash_flow: List[float]
    cumulative_cash_flow: List[float]
    npv: float
    irr: float | None
    levelized_cost: float


class TechnoEconomicModel:
    """Compute technoeconomic metrics for a process."""

    def __init__(self, inputs: EconomicInputs):
        self.inputs = inputs
        self.annual_hours = 8760 * inputs.capacity_factor

    def _variable_cost_per_year(self) -> float:
        variable = 0.0
        for entry in self.inputs.operating_costs.get("variable", []):
            variable += entry["amount_per_kg"] * self.inputs.production_rate_kg_per_hr * self.annual_hours
        return variable

    def _fixed_cost_per_year(self) -> float:
        fixed = 0.0
        for entry in self.inputs.operating_costs.get("fixed", []):
            fixed += entry["amount"]
        return fixed

    def _revenue_per_year(self) -> float:
        base_revenue = (
            self.inputs.production_rate_kg_per_hr
            * self.annual_hours
            * self.inputs.product_price_per_kg
        )
        additional = 0.0
        for entry in self.inputs.additional_revenue_streams or []:
            additional += entry.get("amount_per_kg", 0.0) * self.inputs.production_rate_kg_per_hr * self.annual_hours
        return base_revenue + additional

    def _depreciation_schedule(self) -> List[float]:
        years = self.inputs.project_lifetime
        depreciation = [0.0 for _ in range(years)]
        total_capex = sum(item["amount"] for item in self.inputs.capital_expenditures)
        useful_life = min(self.inputs.depreciation_years, years)
        if useful_life == 0:
            return depreciation
        annual = total_capex / useful_life
        for year in range(useful_life):
            depreciation[year] = annual
        return depreciation

    def discounted_cash_flow(self) -> CashFlowResult:
        years = self.inputs.project_lifetime
        operating_years = years
        annual_revenue = [0.0]
        total_operating_cost = self._variable_cost_per_year() + self._fixed_cost_per_year()
        annual_costs = [0.0]
        depreciation_schedule = self._depreciation_schedule()
        depreciation = [0.0]

        for year in range(operating_years):
            annual_revenue.append(self._revenue_per_year())
            annual_costs.append(total_operating_cost)
            depreciation.append(depreciation_schedule[year] if year < len(depreciation_schedule) else 0.0)

        taxable_income = [rev - cost - dep for rev, cost, dep in zip(annual_revenue, annual_costs, depreciation)]
        taxes = [max(taxable, 0) * self.inputs.tax_rate for taxable in taxable_income]
        net_income = [taxable - tax for taxable, tax in zip(taxable_income, taxes)]
        cash_flow = [ni + dep for ni, dep in zip(net_income, depreciation)]
        upfront_capex = sum(item["amount"] for item in self.inputs.capital_expenditures if item.get("year", 0) == 0)
        cash_flow[0] -= upfront_capex
        cumulative_cash_flow = self._cumulative_sum(cash_flow)
        discount_factors = [(1 + self.inputs.discount_rate) ** year for year in range(len(cash_flow))]
        discounted = [cf / df for cf, df in zip(cash_flow, discount_factors)]
        npv = float(sum(discounted))
        irr = self._internal_rate_of_return(cash_flow)
        levelized_cost = self._levelized_cost_of_production(cash_flow)
        return CashFlowResult(
            annual_revenue=annual_revenue,
            annual_costs=annual_costs,
            depreciation=depreciation,
            taxable_income=taxable_income,
            cash_flow=cash_flow,
            cumulative_cash_flow=cumulative_cash_flow,
            npv=npv,
            irr=irr,
            levelized_cost=levelized_cost,
        )

    def _internal_rate_of_return(self, cash_flow: List[float]) -> float | None:
        if not any(cf < 0 for cf in cash_flow) or not any(cf > 0 for cf in cash_flow):
            return None

        def npv(rate: float) -> float:
            total = 0.0
            for year, cf in enumerate(cash_flow):
                total += cf / ((1 + rate) ** year)
            return total

        low, high = -0.9, 1.0
        npv_low = npv(low)
        npv_high = npv(high)
        iterations = 0
        while npv_low * npv_high > 0 and iterations < 100:
            high += 1.0
            npv_high = npv(high)
            iterations += 1
            if high > 100:
                return None

        for _ in range(200):
            mid = (low + high) / 2
            npv_mid = npv(mid)
            if abs(npv_mid) < 1e-6:
                return mid
            if npv_low * npv_mid > 0:
                low, npv_low = mid, npv_mid
            else:
                high, npv_high = mid, npv_mid
        return (low + high) / 2

    def _levelized_cost_of_production(self, cash_flow: List[float]) -> float:
        annual_output = self.inputs.production_rate_kg_per_hr * self.annual_hours
        if annual_output <= 0:
            return math.inf
        discounted_costs = 0.0
        discounted_output = 0.0
        for year, cf in enumerate(cash_flow):
            factor = (1 + self.inputs.discount_rate) ** year
            if cf < 0:
                discounted_costs += -cf / factor
            if year > 0:
                discounted_output += annual_output / factor
        return discounted_costs / discounted_output

    @staticmethod
    def _cumulative_sum(values: List[float]) -> List[float]:
        total = 0.0
        result: List[float] = []
        for value in values:
            total += value
            result.append(total)
        return result


__all__ = ["EconomicInputs", "CashFlowResult", "TechnoEconomicModel"]
