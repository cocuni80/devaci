"""devaci - Generate and push Cisco ACI configuration via the Cobra SDK."""

from importlib.metadata import PackageNotFoundError, version

from devaci.cobra import CobraBuilder
from devaci.config import DeployConfig
from devaci.console import configure_logging
from devaci.deploy import DeployClass
from devaci.exceptions import CobraError, DataError, DeployError, DevaciError, JinjaError
from devaci.rendering.jinja import JinjaRenderer

try:
    __version__ = version("devaci")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "CobraBuilder",
    "DeployClass",
    "DeployConfig",
    "JinjaRenderer",
    "configure_logging",
    "DevaciError",
    "CobraError",
    "JinjaError",
    "DataError",
    "DeployError",
    "__version__",
]
