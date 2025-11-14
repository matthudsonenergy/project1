"""Data utilities for TEALCA."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml


@dataclass
class Configuration:
    """Representation of an assessment configuration file."""

    metadata: Dict[str, Any]
    economics: Dict[str, Any]
    lca: Dict[str, Any] | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Configuration":
        """Load a configuration from a YAML file."""
        path = Path(path)
        with path.open("r", encoding="utf-8") as stream:
            content = yaml.safe_load(stream)
        if content is None:
            raise ValueError(f"Configuration file {path} is empty")
        metadata = content.get("metadata", {})
        economics = content.get("economics", {})
        lca = content.get("lca")
        return cls(metadata=metadata, economics=economics, lca=lca)


def load_cost_table(path: str | Path) -> pd.DataFrame:
    """Load a CSV cost table for supporting analysis."""
    return pd.read_csv(path)


__all__ = ["Configuration", "load_cost_table"]
