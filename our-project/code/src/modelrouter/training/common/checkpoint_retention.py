"""Public checkpoint-retention API used by ModelRouter training entry points."""
import sys
from pathlib import Path
_WORKSPACE_ROOT = str(Path(__file__).resolve().parents[6])
if _WORKSPACE_ROOT not in sys.path: sys.path.insert(0, _WORKSPACE_ROOT)
from .checkpoint_metrics import *
from .checkpoint_metrics import _atomic_write_json, _clip_improvement, _normalize_baseline_0_dict, _now_iso
from .checkpoint_identity import *
from .checkpoint_identity import (
    _finite_metric, _kev_recipe_issue, _kev_val_issue, _node_primary_sort_key,
    _quantile_sorted, _rankable_node,
)
from .checkpoint_policy import *
from .checkpoint_inventory import load_and_evaluate_all as _checkpoint_inventory_load_and_evaluate_all
from .checkpoint_disk import is_whitelisted_checkpoint_dir as _checkpoint_disk_is_whitelisted_checkpoint_dir, is_mandatory_checkpoint as _checkpoint_disk_is_mandatory_checkpoint, disk_status as _checkpoint_disk_disk_status, two_phase_cleanup as _checkpoint_disk_two_phase_cleanup, pre_run_disk_check as _checkpoint_disk_pre_run_disk_check
from .checkpoint_writer import _sync_run_best_symlink as _checkpoint_writer__sync_run_best_symlink, handle_epoch_checkpoint as _checkpoint_writer_handle_epoch_checkpoint, finalize_run_checkpoints as _checkpoint_writer_finalize_run_checkpoints, write_checkpoint_manifest as _checkpoint_writer_write_checkpoint_manifest

class CheckpointRetentionManager:
    def __init__(
        self,
        out_root: Path,
        active_budget_bytes: int = DEFAULT_ACTIVE_BUDGET_BYTES,
        warn_free_pct: float = DISK_WARN_FREE_PCT,
        stop_free_pct: float = DISK_STOP_FREE_PCT,
        warn_free_bytes: int = DISK_WARN_FREE_BYTES,
        stop_free_bytes: int = DISK_STOP_FREE_BYTES,
        s2_audit_passed: bool = False,
        explicit_pinned: Optional[Iterable[str]] = None,
    ):
        self.out_root = Path(out_root).resolve()
        self.active_budget_bytes = int(active_budget_bytes)
        self.warn_free_pct = float(warn_free_pct)
        self.stop_free_pct = float(stop_free_pct)
        self.warn_free_bytes = int(warn_free_bytes)
        self.stop_free_bytes = int(stop_free_bytes)
        self.s2_audit_passed = bool(s2_audit_passed)
        self.explicit_pinned: Set[str] = set(explicit_pinned or ())

    def load_and_evaluate_all(self, manifest: Optional[Dict[str, Any]]=None) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]], Dict[str, List[str]], Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Load all `run.json` files in `out_root` and evaluate P1/P2 retention across all nodes."""
        return _checkpoint_inventory_load_and_evaluate_all(self, manifest)

    def is_whitelisted_checkpoint_dir(self, target_dir: Path) -> Tuple[bool, str]:
        """Verify `target_dir` is strictly inside `<out_root>/<run_id>/checkpoints/<name>` and not forbidden."""
        return _checkpoint_disk_is_whitelisted_checkpoint_dir(self, target_dir)

    def is_mandatory_checkpoint(self, cid: str, dec: Dict[str, Any], node: Optional[Dict[str, Any]]=None, pinned_map: Optional[Dict[str, Any]]=None, run_status: Optional[str]=None) -> Tuple[bool, Optional[str]]:
        """Return (True, reason) if this checkpoint is mandatory to retain and must NEVER be pruned or evicted."""
        return _checkpoint_disk_is_mandatory_checkpoint(self, cid, dec, node, pinned_map, run_status)

    def disk_status(self, simulated_statvfs: Optional[Dict[str, int]]=None) -> Dict[str, Any]:
        """Query real-time filesystem capacity and active weight usage."""
        return _checkpoint_disk_disk_status(self, simulated_statvfs)

    def two_phase_cleanup(self, manifest: Optional[Dict[str, Any]]=None, allow_legacy_cleanup: bool=False, dry_run: bool=False) -> Dict[str, Any]:
        """Execute P3 Two-Phase Checkpoint Cleanup within the authorized `out_root` whitelist.

            Phase 1: Build cleanup plan, verify history persistence, pinned parent references,
                     whitelist path boundaries, and active write locks.
            Phase 2: Delete verified low-score / duplicate / completed-run temporary checkpoints
                     directly (never moving to `.Trash`) and record exact freed bytes.
            """
        return _checkpoint_disk_two_phase_cleanup(self, manifest, allow_legacy_cleanup, dry_run)

    def pre_run_disk_check(self, run_id: str, manifest: Optional[Dict[str, Any]]=None, simulated_statvfs: Optional[Dict[str, int]]=None, estimated_peak_bytes: int=ESTIMATED_RUN_PEAK_TEMP_BYTES) -> Dict[str, Any]:
        """P3 Pre-Run Disk & Budget Check before launching any new Run.

            Checks:
            1. Free disk space (percentage & absolute GiB)
            2. Estimated temporary peak for this Run
            3. Current active weights total
            4. Best, PINNED, and temp recovery usage
            5. Whether low-value non-dependent weights need to be freed first.
            """
        return _checkpoint_disk_pre_run_disk_check(self, run_id, manifest, simulated_statvfs, estimated_peak_bytes)

    def _sync_run_best_symlink(self, run_id: str, rdata: Dict[str, Any]) -> None:
        """Ensure `checkpoints/best` points to the true scientific best epoch directory ONLY if it exists physically.
            Never overwrite `best_epoch` with a suboptimal surviving epoch after pruning.
            """
        return _checkpoint_writer__sync_run_best_symlink(self, run_id, rdata)

    def handle_epoch_checkpoint(self, run_id: str, epoch: int, is_final_epoch: bool, save_fn, run_meta: Dict[str, Any], entry: Dict[str, Any], manifest: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        """P0 + P1 + P2 + P3 per-epoch checkpoint handler.

            1. Records full epoch metrics into `run_meta['history']`, `run.json`, and `epoch_metrics.json`.
            2. Evaluates across all comparable runs in `out_root` whether this epoch qualifies for retention.
            3. Writes physical weights ONLY if qualified (or writes temporary recovery if run is still active).
            4. Deduplicates `best` and `latest` via relative symlinks (never writing duplicate `model.safetensors`).
            5. Runs Two-Phase Cleanup if an earlier Top-K / cold-start checkpoint in the group was displaced.
            """
        return _checkpoint_writer_handle_epoch_checkpoint(self, run_id, epoch, is_final_epoch, save_fn, run_meta, entry, manifest)

    def finalize_run_checkpoints(self, run_id: str, run_meta: Dict[str, Any], manifest: Optional[Dict[str, Any]]=None) -> None:
        """Clean up temporary `latest` / `_temp_recovery` upon Run completion and sync `best` symlink."""
        return _checkpoint_writer_finalize_run_checkpoints(self, run_id, run_meta, manifest)

    def write_checkpoint_manifest(self, manifest: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        """Write comprehensive `checkpoint_manifest.json` in `out_root` covering P4 & P5."""
        return _checkpoint_writer_write_checkpoint_manifest(self, manifest)

def sync_server_metadata_and_build_dashboard(
    project_root: Path,
    dashboard_dir: Optional[Path] = None,
    run_official_load: bool = True,
) -> Dict[str, Any]:
    """Refresh read-only training observations using the maintained collector."""
    from scripts.fetch_live_status import build_training_history

    history = build_training_history(Path(project_root), dashboard_dir)
    return {"counts": history["counts"], "history": "shards/training_history.json",
            "generated_at": history["generated_at"]}
