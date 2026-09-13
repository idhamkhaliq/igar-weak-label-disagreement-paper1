# ============================================================
# EXACT CELL 60A–60E ARCHIVAL EXTRACT
# Source notebook:
# /content/drive/MyDrive/Colab Notebooks/Paper1_Phase1_RUN.ipynb
# Notebook SHA256: b8cdc2ec148ca65dc90e5124776fcf05a385a4d930eb1fb0a245c1d1f059340f
# DO NOT EDIT FOR REPRODUCTION
# ============================================================


# ============================================================
# CELL 60A
# Notebook cell index: 63
# Section SHA256: 2ac121dbecfda1db2d69d6ffcb641364055dacae06bbac59a98f4dda586351b4
# ============================================================

# [PHASE3][RQ4 RECOVERY] CELL 60A
# EXACT DETERMINISTIC REPRODUCTION ENGINE
#
# ONLY for the four missing scientific runs:
#   seed_123_ModelR
#   seed_123_ModelV
#   seed_2026_ModelR
#   seed_2026_ModelV
#
# Properties:
# - same frozen protocol
# - same paired initialization
# - same sample order
# - same eager attention
# - strict determinism
# - same FP16 overflow-retry semantics
# - checkpoints 2000/4000/6000 are RETAINED
# - final model accepted ONLY if SHA-256 exactly matches
#   the original Cell-58 scientific model
#
# NO TEST INFERENCE.
# ============================================================

import os
import gc
import json
import time
import random
import shutil
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import torch


# ============================================================
# 1. ORIGINAL SCIENTIFIC RESULTS TO REPRODUCE EXACTLY
# ============================================================

EXPECTED_REPRO = {

    "seed_123_ModelR": {

        "final_sha256":
            "53da37dcbd5ca2ada3d707890c9d839e93b9133c2d684bbad3bccd8a2e5d4c84",

        "overflow_step":
            6005,

        "scale_before":
            524288.0,

        "scale_after":
            262144.0,
    },

    "seed_123_ModelV": {

        "final_sha256":
            "7be38e2def25d35408024f3156f0c662614657d527d02241882b30c5e2472e88",

        "overflow_step":
            6564,

        "scale_before":
            524288.0,

        "scale_after":
            262144.0,
    },

    "seed_2026_ModelR": {

        "final_sha256":
            "130d4bdc1e77312b4d65fb2719791121f07a00a4fb47602fe307aa2577864754",

        "overflow_step":
            6171,

        "scale_before":
            524288.0,

        "scale_after":
            262144.0,
    },

    "seed_2026_ModelV": {

        "final_sha256":
            "92ed977edc8b977e291a8707d2a1aa85781ad68f0746c7c7522b18278855b86c",

        "overflow_step":
            6280,

        "scale_before":
            524288.0,

        "scale_after":
            262144.0,
    },
}


MISSING_RUN_NAMES = list(
    EXPECTED_REPRO.keys()
)

OVERFLOW_POLICY_ID = "61ec4762487c"


# ============================================================
# 2. REPRODUCTION STORAGE
#
# Separate from original run directories until the final
# model passes the original SHA-256 acceptance gate.
# ============================================================

REPRO_ROOT = (
    RQ4_FINAL_ROOT
    /
    "exact_reproduction"
)

REPRO_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 3. SAFETY: TWO SEED-42 MODELS MUST REMAIN VALID
# ============================================================

for protected_run in [
    "seed_42_ModelR",
    "seed_42_ModelV",
]:

    protected_config = next(

        x
        for x in FINAL_RUN_CONFIGS
        if x["run_name"] == protected_run
    )

    assert completed_run_is_valid(
        protected_config
    ), (
        f"Protected recovered model invalid: {protected_run}"
    )


print("✓ Both seed-42 final scientific models remain valid.")


# ============================================================
# 4. JSON FSYNC HELPER
# ============================================================

def write_json_fsync(
    obj,
    path,
):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            obj,
            f,
            indent=2
        )

        f.flush()

        os.fsync(
            f.fileno()
        )


# ============================================================
# 5. DIRECT FILE COPY
#
# No os.replace() for large final model files.
# ============================================================

def direct_copy_fsync(
    source,
    destination,
    chunk_size=16 * 1024 * 1024,
):

    source = Path(source)
    destination = Path(destination)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if destination.exists():
        destination.unlink()

    total = source.stat().st_size
    copied = 0

    with open(
        source,
        "rb"
    ) as src, open(
        destination,
        "wb"
    ) as dst:

        while True:

            chunk = src.read(
                chunk_size
            )

            if not chunk:
                break

            dst.write(chunk)

            copied += len(chunk)

        dst.flush()

        os.fsync(
            dst.fileno()
        )

    assert copied == total

    return destination


# ============================================================
# 6. REPRO CONFIG
# ============================================================

def make_repro_config(
    run_name
):

    original = next(

        x
        for x in FINAL_RUN_CONFIGS

        if x[
            "run_name"
        ]
        ==
        run_name
    )


    repro_run_root = (
        REPRO_ROOT
        /
        run_name
    )

    repro_checkpoint_root = (
        repro_run_root
        /
        "checkpoints"
    )

    repro_run_root.mkdir(
        parents=True,
        exist_ok=True
    )

    repro_checkpoint_root.mkdir(
        parents=True,
        exist_ok=True
    )


    repro = dict(
        original
    )

    # Important:
    # scientific run_id remains the ORIGINAL run_id.
    repro[
        "run_root"
    ] = str(
        repro_run_root
    )

    repro[
        "checkpoint_root"
    ] = str(
        repro_checkpoint_root
    )

    repro[
        "final_model_dir"
    ] = str(
        repro_run_root
        /
        "candidate_final_model"
    )

    return repro, original


# ============================================================
# 7. REPRO CHECKPOINT SAVE
#
# Unlike Cell 58:
# NEVER deletes earlier valid checkpoints.
# ============================================================

def save_repro_checkpoint(
    run_config,
    global_step,
    model,
    optimizer,
    scheduler,
    scaler,
    history,
    examples_seen_total,
    cumulative_training_seconds,
):

    checkpoint_dir = (

        Path(
            run_config[
                "checkpoint_root"
            ]
        )

        /

        f"checkpoint_step_{int(global_step):06d}"
    )


    if checkpoint_is_valid(
        checkpoint_dir,
        run_config,
    ):

        return checkpoint_dir


    # Remove only an incomplete checkpoint at THIS exact step.
    if checkpoint_dir.exists():

        shutil.rmtree(
            checkpoint_dir
        )


    checkpoint_dir.mkdir(
        parents=True,
        exist_ok=False
    )


    # --------------------------------------------------------
    # Model state
    # --------------------------------------------------------

    model.save_pretrained(

        checkpoint_dir,

        safe_serialization=True,
    )


    # --------------------------------------------------------
    # Full exact recovery state
    # --------------------------------------------------------

    recovery_state = {

        "run_id":
            run_config[
                "run_id"
            ],

        "final_rq4_protocol_id":
            FINAL_RQ4_PROTOCOL_ID,

        "global_step":
            int(
                global_step
            ),

        "examples_seen_total":
            int(
                examples_seen_total
            ),

        "cumulative_training_seconds":
            float(
                cumulative_training_seconds
            ),

        "classifier_init_hash":
            run_config[
                "expected_classifier_init_hash"
            ],

        "optimizer_state":
            optimizer.state_dict(),

        "scheduler_state":
            scheduler.state_dict(),

        "scaler_state":
            scaler.state_dict(),

        "python_rng":
            random.getstate(),

        "numpy_rng":
            np.random.get_state(),

        "torch_rng":
            torch.get_rng_state(),

        "cuda_rng":
            torch.cuda.get_rng_state_all(),

        "history":
            history,
    }


    torch.save(

        recovery_state,

        checkpoint_dir
        /
        "training_state.pt",
    )


    checkpoint_meta = {

        "status":
            "VALID",

        "run_id":
            run_config[
                "run_id"
            ],

        "run_name":
            run_config[
                "run_name"
            ],

        "final_rq4_protocol_id":
            FINAL_RQ4_PROTOCOL_ID,

        "global_step":
            int(
                global_step
            ),

        "created_at":
            datetime.datetime.now()
            .isoformat(),
    }


    # Meta written LAST.
    write_json_fsync(

        checkpoint_meta,

        checkpoint_dir
        /
        "checkpoint_meta.json",
    )


    assert checkpoint_is_valid(
        checkpoint_dir,
        run_config,
    )


    print(
        "✓ DURABLE checkpoint retained:",
        checkpoint_dir
    )


    return checkpoint_dir


# ============================================================
# 8. RNG SNAPSHOT
# ============================================================

def capture_repro_rng():

    return {

        "python":
            random.getstate(),

        "numpy":
            np.random.get_state(),

        "torch":
            torch.get_rng_state(),

        "cuda":
            torch.cuda.get_rng_state_all(),
    }


def restore_repro_rng(
    state
):

    random.setstate(
        state[
            "python"
        ]
    )

    np.random.set_state(
        state[
            "numpy"
        ]
    )

    torch.set_rng_state(
        state[
            "torch"
        ]
    )

    torch.cuda.set_rng_state_all(
        state[
            "cuda"
        ]
    )


# ============================================================
# 9. OVERFLOW EVENT ARTIFACT
# ============================================================

def save_repro_overflow_event(
    run_config,
    global_step,
    retry_number,
    scale_before,
    scale_after,
    epoch_idx,
    step_within_epoch,
):

    event_dir = (

        Path(
            run_config[
                "run_root"
            ]
        )

        /
        "overflow_events"
    )

    event_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    attempted_step = (
        int(
            global_step
        )
        +
        1
    )


    event = {

        "status":
            "FP16_OVERFLOW_RETRY",

        "final_rq4_protocol_id":
            FINAL_RQ4_PROTOCOL_ID,

        "overflow_policy_id":
            OVERFLOW_POLICY_ID,

        "run_id":
            run_config[
                "run_id"
            ],

        "run_name":
            run_config[
                "run_name"
            ],

        "completed_global_step_before_attempt":
            int(
                global_step
            ),

        "attempted_optimizer_step":
            attempted_step,

        "epoch":
            int(
                epoch_idx
                +
                1
            ),

        "optimizer_step_within_epoch":
            int(
                step_within_epoch
                +
                1
            ),

        "retry_number":
            int(
                retry_number
            ),

        "scale_before":
            float(
                scale_before
            ),

        "scale_after":
            float(
                scale_after
            ),

        "optimizer_update_counted":
            False,

        "scheduler_advanced":
            False,

        "scientific_examples_counted":
            False,

        "same_batch_will_be_retried":
            True,

        "rng_restored":
            True,

        "created_at":
            datetime.datetime.now()
            .isoformat(),
    }


    event_file = (

        event_dir

        /

        (
            f"overflow_step_{attempted_step:06d}"
            f"_retry_{int(retry_number):02d}.json"
        )
    )


    write_json_fsync(
        event,
        event_file
    )


    return event


# ============================================================
# 10. EXACT REPRODUCTION FUNCTION
# ============================================================

def reproduce_exact_run(
    run_name
):

    assert run_name in EXPECTED_REPRO


    expected = (
        EXPECTED_REPRO[
            run_name
        ]
    )


    (
        repro_config,
        original_config,
    ) = make_repro_config(
        run_name
    )


    print(
        "\n"
        +
        "=" * 110
    )

    print(
        "EXACT SCIENTIFIC REPRODUCTION:",
        run_name
    )

    print(
        "=" * 110
    )

    print(
        "Expected final SHA:"
    )

    print(
        expected[
            "final_sha256"
        ]
    )

    print(
        "Expected overflow:",
        expected[
            "overflow_step"
        ],
        "|",
        int(
            expected[
                "scale_before"
            ]
        ),
        "->",
        int(
            expected[
                "scale_after"
            ]
        ),
    )


    # ========================================================
    # A. Never overwrite a valid recovered final model
    # ========================================================

    canonical_final_model = (

        Path(
            original_config[
                "final_model_dir"
            ]
        )

        /
        "model.safetensors"
    )


    if canonical_final_model.exists():

        observed = sha256_file(
            canonical_final_model
        )

        if (
            observed
            ==
            expected[
                "final_sha256"
            ]
        ):

            print(
                "\n✓ Original scientific model already exists."
            )

            print(
                "✓ Exact SHA verified; reproduction unnecessary."
            )

            return {
                "status":
                    "ALREADY_RECOVERED",
                "run_name":
                    run_name,
                "sha256":
                    observed,
            }

        raise RuntimeError(
            "A canonical model exists but its SHA does "
            "not match the original scientific result."
        )


    # ========================================================
    # B. Fresh or resume from reproduction checkpoint
    # ========================================================

    torch.cuda.empty_cache()
    gc.collect()


    state = initialize_or_resume_run(
        repro_config
    )


    model = state[
        "model"
    ]

    optimizer = state[
        "optimizer"
    ]

    scheduler = state[
        "scheduler"
    ]

    scaler = state[
        "scaler"
    ]

    global_step = int(
        state[
            "global_step"
        ]
    )

    examples_seen_total = int(
        state[
            "examples_seen_total"
        ]
    )

    cumulative_training_seconds = float(
        state[
            "cumulative_training_seconds"
        ]
    )

    history = list(
        state[
            "history"
        ]
    )


    if state[
        "resumed"
    ]:

        print(
            "\n✓ RESUMING exact reproduction"
        )

        print(
            "Starting step:",
            global_step
        )

        print(
            "From:",
            state[
                "resumed_from"
            ]
        )

    else:

        print(
            "\n✓ Fresh original paired initialization verified."
        )

        print(
            "Starting step: 0"
        )


    model.train()

    segment_start = (
        time.perf_counter()
    )


    # ========================================================
    # C. Successful optimizer update loop
    # ========================================================

    while (
        global_step
        <
        TOTAL_OPTIMIZER_STEPS
    ):

        epoch_idx = (

            global_step
            //
            OPTIMIZER_STEPS_PER_EPOCH
        )

        step_within_epoch = (

            global_step
            %
            OPTIMIZER_STEPS_PER_EPOCH
        )


        permutation = (
            ORDER_CACHE[
                repro_config[
                    "seed"
                ]
            ][
                epoch_idx
            ]
        )


        micro_start = (

            step_within_epoch
            *
            RQ4_GRAD_ACCUM
        )


        micro_end = min(

            micro_start
            +
            RQ4_GRAD_ACCUM,

            N_MICROBATCHES_PER_EPOCH,
        )


        actual_micro_count = (

            micro_end
            -
            micro_start
        )


        assert actual_micro_count in [
            1,
            2,
        ]


        retry_number = 0


        # ====================================================
        # Same optimizer step until one successful update
        # ====================================================

        while True:

            rng_before_attempt = (
                capture_repro_rng()
            )


            optimizer.zero_grad(
                set_to_none=True
            )


            micro_losses = []

            optimizer_step_examples = 0


            for micro_idx in range(
                micro_start,
                micro_end,
            ):

                row_start = (

                    micro_idx
                    *
                    RQ4_PHYSICAL_BATCH
                )


                row_end = min(

                    row_start
                    +
                    RQ4_PHYSICAL_BATCH,

                    len(
                        train_final
                    ),
                )


                batch_indices = (
                    permutation[
                        row_start:row_end
                    ]
                )


                batch = build_rq4_batch(

                    train_final,

                    batch_indices,

                    repro_config[
                        "target_column"
                    ],
                )


                batch_n = int(
                    batch[
                        "labels"
                    ].shape[0]
                )


                optimizer_step_examples += (
                    batch_n
                )


                batch = {

                    key:
                        value.to(
                            "cuda",
                            non_blocking=True
                        )

                    for key, value
                    in batch.items()
                }


                with torch.autocast(

                    device_type="cuda",

                    dtype=torch.float16,

                    enabled=True,
                ):

                    outputs = model(
                        **batch
                    )

                    raw_loss = (
                        outputs.loss
                    )


                    if not torch.isfinite(
                        raw_loss
                    ).item():

                        raise RuntimeError(
                            "Non-finite raw loss."
                        )


                    scaled_loss = (

                        raw_loss
                        /
                        actual_micro_count
                    )


                scaler.scale(
                    scaled_loss
                ).backward()


                micro_losses.append(

                    float(
                        raw_loss
                        .detach()
                        .float()
                        .cpu()
                    )
                )


                del outputs
                del raw_loss
                del scaled_loss
                del batch


            scale_before = float(
                scaler.get_scale()
            )


            scaler.step(
                optimizer
            )

            scaler.update()


            scale_after = float(
                scaler.get_scale()
            )


            # =================================================
            # FP16 overflow
            # =================================================

            if (
                scale_after
                <
                scale_before
            ):

                retry_number += 1


                event = save_repro_overflow_event(

                    run_config=
                        repro_config,

                    global_step=
                        global_step,

                    retry_number=
                        retry_number,

                    scale_before=
                        scale_before,

                    scale_after=
                        scale_after,

                    epoch_idx=
                        epoch_idx,

                    step_within_epoch=
                        step_within_epoch,
                )


                # HARD trajectory gate immediately.
                assert (
                    event[
                        "attempted_optimizer_step"
                    ]
                    ==
                    expected[
                        "overflow_step"
                    ]
                ), (
                    "Overflow occurred at a different "
                    "optimizer step than the original run."
                )


                assert (
                    scale_before
                    ==
                    expected[
                        "scale_before"
                    ]
                )


                assert (
                    scale_after
                    ==
                    expected[
                        "scale_after"
                    ]
                )


                restore_repro_rng(
                    rng_before_attempt
                )


                optimizer.zero_grad(
                    set_to_none=True
                )


                print(
                    f"\n✓ EXPECTED FP16 overflow | "
                    f"step {global_step + 1:,} | "
                    f"{scale_before:.0f} -> "
                    f"{scale_after:.0f} | "
                    f"retry {retry_number}"
                )


                assert retry_number <= 8

                continue


            break


        # ====================================================
        # Successful update
        # ====================================================

        scheduler.step()

        global_step += 1

        examples_seen_total += (
            optimizer_step_examples
        )


        step_loss = float(
            np.mean(
                micro_losses
            )
        )


        history.append({

            "global_step":
                int(
                    global_step
                ),

            "epoch":
                int(
                    epoch_idx
                    +
                    1
                ),

            "optimizer_step_within_epoch":
                int(
                    step_within_epoch
                    +
                    1
                ),

            "microbatches":
                int(
                    actual_micro_count
                ),

            "examples":
                int(
                    optimizer_step_examples
                ),

            "loss":
                step_loss,

            "learning_rate":
                float(
                    scheduler.get_last_lr()[
                        0
                    ]
                ),

            "grad_scale_after_success":
                float(
                    scaler.get_scale()
                ),

            "overflow_retries_before_success":
                int(
                    retry_number
                ),
        })


        # ====================================================
        # Progress
        # ====================================================

        if (

            global_step
            %
            250
            ==
            0

            or

            global_step
            ==
            TOTAL_OPTIMIZER_STEPS
        ):

            print(

                f"{run_name} | "
                f"step {global_step:,}/"
                f"{TOTAL_OPTIMIZER_STEPS:,} | "
                f"epoch {epoch_idx+1}/2 | "
                f"loss={step_loss:.4f}"
            )


        # ====================================================
        # Permanent reproduction checkpoint
        # ====================================================

        if global_step in [
            2000,
            4000,
            6000,
        ]:

            torch.cuda.synchronize()


            now = (
                time.perf_counter()
            )


            cumulative_training_seconds += (

                now
                -
                segment_start
            )


            save_repro_checkpoint(

                run_config=
                    repro_config,

                global_step=
                    global_step,

                model=
                    model,

                optimizer=
                    optimizer,

                scheduler=
                    scheduler,

                scaler=
                    scaler,

                history=
                    history,

                examples_seen_total=
                    examples_seen_total,

                cumulative_training_seconds=
                    cumulative_training_seconds,
            )


            segment_start = (
                time.perf_counter()
            )


    # ========================================================
    # D. Exact final budget
    # ========================================================

    torch.cuda.synchronize()


    cumulative_training_seconds += (

        time.perf_counter()
        -
        segment_start
    )


    assert global_step == 6564

    assert examples_seen_total == 210000


    partial_steps = [

        x
        for x in history

        if x[
            "microbatches"
        ]
        ==
        1
    ]


    assert len(
        partial_steps
    ) == 2


    # ========================================================
    # E. Overflow trajectory audit
    # ========================================================

    overflow_event_dir = (

        Path(
            repro_config[
                "run_root"
            ]
        )

        /
        "overflow_events"
    )


    overflow_files = sorted(

        overflow_event_dir.glob(
            "overflow_step_*_retry_*.json"
        )
    )


    assert len(
        overflow_files
    ) == 1


    with open(
        overflow_files[0],
        encoding="utf-8"
    ) as f:

        final_overflow_event = json.load(f)


    assert (
        final_overflow_event[
            "attempted_optimizer_step"
        ]
        ==
        expected[
            "overflow_step"
        ]
    )


    print(
        "\n✓ Original overflow trajectory reproduced exactly."
    )


    # ========================================================
    # F. SAVE LOCALLY FIRST — SCIENTIFIC ACCEPTANCE GATE
    # ========================================================

    local_root = Path(
        "/content/rq4_exact_candidates"
    )

    local_root.mkdir(
        parents=True,
        exist_ok=True
    )


    local_candidate = (

        local_root
        /
        run_name
    )


    if local_candidate.exists():

        shutil.rmtree(
            local_candidate
        )


    model.save_pretrained(

        local_candidate,

        safe_serialization=True,
    )


    local_model_file = (

        local_candidate
        /
        "model.safetensors"
    )


    assert local_model_file.exists()


    observed_final_sha = (
        sha256_file(
            local_model_file
        )
    )


    print(
        "\nExpected original SHA:"
    )

    print(
        expected[
            "final_sha256"
        ]
    )

    print(
        "\nReproduced SHA:"
    )

    print(
        observed_final_sha
    )


    # ========================================================
    # HARD SCIENTIFIC ACCEPTANCE
    # ========================================================

    assert (
        observed_final_sha
        ==
        expected[
            "final_sha256"
        ]
    ), (
        "FINAL MODEL HASH MISMATCH. "
        "Do not promote this reproduction."
    )


    print(
        "\n✓ EXACT FINAL MODEL SHA-256 MATCH."
    )

    print(
        "✓ Scientific model reproduced byte-for-byte."
    )


    # ========================================================
    # G. VALIDATION DIAGNOSTIC
    # ========================================================

    print(
        "\nRunning validation diagnostic..."
    )


    validation_metrics = evaluate_validation(

        model,

        repro_config[
            "target_column"
        ],
    )


    print(
        "Validation Macro-F1:",
        f"{validation_metrics['macro_f1']:.4f}"
    )

    print(
        "Validation accuracy:",
        f"{validation_metrics['accuracy']:.4f}"
    )


    # ========================================================
    # H. PROMOTE TO CANONICAL RUN
    #
    # Direct file write, not large-file os.replace().
    # ========================================================

    canonical_final_dir = Path(

        original_config[
            "final_model_dir"
        ]
    )


    canonical_final_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    canonical_model_file = (

        canonical_final_dir
        /
        "model.safetensors"
    )


    canonical_config_file = (

        canonical_final_dir
        /
        "config.json"
    )


    direct_copy_fsync(

        local_candidate
        /
        "model.safetensors",

        canonical_model_file,
    )


    direct_copy_fsync(

        local_candidate
        /
        "config.json",

        canonical_config_file,
    )


    os.sync()


    # Hard verification from Drive filesystem.
    canonical_sha = sha256_file(
        canonical_model_file
    )


    assert (
        canonical_sha
        ==
        expected[
            "final_sha256"
        ]
    )


    print(
        "\n✓ Canonical Drive model verified."
    )


    # ========================================================
    # I. SAVE REPRODUCTION TRAINING HISTORY
    # ========================================================

    history_file = (

        Path(
            repro_config[
                "run_root"
            ]
        )

        /
        "training_history.csv"
    )


    pd.DataFrame(
        history
    ).to_csv(
        history_file,
        index=False
    )


    # Validation CM
    cm = np.asarray(
        validation_metrics[
            "confusion_matrix"
        ]
    )


    cm_file = (

        Path(
            repro_config[
                "run_root"
            ]
        )

        /
        "validation_confusion_matrix.csv"
    )


    pd.DataFrame(

        cm,

        index=[
            "true_negative",
            "true_neutral",
            "true_positive",
        ],

        columns=[
            "pred_negative",
            "pred_neutral",
            "pred_positive",
        ],

    ).to_csv(
        cm_file
    )


    # ========================================================
    # J. RECONSTRUCT COMPATIBLE COMPLETION MANIFEST
    # ========================================================

    canonical_run_root = Path(

        original_config[
            "run_root"
        ]
    )


    completion_file = (

        canonical_run_root
        /
        "RUN_COMPLETE.json"
    )


    completion = {

        "status":
            "COMPLETE",

        "artifact_recovery_mode":
            "DETERMINISTIC_REPRODUCTION_EXACT_HASH",

        "original_scientific_training_completed":
            True,

        "reproduction_exact_hash_verified":
            True,

        "run_id":
            original_config[
                "run_id"
            ],

        "run_name":
            run_name,

        "final_rq4_protocol_id":
            FINAL_RQ4_PROTOCOL_ID,

        "overflow_policy_id":
            OVERFLOW_POLICY_ID,

        "seed":
            original_config[
                "seed"
            ],

        "model_tag":
            original_config[
                "model_tag"
            ],

        "target_column":
            original_config[
                "target_column"
            ],

        "classifier_init_hash":
            original_config[
                "expected_classifier_init_hash"
            ],

        "attention_implementation":
            "eager",

        "strict_determinism":
            True,

        "epochs":
            2,

        "optimizer_steps_per_epoch":
            3282,

        "final_global_step":
            6564,

        "training_examples_seen":
            210000,

        "partial_accumulation_steps":
            2,

        "fp16_overflow_events":
            1,

        "fp16_overflow_successfully_retried":
            True,

        "overflow_events_directory":
            str(
                overflow_event_dir
            ),

        "training_seconds":
            float(
                cumulative_training_seconds
            ),

        "training_reviews_per_second":
            float(
                210000
                /
                cumulative_training_seconds
            ),

        "peak_allocated_gb":
            float(
                torch.cuda
                .max_memory_allocated()
                /
                (1024 ** 3)
            ),

        "peak_reserved_gb":
            float(
                torch.cuda
                .max_memory_reserved()
                /
                (1024 ** 3)
            ),

        "validation":
            validation_metrics,

        "test_evaluated":
            False,

        "final_model_dir":
            str(
                canonical_final_dir
            ),

        "model_safetensors_sha256":
            canonical_sha,

        "config_sha256":
            sha256_file(
                canonical_config_file
            ),

        "training_history":
            str(
                history_file
            ),

        "reproduction_checkpoint_root":
            str(
                repro_config[
                    "checkpoint_root"
                ]
            ),

        "checkpoints_retained":
            True,

        "completed_at":
            datetime.datetime.now()
            .isoformat(),
    }


    write_json_fsync(
        completion,
        completion_file
    )


    # ========================================================
    # K. ORIGINAL VALIDATOR MUST PASS
    # ========================================================

    assert completed_run_is_valid(
        original_config
    )


    # ========================================================
    # L. RECOVERY AUDIT
    # ========================================================

    audit_file = (

        Path(
            repro_config[
                "run_root"
            ]
        )

        /
        "EXACT_REPRODUCTION_PASS.json"
    )


    audit = {

        "status":
            "PASS",

        "run_name":
            run_name,

        "final_rq4_protocol_id":
            FINAL_RQ4_PROTOCOL_ID,

        "expected_original_sha256":
            expected[
                "final_sha256"
            ],

        "reproduced_local_sha256":
            observed_final_sha,

        "canonical_drive_sha256":
            canonical_sha,

        "exact_hash_match":
            True,

        "expected_overflow_step":
            expected[
                "overflow_step"
            ],

        "observed_overflow_step":
            final_overflow_event[
                "attempted_optimizer_step"
            ],

        "overflow_trajectory_match":
            True,

        "successful_optimizer_steps":
            6564,

        "scientific_examples":
            210000,

        "checkpoints_retained":
            [
                2000,
                4000,
                6000,
            ],

        "test_accessed":
            False,

        "created_at":
            datetime.datetime.now()
            .isoformat(),
    }


    write_json_fsync(
        audit,
        audit_file
    )


    print(
        "\n"
        +
        "=" * 110
    )

    print(
        "✓ EXACT REPRODUCTION PASS —",
        run_name
    )

    print(
        "=" * 110
    )

    print(
        "\nFinal steps:",
        6564
    )

    print(
        "Scientific examples:",
        210000
    )

    print(
        "Overflow step:",
        final_overflow_event[
            "attempted_optimizer_step"
        ]
    )

    print(
        "Expected SHA:"
    )

    print(
        expected[
            "final_sha256"
        ]
    )

    print(
        "Canonical Drive SHA:"
    )

    print(
        canonical_sha
    )

    print(
        "\nEXACT HASH MATCH:",
        True
    )

    print(
        "Original completion validator:",
        True
    )

    print(
        "Checkpoints retained:",
        "2000 / 4000 / 6000"
    )

    print(
        "Test accessed:",
        False
    )


    del model
    del optimizer
    del scheduler
    del scaler

    torch.cuda.empty_cache()
    gc.collect()


    return completion


print(
    "=" * 110
)

print(


# ============================================================
# CELL 60B
# Notebook cell index: 64
# Section SHA256: ddd0a5b0ecbde4793ee728620a6bba7745f52e13f7502f2ac66f47bcefefb445
# ============================================================

# CELL 60B
# EXACT REPRODUCTION 1/4
# ============================================================

result_123_R = reproduce_exact_run(
    "seed_123_ModelR"
)


# ============================================================
# CELL 60C
# Notebook cell index: 65
# Section SHA256: ef7abd7a49c727a96b2abb485eb961e047a4fa48a54c48590e9f0ae1499fe463
# ============================================================

# CELL 60C
# EXACT REPRODUCTION 2/4
# ============================================================

result_123_V = reproduce_exact_run(
    "seed_123_ModelV"
)


# ============================================================
# CELL 60D
# Notebook cell index: 66
# Section SHA256: 065c4d77375a34c783172a94845702b035999829553ad594ed8d0d5c1406f349
# ============================================================

# CELL 60D
# EXACT REPRODUCTION 3/4

result_2026_R = reproduce_exact_run(
    "seed_2026_ModelR"
)


# ============================================================
# CELL 60E
# Notebook cell index: 67
# Section SHA256: 95cb1e437907d6167707655125062d80f9a0b8483e071332df922d0d8164287a
# ============================================================

# CELL 60E
# EXACT REPRODUCTION 4/4 — FINAL MISSING RUN
# ============================================================

result_2026_V = reproduce_exact_run(
    "seed_2026_ModelV"
)
