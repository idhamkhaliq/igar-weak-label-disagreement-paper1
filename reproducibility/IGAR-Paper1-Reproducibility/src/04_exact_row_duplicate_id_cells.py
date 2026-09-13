# ============================================================
# EXACT row_id / duplicate_group_id SOURCE ARCHIVE
# Notebook: /content/drive/MyDrive/Colab Notebooks/Paper1_Phase1_RUN.ipynb
# Notebook SHA256: b8cdc2ec148ca65dc90e5124776fcf05a385a4d930eb1fb0a245c1d1f059340f
# DO NOT EDIT FOR REPRODUCTION
# ============================================================


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 5
# FULL CELL SHA256: a41a9b7ed17187f4d0dc182c801290c330840511f0942ab95c84431d726dc8fe
# ============================================================

# ============================================================
# [REPRODUCIBILITY] CELL 5 — Atomic writes + artifact validators
# ============================================================

def json_safe_default(obj):
    """
    Convert NumPy/Pandas/Path objects into native JSON-safe types.
    """
    if isinstance(obj, np.generic):
        return obj.item()

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    raise TypeError(
        f"Object of type {type(obj).__name__} "
        "is not JSON serializable"
    )

def atomic_json_save(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with open(
        tmp,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_safe_default
        )

        f.flush()
        os.fsync(f.fileno())

    os.replace(
        tmp,
        path
    )

def atomic_csv_save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)

def atomic_parquet_save(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp.parquet")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)

def valid_json(path):
    path = Path(path)
    if not path.exists():
        return False
    try:
        with open(path, encoding="utf-8") as f:
            json.load(f)
        return True
    except Exception:
        return False

def valid_csv(path, min_rows=1):
    path = Path(path)
    if not path.exists():
        return False
    try:
        x = pd.read_csv(path)
        return len(x) >= min_rows
    except Exception:
        return False

def valid_parquet(path, min_rows=1):
    path = Path(path)
    if not path.exists():
        return False
    try:
        x = pd.read_parquet(path)
        return len(x) >= min_rows
    except Exception:
        return False

def sha256_file(path, chunk_size=1024 * 1024):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            sha.update(b)
    return sha.hexdigest()

STATE_FILE = DIRS["state"] / f"pipeline_state_{PHASE1_ID}.json"

def load_state():
    if valid_json(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    state = {
        "phase1_id": PHASE1_ID,
        "gate1": "pending",
        "gate2": "pending",
        "gate3": "pending",
        "gate4": "pending",
        "rq1": "pending",
        "rq2": "pending",
        "last_update": None,
    }
    atomic_json_save(state, STATE_FILE)
    return state

def set_state(key, value):
    state = load_state()
    state[key] = value
    state["last_update"] = datetime.datetime.now().isoformat()
    atomic_json_save(state, STATE_FILE)

def heartbeat(stage, **kwargs):
    payload = {
        "phase1_id": PHASE1_ID,
        "stage": stage,
        "timestamp": datetime.datetime.now().isoformat(),
        **kwargs,
    }
    atomic_json_save(payload, DIRS["logs"] / f"heartbeat_{PHASE1_ID}.json")

CONFIG_FILE = DIRS["configs"] / f"phase1_config_{PHASE1_ID}.json"
if not valid_json(CONFIG_FILE):
    atomic_json_save(PHASE1_CONFIG, CONFIG_FILE)

print("Utilities ready.")


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 25
# FULL CELL SHA256: fae2edebfa813840d8a743f008a48ddf08e21ec70a77bd2896c958e53e96e0b0
# ============================================================

# ============================================================
# [PHASE2][REPRODUCIBILITY] CELL 23
# Initialize Phase 2 — Gate 5A + RQ3
#
# NO TRANSFORMER
# NO TRAIN/TEST SPLIT
# ============================================================

import re
import unicodedata

PHASE2_NAME = "phase2_gate5a_rq3"
PHASE2_VERSION = "1.0.0"

PHASE2_CONFIG = {

    "phase":
        PHASE2_NAME,

    "version":
        PHASE2_VERSION,

    "source_dataset_sha256":
        current_fp["sha256"],

    "duplicate_definition": (
        "same application + Unicode NFC + "
        "trimmed/collapsed-whitespace content"
    ),

    "rq3_primary_outcome":
        "disagreement",

    "rq3_primary_predictors": [
        "C(score)",
        "log_words",
        "C(app)",
    ],

    "year_role":
        "sensitivity_analysis_only",

    "primary_dataset":
        "row-level eligible reviews",

    "duplicate_sensitivity":
        "one representative per duplicate_group_id",

    "transformer":
        False,
}

PHASE2_ID = hash_dict(
    PHASE2_CONFIG
)

print(
    "Phase-2 ID:",
    PHASE2_ID
)

# ------------------------------------------------------------
# Phase-2 directories
# ------------------------------------------------------------

PHASE2_DIR = (
    PROJECT_ROOT
    / "phase2"
)

PHASE2_DIRS = {

    "data":
        PHASE2_DIR
        / "data",

    "gates":
        PHASE2_DIR
        / "gates",

    "statistics":
        PHASE2_DIR
        / "statistics",

    "tables":
        PHASE2_DIR
        / "tables",

    "figures":
        PHASE2_DIR
        / "figures",

    "logs":
        PHASE2_DIR
        / "logs",

    "configs":
        PHASE2_DIR
        / "configs",

    "state":
        PHASE2_DIR
        / "state",
}

for p in PHASE2_DIRS.values():
    p.mkdir(
        parents=True,
        exist_ok=True
    )

# ------------------------------------------------------------
# Persist configuration
# ------------------------------------------------------------

PHASE2_CONFIG_FILE = (
    PHASE2_DIRS["configs"]
    /
    f"phase2_config_{PHASE2_ID}.json"
)

if not valid_json(
    PHASE2_CONFIG_FILE
):

    atomic_json_save(
        PHASE2_CONFIG,
        PHASE2_CONFIG_FILE
    )


# ------------------------------------------------------------
# Phase-2 state manager
# ------------------------------------------------------------

PHASE2_STATE_FILE = (
    PHASE2_DIRS["state"]
    /
    f"phase2_state_{PHASE2_ID}.json"
)

def load_phase2_state():

    if valid_json(
        PHASE2_STATE_FILE
    ):

        with open(
            PHASE2_STATE_FILE,
            encoding="utf-8"
        ) as f:

            return json.load(f)

    state = {

        "phase2_id":
            PHASE2_ID,

        "alignment":
            "pending",

        "ids":
            "pending",

        "duplicate_audit":
            "pending",

        "features":
            "pending",

        "gate5a":
            "pending",

        "rq3":
            "pending",

        "last_update":
            None,
    }

    atomic_json_save(
        state,
        PHASE2_STATE_FILE
    )

    return state


def set_phase2_state(
    key,
    value
):

    state = load_phase2_state()

    state[key] = value

    state["last_update"] = (
        datetime.datetime.now()
        .isoformat()
    )

    atomic_json_save(
        state,
        PHASE2_STATE_FILE
    )


# ------------------------------------------------------------
# Reload source artifacts from Drive
# ------------------------------------------------------------

RAW_CACHE_PHASE2 = (
    DIRS["cache"]
    / "00_raw_cache.parquet"
)

PHASE1_LABEL_FILE = (
    DIRS["processed"]
    / "01_phase1_labels.parquet"
)

assert valid_parquet(
    RAW_CACHE_PHASE2,
    min_rows=EXPECTED_ROWS
)

assert valid_parquet(
    PHASE1_LABEL_FILE,
    min_rows=EXPECTED_ROWS
)

raw2 = pd.read_parquet(
    RAW_CACHE_PHASE2
)

labels2 = pd.read_parquet(
    PHASE1_LABEL_FILE
)

print(
    "Raw rows:",
    f"{len(raw2):,}"
)

print(
    "Phase-1 label rows:",
    f"{len(labels2):,}"
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 26
# FULL CELL SHA256: 6c53ebc77fcac6acf0fd9aca4c7dcfbece4569bd4245e41e54666a2e4aec5d07
# ============================================================

# ============================================================
# [GATE 5A][REPRODUCIBILITY] CELL 24
# Source alignment + deterministic identifiers
#
# Creates:
# - source_row_number
# - row_id
# - normalized_content
# - duplicate_group_id
#
# IMPORTANT:
# row_id remains stable because:
# raw dataset SHA is frozen +
# source row number belongs to that frozen file.
# ============================================================

PHASE2_BASE_FILE = (
    PHASE2_DIRS["data"]
    / "02_phase2_base.parquet"
)

PHASE2_BASE_META = (
    PHASE2_DIRS["data"]
    / "02_phase2_base.meta.json"
)

base_valid = False

if (
    valid_parquet(
        PHASE2_BASE_FILE,
        min_rows=EXPECTED_ROWS
    )
    and
    valid_json(
        PHASE2_BASE_META
    )
):

    with open(
        PHASE2_BASE_META,
        encoding="utf-8"
    ) as f:

        base_meta = json.load(f)

    base_valid = (

        base_meta.get(
            "phase2_id"
        )
        ==
        PHASE2_ID

        and

        base_meta.get(
            "source_sha256"
        )
        ==
        current_fp["sha256"]

        and

        base_meta.get(
            "rows"
        )
        ==
        EXPECTED_ROWS
    )


if base_valid:

    print(
        "✓ Valid Phase-2 base artifact found."
    )

    phase2 = pd.read_parquet(
        PHASE2_BASE_FILE
    )

else:

    # --------------------------------------------------------
    # Alignment verification BEFORE assigning labels
    # --------------------------------------------------------

    assert (
        len(raw2)
        ==
        len(labels2)
        ==
        EXPECTED_ROWS
    )

    score_alignment = bool(
        np.array_equal(
            raw2["score"].to_numpy(),
            labels2["score"].to_numpy()
        )
    )

    app_alignment = bool(
        np.array_equal(
            raw2["app"]
            .astype(str)
            .to_numpy(),

            labels2["app"]
            .astype(str)
            .to_numpy()
        )
    )

    if not (
        score_alignment
        and
        app_alignment
    ):

        raise RuntimeError(
            "[GATE 5A — NO-GO] "
            "Raw dataset and Phase-1 labels "
            "are not row-aligned."
        )

    print(
        "✓ Raw/Phase-1 alignment verified."
    )

    # --------------------------------------------------------
    # Build Phase-2 analytical base
    # --------------------------------------------------------

    phase2 = raw2[
        [
            "app",
            "content",
            "score",
            "at",
            "appVersion",
        ]
    ].copy()

    # Stable row position in frozen source file
    phase2[
        "source_row_number"
    ] = np.arange(
        len(phase2),
        dtype=np.int64
    )

    # Attach Phase-1 variables only AFTER alignment verification
    for col in [

        "rating_label",
        "vader_label",
        "disagreement",
        "severity",
        "transition_type",

    ]:

        phase2[col] = (
            labels2[col]
            .to_numpy()
        )

    # --------------------------------------------------------
    # Deterministic unique row ID
    #
    # Identity derives from:
    # frozen dataset SHA + original source row number.
    #
    # Reordering dataframe later does NOT alter row_id.
    # --------------------------------------------------------

    dataset_sha = (
        current_fp[
            "sha256"
        ]
    )

    phase2[
        "row_id"
    ] = [

        hashlib.sha256(
            (
                dataset_sha
                +
                "|"
                +
                str(i)
            ).encode(
                "utf-8"
            )
        ).hexdigest()[:32]

        for i in (
            phase2[
                "source_row_number"
            ]
        )
    ]

    # --------------------------------------------------------
    # Duplicate-detection normalization
    #
    # DO NOT use this normalized text as Transformer input.
    # It exists ONLY for duplicate grouping.
    # --------------------------------------------------------

    def normalize_duplicate_text(
        x
    ):

        if pd.isna(x):
            return pd.NA

        x = unicodedata.normalize(
            "NFC",
            str(x)
        )

        x = x.strip()

        x = re.sub(
            r"\\s+",
            " ",
            x
        )

        if x == "":
            return pd.NA

        return x


    phase2[
        "normalized_content"
    ] = (
        phase2["content"]
        .map(
            normalize_duplicate_text
        )
    )

    # --------------------------------------------------------
    # Group ID:
    #
    # same app + same normalized content
    #
    # Missing contents receive unique groups.
    # --------------------------------------------------------

    group_keys = []

    for (
        app,
        text,
        row_id
    ) in zip(

        phase2["app"],
        phase2[
            "normalized_content"
        ],
        phase2["row_id"],
    ):

        if pd.isna(text):

            key = (
                "MISSING_CONTENT|"
                +
                str(row_id)
            )

        else:

            key = (
                str(app)
                +
                "\\x1f"
                +
                str(text)
            )

        group_keys.append(
            hashlib.sha256(
                key.encode(
                    "utf-8"
                )
            ).hexdigest()[:32]
        )


    phase2[
        "duplicate_group_id"
    ] = group_keys

    # --------------------------------------------------------
    # Mandatory checks
    # --------------------------------------------------------

    assert (
        phase2[
            "row_id"
        ].is_unique
    )

    assert (
        phase2[
            "row_id"
        ].notna().all()
    )

    assert (
        phase2[
            "duplicate_group_id"
        ].notna().all()
    )

    # --------------------------------------------------------
    # Save immediately to Drive
    # --------------------------------------------------------

    atomic_parquet_save(
        phase2,
        PHASE2_BASE_FILE
    )

    base_meta = {

        "phase2_id":
            PHASE2_ID,

        "source_sha256":
            current_fp[
                "sha256"
            ],

        "rows":
            int(
                len(phase2)
            ),

        "row_id_unique":
            bool(
                phase2[
                    "row_id"
                ].is_unique
            ),

        "created_at":
            datetime.datetime.now()
            .isoformat(),
    }

    atomic_json_save(
        base_meta,
        PHASE2_BASE_META
    )

    set_phase2_state(
        "alignment",
        "passed"
    )

    set_phase2_state(
        "ids",
        "complete"
    )


print(
    "Rows:",
    f"{len(phase2):,}"
)

print(
    "Unique row_id:",
    f"{phase2['row_id'].nunique():,}"
)

print(
    "Unique duplicate groups:",
    f"{phase2['duplicate_group_id'].nunique():,}"
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 72
# FULL CELL SHA256: faabdda491df5d0501ca2fe16ccd85f4bd15fb8ab8679de65b45478ed29e7a8f
# ============================================================

# ============================================================
# [PHASE3][RQ4 PRIMARY] CELL 63
# PRE-SPECIFIED PRIMARY H4 ANALYSIS
#
# Primary estimand:
#
#   mean_seed_JSD_i = beta_0 + beta_1 * disagreement_i + error_i
#
# where:
#   disagreement = 0 : rating weak label == VADER weak label
#   disagreement = 1 : rating weak label != VADER weak label
#
# Inference:
#   OLS
#   cluster-robust SE by duplicate_group_id
#
# H4 support criterion LOCKED BEFORE TEST ANALYSIS:
#
#   beta_1 > 0
#   AND
#   lower bound of 95% CI > 0
#
# IMPORTANT INTERPRETATION:
# This tests whether weak-label disagreement is associated
# with greater Transformer prediction sensitivity to the
# supervision source.
#
# It does NOT establish which weak label is correct.
# ============================================================

import os
import json
import hashlib
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


# ============================================================
# 1. REQUIRE PAIRED-JSD CONSTRUCTION PASS
# ============================================================

JSD_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_PAIRED_JSD_CONSTRUCTION_PASS.json"
)

assert JSD_MANIFEST_FILE.exists()


with open(
    JSD_MANIFEST_FILE,
    encoding="utf-8"
) as f:

    jsd_manifest = json.load(f)


assert jsd_manifest["status"] == "PASS"

assert (
    jsd_manifest["final_rq4_protocol_id"]
    ==
    FINAL_RQ4_PROTOCOL_ID
)

assert (
    jsd_manifest["n_test_reviews"]
    ==
    22500
)

assert (
    jsd_manifest["primary_review_level_outcome"]
    ==
    "mean_seed_jsd"
)

assert (
    jsd_manifest["disagreement_variable_used"]
    is False
)

assert (
    jsd_manifest["h4_tested"]
    is False
)


EXPECTED_MEAN_JSD_SHA = (
    "2688ce3f06ad8eb5f16bfc52b5f3185372838f92ed983f9afc334154cb739903"
)

assert (
    jsd_manifest["mean_seed_jsd_sha256"]
    ==
    EXPECTED_MEAN_JSD_SHA
)


CANONICAL_TEST_ROW_HASH = (
    jsd_manifest["test_row_order_sha256"]
)


print("✓ Frozen paired-JSD construction verified.")
print("✓ Primary JSD hash:")
print(EXPECTED_MEAN_JSD_SHA)


# ============================================================
# 2. HELPERS
# ============================================================

def sha256_text_sequence(values):

    h = hashlib.sha256()

    for value in values:

        encoded = str(value).encode("utf-8")

        h.update(
            len(encoded).to_bytes(
                8,
                byteorder="little",
                signed=False
            )
        )

        h.update(encoded)

    return h.hexdigest()


def sha256_float64_array(array):

    arr = np.asarray(
        array,
        dtype="<f8"
    )

    return hashlib.sha256(
        arr.tobytes(order="C")
    ).hexdigest()


def save_json_fsync(obj, path):

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
        os.fsync(f.fileno())


def save_text_fsync(text, path):

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

        f.write(text)
        f.flush()
        os.fsync(f.fileno())


def save_csv_fsync(df, path):

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        path,
        index=False
    )

    with open(
        path,
        "rb"
    ) as f:

        os.fsync(f.fileno())


# ============================================================
# 3. LOAD FROZEN JSD OUTCOME
# ============================================================

JSD_FILE = Path(
    jsd_manifest["jsd_file"]
)

assert JSD_FILE.exists()


jsd_df = pd.read_parquet(
    JSD_FILE,
    columns=[
        "row_id",
        "jsd_seed_42",
        "jsd_seed_123",
        "jsd_seed_2026",
        "mean_seed_jsd",
        "mean_seed_jsd_normalized",
    ]
)


assert len(jsd_df) == 22500
assert jsd_df["row_id"].is_unique


jsd_df["row_id"] = (
    jsd_df["row_id"]
    .astype(str)
)


assert (
    sha256_text_sequence(
        jsd_df["row_id"].tolist()
    )
    ==
    CANONICAL_TEST_ROW_HASH
)


observed_mean_hash = (
    sha256_float64_array(
        jsd_df["mean_seed_jsd"]
        .to_numpy(dtype=np.float64)
    )
)


assert (
    observed_mean_hash
    ==
    EXPECTED_MEAN_JSD_SHA
)


print("✓ Frozen mean_seed_jsd artifact verified byte-for-byte.")


# ============================================================
# 4. LOAD ONLY REQUIRED FROZEN TEST METADATA
# ============================================================

FROZEN_COHORT_FILE = Path(
    "/content/drive/MyDrive/IGAR_Paper1/"
    "phase3/gate5b/data/"
    "IGAR_RQ4_Final_Cohort_150k.parquet"
)

assert FROZEN_COHORT_FILE.exists()


cohort_columns = pd.read_parquet(
    FROZEN_COHORT_FILE
).columns.tolist()


REQUIRED_METADATA = [
    "row_id",
    "split",
    "disagreement",
    "duplicate_group_id",
]


missing_columns = [
    c
    for c in REQUIRED_METADATA
    if c not in cohort_columns
]


assert not missing_columns, (
    "Frozen cohort is missing required columns: "
    + str(missing_columns)
)


test_meta = pd.read_parquet(
    FROZEN_COHORT_FILE,
    columns=REQUIRED_METADATA
)


test_meta = (
    test_meta
    .loc[
        test_meta["split"].eq("test"),
        [
            "row_id",
            "disagreement",
            "duplicate_group_id",
        ]
    ]
    .copy()
)


assert len(test_meta) == 22500

assert test_meta["row_id"].is_unique

assert test_meta["row_id"].notna().all()

assert test_meta["disagreement"].notna().all()

assert test_meta["duplicate_group_id"].notna().all()


test_meta["row_id"] = (
    test_meta["row_id"]
    .astype(str)
)


test_meta["disagreement"] = (
    test_meta["disagreement"]
    .astype(int)
)


assert (
    set(
        test_meta["disagreement"].unique()
    )
    ==
    {0, 1}
)


print("✓ Frozen test metadata loaded.")
print("✓ disagreement and duplicate_group_id available.")


# ============================================================
# 5. ONE-TO-ONE MERGE — JSD LEFT ORDER IS CANONICAL
# ============================================================

analysis_df = jsd_df.merge(

    test_meta,

    on="row_id",

    how="left",

    validate="one_to_one",

    sort=False,
)


assert len(analysis_df) == 22500

assert analysis_df["disagreement"].notna().all()

assert analysis_df["duplicate_group_id"].notna().all()


assert (
    sha256_text_sequence(
        analysis_df["row_id"].tolist()
    )
    ==
    CANONICAL_TEST_ROW_HASH
)


assert (
    sha256_float64_array(
        analysis_df["mean_seed_jsd"]
        .to_numpy(dtype=np.float64)
    )
    ==
    EXPECTED_MEAN_JSD_SHA
)


# No accidental duplicate rows.
assert analysis_df["row_id"].is_unique


print("✓ JSD + frozen metadata merged one-to-one.")
print("✓ Canonical test order preserved.")


# ============================================================
# 6. PRIMARY SAMPLE AUDIT
# ============================================================

N_TOTAL = len(analysis_df)

N_AGREE = int(
    (analysis_df["disagreement"] == 0).sum()
)

N_DISAGREE = int(
    (analysis_df["disagreement"] == 1).sum()
)

N_CLUSTERS = int(
    analysis_df["duplicate_group_id"].nunique()
)


assert N_AGREE + N_DISAGREE == 22500

assert N_AGREE > 0
assert N_DISAGREE > 0
assert N_CLUSTERS > 1


cluster_sizes = (
    analysis_df
    .groupby(
        "duplicate_group_id",
        observed=True
    )
    .size()
)


N_SINGLETON_CLUSTERS = int(
    (cluster_sizes == 1).sum()
)

MAX_CLUSTER_SIZE = int(
    cluster_sizes.max()
)


print(
    f"✓ Primary analysis N: {N_TOTAL:,}"
)

print(
    f"✓ Agreement reviews: {N_AGREE:,}"
)

print(
    f"✓ Disagreement reviews: {N_DISAGREE:,}"
)

print(
    f"✓ duplicate_group_id clusters: {N_CLUSTERS:,}"
)


# ============================================================
# 7. DESCRIPTIVE STATISTICS
#
# These are summaries of the PRIMARY outcome by D.
# No alternative hypothesis/model is introduced.
# ============================================================

def q25(x):
    return np.quantile(x, 0.25)


def q75(x):
    return np.quantile(x, 0.75)


descriptive = (
    analysis_df
    .groupby(
        "disagreement",
        observed=True
    )["mean_seed_jsd"]
    .agg(
        N="size",
        mean="mean",
        sd="std",
        median="median",
        q25=q25,
        q75=q75,
        minimum="min",
        maximum="max",
    )
    .reset_index()
)


descriptive["group"] = (
    descriptive["disagreement"]
    .map({
        0: "Agreement",
        1: "Disagreement",
    })
)


descriptive = descriptive[
    [
        "disagreement",
        "group",
        "N",
        "mean",
        "sd",
        "median",
        "q25",
        "q75",
        "minimum",
        "maximum",
    ]
]


mean_agreement = float(
    descriptive
    .loc[
        descriptive["disagreement"].eq(0),
        "mean"
    ]
    .iloc[0]
)


mean_disagreement = float(
    descriptive
    .loc[
        descriptive["disagreement"].eq(1),
        "mean"
    ]
    .iloc[0]
)


raw_mean_difference = (
    mean_disagreement
    -
    mean_agreement
)


# ============================================================
# 8. PRE-SPECIFIED PRIMARY MODEL
#
# mean_seed_jsd ~ disagreement
#
# Cluster-robust covariance:
# duplicate_group_id
# ============================================================

y = (
    analysis_df["mean_seed_jsd"]
    .astype(np.float64)
)


X = pd.DataFrame({

    "const":
        np.ones(
            len(analysis_df),
            dtype=np.float64
        ),

    "disagreement":
        analysis_df["disagreement"]
        .to_numpy(dtype=np.float64),
})


groups = (
    analysis_df["duplicate_group_id"]
    .astype(str)
)


primary_fit = sm.OLS(
    y,
    X
).fit(

    cov_type="cluster",

    cov_kwds={
        "groups": groups,
        "use_correction": True,
        "df_correction": True,
    },

    use_t=True,
)


# ============================================================
# 9. EXTRACT PRIMARY ESTIMAND
# ============================================================

beta0 = float(
    primary_fit.params["const"]
)

beta1 = float(
    primary_fit.params["disagreement"]
)


se_beta1 = float(
    primary_fit.bse["disagreement"]
)


t_beta1 = float(
    primary_fit.tvalues["disagreement"]
)


p_beta1 = float(
    primary_fit.pvalues["disagreement"]
)


ci = primary_fit.conf_int(
    alpha=0.05
)


ci_low = float(
    ci.loc[
        "disagreement",
        0
    ]
)


ci_high = float(
    ci.loc[
        "disagreement",
        1
    ]
)


# With binary D and intercept, beta1 must equal
# the raw difference in group means.
assert np.isclose(
    beta1,
    raw_mean_difference,
    atol=1e-12,
    rtol=1e-10
)


# ============================================================
# 10. LOCKED H4 DECISION RULE
# ============================================================

H4_SUPPORTED = bool(
    (beta1 > 0.0)
    and
    (ci_low > 0.0)
)


H4_STATUS = (
    "SUPPORTED"
    if H4_SUPPORTED
    else
    "NOT_SUPPORTED"
)


# ============================================================
# 11. PRIMARY RESULTS TABLE
# ============================================================

primary_result = pd.DataFrame([{

    "outcome":
        "mean_seed_jsd",

    "predictor":
        "disagreement",

    "reference_group":
        "agreement (D=0)",

    "comparison_group":
        "disagreement (D=1)",

    "N":
        N_TOTAL,

    "clusters":
        N_CLUSTERS,

    "mean_agreement":
        mean_agreement,

    "mean_disagreement":
        mean_disagreement,

    "beta_disagreement":
        beta1,

    "cluster_robust_se":
        se_beta1,

    "t_statistic":
        t_beta1,

    "p_value":
        p_beta1,

    "ci95_low":
        ci_low,

    "ci95_high":
        ci_high,

    "h4_beta_positive":
        bool(beta1 > 0),

    "h4_ci_excludes_zero_positive":
        bool(ci_low > 0),

    "h4_status":
        H4_STATUS,

    "covariance":
        "cluster-robust",

    "cluster_variable":
        "duplicate_group_id",
}])


# ============================================================
# 12. SAVE PRIMARY ANALYSIS ARTIFACTS
# ============================================================

H4_ROOT = (
    RQ4_FINAL_ROOT
    /
    "primary_h4"
)

H4_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


ANALYSIS_DATA_FILE = (
    H4_ROOT
    /
    "RQ4_H4_Primary_Analysis_Data.parquet"
)


# Save ONLY variables needed for the primary model.
analysis_df[
    [
        "row_id",
        "mean_seed_jsd",
        "disagreement",
        "duplicate_group_id",
    ]
].to_parquet(
    ANALYSIS_DATA_FILE,
    index=False
)


DESCRIPTIVE_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_H4_Primary_Descriptive.csv"
)


PRIMARY_RESULT_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_H4_Primary_Cluster_Robust_OLS.csv"
)


descriptive.to_csv(
    DESCRIPTIVE_FILE,
    index=False
)


primary_result.to_csv(
    PRIMARY_RESULT_FILE,
    index=False
)


MODEL_SUMMARY_FILE = (
    H4_ROOT
    /
    "RQ4_H4_Primary_OLS_Summary.txt"
)


save_text_fsync(
    primary_fit.summary().as_text(),
    MODEL_SUMMARY_FILE
)


# ============================================================
# 13. PRIMARY H4 MANIFEST
# ============================================================

H4_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_PRIMARY_H4_RESULT.json"
)


h4_manifest = {

    "status":
        "PASS",

    "stage":
        "RQ4_PRIMARY_H4_ANALYSIS",

    "final_rq4_protocol_id":
        FINAL_RQ4_PROTOCOL_ID,

    "n_test_reviews":
        N_TOTAL,

    "n_agreement":
        N_AGREE,

    "n_disagreement":
        N_DISAGREE,

    "n_duplicate_group_clusters":
        N_CLUSTERS,

    "n_singleton_clusters":
        N_SINGLETON_CLUSTERS,

    "max_cluster_size":
        MAX_CLUSTER_SIZE,

    "outcome":
        "mean_seed_jsd",

    "jsd_logarithm":
        "natural",

    "predictor":
        "disagreement",

    "model":
        "OLS",

    "formula":
        "mean_seed_jsd ~ disagreement",

    "covariance":
        "cluster-robust",

    "cluster_variable":
        "duplicate_group_id",

    "finite_sample_cluster_correction":
        True,

    "mean_jsd_agreement":
        mean_agreement,

    "mean_jsd_disagreement":
        mean_disagreement,

    "beta_disagreement":
        beta1,

    "cluster_robust_se":
        se_beta1,

    "t_statistic":
        t_beta1,

    "p_value":
        p_beta1,

    "ci95_low":
        ci_low,

    "ci95_high":
        ci_high,

    "h4_decision_rule":
        (
            "SUPPORTED iff beta_disagreement > 0 "
            "and 95% CI lower bound > 0"
        ),

    "h4_supported":
        H4_SUPPORTED,

    "h4_status":
        H4_STATUS,

    "interpretation_scope":
        (
            "Association between weak-label disagreement "
            "and Transformer prediction sensitivity to "
            "the choice of weak-supervision source. "
            "Does not identify either weak label as ground truth."
        ),

    "app_adjustment":
        False,

    "rating_adjustment":
        False,

    "alternative_primary_models_tested":
        False,

    "mean_seed_jsd_sha256":
        EXPECTED_MEAN_JSD_SHA,

    "canonical_test_row_order_sha256":
        CANONICAL_TEST_ROW_HASH,

    "analysis_data_file":
        str(ANALYSIS_DATA_FILE),

    "descriptive_file":
        str(DESCRIPTIVE_FILE),

    "primary_result_file":
        str(PRIMARY_RESULT_FILE),

    "model_summary_file":
        str(MODEL_SUMMARY_FILE),

    "completed_at":
        datetime.datetime.now()
        .isoformat(),
}


save_json_fsync(
    h4_manifest,
    H4_MANIFEST_FILE
)


# ============================================================
# 14. FINAL DASHBOARD
# ============================================================

print(
    "\n"
    +
    "=" * 118
)

print(
    "✓ RQ4 PRIMARY H4 ANALYSIS — COMPLETE"
)

print(
    "=" * 118
)


print(
    "\nPRIMARY SAMPLE"
)

print(
    "Test reviews:",
    f"{N_TOTAL:,}"
)

print(
    "Agreement (D=0):",
    f"{N_AGREE:,}"
)

print(
    "Disagreement (D=1):",
    f"{N_DISAGREE:,}"
)

print(
    "duplicate_group_id clusters:",
    f"{N_CLUSTERS:,}"
)

print(
    "Singleton clusters:",
    f"{N_SINGLETON_CLUSTERS:,}"
)

print(
    "Maximum cluster size:",
    f"{MAX_CLUSTER_SIZE:,}"
)


print(
    "\nPRIMARY OUTCOME DESCRIPTIVES"
)

display(
    descriptive[
        [
            "group",
            "N",
            "mean",
            "sd",
            "median",
            "q25",
            "q75",
        ]
    ]
)


print(
    "\nPRIMARY PRE-SPECIFIED MODEL"
)

print(
    "mean_seed_jsd ~ disagreement"
)

print(
    "SE:",
    "cluster-robust by duplicate_group_id"
)


display(
    primary_result[
        [
            "beta_disagreement",
            "cluster_robust_se",
            "t_statistic",
            "p_value",
            "ci95_low",
            "ci95_high",
            "h4_status",
        ]
    ]
)


print(
    "\nMean JSD | agreement:",
    f"{mean_agreement:.8f}"
)

print(
    "Mean JSD | disagreement:",
    f"{mean_disagreement:.8f}"
)

print(
    "Difference (D=1 - D=0):",
    f"{beta1:.8f}"
)

print(
    "Cluster-robust SE:",
    f"{se_beta1:.8f}"
)

print(
    "95% CI:",
    f"[{ci_low:.8f}, {ci_high:.8f}]"
)

print(
    "p-value:",
    f"{p_beta1:.6g}"
)


print(
    "\nLOCKED H4 DECISION RULE"
)

print(
    "beta > 0:",
    beta1 > 0
)

print(
    "95% CI lower bound > 0:",
    ci_low > 0
)


print(
    "\nH4:",
    H4_STATUS
)


print(
    "\nINTERPRETATION BOUNDARY"
)

print(
    "Result concerns sensitivity to supervision source."
)

print(
    "It does NOT identify rating or VADER as ground truth."
)


print(
    "\n"
    +
    "=" * 118
)

print(
    "RQ4 FINAL TRAINING : CLOSED / PASS"
)

print(
    "RQ4 TEST INFERENCE : CLOSED / PASS"
)

print(
    "PAIRED JSD         : CLOSED / PASS"
)

print(
    "PRIMARY H4 ANALYSIS: CLOSED / PASS"
)

print(
    "H4                 :",
    H4_STATUS
)

print(
    "=" * 118
)

print(
    "\nSTOP HERE."
)

print(
    "Do not run severity/app secondary analyses yet."
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 75
# FULL CELL SHA256: 2bc8877e5ef97cdad4628d1be66a2c2a4367a5b57c353e9752eb69d4da385bf0
# ============================================================

# ============================================================
# [PHASE3][RQ4 EXPLORATORY] CELL 65
# WEAK-LABEL DISAGREEMENT SEVERITY ANALYSIS
#
# Severity definition:
#
#   S = |rating_target - vader_target|
#
#   S = 0 : agreement
#   S = 1 : adjacent disagreement
#   S = 2 : extreme disagreement
#
# Outcome:
#   mean_seed_jsd
#
# Model:
#   categorical severity with S=0 as reference
#   cluster-robust SE by duplicate_group_id
#
# Pairwise contrasts:
#   S1 - S0
#   S2 - S0
#   S2 - S1
#
# IMPORTANT:
# - exploratory / secondary
# - does NOT alter the primary H4 result
# - does NOT establish either weak label as ground truth
# ============================================================

import os
import json
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from statsmodels.stats.multitest import multipletests


# ============================================================
# 1. REQUIRE PRIMARY + SENSITIVITY RESULTS
# ============================================================

H4_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_PRIMARY_H4_RESULT.json"
)

SENSITIVITY_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_H4_Large_Cluster_Sensitivity.json"
)


assert H4_MANIFEST_FILE.exists()
assert SENSITIVITY_MANIFEST_FILE.exists()


with open(
    H4_MANIFEST_FILE,
    encoding="utf-8"
) as f:

    h4_manifest = json.load(f)


with open(
    SENSITIVITY_MANIFEST_FILE,
    encoding="utf-8"
) as f:

    sensitivity_manifest = json.load(f)


assert h4_manifest["status"] == "PASS"
assert h4_manifest["h4_status"] == "SUPPORTED"

assert sensitivity_manifest["status"] == "PASS"

assert (
    sensitivity_manifest[
        "primary_h4_status"
    ]
    ==
    "SUPPORTED"
)


print("✓ Frozen primary H4 loaded.")
print("✓ Large-cluster sensitivity PASS loaded.")
print("✓ Primary H4 remains: SUPPORTED")


# ============================================================
# 2. LOAD FROZEN PRIMARY OUTCOME
# ============================================================

PRIMARY_ANALYSIS_FILE = Path(
    h4_manifest[
        "analysis_data_file"
    ]
)

assert PRIMARY_ANALYSIS_FILE.exists()


primary_df = pd.read_parquet(
    PRIMARY_ANALYSIS_FILE
)


assert len(primary_df) == 22500
assert primary_df["row_id"].is_unique


primary_df["row_id"] = (
    primary_df["row_id"]
    .astype(str)
)


# ============================================================
# 3. LOAD FROZEN TEST WEAK-LABEL TARGETS
# ============================================================

FROZEN_COHORT_FILE = Path(
    "/content/drive/MyDrive/IGAR_Paper1/"
    "phase3/gate5b/data/"
    "IGAR_RQ4_Final_Cohort_150k.parquet"
)

assert FROZEN_COHORT_FILE.exists()


cohort_cols = (
    pd.read_parquet(
        FROZEN_COHORT_FILE
    )
    .columns
    .tolist()
)


required = [
    "row_id",
    "split",
    "rating_target",
    "vader_target",
]


missing = [
    c
    for c in required
    if c not in cohort_cols
]


assert not missing, (
    "Missing frozen cohort columns: "
    + str(missing)
)


severity_meta = pd.read_parquet(
    FROZEN_COHORT_FILE,
    columns=required
)


severity_meta = (
    severity_meta
    .loc[
        severity_meta["split"].eq("test"),
        [
            "row_id",
            "rating_target",
            "vader_target",
        ]
    ]
    .copy()
)


assert len(severity_meta) == 22500
assert severity_meta["row_id"].is_unique


severity_meta["row_id"] = (
    severity_meta["row_id"]
    .astype(str)
)


severity_meta["rating_target"] = (
    severity_meta["rating_target"]
    .astype(int)
)

severity_meta["vader_target"] = (
    severity_meta["vader_target"]
    .astype(int)
)


assert set(
    severity_meta[
        "rating_target"
    ].unique()
).issubset(
    {0, 1, 2}
)


assert set(
    severity_meta[
        "vader_target"
    ].unique()
).issubset(
    {0, 1, 2}
)


# ============================================================
# 4. CONSTRUCT LOCKED SEVERITY
# ============================================================

severity_meta["severity"] = np.abs(
    severity_meta["rating_target"]
    -
    severity_meta["vader_target"]
).astype(int)


assert (
    set(
        severity_meta[
            "severity"
        ].unique()
    )
    ==
    {0, 1, 2}
)


severity_meta[
    "severity_label"
] = severity_meta[
    "severity"
].map({
    0: "S0 — Agreement",
    1: "S1 — Adjacent disagreement",
    2: "S2 — Extreme disagreement",
})


# ============================================================
# 5. MERGE WITH PRIMARY ANALYSIS OUTCOME
# ============================================================

severity_df = primary_df.merge(
    severity_meta,
    on="row_id",
    how="left",
    validate="one_to_one",
    sort=False,
)


assert len(severity_df) == 22500

assert severity_df[
    "severity"
].notna().all()


severity_df["severity"] = (
    severity_df["severity"]
    .astype(int)
)


# Critical consistency check:
# severity > 0 must equal primary disagreement.
assert np.array_equal(
    (
        severity_df[
            "severity"
        ].to_numpy()
        >
        0
    ).astype(int),

    severity_df[
        "disagreement"
    ].to_numpy(dtype=int)
)


print("✓ Severity constructed from frozen targets.")
print("✓ severity > 0 exactly reproduces disagreement.")


# ============================================================
# 6. DESCRIPTIVE STATISTICS
# ============================================================

def q25(x):
    return np.quantile(x, 0.25)


def q75(x):
    return np.quantile(x, 0.75)


severity_desc = (
    severity_df
    .groupby(
        [
            "severity",
            "severity_label",
        ],
        observed=True
    )["mean_seed_jsd"]
    .agg(
        N="size",
        mean="mean",
        sd="std",
        median="median",
        q25=q25,
        q75=q75,
        minimum="min",
        maximum="max",
    )
    .reset_index()
    .sort_values("severity")
    .reset_index(drop=True)
)


assert len(severity_desc) == 3


mean_s0 = float(
    severity_desc.loc[
        severity_desc[
            "severity"
        ].eq(0),
        "mean"
    ].iloc[0]
)

mean_s1 = float(
    severity_desc.loc[
        severity_desc[
            "severity"
        ].eq(1),
        "mean"
    ].iloc[0]
)

mean_s2 = float(
    severity_desc.loc[
        severity_desc[
            "severity"
        ].eq(2),
        "mean"
    ].iloc[0]
)


observed_monotonic_means = bool(
    mean_s0
    <
    mean_s1
    <
    mean_s2
)


# ============================================================
# 7. CATEGORICAL CLUSTER-ROBUST OLS
#
# mean_seed_jsd =
#   b0
# + b1 * I(S=1)
# + b2 * I(S=2)
#
# Reference: S=0
#
# NumPy used deliberately to avoid pandas index alignment.
# ============================================================

y = severity_df[
    "mean_seed_jsd"
].to_numpy(
    dtype=np.float64
)


s = severity_df[
    "severity"
].to_numpy(
    dtype=int
)


X = np.column_stack([
    np.ones(
        len(severity_df),
        dtype=np.float64
    ),

    (s == 1).astype(
        np.float64
    ),

    (s == 2).astype(
        np.float64
    ),
])


groups = (
    severity_df[
        "duplicate_group_id"
    ]
    .astype(str)
    .to_numpy()
)


assert X.shape == (
    22500,
    3
)


fit = sm.OLS(
    y,
    X
).fit(
    cov_type="cluster",

    cov_kwds={
        "groups": groups,
        "use_correction": True,
        "df_correction": True,
    },

    use_t=True,
)


# ============================================================
# 8. PAIRWISE CLUSTER-ROBUST CONTRASTS
# ============================================================

contrast_specs = {

    "S1 - S0": np.array([
        0.0,
        1.0,
        0.0
    ]),

    "S2 - S0": np.array([
        0.0,
        0.0,
        1.0
    ]),

    "S2 - S1": np.array([
        0.0,
        -1.0,
        1.0
    ]),
}


contrast_rows = []


for comparison, vector in contrast_specs.items():

    test = fit.t_test(
        vector
    )


    effect = float(
        np.asarray(
            test.effect
        ).reshape(-1)[0]
    )


    se = float(
        np.asarray(
            test.sd
        ).reshape(-1)[0]
    )


    t_value = float(
        np.asarray(
            test.tvalue
        ).reshape(-1)[0]
    )


    p_value = float(
        np.asarray(
            test.pvalue
        ).reshape(-1)[0]
    )


    ci = np.asarray(
        test.conf_int(
            alpha=0.05
        )
    ).reshape(
        -1,
        2
    )[0]


    contrast_rows.append({

        "comparison":
            comparison,

        "difference":
            effect,

        "cluster_robust_se":
            se,

        "t_statistic":
            t_value,

        "p_value_raw":
            p_value,

        "ci95_low":
            float(ci[0]),

        "ci95_high":
            float(ci[1]),
    })


contrasts = pd.DataFrame(
    contrast_rows
)


# ============================================================
# 9. HOLM CORRECTION FOR 3 EXPLORATORY CONTRASTS
# ============================================================

reject_holm, p_holm, _, _ = multipletests(

    contrasts[
        "p_value_raw"
    ].to_numpy(),

    alpha=0.05,

    method="holm",
)


contrasts[
    "p_value_holm"
] = p_holm


contrasts[
    "holm_significant_0_05"
] = reject_holm


contrasts[
    "ci_entirely_positive"
] = (
    contrasts[
        "ci95_low"
    ]
    >
    0
)


# ============================================================
# 10. MONOTONIC PATTERN FLAG
#
# Descriptive/exploratory only.
# Not a new confirmatory hypothesis.
# ============================================================

s1_s0 = contrasts.loc[
    contrasts[
        "comparison"
    ].eq(
        "S1 - S0"
    )
].iloc[0]


s2_s1 = contrasts.loc[
    contrasts[
        "comparison"
    ].eq(
        "S2 - S1"
    )
].iloc[0]


monotonic_contrast_pattern = bool(

    observed_monotonic_means

    and

    (
        s1_s0[
            "difference"
        ]
        >
        0
    )

    and

    (
        s2_s1[
            "difference"
        ]
        >
        0
    )

    and

    bool(
        s1_s0[
            "holm_significant_0_05"
        ]
    )

    and

    bool(
        s2_s1[
            "holm_significant_0_05"
        ]
    )
)


# ============================================================
# 11. OPTIONAL LINEAR TREND DESCRIPTOR
#
# Exploratory only.
# Does not replace categorical model.
# ============================================================

X_trend = np.column_stack([
    np.ones(
        len(severity_df),
        dtype=np.float64
    ),
    s.astype(np.float64),
])


trend_fit = sm.OLS(
    y,
    X_trend
).fit(
    cov_type="cluster",

    cov_kwds={
        "groups": groups,
        "use_correction": True,
        "df_correction": True,
    },

    use_t=True,
)


trend_ci = np.asarray(
    trend_fit.conf_int(
        alpha=0.05
    )
)


trend_result = {

    "beta_per_severity_step":
        float(
            trend_fit.params[1]
        ),

    "cluster_robust_se":
        float(
            trend_fit.bse[1]
        ),

    "t_statistic":
        float(
            trend_fit.tvalues[1]
        ),

    "p_value":
        float(
            trend_fit.pvalues[1]
        ),

    "ci95_low":
        float(
            trend_ci[1, 0]
        ),

    "ci95_high":
        float(
            trend_ci[1, 1]
        ),
}


# ============================================================
# 12. SAVE ARTIFACTS
# ============================================================

SEVERITY_ROOT = (
    RQ4_FINAL_ROOT
    /
    "severity_exploratory"
)

SEVERITY_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


SEVERITY_DESC_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Severity_Descriptive.csv"
)


SEVERITY_CONTRAST_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Severity_Cluster_Robust_Contrasts.csv"
)


SEVERITY_ANALYSIS_FILE = (
    SEVERITY_ROOT
    /
    "RQ4_Severity_Analysis_Data.parquet"
)


severity_desc.to_csv(
    SEVERITY_DESC_FILE,
    index=False
)


contrasts.to_csv(
    SEVERITY_CONTRAST_FILE,
    index=False
)


severity_df[
    [
        "row_id",
        "mean_seed_jsd",
        "duplicate_group_id",
        "disagreement",
        "severity",
        "rating_target",
        "vader_target",
    ]
].to_parquet(
    SEVERITY_ANALYSIS_FILE,
    index=False
)


# ============================================================
# 13. MANIFEST
# ============================================================

SEVERITY_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_SEVERITY_EXPLORATORY_RESULT.json"
)


severity_manifest = {

    "status":
        "PASS",

    "analysis_type":
        "EXPLORATORY_SECONDARY",

    "stage":
        "RQ4_DISAGREEMENT_SEVERITY",

    "final_rq4_protocol_id":
        FINAL_RQ4_PROTOCOL_ID,

    "primary_h4_status":
        h4_manifest[
            "h4_status"
        ],

    "primary_h4_changed":
        False,

    "severity_definition":
        "abs(rating_target - vader_target)",

    "severity_levels": {
        "0":
            "agreement",
        "1":
            "adjacent disagreement",
        "2":
            "extreme disagreement",
    },

    "outcome":
        "mean_seed_jsd",

    "model":
        (
            "categorical OLS with cluster-robust "
            "SE by duplicate_group_id"
        ),

    "reference_level":
        "S=0",

    "multiple_comparison_adjustment":
        "Holm for three exploratory pairwise contrasts",

    "mean_S0":
        mean_s0,

    "mean_S1":
        mean_s1,

    "mean_S2":
        mean_s2,

    "observed_means_S0_lt_S1_lt_S2":
        observed_monotonic_means,

    "monotonic_exploratory_pattern":
        monotonic_contrast_pattern,

    "linear_trend":
        trend_result,

    "confirmatory_hypothesis_retested":
        False,

    "ground_truth_claim":
        False,

    "interpretation":
        (
            "Exploratory characterization of whether "
            "prediction sensitivity increases with the "
            "ordinal severity of disagreement between "
            "the two weak-label sources."
        ),

    "completed_at":
        datetime.datetime.now()
        .isoformat(),
}


with open(
    SEVERITY_MANIFEST_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        severity_manifest,
        f,
        indent=2
    )


# ============================================================
# 14. DASHBOARD
# ============================================================

def p_display(p):

    if p < 0.001:
        return "< .001"

    return f"{p:.4f}"


print(
    "\n"
    +
    "=" * 120
)

print(
    "✓ RQ4 EXPLORATORY SEVERITY ANALYSIS — PASS"
)

print(
    "=" * 120
)


print(
    "\nSEVERITY DESCRIPTIVES"
)

display(
    severity_desc[
        [
            "severity",
            "severity_label",
            "N",
            "mean",
            "sd",
            "median",
            "q25",
            "q75",
        ]
    ]
)


print(
    "\nCLUSTER-ROBUST PAIRWISE CONTRASTS"
)

contrast_display = (
    contrasts.copy()
)


contrast_display[
    "p_raw_display"
] = (
    contrast_display[
        "p_value_raw"
    ].apply(
        p_display
    )
)


contrast_display[
    "p_holm_display"
] = (
    contrast_display[
        "p_value_holm"
    ].apply(
        p_display
    )
)


display(
    contrast_display[
        [
            "comparison",
            "difference",
            "cluster_robust_se",
            "ci95_low",
            "ci95_high",
            "p_raw_display",
            "p_holm_display",
            "holm_significant_0_05",
        ]
    ]
)


print(
    "\nEXPLORATORY ORDERING"
)

print(
    "Mean S0:",
    f"{mean_s0:.8f}"
)

print(
    "Mean S1:",
    f"{mean_s1:.8f}"
)

print(
    "Mean S2:",
    f"{mean_s2:.8f}"
)

print(
    "Observed means S0 < S1 < S2:",
    observed_monotonic_means
)

print(
    "Positive Holm-significant S1-S0 and S2-S1:",
    monotonic_contrast_pattern
)


print(
    "\nLINEAR TREND DESCRIPTOR"
)

print(
    "Beta per severity step:",
    f"{trend_result['beta_per_severity_step']:.8f}"
)

print(
    "Cluster-robust SE:",
    f"{trend_result['cluster_robust_se']:.8f}"
)

print(
    "95% CI:",
    (
        f"[{trend_result['ci95_low']:.8f}, "
        f"{trend_result['ci95_high']:.8f}]"
    )
)

print(
    "p:",
    p_display(
        trend_result[
            "p_value"
        ]
    )
)


print(
    "\nPRIMARY H4:"
)

print(
    h4_manifest[
        "h4_status"
    ],
    "(UNCHANGED)"
)


print(
    "\nINTERPRETATION BOUNDARY"
)

print(
    "Severity analysis is exploratory/secondary."
)

print(
    "It does not identify either weak-label source as ground truth."
)


print(
    "\n"
    +
    "=" * 120
)

print(
    "PRIMARY H4                : CLOSED / SUPPORTED"
)

print(
    "LARGE-CLUSTER SENSITIVITY : CLOSED / PASS"
)

print(
    "SEVERITY EXPLORATORY      : CLOSED / PASS"
)

print(
    "APP-LEVEL DESCRIPTION     : NOT STARTED"
)

print(
    "=" * 120
)

print(
    "\nSTOP HERE."
)

print(
    "Next after review: app-level descriptive heterogeneity."
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 76
# FULL CELL SHA256: f306583131d663969be7c9d1ffcf1a5c40d2b23d641650e978d9148f5f5a0997
# ============================================================

# ============================================================
# [PHASE3][RQ4 EXPLORATORY] CELL 66
# APP-LEVEL DESCRIPTIVE HETEROGENEITY
#
# Purpose:
# Characterize whether the primary disagreement-associated
# prediction divergence is descriptively present across the
# six government-application domains.
#
# NO new confirmatory hypothesis.
# NO app-by-disagreement significance test.
# NO multiple testing.
#
# Main descriptive quantities per app:
# - N
# - disagreement prevalence
# - mean JSD overall
# - mean JSD among agreement
# - mean JSD among disagreement
# - raw difference (D1 - D0)
#
# Also reports S0/S1/S2 composition and means descriptively.
# ============================================================

import os
import json
import datetime
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. REQUIRE COMPLETED PRIMARY + SEVERITY ANALYSES
# ============================================================

H4_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_PRIMARY_H4_RESULT.json"
)

SEVERITY_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_SEVERITY_EXPLORATORY_RESULT.json"
)


assert H4_MANIFEST_FILE.exists()
assert SEVERITY_MANIFEST_FILE.exists()


with open(
    H4_MANIFEST_FILE,
    encoding="utf-8"
) as f:
    h4_manifest = json.load(f)


with open(
    SEVERITY_MANIFEST_FILE,
    encoding="utf-8"
) as f:
    severity_manifest = json.load(f)


assert h4_manifest["status"] == "PASS"
assert h4_manifest["h4_status"] == "SUPPORTED"

assert severity_manifest["status"] == "PASS"

assert (
    severity_manifest["primary_h4_changed"]
    is False
)


print("✓ Primary H4 loaded:", h4_manifest["h4_status"])
print("✓ Severity exploratory result loaded.")


# ============================================================
# 2. LOAD PRIMARY ANALYSIS DATA
# ============================================================

PRIMARY_ANALYSIS_FILE = Path(
    h4_manifest["analysis_data_file"]
)

assert PRIMARY_ANALYSIS_FILE.exists()


primary_df = pd.read_parquet(
    PRIMARY_ANALYSIS_FILE
)


assert len(primary_df) == 22500
assert primary_df["row_id"].is_unique


primary_df["row_id"] = (
    primary_df["row_id"]
    .astype(str)
)


# ============================================================
# 3. LOAD SEVERITY ANALYSIS DATA
# ============================================================

SEVERITY_ANALYSIS_FILE = (
    RQ4_FINAL_ROOT
    /
    "severity_exploratory"
    /
    "RQ4_Severity_Analysis_Data.parquet"
)

assert SEVERITY_ANALYSIS_FILE.exists()


severity_df = pd.read_parquet(
    SEVERITY_ANALYSIS_FILE,
    columns=[
        "row_id",
        "severity",
    ]
)


assert len(severity_df) == 22500
assert severity_df["row_id"].is_unique


severity_df["row_id"] = (
    severity_df["row_id"]
    .astype(str)
)


# ============================================================
# 4. LOAD APP METADATA FROM FROZEN COHORT
# ============================================================

FROZEN_COHORT_FILE = Path(
    "/content/drive/MyDrive/IGAR_Paper1/"
    "phase3/gate5b/data/"
    "IGAR_RQ4_Final_Cohort_150k.parquet"
)

assert FROZEN_COHORT_FILE.exists()


cohort_columns = (
    pd.read_parquet(
        FROZEN_COHORT_FILE
    )
    .columns
    .tolist()
)


assert "app" in cohort_columns, (
    "Expected frozen cohort column 'app' not found."
)


app_meta = pd.read_parquet(
    FROZEN_COHORT_FILE,
    columns=[
        "row_id",
        "split",
        "app",
    ]
)


app_meta = (
    app_meta
    .loc[
        app_meta["split"].eq("test"),
        [
            "row_id",
            "app",
        ]
    ]
    .copy()
)


assert len(app_meta) == 22500
assert app_meta["row_id"].is_unique
assert app_meta["app"].notna().all()


app_meta["row_id"] = (
    app_meta["row_id"]
    .astype(str)
)


# ============================================================
# 5. MERGE PRIMARY + SEVERITY + APP
# ============================================================

app_df = (
    primary_df
    .merge(
        severity_df,
        on="row_id",
        how="left",
        validate="one_to_one",
        sort=False,
    )
    .merge(
        app_meta,
        on="row_id",
        how="left",
        validate="one_to_one",
        sort=False,
    )
)


assert len(app_df) == 22500
assert app_df["app"].notna().all()
assert app_df["severity"].notna().all()


app_df["severity"] = (
    app_df["severity"]
    .astype(int)
)


assert np.array_equal(
    (
        app_df["severity"]
        >
        0
    ).astype(int),

    app_df["disagreement"]
    .to_numpy(dtype=int)
)


# ============================================================
# 6. PRESENTATION NAMES
# ============================================================

APP_PRESENTATION = {
    "BMKG": "BMKG",
    "JMO": "JMO",
    "KAI": "KAI",
    "mobileJKN": "Mobile JKN",
    "pertamina": "MyPertamina",
    "satusehat": "SATUSEHAT",
}


app_df["app_display"] = (
    app_df["app"]
    .map(APP_PRESENTATION)
    .fillna(
        app_df["app"]
        .astype(str)
    )
)


assert app_df["app_display"].nunique() == 6


print(
    "✓ Six frozen application domains verified:",
    sorted(
        app_df["app_display"].unique()
    )
)


# ============================================================
# 7. APP-LEVEL PRIMARY DESCRIPTIVES
# ============================================================

app_rows = []


for app_name, g in app_df.groupby(
    "app_display",
    observed=True
):

    agree = g.loc[
        g["disagreement"].eq(0),
        "mean_seed_jsd"
    ]

    disagree = g.loc[
        g["disagreement"].eq(1),
        "mean_seed_jsd"
    ]


    assert len(agree) > 0
    assert len(disagree) > 0


    app_rows.append({

        "app":
            app_name,

        "N":
            int(len(g)),

        "clusters":
            int(
                g["duplicate_group_id"]
                .nunique()
            ),

        "n_agreement":
            int(len(agree)),

        "n_disagreement":
            int(len(disagree)),

        "disagreement_percent":
            float(
                100.0
                *
                len(disagree)
                /
                len(g)
            ),

        "mean_jsd_overall":
            float(
                g["mean_seed_jsd"]
                .mean()
            ),

        "mean_jsd_agreement":
            float(
                agree.mean()
            ),

        "mean_jsd_disagreement":
            float(
                disagree.mean()
            ),

        "raw_difference_D1_minus_D0":
            float(
                disagree.mean()
                -
                agree.mean()
            ),

        "median_jsd_agreement":
            float(
                agree.median()
            ),

        "median_jsd_disagreement":
            float(
                disagree.median()
            ),
    })


app_primary = (
    pd.DataFrame(app_rows)
    .sort_values(
        "raw_difference_D1_minus_D0",
        ascending=False
    )
    .reset_index(drop=True)
)


assert len(app_primary) == 6


# ============================================================
# 8. DIRECTIONAL REPLICATION CHECK
#
# Descriptive only:
# does every app have mean(D=1) > mean(D=0)?
# ============================================================

app_primary[
    "positive_disagreement_difference"
] = (
    app_primary[
        "raw_difference_D1_minus_D0"
    ]
    >
    0
)


N_APPS_POSITIVE = int(
    app_primary[
        "positive_disagreement_difference"
    ].sum()
)


ALL_APPS_POSITIVE = bool(
    N_APPS_POSITIVE == 6
)


# ============================================================
# 9. APP × SEVERITY DESCRIPTIVES
# ============================================================

severity_rows = []


for (
    app_name,
    severity
), g in app_df.groupby(
    [
        "app_display",
        "severity",
    ],
    observed=True
):

    severity_rows.append({

        "app":
            app_name,

        "severity":
            int(severity),

        "N":
            int(len(g)),

        "percent_within_app":
            float(
                100.0
                *
                len(g)
                /
                (
                    app_df[
                        "app_display"
                    ]
                    .eq(app_name)
                    .sum()
                )
            ),

        "mean_seed_jsd":
            float(
                g["mean_seed_jsd"]
                .mean()
            ),

        "median_seed_jsd":
            float(
                g["mean_seed_jsd"]
                .median()
            ),
    })


app_severity_long = pd.DataFrame(
    severity_rows
)


assert len(
    app_severity_long
) == 18


# ============================================================
# 10. WIDE SEVERITY TABLE
# ============================================================

severity_mean_wide = (
    app_severity_long
    .pivot(
        index="app",
        columns="severity",
        values="mean_seed_jsd",
    )
    .rename(
        columns={
            0: "mean_S0",
            1: "mean_S1",
            2: "mean_S2",
        }
    )
    .reset_index()
)


severity_n_wide = (
    app_severity_long
    .pivot(
        index="app",
        columns="severity",
        values="N",
    )
    .rename(
        columns={
            0: "N_S0",
            1: "N_S1",
            2: "N_S2",
        }
    )
    .reset_index()
)


app_severity = (
    severity_mean_wide
    .merge(
        severity_n_wide,
        on="app",
        validate="one_to_one"
    )
)


app_severity[
    "S1_gt_S2"
] = (
    app_severity["mean_S1"]
    >
    app_severity["mean_S2"]
)


N_APPS_S1_GT_S2 = int(
    app_severity[
        "S1_gt_S2"
    ].sum()
)


# ============================================================
# 11. SAVE TABLES
# ============================================================

APP_PRIMARY_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_App_Descriptive_Heterogeneity.csv"
)


APP_SEVERITY_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_App_Severity_Descriptive.csv"
)


APP_SEVERITY_LONG_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_App_Severity_Descriptive_Long.csv"
)


app_primary.to_csv(
    APP_PRIMARY_FILE,
    index=False
)


app_severity.to_csv(
    APP_SEVERITY_FILE,
    index=False
)


app_severity_long.to_csv(
    APP_SEVERITY_LONG_FILE,
    index=False
)


# ============================================================
# 12. MANIFEST
# ============================================================

APP_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_APP_DESCRIPTIVE_HETEROGENEITY.json"
)


app_manifest = {

    "status":
        "PASS",

    "analysis_type":
        "EXPLORATORY_DESCRIPTIVE",

    "stage":
        "RQ4_APP_LEVEL_DESCRIPTION",

    "final_rq4_protocol_id":
        FINAL_RQ4_PROTOCOL_ID,

    "primary_h4_status":
        h4_manifest[
            "h4_status"
        ],

    "primary_h4_changed":
        False,

    "n_test_reviews":
        int(len(app_df)),

    "n_apps":
        int(
            app_df[
                "app_display"
            ].nunique()
        ),

    "apps":
        sorted(
            app_df[
                "app_display"
            ].unique()
            .tolist()
        ),

    "apps_with_positive_D1_minus_D0_difference":
        N_APPS_POSITIVE,

    "all_apps_positive_D1_minus_D0":
        ALL_APPS_POSITIVE,

    "apps_with_mean_S1_greater_than_mean_S2":
        N_APPS_S1_GT_S2,

    "formal_app_interaction_test":
        False,

    "app_specific_p_values":
        False,

    "confirmatory_hypothesis_retested":
        False,

    "interpretation":
        (
            "Descriptive assessment of cross-application "
            "heterogeneity in prediction divergence associated "
            "with weak-label disagreement."
        ),

    "completed_at":
        datetime.datetime.now()
        .isoformat(),
}


with open(
    APP_MANIFEST_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        app_manifest,
        f,
        indent=2
    )


# ============================================================
# 13. DASHBOARD
# ============================================================

print(
    "\n"
    +
    "=" * 124
)

print(
    "✓ RQ4 APP-LEVEL DESCRIPTIVE HETEROGENEITY — PASS"
)

print(
    "=" * 124
)


print(
    "\nAPP-LEVEL DISAGREEMENT / JSD DESCRIPTION"
)

display(
    app_primary[
        [
            "app",
            "N",
            "clusters",
            "disagreement_percent",
            "mean_jsd_agreement",
            "mean_jsd_disagreement",
            "raw_difference_D1_minus_D0",
            "positive_disagreement_difference",
        ]
    ]
)


print(
    "\nAPP × SEVERITY MEAN JSD"
)

display(
    app_severity[
        [
            "app",
            "N_S0",
            "N_S1",
            "N_S2",
            "mean_S0",
            "mean_S1",
            "mean_S2",
            "S1_gt_S2",
        ]
    ]
)


print(
    "\nCROSS-APP DIRECTIONAL SUMMARY"
)

print(
    "Apps with mean JSD(D=1) > mean JSD(D=0):",
    f"{N_APPS_POSITIVE} / 6"
)

print(
    "All apps positive:",
    ALL_APPS_POSITIVE
)


print(
    "\nSEVERITY SHAPE SUMMARY"
)

print(
    "Apps with mean(S1) > mean(S2):",
    f"{N_APPS_S1_GT_S2} / 6"
)


print(
    "\nPRIMARY H4:",
    h4_manifest["h4_status"],
    "(UNCHANGED)"
)


print(
    "\nIMPORTANT:"
)

print(
    "No app-specific hypothesis tests were performed."
)

print(
    "No app × disagreement interaction was tested."
)

print(
    "This stage is descriptive/exploratory."
)


print(
    "\n"
    +
    "=" * 124
)

print(
    "PRIMARY H4                : CLOSED / SUPPORTED"
)

print(
    "LARGE-CLUSTER SENSITIVITY : CLOSED / PASS"
)

print(
    "SEVERITY EXPLORATORY      : CLOSED / PASS"
)

print(
    "APP-LEVEL DESCRIPTION     : CLOSED / PASS"
)

print(
    "=" * 124
)

print(
    "\nSTOP HERE."
)

print(
    "Next after review: transition-level explanation "
    "of the non-monotonic severity result."
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 78
# FULL CELL SHA256: 03306f1cb563f482e6a8eb1c39cdd99b801ee4d4367771ebf1b7b8b6a6ee2b17
# ============================================================

# ============================================================
# [PHASE3][RQ4 SECONDARY] CELL 68
# SECONDARY PREDICTION DIAGNOSTICS
#
# Components:
# 1. Hard R-vs-V prediction disagreement within each seed
# 2. Paired entropy / max-confidence description
# 3. Within-supervision test Accuracy + Macro-F1
#
# IMPORTANT:
# - SECONDARY / DIAGNOSTIC
# - no new confirmatory hypothesis
# - H4 remains unchanged
#
# Model-R test diagnostic:
#   prediction vs rating_target
#
# Model-V test diagnostic:
#   prediction vs vader_target
#
# NEVER interpret R-vs-V Macro-F1 difference as evidence
# that one weak-label source is superior, because targets differ.
# ============================================================

import json
import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# 1. REQUIRE COMPLETED PRIMARY + EXPLORATORY STAGES
# ============================================================

H4_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_PRIMARY_H4_RESULT.json"
)

TRANSITION_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_TRANSITION_EXPLORATORY_RESULT.json"
)


assert H4_MANIFEST_FILE.exists()
assert TRANSITION_MANIFEST_FILE.exists()


with open(
    H4_MANIFEST_FILE,
    encoding="utf-8"
) as f:
    h4_manifest = json.load(f)


with open(
    TRANSITION_MANIFEST_FILE,
    encoding="utf-8"
) as f:
    transition_manifest = json.load(f)


assert h4_manifest["status"] == "PASS"
assert h4_manifest["h4_status"] == "SUPPORTED"

assert transition_manifest["status"] == "PASS"
assert transition_manifest["primary_h4_changed"] is False


print(
    "✓ Primary H4:",
    h4_manifest["h4_status"]
)

print(
    "✓ Transition exploratory stage:",
    transition_manifest["status"]
)


# ============================================================
# 2. PATHS
# ============================================================

TEST_INFERENCE_ROOT = (
    RQ4_FINAL_ROOT
    /
    "test_inference"
)

TEST_PREDICTION_DIR = (
    TEST_INFERENCE_ROOT
    /
    "predictions"
)


FROZEN_COHORT_FILE = Path(
    "/content/drive/MyDrive/IGAR_Paper1/"
    "phase3/gate5b/data/"
    "IGAR_RQ4_Final_Cohort_150k.parquet"
)


assert FROZEN_COHORT_FILE.exists()


# ============================================================
# 3. LOAD FROZEN TEST METADATA
# ============================================================

meta = pd.read_parquet(
    FROZEN_COHORT_FILE,
    columns=[
        "row_id",
        "split",
        "rating_target",
        "vader_target",
        "disagreement",
        "duplicate_group_id",
    ]
)


meta = (
    meta.loc[
        meta["split"].eq("test")
    ]
    .drop(
        columns="split"
    )
    .copy()
)


assert len(meta) == 22500
assert meta["row_id"].is_unique


meta["row_id"] = (
    meta["row_id"]
    .astype(str)
)

meta["rating_target"] = (
    meta["rating_target"]
    .astype(int)
)

meta["vader_target"] = (
    meta["vader_target"]
    .astype(int)
)

meta["disagreement"] = (
    meta["disagreement"]
    .astype(int)
)


assert set(
    meta["rating_target"].unique()
) == {0, 1, 2}

assert set(
    meta["vader_target"].unique()
) == {0, 1, 2}

assert set(
    meta["disagreement"].unique()
) == {0, 1}


# Canonical row order.
meta = (
    meta.sort_values(
        "row_id",
        kind="mergesort"
    )
    .reset_index(drop=True)
)


canonical_row_ids = (
    meta["row_id"]
    .to_numpy()
)


print(
    "✓ Frozen test metadata loaded:",
    len(meta)
)


# ============================================================
# 4. LOAD ALL SIX PREDICTION ARTIFACTS
# ============================================================

SEEDS = [
    42,
    123,
    2026,
]


predictions = {}


for seed in SEEDS:

    for short_model in [
        "ModelR",
        "ModelV",
    ]:

        run_name = (
            f"seed_{seed}_{short_model}"
        )


        pred_file = (
            TEST_PREDICTION_DIR
            /
            f"{run_name}_test_probabilities.parquet"
        )


        assert pred_file.exists(), (
            f"Missing prediction file: {pred_file}"
        )


        p = pd.read_parquet(
            pred_file,
            columns=[
                "row_id",
                "pred_class_id",
                "max_confidence",
                "entropy_nats",
            ]
        )


        p["row_id"] = (
            p["row_id"]
            .astype(str)
        )


        assert len(p) == 22500

        assert np.array_equal(
            p["row_id"].to_numpy(),
            canonical_row_ids
        )


        assert set(
            p["pred_class_id"]
            .astype(int)
            .unique()
        ).issubset(
            {0, 1, 2}
        )


        predictions[
            (
                seed,
                short_model
            )
        ] = p


print(
    "✓ Six frozen prediction artifacts loaded."
)


# ============================================================
# 5. WITHIN-SUPERVISION TEST DIAGNOSTICS
# ============================================================

metric_rows = []

cm_tables = {}


for seed in SEEDS:

    # --------------------------------------------------------
    # Model-R evaluated ONLY against rating target
    # --------------------------------------------------------

    p_r = predictions[
        (
            seed,
            "ModelR"
        )
    ]


    y_rating = (
        meta["rating_target"]
        .to_numpy(dtype=int)
    )


    pred_r = (
        p_r["pred_class_id"]
        .to_numpy(dtype=int)
    )


    acc_r = accuracy_score(
        y_rating,
        pred_r
    )


    f1_r = f1_score(
        y_rating,
        pred_r,
        labels=[0, 1, 2],
        average="macro",
        zero_division=0,
    )


    cm_r = confusion_matrix(
        y_rating,
        pred_r,
        labels=[0, 1, 2],
    )


    metric_rows.append({

        "seed":
            seed,

        "model":
            "Model-R",

        "supervision_target":
            "rating_target",

        "accuracy":
            float(acc_r),

        "macro_f1":
            float(f1_r),
    })


    cm_tables[
        f"seed_{seed}_ModelR"
    ] = cm_r


    # --------------------------------------------------------
    # Model-V evaluated ONLY against VADER target
    # --------------------------------------------------------

    p_v = predictions[
        (
            seed,
            "ModelV"
        )
    ]


    y_vader = (
        meta["vader_target"]
        .to_numpy(dtype=int)
    )


    pred_v = (
        p_v["pred_class_id"]
        .to_numpy(dtype=int)
    )


    acc_v = accuracy_score(
        y_vader,
        pred_v
    )


    f1_v = f1_score(
        y_vader,
        pred_v,
        labels=[0, 1, 2],
        average="macro",
        zero_division=0,
    )


    cm_v = confusion_matrix(
        y_vader,
        pred_v,
        labels=[0, 1, 2],
    )


    metric_rows.append({

        "seed":
            seed,

        "model":
            "Model-V",

        "supervision_target":
            "vader_target",

        "accuracy":
            float(acc_v),

        "macro_f1":
            float(f1_v),
    })


    cm_tables[
        f"seed_{seed}_ModelV"
    ] = cm_v


within_metrics = pd.DataFrame(
    metric_rows
)


assert len(
    within_metrics
) == 6


# ============================================================
# 6. THREE-SEED SUMMARY
# ============================================================

within_summary = (
    within_metrics
    .groupby(
        [
            "model",
            "supervision_target",
        ],
        observed=True
    )
    .agg(
        accuracy_mean=(
            "accuracy",
            "mean"
        ),
        accuracy_sd=(
            "accuracy",
            "std"
        ),
        macro_f1_mean=(
            "macro_f1",
            "mean"
        ),
        macro_f1_sd=(
            "macro_f1",
            "std"
        ),
    )
    .reset_index()
)


# ============================================================
# 7. HARD R-vs-V PREDICTION DISAGREEMENT
# ============================================================

hard_matrix = []

pair_entropy_matrix = []

pair_confidence_matrix = []


hard_seed_rows = []


for seed in SEEDS:

    p_r = predictions[
        (
            seed,
            "ModelR"
        )
    ]

    p_v = predictions[
        (
            seed,
            "ModelV"
        )
    ]


    pred_r = (
        p_r["pred_class_id"]
        .to_numpy(dtype=int)
    )

    pred_v = (
        p_v["pred_class_id"]
        .to_numpy(dtype=int)
    )


    hard = (
        pred_r != pred_v
    ).astype(
        np.float64
    )


    paired_entropy = (
        0.5
        *
        (
            p_r["entropy_nats"]
            .to_numpy(dtype=np.float64)
            +
            p_v["entropy_nats"]
            .to_numpy(dtype=np.float64)
        )
    )


    paired_confidence = (
        0.5
        *
        (
            p_r["max_confidence"]
            .to_numpy(dtype=np.float64)
            +
            p_v["max_confidence"]
            .to_numpy(dtype=np.float64)
        )
    )


    hard_matrix.append(
        hard
    )

    pair_entropy_matrix.append(
        paired_entropy
    )

    pair_confidence_matrix.append(
        paired_confidence
    )


    for d in [
        0,
        1,
    ]:

        mask = (
            meta["disagreement"]
            .to_numpy(dtype=int)
            ==
            d
        )


        hard_seed_rows.append({

            "seed":
                seed,

            "weak_label_group":
                (
                    "Agreement"
                    if d == 0
                    else
                    "Disagreement"
                ),

            "N":
                int(mask.sum()),

            "hard_RV_prediction_disagreement_rate":
                float(
                    hard[
                        mask
                    ].mean()
                ),

            "mean_paired_entropy_nats":
                float(
                    paired_entropy[
                        mask
                    ].mean()
                ),

            "mean_paired_max_confidence":
                float(
                    paired_confidence[
                        mask
                    ].mean()
                ),
        })


hard_seed_desc = pd.DataFrame(
    hard_seed_rows
)


# ============================================================
# 8. REVIEW-LEVEL THREE-SEED SECONDARY OUTCOMES
# ============================================================

hard_matrix = np.column_stack(
    hard_matrix
)

pair_entropy_matrix = np.column_stack(
    pair_entropy_matrix
)

pair_confidence_matrix = np.column_stack(
    pair_confidence_matrix
)


assert hard_matrix.shape == (
    22500,
    3
)


hard_count = (
    hard_matrix
    .sum(axis=1)
    .astype(int)
)


hard_rate = (
    hard_matrix
    .mean(axis=1)
)


mean_paired_entropy = (
    pair_entropy_matrix
    .mean(axis=1)
)


mean_paired_confidence = (
    pair_confidence_matrix
    .mean(axis=1)
)


assert set(
    np.unique(
        hard_count
    )
).issubset(
    {0, 1, 2, 3}
)


secondary_review = pd.DataFrame({

    "row_id":
        canonical_row_ids,

    "disagreement":
        meta[
            "disagreement"
        ].to_numpy(dtype=int),

    "duplicate_group_id":
        meta[
            "duplicate_group_id"
        ].to_numpy(),

    "hard_RV_disagreement_count_3seeds":
        hard_count,

    "hard_RV_disagreement_rate_3seeds":
        hard_rate,

    "mean_paired_entropy_nats":
        mean_paired_entropy,

    "mean_paired_max_confidence":
        mean_paired_confidence,
})


# ============================================================
# 9. WEAK-LABEL GROUP DESCRIPTIVES
# ============================================================

secondary_group_desc = (
    secondary_review
    .groupby(
        "disagreement",
        observed=True
    )
    .agg(
        N=(
            "row_id",
            "size"
        ),

        mean_hard_RV_prediction_disagreement_rate=(
            "hard_RV_disagreement_rate_3seeds",
            "mean"
        ),

        median_hard_RV_prediction_disagreement_rate=(
            "hard_RV_disagreement_rate_3seeds",
            "median"
        ),

        mean_paired_entropy_nats=(
            "mean_paired_entropy_nats",
            "mean"
        ),

        mean_paired_max_confidence=(
            "mean_paired_max_confidence",
            "mean"
        ),
    )
    .reset_index()
)


secondary_group_desc[
    "group"
] = secondary_group_desc[
    "disagreement"
].map({
    0:
        "Agreement",
    1:
        "Disagreement",
})


# Distribution of number of seeds with hard disagreement.
hard_count_dist = (
    secondary_review
    .groupby(
        [
            "disagreement",
            "hard_RV_disagreement_count_3seeds",
        ],
        observed=True
    )
    .size()
    .rename("N")
    .reset_index()
)


hard_count_dist[
    "percent_within_weak_label_group"
] = (
    100.0
    *
    hard_count_dist["N"]
    /
    hard_count_dist
    .groupby(
        "disagreement"
    )["N"]
    .transform("sum")
)


# ============================================================
# 10. SAVE SECONDARY ARTIFACTS
# ============================================================

SECONDARY_ROOT = (
    RQ4_FINAL_ROOT
    /
    "secondary_diagnostics"
)

SECONDARY_ROOT.mkdir(
    parents=True,
    exist_ok=True
)


WITHIN_METRICS_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Within_Supervision_Test_Diagnostics_By_Seed.csv"
)


WITHIN_SUMMARY_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Within_Supervision_Test_Diagnostics_Three_Seed_Summary.csv"
)


HARD_SEED_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Hard_Prediction_Disagreement_By_Seed.csv"
)


SECONDARY_GROUP_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Secondary_Prediction_Diagnostics_By_Weak_Label_Group.csv"
)


HARD_COUNT_FILE = (
    RQ4_FINAL_DIRS["tables"]
    /
    "RQ4_Hard_Prediction_Disagreement_Seed_Count_Distribution.csv"
)


SECONDARY_REVIEW_FILE = (
    SECONDARY_ROOT
    /
    "RQ4_Secondary_Prediction_Diagnostics_Review_Level.parquet"
)


within_metrics.to_csv(
    WITHIN_METRICS_FILE,
    index=False
)


within_summary.to_csv(
    WITHIN_SUMMARY_FILE,
    index=False
)


hard_seed_desc.to_csv(
    HARD_SEED_FILE,
    index=False
)


secondary_group_desc.to_csv(
    SECONDARY_GROUP_FILE,
    index=False
)


hard_count_dist.to_csv(
    HARD_COUNT_FILE,
    index=False
)


secondary_review.to_parquet(
    SECONDARY_REVIEW_FILE,
    index=False
)


# Save confusion matrices.
for run_name, cm in cm_tables.items():

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
        SECONDARY_ROOT
        /
        f"{run_name}_within_supervision_test_confusion_matrix.csv"
    )


# ============================================================
# 11. MANIFEST
# ============================================================

SECONDARY_MANIFEST_FILE = (
    RQ4_FINAL_DIRS["statistics"]
    /
    "RQ4_SECONDARY_PREDICTION_DIAGNOSTICS.json"
)


secondary_manifest = {

    "status":
        "PASS",

    "analysis_type":
        "SECONDARY_DIAGNOSTIC",

    "stage":
        "RQ4_SECONDARY_PREDICTION_DIAGNOSTICS",

    "final_rq4_protocol_id":
        FINAL_RQ4_PROTOCOL_ID,

    "primary_h4_status":
        h4_manifest[
            "h4_status"
        ],

    "primary_h4_changed":
        False,

    "n_test_reviews":
        22500,

    "seeds":
        SEEDS,

    "hard_prediction_disagreement":
        True,

    "entropy_diagnostic":
        True,

    "max_confidence_diagnostic":
        True,

    "within_supervision_test_metrics":
        True,

    "model_R_evaluation_target":
        "rating_target",

    "model_V_evaluation_target":
        "vader_target",

    "cross_supervision_metric_superiority_claim_allowed":
        False,

    "confirmatory_hypothesis_retested":
        False,

    "interpretation_boundary":
        (
            "Within-supervision Accuracy and Macro-F1 are "
            "diagnostic only. Their magnitudes must not be "
            "used to rank rating-derived versus "
            "translation-mediated VADER supervision because "
            "the evaluation targets differ."
        ),

    "completed_at":
        datetime.datetime.now()
        .isoformat(),
}


with open(
    SECONDARY_MANIFEST_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        secondary_manifest,
        f,
        indent=2
    )


# ============================================================
# 12. DASHBOARD
# ============================================================

print(
    "\n"
    +
    "=" * 124
)

print(
    "✓ RQ4 SECONDARY PREDICTION DIAGNOSTICS — PASS"
)

print(
    "=" * 124
)


print(
    "\nWITHIN-SUPERVISION TEST DIAGNOSTICS — BY SEED"
)

display(
    within_metrics
)


print(
    "\nTHREE-SEED WITHIN-SUPERVISION SUMMARY"
)

display(
    within_summary
)


print(
    "\nHARD R-vs-V PREDICTION DISAGREEMENT — BY SEED"
)

display(
    hard_seed_desc
)


print(
    "\nTHREE-SEED REVIEW-LEVEL SECONDARY DESCRIPTION"
)

display(
    secondary_group_desc[
        [
            "group",
            "N",
            "mean_hard_RV_prediction_disagreement_rate",
            "median_hard_RV_prediction_disagreement_rate",
            "mean_paired_entropy_nats",
            "mean_paired_max_confidence",
        ]
    ]
)


print(
    "\nNUMBER OF SEEDS WITH HARD R-vs-V PREDICTION DISAGREEMENT"
)

display(
    hard_count_dist
)


print(
    "\nPRIMARY H4:",
    h4_manifest[
        "h4_status"
    ],
    "(UNCHANGED)"
)


print(
    "\nINTERPRETATION WARNING"
)

print(
    "Model-R F1 is against rating_target."
)

print(
    "Model-V F1 is against vader_target."
)

print(
    "Do NOT use their difference to claim one "
    "weak-supervision source is more accurate."
)


print(
    "\n"
    +
    "=" * 124
)

print(
    "PRIMARY H4                  : CLOSED / SUPPORTED"
)

print(
    "LARGE-CLUSTER SENSITIVITY   : CLOSED / PASS"
)

print(
    "SEVERITY EXPLORATORY        : CLOSED / PASS"
)

print(
    "APP-LEVEL DESCRIPTION       : CLOSED / PASS"
)

print(
    "TRANSITION-LEVEL EXPLORATORY: CLOSED / PASS"
)

print(
    "SECONDARY PRED. DIAGNOSTICS : CLOSED / PASS"
)

print(
    "=" * 124
)

print(
    "\nSTOP HERE."
)

print(
    "Next after review: freeze RQ4 and construct "
    "paper-ready RQ1-RQ4 result tables / figures."
)


# ============================================================
# ORIGINAL NOTEBOOK CELL INDEX: 104
# FULL CELL SHA256: 72c5ba9b77dc0480d7a72d30a734372cb9453c87454f18562a7dc7a008a118f2
# ============================================================

# ============================================================
# [PAPER 1] CELL 74
# STRICT FORENSIC REPRODUCIBILITY CLOSURE
#
# Purpose:
# 1. Validate exact Cell 60A-60E source extraction.
# 2. Extract actual row_id / duplicate_group_id construction
#    cells, not generic keyword hits.
# 3. Separate locked scientific training environment from
#    current packaging runtime.
# 4. Preserve already-closed data/translation provenance.
# 5. Build STRICT final reproducibility ZIP.
#
# NO scientific computation
# NO training
# NO statistical tests
# NO result modification
# ============================================================

from pathlib import Path
import ast
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap


# ============================================================
# 1. PATHS
# ============================================================

PACKAGE_ROOT = Path(
    "/content/drive/MyDrive/IGAR-Paper1-Reproducibility"
)

PROJECT_ROOT = Path(
    "/content/drive/MyDrive/IGAR_Paper1"
)

NOTEBOOK = Path(
    "/content/drive/MyDrive/Colab Notebooks/Paper1_Phase1_RUN.ipynb"
)

assert PACKAGE_ROOT.exists(), PACKAGE_ROOT
assert PROJECT_ROOT.exists(), PROJECT_ROOT
assert NOTEBOOK.exists(), NOTEBOOK


SRC_DIR = PACKAGE_ROOT / "src"
NOTEBOOK_DIR = PACKAGE_ROOT / "notebooks"
ENV_DIR = PACKAGE_ROOT / "environment"
MANIFEST_DIR = PACKAGE_ROOT / "manifests"
DOCS_DIR = PACKAGE_ROOT / "docs"

for d in [
    SRC_DIR,
    NOTEBOOK_DIR,
    ENV_DIR,
    MANIFEST_DIR,
    DOCS_DIR,
]:
    d.mkdir(parents=True, exist_ok=True)


print("✓ Package root:", PACKAGE_ROOT)
print("✓ Scientific project:", PROJECT_ROOT)
print("✓ Authoritative notebook:", NOTEBOOK)


# ============================================================
# 2. HELPERS
# ============================================================

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(
        text.encode("utf-8")
    )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)

            if not block:
                break

            h.update(block)

    return h.hexdigest()


def atomic_json(path: Path, obj):
    tmp = path.with_suffix(
        path.suffix + ".tmp"
    )

    with tmp.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            obj,
            f,
            indent=2,
            ensure_ascii=False
        )

        f.flush()
        os.fsync(
            f.fileno()
        )

    os.replace(
        tmp,
        path
    )


def write_text_fsync(path: Path, text: str):
    with path.open(
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

        f.flush()
        os.fsync(
            f.fileno()
        )


def cell_source(cell):
    src = cell.get(
        "source",
        ""
    )

    if isinstance(src, list):
        return "".join(src)

    return str(src)


# ============================================================
# 3. LOAD ORIGINAL NOTEBOOK
# ============================================================

with NOTEBOOK.open(
    encoding="utf-8"
) as f:
    nb = json.load(f)


cells = nb.get(
    "cells",
    []
)

code_cells = [
    (i, cell_source(cell))
    for i, cell in enumerate(cells)
    if cell.get("cell_type") == "code"
]


assert len(code_cells) > 0


print(
    "✓ Code cells loaded:",
    len(code_cells)
)

print(
    "✓ Notebook SHA256:",
    sha256_file(NOTEBOOK)
)


# ============================================================
# 4. FORENSIC CELL 60A-60E EXTRACTION
#
# Do NOT rely on broad keyword matching.
# Require explicit CELL 60A ... CELL 60E markers.
# ============================================================

marker_re = re.compile(
    r"(?im)^"
    r"[ \t]*"
    r"(?:#+[ \t]*)?"
    r"(?:\[[^\n]*\][ \t]*)?"
    r"CELL[ \t]+60([A-E])\b[^\n]*$"
)


training_marker_records = []
training_sections = {
    label: []
    for label in [
        "A",
        "B",
        "C",
        "D",
        "E",
    ]
}


for cell_index, src in code_cells:

    matches = list(
        marker_re.finditer(src)
    )

    if not matches:
        continue


    for j, match in enumerate(matches):

        label = match.group(1)

        start = match.start()

        if j + 1 < len(matches):
            end = matches[j + 1].start()
        else:
            end = len(src)

        section = src[
            start:end
        ]


        record = {
            "label":
                f"CELL 60{label}",

            "cell_index":
                int(cell_index),

            "section_start_char":
                int(start),

            "section_end_char":
                int(end),

            "section_chars":
                int(len(section)),

            "section_sha256":
                sha256_text(section),

            "full_cell_sha256":
                sha256_text(src),

            "marker_line":
                match.group(0).strip(),
        }


        training_marker_records.append(
            record
        )

        training_sections[
            label
        ].append(
            {
                **record,
                "source":
                    section,
                "full_cell_source":
                    src,
            }
        )


# Require all five explicit labels.
for label in [
    "A",
    "B",
    "C",
    "D",
    "E",
]:

    assert len(
        training_sections[label]
    ) >= 1, (
        f"Explicit CELL 60{label} marker not found."
    )


print(
    "✓ Explicit Cell 60A-60E markers verified."
)


# ============================================================
# 5. SELECT AUTHORITATIVE MARKER OCCURRENCE
#
# If duplicate marker occurrences exist, choose the longest
# marker-delimited section, while preserving all candidates
# in the manifest.
# ============================================================

selected_training = {}


for label in [
    "A",
    "B",
    "C",
    "D",
    "E",
]:

    candidates = sorted(
        training_sections[label],
        key=lambda x: (
            x["section_chars"],
            -x["cell_index"],
        ),
        reverse=True,
    )

    selected_training[
        label
    ] = candidates[0]


# Cell 60A and 60B may legitimately share one notebook cell.
# What matters is that explicit marker-delimited source
# sections exist.
if (
    selected_training["A"]["cell_index"]
    ==
    selected_training["B"]["cell_index"]
):

    assert (
        selected_training["A"][
            "section_start_char"
        ]
        !=
        selected_training["B"][
            "section_start_char"
        ]
    ), (
        "60A and 60B point to the same exact marker span."
    )

    print(
        "ℹ CELL 60A and CELL 60B share notebook cell",
        selected_training["A"]["cell_index"],
        "but have distinct explicit marker spans."
    )


# ============================================================
# 6. ARCHIVE EXACT TRAINING CELLS
# ============================================================

full_training_cells = {}


for label, item in selected_training.items():

    idx = item[
        "cell_index"
    ]

    full_training_cells[
        idx
    ] = item[
        "full_cell_source"
    ]


training_archive = {
    "source_notebook":
        str(NOTEBOOK),

    "source_notebook_sha256":
        sha256_file(NOTEBOOK),

    "extraction_mode":
        "explicit CELL 60A-60E markers",

    "selected_sections":
        {
            f"CELL 60{k}": {
                key: value
                for key, value in v.items()
                if key not in [
                    "source",
                    "full_cell_source",
                ]
            }
            for k, v
            in selected_training.items()
        },

    "all_marker_candidates":
        training_marker_records,

    "full_original_cells":
        [
            {
                "cell_index":
                    idx,

                "sha256":
                    sha256_text(src),

                "source":
                    src,
            }
            for idx, src
            in sorted(
                full_training_cells.items()
            )
        ],
}


TRAIN_ARCHIVE_JSON = (
    NOTEBOOK_DIR
    /
    "Cell60A_60E_EXACT_SOURCE_ARCHIVE.json"
)


atomic_json(
    TRAIN_ARCHIVE_JSON,
    training_archive
)


# Python archival extract.
training_py_parts = [
    "# ========================================================",
    "# EXACT ARCHIVAL EXTRACT FROM ORIGINAL FINAL COLAB",
    "# DO NOT EDIT",
    f"# Notebook: {NOTEBOOK}",
    f"# Notebook SHA256: {sha256_file(NOTEBOOK)}",
    "# ========================================================",
    "",
]


for idx, src in sorted(
    full_training_cells.items()
):

    training_py_parts.extend([
        "",
        "# ========================================================",
        f"# ORIGINAL NOTEBOOK CODE CELL INDEX: {idx}",
        f"# FULL CELL SHA256: {sha256_text(src)}",
        "# ========================================================",
        "",
        src.rstrip(),
        "",
    ])


TRAIN_EXACT_PY = (
    SRC_DIR
    /
    "08_train_paired_indobert_EXACT_EXTRACT.py"
)


write_text_fsync(
    TRAIN_EXACT_PY,
    "\n".join(
        training_py_parts
    )
)


print(
    "✓ Exact training source archive written."
)


# ============================================================
# 7. FIND TRUE row_id / duplicate_group_id CONSTRUCTION CELLS
#
# Broad keyword count is NOT accepted.
# We look for actual assignment syntax.
# ============================================================

TARGET_COLUMNS = {
    "row_id",
    "duplicate_group_id",
}


def subtree_mentions_string(
    node,
    target_name
):

    for child in ast.walk(node):

        if (
            isinstance(
                child,
                ast.Constant
            )
            and
            child.value
            ==
            target_name
        ):
            return True

        if (
            isinstance(
                child,
                ast.Name
            )
            and
            child.id
            ==
            target_name
        ):
            return True

    return False


def assignment_targets(node):

    if isinstance(
        node,
        ast.Assign
    ):
        return node.targets

    if isinstance(
        node,
        ast.AnnAssign
    ):
        return [
            node.target
        ]

    if isinstance(
        node,
        ast.AugAssign
    ):
        return [
            node.target
        ]

    return []


def assignment_evidence(
    src
):

    evidence = {
        "row_id": [],
        "duplicate_group_id": [],
    }


    try:
        tree = ast.parse(
            src
        )
    except SyntaxError:
        tree = None


    if tree is not None:

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                (
                    ast.Assign,
                    ast.AnnAssign,
                    ast.AugAssign,
                )
            ):

                targets = assignment_targets(
                    node
                )

                for target_name in TARGET_COLUMNS:

                    if any(
                        subtree_mentions_string(
                            target,
                            target_name
                        )
                        for target
                        in targets
                    ):

                        evidence[
                            target_name
                        ].append(
                            {
                                "lineno":
                                    getattr(
                                        node,
                                        "lineno",
                                        None
                                    ),

                                "type":
                                    type(node).__name__,
                            }
                        )


            # DataFrame.assign(row_id=..., duplicate_group_id=...)
            if isinstance(
                node,
                ast.Call
            ):

                for kw in node.keywords:

                    if (
                        kw.arg
                        in TARGET_COLUMNS
                    ):

                        evidence[
                            kw.arg
                        ].append(
                            {
                                "lineno":
                                    getattr(
                                        node,
                                        "lineno",
                                        None
                                    ),

                                "type":
                                    "DataFrame.assign keyword",
                            }
                        )


    # Conservative fallback for notebook code that cannot
    # be parsed because it contains magics.
    for target_name in TARGET_COLUMNS:

        patterns = [
            rf"""[\[\(]\s*["']{re.escape(target_name)}["']\s*[\]\)]\s*=""",
            rf"""\.assign\s*\([^)]*\b{re.escape(target_name)}\s*=""",
            rf"""\b{re.escape(target_name)}\s*=""",
        ]

        if (
            not evidence[target_name]
            and
            any(
                re.search(
                    p,
                    src,
                    flags=re.S
                )
                for p in patterns
            )
        ):

            evidence[
                target_name
            ].append(
                {
                    "lineno":
                        None,

                    "type":
                        "regex_assignment_fallback",
                }
            )


    return evidence


id_assignment_cells = []


for cell_index, src in code_cells:

    evidence = assignment_evidence(
        src
    )

    if (
        evidence["row_id"]
        or
        evidence["duplicate_group_id"]
    ):

        id_assignment_cells.append(
            {
                "cell_index":
                    int(cell_index),

                "row_id_assignment":
                    bool(
                        evidence[
                            "row_id"
                        ]
                    ),

                "duplicate_group_id_assignment":
                    bool(
                        evidence[
                            "duplicate_group_id"
                        ]
                    ),

                "evidence":
                    evidence,

                "source_sha256":
                    sha256_text(src),

                "source":
                    src,
            }
        )


assert any(
    x["row_id_assignment"]
    for x in id_assignment_cells
), "No actual row_id assignment found."


assert any(
    x["duplicate_group_id_assignment"]
    for x in id_assignment_cells
), "No actual duplicate_group_id assignment found."


print(
    "✓ Actual assignment cells found:",
    len(id_assignment_cells)
)


# ============================================================
# 8. RESOLVE FUNCTION DEPENDENCIES
#
# Include user-defined functions called from assignment cells
# so normalization/hash helpers are preserved.
# ============================================================

function_def_cells = {}


for cell_index, src in code_cells:

    try:
        tree = ast.parse(
            src
        )
    except SyntaxError:
        continue


    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            )
        ):

            function_def_cells[
                node.name
            ] = {
                "cell_index":
                    int(cell_index),

                "source":
                    src,
            }


called_functions = set()


for item in id_assignment_cells:

    try:
        tree = ast.parse(
            item["source"]
        )
    except SyntaxError:
        continue


    for node in ast.walk(
        tree
    ):

        if isinstance(
            node,
            ast.Call
        ):

            if isinstance(
                node.func,
                ast.Name
            ):

                called_functions.add(
                    node.func.id
                )


dependency_cells = {}


for name in called_functions:

    if name in function_def_cells:

        info = function_def_cells[
            name
        ]

        dependency_cells[
            info["cell_index"]
        ] = info[
            "source"
        ]


# Union exact source cells.
rowdup_cells = {
    item["cell_index"]:
        item["source"]
    for item in id_assignment_cells
}


rowdup_cells.update(
    dependency_cells
)


# ============================================================
# 9. WRITE EXACT ROW/DUP SOURCE ARCHIVE
# ============================================================

ROWDUP_JSON = (
    NOTEBOOK_DIR
    /
    "row_id_duplicate_group_id_EXACT_SOURCE_ARCHIVE.json"
)


atomic_json(
    ROWDUP_JSON,
    {
        "source_notebook":
            str(NOTEBOOK),

        "source_notebook_sha256":
            sha256_file(NOTEBOOK),

        "selection_rule":
            (
                "actual AST/assignment evidence for row_id or "
                "duplicate_group_id plus directly called "
                "user-defined function dependencies"
            ),

        "assignment_cells":
            [
                {
                    k: v
                    for k, v
                    in item.items()
                    if k != "source"
                }
                for item
                in id_assignment_cells
            ],

        "included_full_cells":
            [
                {
                    "cell_index":
                        idx,

                    "sha256":
                        sha256_text(src),

                    "source":
                        src,
                }
                for idx, src
                in sorted(
                    rowdup_cells.items()
                )
            ],
    }
)


rowdup_py = [
    "# ========================================================",
    "# EXACT row_id / duplicate_group_id SOURCE ARCHIVE",
    "# Extracted from original final Colab",
    "# DO NOT EDIT",
    f"# Notebook: {NOTEBOOK}",
    f"# Notebook SHA256: {sha256_file(NOTEBOOK)}",
    "# ========================================================",
    "",
]


for idx, src in sorted(
    rowdup_cells.items()
):

    rowdup_py.extend([
        "",
        "# ========================================================",
        f"# ORIGINAL NOTEBOOK CODE CELL INDEX: {idx}",
        f"# FULL CELL SHA256: {sha256_text(src)}",
        "# ========================================================",
        "",
        src.rstrip(),
        "",
    ])


ROWDUP_PY = (
    SRC_DIR
    /
    "04_exact_row_duplicate_id_cells.py"
)


write_text_fsync(
    ROWDUP_PY,
    "\n".join(
        rowdup_py
    )
)


print(
    "✓ Exact row/group-ID source archive written."
)


# ============================================================
# 10. ENVIRONMENT FORENSICS
#
# Critical distinction:
# - scientific training/model-stack runtime
# - current packaging/runtime capture
#
# Current transformers/tokenizers MUST NOT overwrite the
# locked training versions.
# ============================================================

def package_version(
    distribution,
    import_name=None
):

    try:
        return importlib.metadata.version(
            distribution
        )
    except Exception:
        pass

    if import_name:

        try:
            module = __import__(
                import_name
            )

            return getattr(
                module,
                "__version__",
                None
            )
        except Exception:
            pass

    return None


current_env = {
    "captured_at":
        datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),

    "scope":
        "CURRENT_PACKAGING_RUNTIME_NOT_TRAINING_LOCK",

    "python":
        sys.version,

    "platform":
        platform.platform(),

    "torch":
        package_version(
            "torch"
        ),

    "transformers":
        package_version(
            "transformers"
        ),

    "accelerate":
        package_version(
            "accelerate"
        ),

    "tokenizers":
        package_version(
            "tokenizers"
        ),

    "safetensors":
        package_version(
            "safetensors"
        ),

    "sentencepiece":
        package_version(
            "sentencepiece"
        ),

    "numpy":
        package_version(
            "numpy"
        ),

    "pandas":
        package_version(
            "pandas"
        ),

    "sklearn":
        package_version(
            "scikit-learn",
            "sklearn"
        ),

    "statsmodels":
        package_version(
            "statsmodels"
        ),
}


try:
    import torch

    current_env.update(
        {
            "cuda_runtime_reported_by_torch":
                torch.version.cuda,

            "cuda_available":
                bool(
                    torch.cuda.is_available()
                ),

            "gpu":
                (
                    torch.cuda.get_device_name(0)
                    if torch.cuda.is_available()
                    else None
                ),
        }
    )

except Exception:
    pass


# Locked scientific training environment from Gate 6A / 6B.
locked_training_env = {
    "scope":
        "LOCKED_SCIENTIFIC_TRAINING_RUNTIME",

    "source":
        "Gate 6A / Gate 6B scientific freeze",

    "python":
        "3.13.15",

    "torch":
        "2.11.0+cu128",

    "cuda":
        "12.8",

    "gpu":
        "Tesla T4",

    "transformers":
        "4.57.6",

    "accelerate":
        "1.14.0",

    "tokenizers":
        "0.22.2",

    "safetensors":
        "0.8.0",

    "sentencepiece":
        "0.2.2",

    "attention_implementation":
        "eager",

    "torch_deterministic_algorithms":
        True,

    "warn_only":
        False,

    "tf32":
        False,

    "protocol_id":
        "5b7ffaa036af",

    "overflow_policy_id":
        "61ec4762487c",
}


# ============================================================
# 11. SEARCH NOTEBOOK OUTPUTS FOR VERSION EVIDENCE
# ============================================================

output_fragments = []


for idx, cell in enumerate(
    cells
):

    for output in cell.get(
        "outputs",
        []
    ):

        text = ""

        if "text" in output:

            val = output["text"]

            text += (
                "".join(val)
                if isinstance(val, list)
                else str(val)
            )


        data = output.get(
            "data",
            {}
        )

        for mime in [
            "text/plain",
            "text/markdown",
        ]:

            if mime in data:

                val = data[mime]

                text += (
                    "".join(val)
                    if isinstance(val, list)
                    else str(val)
                )


        if text.strip():

            output_fragments.append(
                (
                    idx,
                    text
                )
            )


version_evidence_re = re.compile(
    r"(?i)"
    r"(python|torch|pytorch|transformers|accelerate|"
    r"tokenizers|safetensors|sentencepiece|numpy|"
    r"pandas|sklearn|scikit-learn|statsmodels|cuda)"
)


version_evidence = []


for idx, text in output_fragments:

    lines = text.splitlines()

    selected = [
        line
        for line in lines
        if version_evidence_re.search(
            line
        )
    ]

    if selected:

        version_evidence.append(
            {
                "cell_index":
                    int(idx),

                "lines":
                    selected[:100],
            }
        )


ENV_PROVENANCE = {
    "important_note":
        (
            "Current packaging runtime is intentionally "
            "separated from the frozen scientific training "
            "runtime. Current library versions must not "
            "overwrite Gate 6A/6B versions."
        ),

    "scientific_training_runtime_locked":
        locked_training_env,

    "current_packaging_runtime":
        current_env,

    "notebook_output_version_evidence":
        version_evidence,
}


ENV_JSON = (
    ENV_DIR
    /
    "environment_provenance_STRICT.json"
)


atomic_json(
    ENV_JSON,
    ENV_PROVENANCE
)


# Current pip freeze is useful, but explicitly scoped.
PIP_FREEZE = (
    ENV_DIR
    /
    "pip-freeze_CURRENT_PACKAGING_RUNTIME.txt"
)


result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "freeze",
    ],
    capture_output=True,
    text=True,
    check=True,
)


write_text_fsync(
    PIP_FREEZE,
    result.stdout
)


print(
    "✓ Environment provenance separated correctly."
)

print(
    "  Locked training transformers:",
    locked_training_env[
        "transformers"
    ]
)

print(
    "  Current packaging transformers:",
    current_env[
        "transformers"
    ]
)


# ============================================================
# 12. LOAD PREVIOUS DATA-PROVENANCE CLOSURE
# ============================================================

OLD_STATUS = (
    MANIFEST_DIR
    /
    "REPRODUCIBILITY_STATUS.json"
)


assert OLD_STATUS.exists()


with OLD_STATUS.open(
    encoding="utf-8"
) as f:
    old_status = json.load(f)


data_gap = (
    old_status
    .get(
        "gaps",
        {}
    )
    .get(
        "data_translation_provenance",
        {}
    )
)


assert (
    data_gap.get(
        "closed"
    )
    is True
), (
    "Data/translation provenance was not closed "
    "in prior Cell 73."
)


print(
    "✓ Existing data/translation provenance closure verified."
)


# ============================================================
# 13. STRICT CLOSURE CHECKS
# ============================================================

training_checks = {}


for label in [
    "A",
    "B",
    "C",
    "D",
    "E",
]:

    item = selected_training[
        label
    ]

    training_checks[
        f"CELL_60{label}"
    ] = {
        "closed":
            True,

        "cell_index":
            item[
                "cell_index"
            ],

        "marker_line":
            item[
                "marker_line"
            ],

        "section_chars":
            item[
                "section_chars"
            ],

        "section_sha256":
            item[
                "section_sha256"
            ],

        "full_cell_sha256":
            item[
                "full_cell_sha256"
            ],
    }


row_assignment_count = sum(
    x["row_id_assignment"]
    for x in id_assignment_cells
)

dup_assignment_count = sum(
    x["duplicate_group_id_assignment"]
    for x in id_assignment_cells
)


strict_gaps = {

    "exact_cell_60A_60E_source": {
        "closed":
            all(
                x["closed"]
                for x in training_checks.values()
            ),

        "detail":
            training_checks,

        "archive_json":
            str(
                TRAIN_ARCHIVE_JSON
            ),

        "archive_py":
            str(
                TRAIN_EXACT_PY
            ),
    },


    "exact_row_duplicate_id_source": {
        "closed":
            (
                row_assignment_count >= 1
                and
                dup_assignment_count >= 1
            ),

        "detail": {
            "actual_row_id_assignment_cells":
                int(
                    row_assignment_count
                ),

            "actual_duplicate_group_id_assignment_cells":
                int(
                    dup_assignment_count
                ),

            "total_included_source_cells":
                int(
                    len(
                        rowdup_cells
                    )
                ),

            "keyword_hit_count_used_for_closure":
                False,
        },

        "archive_json":
            str(
                ROWDUP_JSON
            ),

        "archive_py":
            str(
                ROWDUP_PY
            ),
    },


    "environment_provenance": {
        "closed":
            True,

        "detail": {
            "training_runtime_locked":
                True,

            "current_runtime_separately_captured":
                True,

            "current_runtime_does_not_override_training_runtime":
                True,

            "training_transformers":
                locked_training_env[
                    "transformers"
                ],

            "current_transformers":
                current_env[
                    "transformers"
                ],

            "training_tokenizers":
                locked_training_env[
                    "tokenizers"
                ],

            "current_tokenizers":
                current_env[
                    "tokenizers"
                ],
        },

        "file":
            str(
                ENV_JSON
            ),
    },


    "data_translation_provenance": {
        "closed":
            True,

        "detail":
            data_gap.get(
                "detail",
                {}
            ),
    },
}


strict_closed = all(
    gap[
        "closed"
    ]
    for gap in strict_gaps.values()
)


assert strict_closed


# ============================================================
# 14. STRICT STATUS MANIFEST
# ============================================================

STRICT_STATUS_FILE = (
    MANIFEST_DIR
    /
    "REPRODUCIBILITY_STATUS_STRICT.json"
)


strict_status = {
    "status":
        "CLOSED",

    "closure_level":
        "STRICT_FORENSIC",

    "closed_at":
        datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),

    "authoritative_notebook":
        str(
            NOTEBOOK
        ),

    "authoritative_notebook_sha256":
        sha256_file(
            NOTEBOOK
        ),

    "gaps":
        strict_gaps,

    "scientific_results_changed":
        False,

    "scientific_results_recomputed":
        False,

    "new_statistical_tests":
        False,

    "training_rerun":
        False,

    "important_environment_scope":
        (
            "Gate 6A/6B versions remain authoritative "
            "for model training; Cell 74 package versions "
            "describe only the current packaging runtime."
        ),
}


atomic_json(
    STRICT_STATUS_FILE,
    strict_status
)


# ============================================================
# 15. FORENSIC README
# ============================================================

FORENSIC_NOTE = (
    DOCS_DIR
    /
    "STRICT_FORENSIC_CLOSURE.md"
)


note = f"""# Strict Forensic Reproducibility Closure

Status: **CLOSED / PASS**

Closed at:

```text
{strict_status["closed_at"]}
