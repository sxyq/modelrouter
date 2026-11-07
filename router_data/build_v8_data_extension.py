"""Legacy CLI and import path for canonical V8 and Kev data exports."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "our-project" / "code" / "src"))

from modelrouter.data_pipeline.build_v8_data_extension import *
from modelrouter.data_pipeline.build_v8_data_extension import (
    _kev_coverage_rows, _kev_labeled_question, _kev_source_targets, main,
)

if __name__ == "__main__":
    main()

