"""Backward-compatibility shim for modelrouter.baselines.policy."""
import os
import sys

_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "our-project", "code", "src"))
if os.path.isdir(_src_dir) and _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from modelrouter.baselines.policy import *
from modelrouter.baselines.policy import (
    BasePolicy,
    FixedStrongPolicy,
    FixedCheapPolicy,
    RandomPolicy,
    RuleStickyPolicy,
    RouteLLMPolicy,
    SRKNNPolicy,
    LayaServerPolicy,
    KevServerPolicy,
    create_policy,
)
