# TEALCA: Technoeconomic and Life Cycle Assessment Toolkit

TEALCA is a Python-based repository designed to streamline technoeconomic analysis (TEA) and life cycle assessment (LCA) workflows with open source tools. The project offers modular building blocks that help analysts evaluate industrial processes, energy systems, and emerging technologies from both economic and environmental perspectives.

## Key Features

- **Modular TEA models** for capital and operating expenditures, discounted cashflow analysis, and performance metrics such as net present value (NPV) and levelized cost of production (LCOP).
- **LCA integration hooks** that wrap the [Brightway2](https://brightway.dev/) ecosystem for inventory, impact assessment, and scenario analysis.
- **Configuration-driven workflows** using YAML files to define process parameters, cashflow assumptions, and environmental scenarios.
- **Command line interface (CLI)** for running TEA, LCA, or combined assessments in reproducible pipelines.
- **Extensible architecture** implemented with type hints and dataclasses so teams can build custom sector-specific models.

## Getting Started

### Installation

Create and activate a Python 3.10+ environment, then install the package:

```bash
pip install -e .
```

To enable the optional LCA functionality backed by Brightway2, install with the `lca` extra:

```bash
pip install -e .[lca]
```

### Repository Structure

```
├── LICENSE
├── README.md
├── pyproject.toml
├── data/
│   └── sample_costs.csv
├── examples/
│   └── ethanol_biorefinery.yaml
├── src/
│   └── tealca/
│       ├── __init__.py
│       ├── cli.py
│       ├── data.py
│       ├── economics.py
│       ├── integrated.py
│       └── lca.py
└── tests/
    └── test_economics.py
```

## Usage

### Run technoeconomic analysis

```bash
tealca run-tea examples/ethanol_biorefinery.yaml
```

The command computes discounted cashflows, net present value, and levelized cost of production based on the configuration file.

### Run life cycle assessment

```bash
tealca run-lca examples/ethanol_biorefinery.yaml --bw-project MyProject
```

This command expects that you have already initialized a Brightway2 project containing the inventory data referenced in the configuration file.

### Run integrated TEA + LCA scenario

```bash
tealca run-integrated examples/ethanol_biorefinery.yaml --bw-project MyProject
```

The integrated workflow combines economic and environmental metrics, summarizing the results in a single report.

## Configuration File

YAML configuration files include `metadata`, `economics`, and optional `lca` sections. The ethanol biorefinery example demonstrates how to define CAPEX, OPEX, production levels, and impact assessment methods.

## Contributing

1. Fork the repository and create a new branch.
2. Run tests with `pytest` before submitting changes.
3. Submit a pull request describing your improvements and referencing any related issues.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
