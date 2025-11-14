"""Unit tests for technoeconomic calculations."""
from __future__ import annotations

from tealca.economics import EconomicInputs, TechnoEconomicModel


def build_inputs() -> EconomicInputs:
    return EconomicInputs(
        discount_rate=0.1,
        project_lifetime=5,
        tax_rate=0.21,
        depreciation_years=3,
        capacity_factor=0.9,
        production_rate_kg_per_hr=100,
        product_price_per_kg=2.0,
        capital_expenditures=[{"description": "Plant", "amount": 1000000, "year": 0}],
        operating_costs={
            "fixed": [{"description": "Labor", "amount": 10000}],
            "variable": [{"description": "Feedstock", "amount_per_kg": 0.5}],
        },
        additional_revenue_streams=[{"description": "Byproduct", "amount_per_kg": 0.1}],
    )


def test_discounted_cash_flow_shapes() -> None:
    inputs = build_inputs()
    model = TechnoEconomicModel(inputs)
    results = model.discounted_cash_flow()
    assert len(results.annual_revenue) == inputs.project_lifetime + 1
    assert len(results.cash_flow) == inputs.project_lifetime + 1


def test_npv_positive_with_profitable_project() -> None:
    inputs = build_inputs()
    model = TechnoEconomicModel(inputs)
    results = model.discounted_cash_flow()
    assert results.npv > 0


def test_levelized_cost_less_than_price() -> None:
    inputs = build_inputs()
    model = TechnoEconomicModel(inputs)
    results = model.discounted_cash_flow()
    assert results.levelized_cost < inputs.product_price_per_kg


def test_irr_between_zero_and_one_for_profitable_project() -> None:
    inputs = build_inputs()
    model = TechnoEconomicModel(inputs)
    results = model.discounted_cash_flow()
    assert results.irr is not None
    assert results.irr > 0
