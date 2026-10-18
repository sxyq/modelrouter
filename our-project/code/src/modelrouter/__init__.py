"""ModelRouter: Dynamic Cost-Effective Routing for Large Language Model Agents."""

__version__ = "0.1.0"

from . import agent
from . import baselines
from . import providers
from . import sandbox
from . import serving
from . import telemetry

__all__ = [
    "agent",
    "baselines",
    "providers",
    "sandbox",
    "serving",
    "telemetry",
    "__version__",
]
