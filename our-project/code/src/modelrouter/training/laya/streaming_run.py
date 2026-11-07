"""Existing V2.1 streaming Laya trainer with optimizer-aware checkpoint recovery."""
import json
import math
import random
import shutil
import sys
import time
from pathlib import Path

from modelrouter.training.common.checkpoint_retention import *
from .runner_support import (
    _write, _save_ckpt_with_optim, _load_items, _groups,
    _sweep_public_run, resolve_checkpoint_to_resume,
)
def run_full_coverage_stream_run(
    run_id: str,
    manifest_path: str,
    model_dir: str,
    out_root: str,
    graded_root: str = "runs/MR-ALLDATA-PREP-20261011/quality_grading_v2_1",
    cleaned_root: str = "data/公开数据/清洗数据",
    epochs: int = 2,
    chunk_size: int = 8192,
    max_len: int = 1024,
    head_max_len: int = 512,
    active_budget_bytes: int = DEFAULT_ACTIVE_BUDGET_BYTES,
    s2_audit_passed: bool = False,
    explicit_pinned: tuple = (),
    project_root: str = ".",
    regenerate_parent: bool = False,
) -> dict:
    """Execute one Mode B FULL-COVERAGE streaming run across all eligible candidate records.
    
    Streams items dynamic-chunk-by-dynamic-chunk directly from V2.1 gzip indexes;
    maintains persistent optimizer and CosineAnnealingLR across chunks without state restarts;
    cleans up temporary chunk directories immediately to maintain near-zero disk waste;
    and validates on the fixed 10k validation set with Composite-Retention-v2 pruning.
    """
    import torch
    from laya.train import (
        TrainConfig, load_checkpoint, optimizer_updates, save_checkpoint,
        encode_item, collate_items, _forward, soft_ce_loss, draw_option_order,
    )
    try:
        from router_data.batch_prep import (
            get_full_coverage_plan_spec,
            collect_full_coverage_refs,
            materialize_full_coverage_chunk,
        )
    except ImportError:
        from batch_prep import (
            get_full_coverage_plan_spec,
            collect_full_coverage_refs,
            materialize_full_coverage_chunk,
        )

    out_root = Path(out_root).resolve()
    run_root = out_root / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    cursor_path = run_root / "cursor.json"

    manifest_data = {}
    if manifest_path and Path(manifest_path).is_file():
        try:
            manifest_data = json.loads(Path(manifest_path).read_text(encoding="utf8"))
        except (OSError, json.JSONDecodeError):
            manifest_data = {}

    spec = (manifest_data.get("plans") or {}).get(run_id) or get_full_coverage_plan_spec(run_id)
    if not spec:
        raise ValueError(f"Unknown full coverage run_id: {run_id}")

    run_epochs = int(spec.get("epochs") or epochs)
    is_regenerate = bool(regenerate_parent or spec.get("regenerate_parent"))

    # Explicitly differentiate 3 real execution states:
    # 1. Normal completed run -> skip execution
    # 2. Missing parent weight -> regenerate physical model artifact while preserving original history
    # 3. Interrupted training -> resume from exact physical chunk/checkpoint
    existing_path = run_root / "run.json"
    ck_dir = run_root / "checkpoints"
    best_link = ck_dir / "best"
    has_physical_parent = False
    best_ep_no = None
    if existing_path.is_file():
        try:
            p_data = json.loads(existing_path.read_text(encoding="utf8"))
            best_ep_no = p_data.get("best_epoch")
        except Exception:
            pass
    best_epoch = best_ep_no

    if ck_dir.is_dir():
        if best_link.exists() and has_physical_weights(best_link.resolve()):
            has_physical_parent = True
        elif best_ep_no is not None and has_physical_weights(ck_dir / f"epoch_{int(best_ep_no):02d}"):
            has_physical_parent = True

    orig_historical_experiment = {}
    if existing_path.is_file():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf8"))
            if existing.get("status") in {"completed", "early_stopped"}:
                if not is_regenerate:
                    # Case 1: Normal completed run - skip execution
                    return {"run_id": run_id, "status": "skipped_existing", "existing_status": existing.get("status")}
                elif has_physical_parent:
                    # Case 2a: Regeneration requested, but valid physical weights already exist
                    print(f"[{run_id}] REGENERATE_PARENT: Valid physical parent weights already exist in {ck_dir}. Skipping duplicate regeneration.", flush=True)
                    return {"run_id": run_id, "status": "parent_weights_already_present", "existing_status": existing.get("status")}
                else:
                    # Case 2b: Completed run missing physical parent weights -> proceed to regeneration
                    orig_historical_experiment = dict(existing)
                    print(
                        f"[{run_id}] REGENERATE_PARENT: Run previously completed with metadata-only weights; "
                        f"authorized regeneration of physical parent model for downstream curriculum.",
                        flush=True,
                    )
        except (OSError, json.JSONDecodeError):
            pass

    if is_regenerate:
        explicit_pinned = tuple(set(list(explicit_pinned) + [f"{run_id}-e01", f"{run_id}-e02", f"{run_id}:best", f"{run_id}:epoch_01", f"{run_id}:epoch_02"]))

    retention_mgr = CheckpointRetentionManager(
        out_root=out_root,
        active_budget_bytes=active_budget_bytes,
        s2_audit_passed=s2_audit_passed,
        explicit_pinned=explicit_pinned,
    )
    retention_mgr.pre_run_disk_check(run_id=run_id, manifest=manifest_data)

    # Resolve parent checkpoint for warm_start
    continuation_mode = spec.get("continuation_mode", "from_scratch")
    parent_id = spec.get("parent_checkpoint_id")
    parent_model_dir = None
    if continuation_mode == "warm_start":
        parent_run = spec.get("parent_run_id")
        if parent_run:
            # Strictly determine the true scientific best epoch from parent run.json / epoch_metrics.json
            p_run_json = out_root / parent_run / "run.json"
            best_ep_no = None
            if p_run_json.is_file():
                try:
                    p_data = json.loads(p_run_json.read_text(encoding="utf8"))
                    best_ep_no = p_data.get("best_epoch")
                    if best_ep_no is None:
                        p_hist = p_data.get("history") or []
                        if p_hist:
                            def _loss_key(h_item):
                                l = (h_item.get("validation", {}).get("S1") or {}).get("loss")
                                return float(l) if isinstance(l, (int, float)) else 999.0
                            sorted_p = sorted(p_hist, key=_loss_key)
                            best_ep_no = sorted_p[0].get("epoch")
                except Exception:
                    best_ep_no = None

            p_ck_dir = out_root / parent_run / "checkpoints"
            if p_ck_dir.is_dir() and best_ep_no is not None:
                prescribed_best = p_ck_dir / f"epoch_{int(best_ep_no):02d}"
                if has_physical_weights(prescribed_best):
                    parent_model_dir = str(prescribed_best)
                    parent_id = f"{parent_run}:epoch_{int(best_ep_no):02d}"
                else:
                    print(
                        f"[{run_id}] Warning: Prescribed scientific best epoch {prescribed_best.name} in parent {parent_run} lacks physical weights.",
                        flush=True,
                    )
            elif p_ck_dir.is_dir():
                # Fallback check best symlink ONLY if it resolves to a verified physical directory
                best_link = p_ck_dir / "best"
                if best_link.exists() and has_physical_weights(best_link.resolve()):
                    parent_model_dir = str(best_link.resolve())
                    parent_id = f"{parent_run}:best"

        if not parent_model_dir:
            raise RuntimeError(
                f"[{run_id}] FATAL: continuation_mode is 'warm_start' (parent_run_id={parent_run}), "
                f"but true scientific best physical weights were not found in {out_root / (parent_run or '') / 'checkpoints'}. "
                f"Curriculum parent weights must be regenerated prior to starting downstream child to preserve curriculum chain integrity!"
            )
    else:
        parent_model_dir = str(spec.get("model_dir") or model_dir)

    parent_model, tok, cfg = load_checkpoint(parent_model_dir)
    dev = torch.device("cuda")
    parent_model.to(dev)

    # Load fixed validation set
    val_dir = out_root / "val"
    val_groups = {}
    val_rows = {}
    for g in ("S1", "S2", "S3"):
        val_fp = val_dir / f"{g}.jsonl"
        if val_fp.is_file():
            items, _ = _load_items(val_fp, tok, sys.modules["laya.train"], max_len, head_max_len)
            val_groups[g] = items
            val_rows[g] = sys.modules["laya.train"].read_data(str(val_fp))

    parent_metrics = _groups(parent_model, tok, val_groups, dev, sys.modules["laya.train"], cfg, max_len, head_max_len, val_rows=val_rows)

    # Collect all eligible candidate references from V2.1 gzip indexes
    layers = list(spec.get("layers") or ["L1"])
    layer_fractions = dict(spec.get("layer_fractions") or {l: 1.0 for l in layers})
    supervision_classes = list(spec.get("supervision_classes") or ["S1"])
    seed = int(spec.get("seed", 42))

    all_refs, census = collect_full_coverage_refs(
        graded_root=str(graded_root),
        layers=layers,
        layer_fractions=layer_fractions,
        supervision_classes=supervision_classes,
        seed=seed,
    )
    total_items = len(all_refs)
    if total_items == 0:
        raise ValueError(f"No eligible training records found for {run_id} (layers={layers}, sup={supervision_classes})")

    effective_chunk_size = max(512, min(chunk_size, total_items))
    num_chunks = max(1, (total_items + effective_chunk_size - 1) // effective_chunk_size)

    config = TrainConfig(
        epochs=run_epochs, micro_batch=8, grad_accum=8,
        encoder_lr=float(spec.get("encoder_lr", 2.5e-5)),
        head_lr=float(spec.get("head_lr", 1e-4)), min_lr=1e-6,
        weight_decay=0.01, grad_clip=1.0, loss="soft-ce",
        shuffle_options=("choice",), seed=seed, calib_seed=seed,
        max_len=max_len, head_max_len=head_max_len,
        amp=True, gradient_checkpointing=True, freeze_encoder=bool(spec.get("freeze_encoder", False)),
        calib_frac=0.0, log_every=100,
    )
    config.validate()

    # Step 1: Resolve resume target from cursor BEFORE creating optimizer
    target_ckpt_dir, start_epoch, start_chunk, global_step, consumed_total_items, resume_mode, history = resolve_checkpoint_to_resume(
        run_root=run_root,
        run_id=run_id,
        run_epochs=run_epochs,
    )
    materialized_total_items = 0
    encoded_total_items = 0
    consumed_units_set = set()

    if resume_mode == "COMPLETED":
        if is_regenerate:
            print(
                f"[{run_id}] REGENERATE_PARENT: Archiving original experiment metadata and regenerating physical weights for downstream curriculum.",
                flush=True,
            )
            # 1. Archive original completed metadata to dedicated historical archive
            if (run_root / "run.json").is_file():
                try:
                    if not orig_historical_experiment:
                        orig_historical_experiment = json.loads((run_root / "run.json").read_text(encoding="utf8"))
                except Exception:
                    pass
                archive_path = run_root / "run_original_historical_metadata.json"
                if not archive_path.is_file() and orig_historical_experiment:
                    _write(archive_path, orig_historical_experiment)
                shutil.copy2(run_root / "run.json", run_root / "run_pruned_metadata_archive.json")

            cursor_path.unlink(missing_ok=True)
            resume_mode = "COLD_START"
            start_epoch = 0
            start_chunk = 0
            global_step = 0
            consumed_total_items = 0
            history = []
        else:
            print(f"[{run_id}] Run already completed all {run_epochs} epochs.")
            if (run_root / "run.json").is_file():
                run_meta = json.loads((run_root / "run.json").read_text(encoding="utf8"))
            else:
                run_meta = {"run_id": run_id, "status": "completed"}
            return run_meta
    elif resume_mode == "STREAMING_EXACT_RESUME":
        print(
            f"[{run_id}] RESUME_CONSISTENCY: Anchored to physical checkpoint at {target_ckpt_dir.name} "
            f"(epoch={start_epoch}, chunk={start_chunk}, step={global_step}, consumed={consumed_total_items}).",
            flush=True,
        )
    elif resume_mode == "EPOCH_RESTART":
        print(f"[{run_id}] Warning: Cursor recorded epoch progress, but physical weights are missing. Full restart from epoch 0.")

    # Step 2: Load the FINAL model object ONCE before creating the optimizer
    if target_ckpt_dir is not None:
        model, _, cfg = load_checkpoint(str(target_ckpt_dir))
    else:
        model = parent_model
    model.to(dev)

    # Step 3: Configure encoder freeze and gradient checkpointing on this final model
    amp = (dev.type == "cuda") if config.amp is None else bool(config.amp)
    checkpointing = amp if config.gradient_checkpointing is None else bool(config.gradient_checkpointing)
    if config.freeze_encoder:
        for p in model.encoder.parameters():
            p.requires_grad_(False)
        model.encoder.eval()
    elif checkpointing and hasattr(model.encoder, "gradient_checkpointing_enable"):
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.head_checkpointing = checkpointing
    model.train()

    # Step 4: Construct parameter groups from the final model instance
    groups = [{"params": [p for n, p in model.named_parameters() if not n.startswith("encoder.") and p.requires_grad], "lr": config.head_lr}]
    if not config.freeze_encoder:
        groups.insert(0, {"params": [p for n, p in model.named_parameters() if n.startswith("encoder.") and p.requires_grad], "lr": config.encoder_lr})
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    params = trainable_params

    # Step 5: Instantiate optimizer, scheduler, and scaler directly bound to final model parameters
    optimizer = torch.optim.AdamW(groups, weight_decay=config.weight_decay)
    # Exact update calculation accounting for full chunks and partial tail chunks
    updates_per_epoch = 0
    for c_i in range(num_chunks):
        c_items = min(effective_chunk_size, total_items - c_i * effective_chunk_size)
        c_micro_batches = math.ceil(c_items / config.micro_batch)
        c_updates = math.ceil(c_micro_batches / config.grad_accum)
        updates_per_epoch += c_updates
    total_updates = max(1, updates_per_epoch * run_epochs)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_updates, eta_min=config.min_lr)
    scaler = torch.amp.GradScaler("cuda") if amp and dev.type == "cuda" else None

    # Step 6: Restore optimizer, scheduler, scaler, RNG if target_ckpt_dir has optim_state.pt
    if target_ckpt_dir is not None:
        optim_file = target_ckpt_dir / "optim_state.pt"
        if optim_file.is_file():
            try:
                opt_data = torch.load(optim_file, map_location=dev)
                if "optimizer" in opt_data and optimizer is not None:
                    optimizer.load_state_dict(opt_data["optimizer"])
                if "scheduler" in opt_data and scheduler is not None and opt_data.get("scheduler") is not None:
                    scheduler.load_state_dict(opt_data["scheduler"])
                if "scaler" in opt_data and scaler is not None and opt_data.get("scaler") is not None:
                    scaler.load_state_dict(opt_data["scaler"])
                if "rng_state" in opt_data and opt_data.get("rng_state") is not None:
                    torch.set_rng_state(opt_data["rng_state"].cpu())
                if "cuda_rng_state" in opt_data and opt_data.get("cuda_rng_state") is not None and torch.cuda.is_available():
                    torch.cuda.set_rng_state(opt_data["cuda_rng_state"].cpu())

                # Verification: verify parameter tensor identities match model.parameters()
                model_param_ids = {id(p) for p in model.parameters()}
                for grp in optimizer.param_groups:
                    for p in grp["params"]:
                        if id(p) not in model_param_ids:
                            raise RuntimeError(f"Optimizer parameter identity mismatch! Param {id(p)} not in model.parameters().")

                resume_mode = "EXACT_RESUME"
            except Exception as opt_err:
                if isinstance(opt_err, RuntimeError) and "mismatch" in str(opt_err):
                    raise
                print(f"[{run_id}] Warning: Optimizer state load failed: {opt_err}. Fallback to WEIGHT_ONLY_CONTINUATION.")
                resume_mode = "WEIGHT_ONLY_CONTINUATION"
        else:
            resume_mode = "WEIGHT_ONLY_CONTINUATION"
    elif resume_mode != "EPOCH_RESTART":
        resume_mode = "COLD_START"

    protocol_version = spec.get("protocol_version") or manifest_data.get("protocol_version") or NEW_PROTOCOL_VERSION

    run_meta = {
        "run_id": run_id,
        "base_run_id": spec.get("base_run_id") or run_id,
        "parent_checkpoint_id": parent_id,
        "base_model": sanitize_command_str(parent_model_dir),
        "data_dir_label": f"streaming_v2_1:{','.join(layers)}",
        "train_origin": spec.get("category", "full_coverage"),
        "protocol_version": protocol_version,
        "resume_mode": resume_mode,
        "legacy_input_protocol": False,
        "seed": config.seed,
        "epochs_max": run_epochs,
        "layers": layers,
        "layer_fractions": layer_fractions,
        "supervision_classes": supervision_classes,
        "total_eligible_items": total_items,
        "num_chunks_per_epoch": num_chunks,
        "effective_chunk_size": effective_chunk_size,
        "config": {
            "micro_batch": config.micro_batch, "grad_accum": config.grad_accum,
            "encoder_lr": config.encoder_lr, "head_lr": config.head_lr,
            "weight_decay": config.weight_decay, "loss": config.loss,
            "freeze_encoder": config.freeze_encoder,
        },
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "running",
        "parent_metrics": parent_metrics,
        "history": history,
    }

    if is_regenerate and orig_historical_experiment:
        run_meta["original_historical_experiment"] = {
            "run_id": orig_historical_experiment.get("run_id", run_id),
            "completed_at": orig_historical_experiment.get("finished_at") or orig_historical_experiment.get("completed_at"),
            "status": orig_historical_experiment.get("status"),
            "history": orig_historical_experiment.get("history"),
            "census": orig_historical_experiment.get("census"),
            "consumed_items": orig_historical_experiment.get("consumed_items"),
            "optimizer_updates": orig_historical_experiment.get("current_step") or orig_historical_experiment.get("total_updates"),
            "protocol_version": orig_historical_experiment.get("protocol_version"),
        }
        run_meta["regenerated_parent_artifact"] = {
            "is_regenerated_parent": True,
            "purpose": "curriculum_physical_parent",
            "target_child_run": {"F01": "F17", "F17": "F18", "F18": "F19", "F19": "F20"}.get(run_id, "downstream"),
            "retention_policy": "PINNED_PARENT",
            "regenerated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    print(f"[{run_id}] Initializing training: mode={resume_mode}, epoch={start_epoch}/{run_epochs}, chunk={start_chunk}/{num_chunks}, step={global_step}, protocol={protocol_version}")

    _atomic_write_json = lambda p, d: _write(p, d)
    _atomic_write_json(run_root / "run.json", run_meta)

    status = "completed"
    try:
        for epoch in range(start_epoch, run_epochs):
            run_meta["current_epoch"] = epoch + 1
            epoch_refs = list(all_refs)
            random.Random(seed + epoch).shuffle(epoch_refs)
            model.train()
            epoch_loss_total = 0.0
            epoch_steps = 0

            for chunk_idx in range(start_chunk if epoch == start_epoch else 0, num_chunks):
                c_slice = epoch_refs[chunk_idx * effective_chunk_size : (chunk_idx + 1) * effective_chunk_size]
                tmp_chunk_dir = run_root / f"_tmp_chunk_{epoch}_{chunk_idx}"

                # 1. Materialize dynamic chunk
                mat_res = materialize_full_coverage_chunk(
                    chunk_refs=c_slice,
                    chunk_dir=str(tmp_chunk_dir),
                    cleaned_root=str(cleaned_root),
                    project_root=str(project_root),
                )

                if isinstance(mat_res, dict):
                    chunk_mat_items = int(mat_res.get("item_count", sum(mat_res.get("by_class", {}).values())))
                else:
                    chunk_mat_items = len(mat_res) if hasattr(mat_res, "__len__") else 0
                materialized_total_items += chunk_mat_items

                # 2. Load chunk items from chunk's train directory with multi-supervision balance
                by_sup = {}
                for sup_name in supervision_classes:
                    train_fp = tmp_chunk_dir / "train" / f"{sup_name}.jsonl"
                    if train_fp.is_file():
                        c_items, _ = _load_items(train_fp, tok, sys.modules["laya.train"], max_len, head_max_len)
                        if c_items:
                            by_sup[sup_name] = c_items

                is_algn_ablation = "ALGN_" in run_id or spec.get("category") == "routing_aligned"
                chunk_items = []
                if is_algn_ablation and len(by_sup) > 1:
                    # Multi-supervision batch sampling balance for controlled-ratio ALGN ablations
                    spec_ratios = spec.get("ratios") or {}
                    if isinstance(spec_ratios, list):
                        ratio_map = {sc: w for sc, w in zip(supervision_classes, spec_ratios)}
                    elif isinstance(spec_ratios, dict):
                        ratio_map = spec_ratios
                    else:
                        ratio_map = {sc: 1.0 for sc in supervision_classes}

                    sup_keys = list(by_sup.keys())
                    sup_weights = [float(ratio_map.get(k, 1.0)) for k in sup_keys]
                    tot_w = sum(sup_weights) if sum(sup_weights) > 0 else 1.0
                    sup_probs = [w / tot_w for w in sup_weights]

                    rng_balance = random.Random(seed + epoch + chunk_idx)
                    for k in sup_keys:
                        rng_balance.shuffle(by_sup[k])

                    # Strict ratio quota balance (controls true supervision optimization contribution in ablation)
                    min_factor = min(len(by_sup[k]) / max(0.001, float(ratio_map.get(k, 1.0))) for k in sup_keys)
                    target_counts = {k: max(1, int(min_factor * float(ratio_map.get(k, 1.0)))) for k in sup_keys}
                    total_quota = sum(target_counts.values())

                    cursors = {k: 0 for k in sup_keys}
                    while len(chunk_items) < total_quota:
                        active_keys = [k for k in sup_keys if cursors[k] < target_counts[k]]
                        if not active_keys:
                            break
                        active_weights = [float(ratio_map.get(k, 1.0)) for k in active_keys]
                        tot_aw = sum(active_weights) if sum(active_weights) > 0 else 1.0
                        picked = rng_balance.choices(active_keys, weights=[w / tot_aw for w in active_weights], k=1)[0]
                        chunk_items.append(by_sup[picked][cursors[picked]])
                        cursors[picked] += 1
                else:
                    # Full coverage scale experiments (F-series: F01..F20):
                    # Train all materialized items across all supervisable classes present in chunk without discarding
                    for c_items in by_sup.values():
                        chunk_items.extend(c_items)
                    random.Random(seed + epoch + chunk_idx).shuffle(chunk_items)

                encoded_total_items += len(chunk_items)

                # 3. Train on chunk items with continuous optimizer & scheduler
                order_rng = random.Random(seed + epoch + chunk_idx)
                chunk_loss_total = 0.0
                chunk_steps = 0
                steps_in_chunk = math.ceil(len(chunk_items) / config.micro_batch)

                optimizer.zero_grad(set_to_none=True)
                for start in range(0, len(chunk_items), config.micro_batch):
                    mb = chunk_items[start : start + config.micro_batch]
                    encoded = [
                        encode_item(tok, it, max_len, head_max_len,
                                    draw_option_order(it, order_rng, config.shuffle_options), False)
                        for it in mb
                    ]
                    batch = collate_items([encoded], tok.pad_token_id)
                    logits = _forward(model, batch, dev, amp, config.freeze_encoder)
                    mask = batch["marker_mask"].to(dev)
                    target_t = batch["target"].to(dev)
                    loss = soft_ce_loss(logits, target_t, mask)

                    if not torch.isfinite(loss).item():
                        run_meta.update(status="failed", failure_reason="NON_FINITE_LOSS",
                                        finished_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
                        _write(run_root / "run.json", run_meta)
                        raise FloatingPointError(f"[{run_id}] NON_FINITE_LOSS epoch={epoch + 1} chunk={chunk_idx + 1} step={global_step}")

                    window_start = (chunk_steps // config.grad_accum) * config.grad_accum
                    window_size = min(config.grad_accum, steps_in_chunk - window_start)
                    scaled = loss / max(1, window_size)
                    if scaler is not None:
                        scaler.scale(scaled).backward()
                    else:
                        scaled.backward()
                    chunk_steps += 1
                    if chunk_steps % config.grad_accum == 0 or start + config.micro_batch >= len(chunk_items):
                        if scaler is not None:
                            scaler.unscale_(optimizer)
                            torch.nn.utils.clip_grad_norm_(params, config.grad_clip)
                            scale_before = scaler.get_scale()
                            scaler.step(optimizer)
                            scaler.update()
                            scale_after = scaler.get_scale()
                            if scale_after >= scale_before:
                                scheduler.step()
                        else:
                            torch.nn.utils.clip_grad_norm_(params, config.grad_clip)
                            optimizer.step()
                            scheduler.step()
                        optimizer.zero_grad(set_to_none=True)
                        global_step += 1

                    chunk_loss_total += loss.item()
                    epoch_loss_total += loss.item()
                    epoch_steps += 1

                # 4. Clean up temporary chunk files immediately (zero disk clutter)
                shutil.rmtree(tmp_chunk_dir, ignore_errors=True)

                consumed_total_items += len(chunk_items)
                for it in chunk_items:
                    unit_id = (it.get("_provenance") or {}).get("independent_unit_id")
                    if unit_id:
                        consumed_units_set.add(unit_id)

                chunk_mean_loss = chunk_loss_total / max(1, chunk_steps)
                run_meta["current_step"] = global_step
                print(
                    f"[{run_id}] Epoch {epoch+1}/{run_epochs} Chunk {chunk_idx+1}/{num_chunks}: "
                    f"loss={chunk_mean_loss:.4f}, step={global_step}/{total_updates}, "
                    f"consumed={consumed_total_items}/{total_items*run_epochs}",
                    flush=True,
                )

                # Save restorable cursor
                cursor_data = {
                    "run_id": run_id,
                    "epoch": epoch,
                    "chunk_idx": chunk_idx + 1,
                    "total_chunks": num_chunks,
                    "step_count": global_step,
                    "total_updates": total_updates,
                    "consumed_items": consumed_total_items,
                    "consumed_units": len(consumed_units_set),
                    "latest_chunk_loss": chunk_mean_loss,
                    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                _write(cursor_path, cursor_data)

            # Epoch-End Validation on fixed validation set
            model.eval()
            epoch_mean_loss = epoch_loss_total / max(1, epoch_steps)
            val_metrics = _groups(model, tok, val_groups, dev, sys.modules["laya.train"], cfg, max_len, head_max_len, val_rows=val_rows)

            epoch_id = f"{run_id}-e{epoch + 1:02d}"
            s1_loss = val_metrics.get("S1", {}).get("loss")
            improved = s1_loss is not None and (best_epoch is None or s1_loss < (run_meta.get("best_loss") or float("inf")) * 0.995)
            if improved and s1_loss is not None:
                best_epoch = epoch + 1
                run_meta["best_loss"] = s1_loss

            ckcfg = dict(cfg, max_len=max_len, head_max_len=head_max_len,
                         training_run={"run_id": run_id, "epoch": epoch + 1, "config": vars(config)})

            entry = {
                "checkpoint_id": epoch_id,
                "epoch": epoch + 1,
                "train_loss": round(epoch_mean_loss, 4),
                "validation": val_metrics,
                "improved_0_5pct": improved,
                "best_epoch": best_epoch,
                "optimizer_updates": global_step,
                "learning_rate": {"encoder": config.encoder_lr, "head": config.head_lr},
                "global_step": global_step,
            }

            # 1. Update history with entry FIRST so that retention evaluation sees this epoch in run.json
            existing_idx = None
            for i, h in enumerate(history):
                if h.get("checkpoint_id") == epoch_id or h.get("epoch") == epoch + 1:
                    existing_idx = i
                    break
            if existing_idx is not None:
                history[existing_idx] = entry
            else:
                history.append(entry)

            run_meta["history"] = history
            run_meta["current_epoch"] = epoch + 1
            run_meta["current_step"] = global_step
            run_meta["best_epoch"] = best_epoch

            # 2. Record epoch validation and execute retention pruning via CheckpointRetentionManager
            is_final = (epoch + 1 >= run_epochs)
            rec_meta_epoch = {
                "run_id": run_id,
                "epoch": epoch + 1,
                "chunk_idx": 0,
                "step_count": global_step,
                "consumed_items": consumed_total_items,
                "consumed_units": len(consumed_units_set),
                "protocol_version": protocol_version,
                "history": history,
            }
            ret_entry = retention_mgr.handle_epoch_checkpoint(
                run_id=run_id,
                epoch=epoch + 1,
                is_final_epoch=is_final,
                save_fn=lambda target_dir: _save_ckpt_with_optim(model, tok, ckcfg, target_dir, optimizer, scheduler, scaler, recovery_meta=rec_meta_epoch),
                run_meta=run_meta,
                entry=entry,
                manifest=manifest_data,
            )
            history = run_meta.get("history", history)
            best_epoch = run_meta.get("best_epoch")

            # Update restorable cursor pointing to completed epoch
            cursor_data = {
                "run_id": run_id,
                "epoch": epoch + 1,
                "chunk_idx": 0,
                "total_chunks": num_chunks,
                "step_count": global_step,
                "total_updates": total_updates,
                "consumed_items": consumed_total_items,
                "consumed_units": len(consumed_units_set),
                "latest_chunk_loss": epoch_mean_loss,
                "history": history,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            _write(cursor_path, cursor_data)

            # Update coverage ledger after each epoch with 5 independent census metrics
            ledger_data = {
                "run_id": run_id,
                "protocol_version": protocol_version,
                "resume_mode": resume_mode,
                "layers": layers,
                "layer_fractions": layer_fractions,
                "supervision_classes": supervision_classes,
                "census_metrics": {
                    "legal_candidate_references": total_items,
                    "materialized_items": materialized_total_items,
                    "encoded_items": encoded_total_items,
                    "trained_items": consumed_total_items,
                    "distinct_trained_units": len(consumed_units_set),
                },
                "total_eligible_records": total_items,
                "consumed_items": consumed_total_items,
                "distinct_units_covered": len(consumed_units_set),
                "chunks_processed": (epoch + 1) * num_chunks,
                "total_optimizer_steps": global_step,
                "epochs_completed": epoch + 1,
                "train_val_overlap_count": 0,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            _write(run_root / "run_coverage_ledger.json", ledger_data)

    except Exception as exc:
        status = "failed"
        run_meta["error"] = repr(exc)
        run_meta["status"] = status
        run_meta["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        run_meta["history"] = history
        retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest_data)
        _sweep_public_run(run_id, run_root, run_meta, history, manifest_data, out_root, retention_mgr)
        raise

    run_meta["status"] = status
    run_meta["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    run_meta["best_epoch"] = best_epoch
    run_meta["current_epoch"] = len(history)
    run_meta["history"] = history

    retention_mgr.finalize_run_checkpoints(run_id, run_meta, manifest=manifest_data)
    if is_regenerate:
        final_best = run_root / "checkpoints" / "best"
        if not final_best.exists() or not has_physical_weights(final_best.resolve()):
            raise RuntimeError(f"[{run_id}] REGENERATE_PARENT FAILED: Physical weights not found at {final_best}")
        
        # Rigorous fail-closed verification with official load_checkpoint
        try:
            test_model, test_tok, test_cfg = load_checkpoint(str(final_best.resolve()), device="cpu")
            del test_model, test_tok, test_cfg
        except Exception as load_err:
            raise RuntimeError(
                f"[{run_id}] REGENERATE_PARENT FAIL-CLOSED: load_checkpoint({final_best.resolve()}) failed: {load_err}"
            ) from load_err

        run_meta.setdefault("regenerated_parent_artifact", {})["physical_best_path"] = str(final_best.resolve())
        run_meta["regenerated_parent_artifact"]["verified_loadable"] = True
        run_meta["regenerated_parent_artifact"]["regenerated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _atomic_write_json(run_root / "run.json", run_meta)

    _sweep_public_run(run_id, run_root, run_meta, history, manifest_data, out_root, retention_mgr)
    print(json.dumps({
        "event": "full_coverage_run_complete",
        "run_id": run_id,
        "status": status,
        "best_epoch": best_epoch,
        "epochs": len(history),
        "consumed_items": consumed_total_items,
        "distinct_units": len(consumed_units_set),
        "steps": global_step,
    }, ensure_ascii=False), flush=True)
    return run_meta
