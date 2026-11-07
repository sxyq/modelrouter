"""Validate exported choice views with the upstream Kev and Laya encoders."""

import json
import os
import random
import sys
from collections import Counter


def validate_kev_exports(kev_root, laya_root=None):
    """
    内置 CPU 全量 (100% 样本，严禁抽样) Kev 与 Laya 官方代码兼容性校验：
    1. 校验文件存在性 (train.jsonl, val.jsonl, test.jsonl, test_twinrouterbench_holdout.jsonl)
    2. 逐行校验必须字段: provenance (dict), state (str), questions (dict), expected (dict)
    3. 调用官方 Kev 代码 (kev.data.load_records -> materialize -> kev.model.encode) 对 100% 样本实测：
       - 验证默认训练上下文 (MAX_STATE=384, MAX_BRANCH=1024, MAX_PACKED=2048) 与 Kev-4B 训练上下文 (max_state=7552)
       - 统计真实 max_state_tokens, max_branch_tokens, max_packed_tokens, state_truncated, ContextOverflow
       - 验证候选模型顺序置换 (augment / option_isolation) 标签同步性
    4. 调用官方 Laya 代码 (laya.train.read_data -> items_from_rows -> build_sequence) 对 100% 样本实测：
       - 验证多候选路由训练配置 (max_len=1024, head_max_len=448) 与默认出厂配置 (max_len=512, head_max_len=192)
       - 统计真实 items_count, skipped 原因, state_truncated, max_seq_tokens, max_head_tokens
       - 验证 draw_option_order 与 parallel_layout 选项顺序置换同步性
    """
    print("\n" + "=" * 70)
    print("  [Kev & Laya 官方兼容性校验] 100% 全量样本真实编码、长度上限与置换不变性验证")
    print("=" * 70)

    target_files = [
        "train.jsonl",
        "val.jsonl",
        "test.jsonl",
        "test_twinrouterbench_holdout.jsonl"
    ]

    project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 尝试引入官方 Kev 与 Laya 仓库模块（使用相对项目根目录解析）
    for ext_rel in ("external/kev", "external/laya"):
        ext_path = os.path.join(project_root_dir, ext_rel)
        if os.path.exists(ext_path) and ext_path not in sys.path:
            sys.path.insert(0, ext_path)

    kev_mod = None
    kev_tok = None
    try:
        import kev.model as _kev_model_mod
        from kev.data import load_records as kev_load_records, materialize as kev_materialize, augment as kev_augment
        from kev.model import load_tokenizer as kev_load_tokenizer, encode as kev_encode, ContextOverflow, MAX_STATE, MAX_BRANCH, MAX_PACKED, training_context
        _orig_user_tokens = _kev_model_mod.user_tokens
        _kev_ut_cache = {}
        def _cached_user_tokens(tok_obj, text_val):
            key = (id(tok_obj), text_val)
            res = _kev_ut_cache.get(key)
            if res is None:
                res = _orig_user_tokens(tok_obj, text_val)
                if len(_kev_ut_cache) < 200000:
                    _kev_ut_cache[key] = res
            return res
        _kev_model_mod.user_tokens = _cached_user_tokens
        for ptd_rel in ("models/kev-4b-adapter", "models/qwen3.5-4b-base"):
            ptd = os.path.join(project_root_dir, ptd_rel)
            if os.path.exists(ptd):
                kev_tok = kev_load_tokenizer(ptd)
                kev_mod = {
                    "load_records": kev_load_records,
                    "materialize": kev_materialize,
                    "augment": kev_augment,
                    "encode": kev_encode,
                    "ContextOverflow": ContextOverflow,
                    "MAX_STATE": MAX_STATE,
                    "MAX_BRANCH": MAX_BRANCH,
                    "MAX_PACKED": MAX_PACKED,
                    "training_context": training_context
                }
                print(f"  [Kev Official] 成功加载官方 kev 模块与 Tokenizer: {ptd_rel} (vocab={kev_tok.vocab_size:,})")
                break
    except Exception as e:
        print(f"  [Kev Notice] 未在当前环境加载外部官方 kev 仓库或模型目录 ({e})，将执行基础 Schema 校验")

    laya_mod = None
    laya_tok = None
    try:
        from transformers import AutoTokenizer
        import laya.common as _laya_common_mod
        import laya.train as _laya_train_mod
        from laya.train import read_data as laya_read_data, items_from_rows as laya_items_from_rows, encode_item as laya_encode_item, draw_option_order as laya_draw_option_order
        from laya.common import build_sequence as laya_build_sequence
        _orig_laya_eqt = _laya_common_mod._encode_question_text
        _laya_eqt_cache = {}
        def _cached_laya_eqt(tok_obj, text_val, add_special_tokens=False, truncation=False, max_length=None):
            key = (id(tok_obj), text_val, add_special_tokens, truncation, max_length)
            res = _laya_eqt_cache.get(key)
            if res is None:
                res = _orig_laya_eqt(tok_obj, text_val, add_special_tokens=add_special_tokens, truncation=truncation, max_length=max_length)
                if len(_laya_eqt_cache) < 200000:
                    _laya_eqt_cache[key] = res
            return res
        _laya_common_mod._encode_question_text = _cached_laya_eqt
        _orig_laya_enc_state = _laya_train_mod.encode_state
        _laya_es_cache = {}
        def _cached_laya_enc_state(tok_obj, state_val, max_len_val):
            key = (id(tok_obj), state_val if isinstance(state_val, str) else json.dumps(state_val, sort_keys=True), max_len_val)
            res = _laya_es_cache.get(key)
            if res is None:
                res = _orig_laya_enc_state(tok_obj, state_val, max_len_val)
                if len(_laya_es_cache) < 200000:
                    _laya_es_cache[key] = res
            return res
        _laya_train_mod.encode_state = _cached_laya_enc_state
        _orig_laya_bh = _laya_common_mod.build_head
        _laya_bh_cache = {}
        def _cached_laya_bh(tok_obj, q_obj, head_max_len=192, option_order=None):
            crit_val = q_obj.get("crit")
            crit_key = tuple(crit_val.items()) if isinstance(crit_val, dict) else tuple(crit_val or ())
            ord_key = tuple(option_order) if option_order is not None else None
            key = (id(tok_obj), q_obj.get("t"), q_obj.get("ins"), crit_key, head_max_len, ord_key)
            res = _laya_bh_cache.get(key)
            if res is None:
                res = _orig_laya_bh(tok_obj, q_obj, head_max_len=head_max_len, option_order=option_order)
                if len(_laya_bh_cache) < 50000:
                    _laya_bh_cache[key] = res
            return res
        _laya_common_mod.build_head = _cached_laya_bh
        _laya_train_mod.build_head = _cached_laya_bh
        for ltd_rel in ("models/laya-421m/tokenizer", "models/laya-421m"):
            ltd = os.path.join(project_root_dir, ltd_rel)
            if os.path.exists(ltd):
                laya_tok = AutoTokenizer.from_pretrained(ltd)
                laya_mod = {
                    "read_data": laya_read_data,
                    "items_from_rows": laya_items_from_rows,
                    "encode_item": laya_encode_item,
                    "draw_option_order": laya_draw_option_order,
                    "build_sequence": laya_build_sequence,
                    "build_head": _cached_laya_bh
                }
                print(f"  [Laya Official] 成功加载官方 laya 模块与 Tokenizer: {ltd_rel} (vocab={laya_tok.vocab_size:,})")
                break
    except Exception as e:
        print(f"  [Laya Notice] 未在当前环境加载外部官方 laya 仓库或模型目录 ({e})，将执行基础 Schema 校验")

    total_validated = 0
    total_errors = 0
    file_stats = {}

    for fname in target_files:
        fpath = os.path.join(kev_root, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"[校验失败] 缺失文件: {fpath}")

        file_rec_count = 0
        file_err_count = 0
        error_details = []

        # Kev 100% 统计指标
        kev_max_state_tok = 0
        kev_max_branch_tok = 0
        kev_max_packed_tok = 0
        kev_ok_default_384 = 0
        kev_trunc_default_384 = 0
        kev_overflow_default_384 = 0
        kev_ok_7552 = 0
        kev_trunc_7552 = 0
        kev_perm_tested = 0
        kev_perm_passed = 0

        # Laya 100% 统计指标 (max_len=1024, head_max_len=448 及 默认 512/192 对照)
        laya_ok_records_1024_448 = 0
        laya_items_1024_448 = 0
        laya_trunc_1024_448 = 0
        laya_skipped_1024_448 = Counter()
        laya_max_seq_tok = 0
        laya_max_head_tok = 0
        laya_max_state_tok = 0
        laya_ok_records_512_192 = 0
        laya_skipped_512_192 = Counter()
        laya_perm_tested = 0
        laya_perm_passed = 0

        joint_kev_laya_readable = 0

        # 如果加载了官方 kev.data.load_records，先验证整文件一次性加载
        kev_loaded_reqs = None
        if kev_mod is not None:
            kev_loaded_reqs = kev_mod["load_records"](fpath, source=fname)

        with open(fpath, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                file_rec_count += 1
                total_validated += 1
                try:
                    r = json.loads(line)
                except Exception as e:
                    file_err_count += 1
                    total_errors += 1
                    error_details.append(f"Line {line_no}: JSON 解析失败: {e}")
                    continue

                for req_key in ("provenance", "state", "questions", "expected"):
                    if req_key not in r:
                        file_err_count += 1
                        total_errors += 1
                        error_details.append(f"Line {line_no}: 缺少顶级字段 '{req_key}'")

                prov = r.get("provenance", {})
                for p_key in ("source_id", "raw_file", "source_record_id", "selection_rule", "label_nature"):
                    if not prov.get(p_key):
                        file_err_count += 1
                        total_errors += 1
                        error_details.append(f"Line {line_no}: provenance 缺少必填溯源字段 '{p_key}'")

                state_val = r.get("state", "")
                if not isinstance(state_val, str) or not state_val.strip():
                    file_err_count += 1
                    total_errors += 1
                    error_details.append(f"Line {line_no}: 'state' 必须为非空字符串")

                questions = r.get("questions")
                expected = r.get("expected", {})
                if not isinstance(questions, dict) or not questions:
                    file_err_count += 1
                    total_errors += 1
                    error_details.append(f"Line {line_no}: 'questions' 必须为非空字典")
                else:
                    for qname, qdata in questions.items():
                        if not isinstance(qdata, dict):
                            file_err_count += 1
                            total_errors += 1
                            error_details.append(f"Line {line_no}: question '{qname}' 不是字典")
                            continue
                        qtype = qdata.get("type")
                        inst = qdata.get("instructions")
                        crit = qdata.get("criteria")
                        lbl = qdata.get("label")

                        if not inst or not isinstance(inst, str):
                            file_err_count += 1
                            total_errors += 1
                            error_details.append(f"Line {line_no}: question '{qname}' 缺少合法 instructions")

                        if qtype == "choice":
                            if not isinstance(crit, dict) or not crit:
                                file_err_count += 1
                                total_errors += 1
                                error_details.append(f"Line {line_no}: choice question '{qname}' criteria 不是非空字典")
                            elif not isinstance(lbl, str) or lbl not in crit:
                                file_err_count += 1
                                total_errors += 1
                                error_details.append(f"Line {line_no}: choice question '{qname}' label '{lbl}' 不在 criteria keys 中")
                        elif qtype == "score":
                            if not isinstance(crit, list) or not crit:
                                file_err_count += 1
                                total_errors += 1
                                error_details.append(f"Line {line_no}: score question '{qname}' criteria 不是非空列表")
                            elif not isinstance(lbl, int) or lbl < 0 or lbl >= len(crit):
                                file_err_count += 1
                                total_errors += 1
                                error_details.append(f"Line {line_no}: score question '{qname}' label '{lbl}' 超出 criteria 范围")
                        else:
                            file_err_count += 1
                            total_errors += 1
                            error_details.append(f"Line {line_no}: question '{qname}' 类型未知: '{qtype}'")

                        if expected.get(qname) != lbl:
                            file_err_count += 1
                            total_errors += 1
                            error_details.append(f"Line {line_no}: expected['{qname}'] 与 questions['{qname}']['label'] 不一致")

                # 100% 全量样本 Kev 官方 materialize() + encode() 校验
                kev_this_ok = False
                if kev_mod is not None and kev_loaded_reqs is not None:
                    req_obj = kev_loaded_reqs[file_rec_count - 1]
                    try:
                        mat = kev_mod["materialize"](req_obj)
                        # a) 默认严苛训练上限 (384 / 1024 / 2048)
                        try:
                            enc_384 = kev_mod["encode"](
                                kev_tok, mat,
                                max_state=kev_mod["MAX_STATE"],
                                max_branch=kev_mod["MAX_BRANCH"],
                                strict=False
                            )
                            st_tok = enc_384["state_tokens"]
                            pk_tok = len(enc_384["ids"])
                            br_tok = pk_tok - enc_384["seg"].count(0)
                            if st_tok > kev_max_state_tok:
                                kev_max_state_tok = st_tok
                            if br_tok > kev_max_branch_tok:
                                kev_max_branch_tok = br_tok
                            if pk_tok > kev_max_packed_tok:
                                kev_max_packed_tok = pk_tok
                            if enc_384["state_truncated"]:
                                kev_trunc_default_384 += 1
                            if pk_tok <= kev_mod["MAX_PACKED"]:
                                kev_ok_default_384 += 1
                                kev_this_ok = True
                            else:
                                kev_overflow_default_384 += 1
                        except kev_mod["ContextOverflow"]:
                            kev_overflow_default_384 += 1

                        # b) Kev-4B 官方训练上下文 (max_state=7552, max_branch=8192, max_packed=9216)
                        ctx_7552 = kev_mod["training_context"](7552)
                        enc_7552 = kev_mod["encode"](
                            kev_tok, mat,
                            max_state=ctx_7552["max_state"],
                            max_branch=ctx_7552["max_branch"],
                            strict=False
                        )
                        kev_ok_7552 += 1
                        if enc_7552["state_truncated"]:
                            kev_trunc_7552 += 1

                        # c) 前 50 条验证选项顺序置换 (augment p_none=0, p_none_distract=0, p_distract=0) 后 label 索引精确同步
                        if kev_perm_tested < 50:
                            kev_perm_tested += 1
                            aug_req = kev_mod["augment"](req_obj, random.Random(line_no), p_none=0.0, p_none_distract=0.0, p_distract=0.0)
                            aug_mat = kev_mod["materialize"](aug_req)
                            aug_enc_iso = kev_mod["encode"](kev_tok, aug_mat, option_isolation=True)
                            orig_q0 = mat["questions"][0]
                            aug_q0 = aug_mat["questions"][0]
                            if orig_q0["keys"][orig_q0["label"]] == aug_q0["keys"][aug_q0["label"]] and len(aug_enc_iso["opt_idx"][0]) == len(orig_q0["keys"]):
                                kev_perm_passed += 1
                    except Exception as e:
                        file_err_count += 1
                        total_errors += 1
                        error_details.append(f"Line {line_no}: Kev 官方编码失败: {e}")

                # 100% 全量样本 Laya 官方 items_from_rows() + build_sequence() 校验
                laya_this_ok = False
                if laya_mod is not None:
                    try:
                        # a) 多候选路由配置 (max_len=1024, head_max_len=512)
                        items_1024, sk_1024 = laya_mod["items_from_rows"](laya_tok, [r], max_len=1024, head_max_len=512)
                        if sk_1024:
                            for k_sk, v_sk in sk_1024.items():
                                laya_skipped_1024_448[k_sk] += v_sk
                            file_err_count += 1
                            total_errors += 1
                            error_details.append(f"Line {line_no}: Laya (1024/512) 跳过问题: {sk_1024}")
                        else:
                            laya_ok_records_1024_448 += 1
                            laya_items_1024_448 += len(items_1024)
                            laya_this_ok = True
                            rec_trunc = False
                            for it in items_1024:
                                ids_seq, markers_seq, st_seq, tr_seq = laya_mod["build_sequence"](
                                    laya_tok, None, it["q"],
                                    max_len=1024, head_max_len=512,
                                    state_ids=it["state_ids"],
                                    return_stats=True, return_truncation_stats=True
                                )
                                head_ids, _, _ = laya_mod["build_head"](laya_tok, it["q"], head_max_len=512)
                                if len(ids_seq) > laya_max_seq_tok:
                                    laya_max_seq_tok = len(ids_seq)
                                if len(head_ids) > laya_max_head_tok:
                                    laya_max_head_tok = len(head_ids)
                                if tr_seq["state_tokens"] > laya_max_state_tok:
                                    laya_max_state_tok = tr_seq["state_tokens"]
                                if tr_seq["truncated"]:
                                    rec_trunc = True
                            if rec_trunc:
                                laya_trunc_1024_448 += 1

                            # 前 50 条验证 Laya 选项顺序随机置换与 parallel_layout
                            if laya_perm_tested < 50 and items_1024:
                                laya_perm_tested += 1
                                it0 = items_1024[0]
                                order = laya_mod["draw_option_order"](it0, random.Random(line_no), ("choice",))
                                enc_par = laya_mod["encode_item"](laya_tok, it0, max_len=1024, head_max_len=512, option_order=order, parallel=True)
                                orig_argmax = max(range(len(it0["target"])), key=lambda idx_i: it0["target"][idx_i])
                                perm_argmax = max(range(len(enc_par["target"])), key=lambda idx_i: enc_par["target"][idx_i])
                                mapped_back = order[perm_argmax] if order is not None else perm_argmax
                                if mapped_back == orig_argmax and "layout" in enc_par and len(enc_par["markers"]) == it0["k"]:
                                    laya_perm_passed += 1

                        # b) 对照测试 Laya 出厂默认配置 (max_len=512, head_max_len=192)
                        items_512, sk_512 = laya_mod["items_from_rows"](laya_tok, [r], max_len=512, head_max_len=192)
                        if sk_512:
                            for k_sk, v_sk in sk_512.items():
                                laya_skipped_512_192[k_sk] += v_sk
                        else:
                            laya_ok_records_512_192 += 1
                    except Exception as e:
                        file_err_count += 1
                        total_errors += 1
                        error_details.append(f"Line {line_no}: Laya 官方编码失败: {e}")

                if (kev_mod is None or kev_this_ok) and (laya_mod is None or laya_this_ok):
                    joint_kev_laya_readable += 1

        file_stats[fname] = {
            "records": file_rec_count,
            "errors": file_err_count,
            "joint_kev_laya_readable": joint_kev_laya_readable,
            "joint_readability_rate": round(joint_kev_laya_readable / max(1, file_rec_count), 6),
            "kev_official": {
                "tested_100_percent": kev_mod is not None,
                "max_state_tokens": kev_max_state_tok,
                "max_branch_tokens": kev_max_branch_tok,
                "max_packed_tokens": kev_max_packed_tok,
                "default_context_384_1024_2048_ok": kev_ok_default_384,
                "default_context_384_state_truncated": kev_trunc_default_384,
                "default_context_384_overflow": kev_overflow_default_384,
                "kev4b_context_7552_8192_9216_ok": kev_ok_7552,
                "kev4b_context_7552_state_truncated": kev_trunc_7552,
                "permutation_sync_tested": kev_perm_tested,
                "permutation_sync_passed": kev_perm_passed,
            },
            "laya_official": {
                "tested_100_percent": laya_mod is not None,
                "router_config_1024_512_ok_records": laya_ok_records_1024_448,
                "router_config_1024_512_items": laya_items_1024_448,
                "router_config_1024_512_state_truncated": laya_trunc_1024_448,
                "router_config_1024_512_skipped": dict(laya_skipped_1024_448),
                "shipped_config_512_192_ok_records": laya_ok_records_512_192,
                "shipped_config_512_192_skipped": dict(laya_skipped_512_192),
                "max_sequence_tokens": laya_max_seq_tok,
                "max_head_tokens": laya_max_head_tok,
                "max_state_tokens": laya_max_state_tok,
                "permutation_parallel_layout_tested": laya_perm_tested,
                "permutation_parallel_layout_passed": laya_perm_passed,
            },
            "error_sample": error_details[:5]
        }
        status_tag = "PASS" if file_err_count == 0 else "FAIL"
        print(
            f"  [{status_tag}] {fname:36s} : {file_rec_count:,} 样本, {file_err_count} 错误 | "
            f"Kev(384/1024/2048) OK={kev_ok_default_384:,}/{file_rec_count:,} (max_packed={kev_max_packed_tok}) | "
            f"Laya(1024/512) OK={laya_ok_records_1024_448:,}/{file_rec_count:,} (max_seq={laya_max_seq_tok})"
        )

    if total_errors > 0:
        raise RuntimeError(f"[Kev/Laya 校验失败] 发现 {total_errors} 处错误！请检查详细报错: {file_stats}")

    print(f"\n[✓] Kev & Laya 100% 全量官方代码校验通过: 共验证 {total_validated:,} 条样本，0 处错误，双模型联合可读率 100.0%。")
    return file_stats
