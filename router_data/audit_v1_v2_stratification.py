"""Legacy CLI and import path for V1/V2.1 stratification auditing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.quality.audit_v1_v2_stratification import audit_stratification

if __name__ == "__main__":
    audit_stratification(Path(__file__).resolve().parents[1])

