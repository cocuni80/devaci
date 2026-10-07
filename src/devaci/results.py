"""Result data classes for devaci."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, cast


def _timestamp() -> str:
    return datetime.now().strftime("%d/%m/%Y-%H:%M:%S")


@dataclass(frozen=True)
class Result:
    """Base result shared by all devaci phases."""

    success: bool = False
    log: list[str] = field(default_factory=list)
    date: str = field(default_factory=_timestamp)

    def to_dict(self) -> dict[str, Any]:
        return {"date": self.date, "success": self.success, "log": self.log}


@dataclass(frozen=True)
class JinjaResult(Result):
    """Result of a Jinja template render."""

    output: Any = None

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["output"] = self.output
        return data


@dataclass(frozen=True)
class CobraResult(Result):
    """Result of building the Cobra configuration."""

    config: Any = None

    @property
    def xml(self) -> str | None:
        if self.config is None or not self.config.configMos:
            return None
        return cast(str | None, self.config.xmldata)

    @property
    def json(self) -> Any:
        if self.config is None or not self.config.configMos:
            return None
        return json.loads(self.config.data)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["json"] = self.json
        data["xml"] = self.xml
        return data


@dataclass(frozen=True)
class DeployResult(Result):
    """Result of deploying a single template."""

    path: str = "/"
    name: str = "template"

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["path"] = self.path
        data["name"] = self.name
        return data
