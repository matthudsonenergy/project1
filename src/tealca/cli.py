"""Command line interface for TEALCA."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import typer

from .data import Configuration
from .economics import EconomicInputs
from .integrated import IntegratedAssessment

app = typer.Typer(help="Technoeconomic and life cycle assessment CLI")


def _load_economic_inputs(config: Dict[str, Any]) -> EconomicInputs:
    return EconomicInputs(
        discount_rate=config["discount_rate"],
        project_lifetime=config["project_lifetime"],
        tax_rate=config.get("tax_rate", 0.0),
        depreciation_years=config.get("depreciation_years", config["project_lifetime"]),
        capacity_factor=config.get("capacity_factor", 1.0),
        production_rate_kg_per_hr=config["production_rate_kg_per_hr"],
        product_price_per_kg=config["product_price_per_kg"],
        capital_expenditures=config.get("capital_expenditures", []),
        operating_costs=config.get("operating_costs", {}),
        additional_revenue_streams=config.get("additional_revenue_streams"),
    )


def _load_configuration(path: Path) -> Configuration:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file {path} not found")
    return Configuration.from_yaml(path)


def _print_json(data: Dict[str, Any]) -> None:
    typer.echo(json.dumps(data, indent=2, sort_keys=True))


@app.command()
def run_tea(config_path: Path) -> None:
    """Run technoeconomic analysis using the provided configuration."""

    config = _load_configuration(config_path)
    inputs = _load_economic_inputs(config.economics)
    assessment = IntegratedAssessment(config.metadata)
    result = assessment.run(inputs)
    _print_json(result.summary)


@app.command()
def run_lca(config_path: Path, bw_project: str | None = None) -> None:
    """Run life cycle assessment using the provided configuration."""

    config = _load_configuration(config_path)
    if not config.lca:
        raise typer.BadParameter("Configuration does not contain an LCA section")
    if bw_project:
        config.lca["brightway_project"] = bw_project
    assessment = IntegratedAssessment(config.metadata)
    inputs = _load_economic_inputs(config.economics)
    result = assessment.run(inputs, config.lca)
    if result.lca is None:
        raise typer.Exit(code=1)
    _print_json(
        {
            "lca_score": result.lca.score,
            "lca_unit": result.lca.unit,
            "method": list(result.lca.method),
        }
    )


@app.command()
def run_integrated(config_path: Path, bw_project: str | None = None) -> None:
    """Run combined TEA and LCA assessments."""

    config = _load_configuration(config_path)
    inputs = _load_economic_inputs(config.economics)
    lca_config = config.lca
    if lca_config and bw_project:
        lca_config["brightway_project"] = bw_project
    assessment = IntegratedAssessment(config.metadata)
    result = assessment.run(inputs, lca_config)
    summary = result.summary
    if result.lca:
        summary["lca_method"] = list(result.lca.method)
    _print_json(summary)


def main() -> None:  # pragma: no cover - console entry point
    app()


if __name__ == "__main__":  # pragma: no cover - console entry point
    main()
