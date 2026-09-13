# AUTHORITATIVE HISTORICAL row_id / duplicate_group_id SOURCE
# Scientific notebook scope: index < 63
# Later packaging/reproducibility cells excluded.


# ========================================================
# ORIGINAL NOTEBOOK CELL INDEX: 5
# SHA256: a41a9b7ed17187f4d0dc182c801290c330840511f0942ab95c84431d726dc8fe
# ========================================================

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


# ========================================================
# ORIGINAL NOTEBOOK CELL INDEX: 25
# SHA256: fae2edebfa813840d8a743f008a48ddf08e21ec70a77bd2896c958e53e96e0b0
# ========================================================

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


# ========================================================
# ORIGINAL NOTEBOOK CELL INDEX: 26
# SHA256: 6c53ebc77fcac6acf0fd9aca4c7dcfbece4569bd4245e41e54666a2e4aec5d07
# ========================================================

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
