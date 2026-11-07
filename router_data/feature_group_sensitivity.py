"""Legacy CLI and import path for canonical feature-group sensitivity analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.quality.feature_group_sensitivity import *

if __name__ == "__main__":
    main()

