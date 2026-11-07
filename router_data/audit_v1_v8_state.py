"""Legacy CLI and import path for the V1/V8 data-state audit."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.quality.audit_v1_v8_state import *

if __name__ == "__main__":
    main()

