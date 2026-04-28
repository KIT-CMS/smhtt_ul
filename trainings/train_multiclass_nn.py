import argparse
import logging
import os
import pickle
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
import tensorflow as tf
from tensorflow.keras import mixed_precision
from sklearn import preprocessing
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)
from tensorflow.keras.layers import BatchNormalization, Concatenate, Dense, Dropout, Input
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam

from src.helper import Keys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="STXS multiclass NN training")
    p.add_argument(
        "--dataset-dir",
        type=str,
        required=True,
        help="Directory containing the feather fold files (e.g. .../folds)",
    )
    p.add_argument(
        "--setup-config",
        type=str,
        default="setup.yaml",
        help="Path to common setup.yaml that defines labels / variables",
    )
    p.add_argument(
        "--output-dir",
        type=str,
        default="output/multiclass_stxs",
        help="Directory to write model, scaler, plots",
    )
    p.add_argument(
        "--fold",
        type=int,
        default=0,
        choices=[0, 1],
        help="Fold to use for training (0 or 1); the other fold is for application",
    )
    p.add_argument(
        "--channel",
        type=str,
        required=True,
        choices=["et", "mt", "tt"],
        help="Decay channel to train on (et, mt, or tt). Each channel trains a separate model.",
    )
    p.add_argument("--epochs", type=int, default=1000, help="Max training epochs")
    p.add_argument("--batch-size", type=int, default=4096, help="Batch size")
    p.add_argument("--early-stopping", type=int, default=50, help="Early stopping patience")
    p.add_argument("--learning-rate", type=float, default=1e-3, help="Initial learning rate")
    p.add_argument("--seed", type=int, default=1234, help="Random seed")
    p.add_argument(
        "--preprocessing",
        type=str,
        default="standard_scaler",
        choices=["standard_scaler", "robust_scaler", "min_max_scaler", "identity"],
        help="Input preprocessing method",
    )
    p.add_argument(
        "--balanced-batches",
        action="store_true",
        default=True,
        help="Use class-balanced mini-batches during training",
    )
    p.add_argument(
        "--no-balanced-batches",
        dest="balanced_batches",
        action="store_false",
    )
    p.add_argument(
        "--class-scheme",
        type=str,
        default="fine",
        choices=["coarse", "fine", "hierarchical"],
        help=(
            "Classification scheme: "
            "'coarse' = production modes (ggH, VBF) + background subtypes (DY, jetFakes, rest); "
            "'fine' = individual STXS bins + background subtypes (DY, jetFakes, rest); "
            "'hierarchical' = both coarse and fine as multi-output (two heads)"
        ),
    )
    p.add_argument(
        "--coarse-loss-weight",
        type=float,
        default=0.3,
        help="Weight of the coarse output loss in hierarchical mode (fine weight = 1 - this). Default 0.3.",
    )
    p.add_argument(
        "--clip-weights",
        type=float,
        default=0,
        help="Clip absolute event weights to this percentile (e.g. 99). 0 = no clipping.",
    )
    p.add_argument(
        "--abs-weights",
        action="store_true",
        default=False,
        help="Take absolute value of weights (useful when negative MC weights cause cancellations)",
    )
    p.add_argument(
        "--equalise-class-weights",
        action="store_true",
        default=False,
        help="Enable class weight equalization. Normalises weights per class so each class has mean |w|=1, "
             "preventing physics cross-sections from drowning signal in loss.",
    )
    p.add_argument(
        "--equalise-era-weights",
        action="store_true",
        default=False,
        help="Enable era weight equalization. Normalises weights per era so each era has mean |w|=1, "
             "preventing high-luminosity eras from dominating training.",
    )
    p.add_argument(
        "--focal-loss",
        action="store_true",
        default=False,
        help="Use focal loss (gamma=2) instead of cross-entropy. "
             "Focuses learning on hard-to-classify examples.",
    )
    p.add_argument(
        "--focal-gamma",
        type=float,
        default=2.0,
        help="Gamma parameter for focal loss (default: 2.0). Higher = more focus on hard examples.",
    )
    p.add_argument(
        "--layers",
        type=str,
        default="256,256,128",
        help="Comma-separated hidden layer sizes (e.g. '256,256,128' or '512,512,256,128').",
    )
    p.add_argument(
        "--dropout",
        type=float,
        default=0.3,
        help="Dropout rate for hidden layers (default: 0.3).",
    )
    p.add_argument(
        "--label-smoothing",
        type=float,
        default=0.0,
        help="Label smoothing factor (e.g. 0.05). Spreads a fraction of the true label "
             "probability uniformly across all classes, reducing overconfidence.",
    )
    p.add_argument(
        "--warmup-epochs",
        type=int,
        default=0,
        help="Number of epochs to linearly warm up the learning rate from ~0 to the target LR. "
             "Useful for large networks to prevent chaotic early updates (e.g. 10-20).",
    )
    p.add_argument(
        "--mixed-precision",
        action="store_true",
        default=False,
        help="Enable mixed-precision (bfloat16) training. Speeds up training on GPUs with Tensor Cores "
             "(Volta/Turing/Ampere/Ada or newer). Uses bfloat16 which is more stable than float16. "
             "The final output layer is kept in float32.",
    )
    p.add_argument(
        "--gpu",
        type=str,
        default=None,
        help="Comma-separated GPU indices to use, e.g. '0' or '0,1'. "
             "Defaults to all visible GPUs. Set to '' to force CPU.",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# GPU configuration
# ---------------------------------------------------------------------------
def setup_gpu(gpu_arg, mixed_precision_flag):
    """Configure GPU visibility, memory growth, and optional mixed precision.

    Returns a tf.distribute.Strategy (MirroredStrategy for multi-GPU,
    OneDeviceStrategy for single GPU/CPU).
    """
    # Select which GPUs are visible
    if gpu_arg is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_arg
        logger.info(f"CUDA_VISIBLE_DEVICES set to '{gpu_arg}'")

    gpus = tf.config.list_physical_devices("GPU")
    if not gpus:
        logger.warning("No GPUs found — training on CPU")
        return tf.distribute.OneDeviceStrategy("/cpu:0")

    logger.info(f"Found {len(gpus)} GPU(s): {[g.name for g in gpus]}")

    if mixed_precision_flag:
        mixed_precision.set_global_policy("mixed_bfloat16")
        logger.info("Mixed precision (bfloat16) enabled")

    if len(gpus) > 1:
        strategy = tf.distribute.MirroredStrategy()
        logger.info(f"Using MirroredStrategy across {strategy.num_replicas_in_sync} GPUs")
    else:
        strategy = tf.distribute.OneDeviceStrategy("/gpu:0")
        logger.info("Using single GPU")

    return strategy


# ---------------------------------------------------------------------------
# Helpers to extract columns from the multi-index feather DataFrames
# ---------------------------------------------------------------------------
def _col(*parts, length=5):
    """Build a tuple column key padded to `length`."""
    return tuple(list(parts) + [""] * (length - len(parts)))


def extract_features(df, variable_names):
    """Return a numpy array of shape (n_events, n_variables) from the Nominal variables."""
    cols = [_col(Keys.NOMINAL, Keys.VARIABLES, v) for v in variable_names]
    missing = [v for v, c in zip(variable_names, cols) if c not in df.columns]
    if missing:
        logger.warning(f"Variables missing in DataFrame (will be dropped): {missing}")
        variable_names = [v for v in variable_names if v not in missing]
        cols = [_col(Keys.NOMINAL, Keys.VARIABLES, v) for v in variable_names]
    return df[cols].values.astype(np.float32), variable_names


def extract_labels(df, label_names):
    """Return (one_hot array, class_names list) from the Labels level."""
    cols = [_col(Keys.LABELS, name) for name in label_names]
    present = [name for name, c in zip(label_names, cols) if c in df.columns]
    cols = [_col(Keys.LABELS, name) for name in present]
    arr = df[cols].values.astype(np.float32)
    return arr, present


def extract_weights(df):
    """Return event weights for training.

    Uses the physics weight from the config (which includes cross-section,
    luminosity, generator weights, etc.). If class_weight is present, it is
    used directly since it already incorporates the nominal weight.
    """
    w_col = _col(Keys.NOMINAL, Keys.WEIGHT)
    cw_col = _col(Keys.NOMINAL, Keys.CLASS_WEIGHT)

    # class_weight from get_class_weights already includes the nominal weight
    # when class_weighted=True, so use it directly to avoid squaring
    if cw_col in df.columns:
        weights = df[cw_col].values.astype(np.float32)
    else:
        weights = df[w_col].values.astype(np.float32)

    return weights


# ---------------------------------------------------------------------------
# Label classification helpers
# ---------------------------------------------------------------------------
def _label_kind(name):
    """Classify a label name as signal-bin, signal-inclusive, or background subtype."""
    if name.startswith("is_ggh_htautau_bin"):
        return "ggh_bin"
    if name == "is_ggh_htautau":
        return "ggh_inclusive"
    if name.startswith("is_vbf_htautau_bin"):
        return "vbf_bin"
    if name == "is_vbf_htautau":
        return "vbf_inclusive"
    if name == "is_dyjets":
        return "bkg_dyjets_tt"
    if name == "is_dy_zl":
        return "bkg_dyjets_ll"
    if name.lower() in ("is_jetfakes", "is_jetfake"):
        return "bkg_jetfakes"
    if name == "is_data":
        return "iso_data"  # signal-region data: not a training class, used only for plot overlay
    return "bkg_rest"


def get_all_raw_classes(setup_cfg):
    """Return the full ordered list of class names from setup.yaml renaming_map."""
    renaming_map = (
        setup_cfg
        .get("dataset_modifications", {})
        .get("labels", {})
        .get("renaming_map", {})
    )
    if not renaming_map:
        raise ValueError("No renaming_map found in setup config")
    return list(renaming_map.keys())


def build_class_scheme(raw_classes, scheme, channel="mt"):
    """
    Build the target class list(s) and a mapping from raw → target indices.

    Parameters
    ----------
    raw_classes : list of str
    scheme : str  'coarse', 'fine', or 'hierarchical'
    channel : str
        Decay channel ('et', 'mt', 'tt').  In the tt channel, Z→ll (dy_zl) is
        folded into is_background_rest because it barely passes the tt selection
        and is unlearnable as a separate class.

    Returns
    -------
    If scheme in ('coarse', 'fine'):
        (target_classes, merge_map)  where merge_map[raw_idx] = target_idx
    If scheme == 'hierarchical':
        ((coarse_classes, coarse_map), (fine_classes, fine_map))
    """
    kinds = [_label_kind(c) for c in raw_classes]

    # --- coarse classes: production modes + background subtypes ----
    coarse_classes = []
    coarse_map = {}  # raw_idx -> coarse_idx
    coarse_lut = {}  # kind -> coarse_idx
    for ri, (name, kind) in enumerate(zip(raw_classes, kinds)):
        if kind in ("ggh_bin", "ggh_inclusive"):
            target = "is_ggh_htautau"
        elif kind in ("vbf_bin", "vbf_inclusive"):
            target = "is_vbf_htautau"
        elif kind == "bkg_dyjets_tt":
            target = "is_dyjets"          # Z→ττ
        elif kind == "bkg_dyjets_ll":
            target = "is_background_rest" if channel == "tt" else "is_dy_zl"
        elif kind == "bkg_jetfakes":
            target = "is_jetFakes"
        elif kind == "iso_data":
            continue  # iso data overlay: not a training class, skip
        else:  # bkg_rest: ttbar, diboson, etc.
            target = "is_background_rest"
        if target not in coarse_lut:
            coarse_lut[target] = len(coarse_classes)
            coarse_classes.append(target)
        coarse_map[ri] = coarse_lut[target]

    # --- fine classes: individual STXS bins + background subtypes ----
    fine_classes = []
    fine_map = {}  # raw_idx -> fine_idx
    fine_lut = {}
    for ri, (name, kind) in enumerate(zip(raw_classes, kinds)):
        if kind in ("ggh_bin", "vbf_bin"):
            target = name  # keep individual bin
        elif kind in ("ggh_inclusive", "vbf_inclusive"):
            # inclusive label overlaps with bins — skip as its own class;
            # events with only the inclusive flag land in their production-mode bin
            # via coarse; for fine, treat them the same as their production mode
            target = name  # keep as separate fine class (events not in any bin)
        elif kind == "bkg_dyjets_tt":
            target = "is_dyjets"          # Z→ττ
        elif kind == "bkg_dyjets_ll":
            target = "is_background_rest" if channel == "tt" else "is_dy_zl"
        elif kind == "bkg_jetfakes":
            target = "is_jetFakes"
        elif kind == "iso_data":
            continue  # iso data overlay: not a training class, skip
        else:  # bkg_rest: ttbar, diboson, etc.
            target = "is_background_rest"
        if target not in fine_lut:
            fine_lut[target] = len(fine_classes)
            fine_classes.append(target)
        fine_map[ri] = fine_lut[target]

    if scheme == "coarse":
        return coarse_classes, coarse_map
    elif scheme == "fine":
        return fine_classes, fine_map
    elif scheme == "hierarchical":
        return (coarse_classes, coarse_map), (fine_classes, fine_map)
    else:
        raise ValueError(f"Unknown class scheme: {scheme}")


def remap_labels(Y_raw, merge_map, n_target):
    """
    Remap a one-hot label array from raw classes to target classes.

    Parameters
    ----------
    Y_raw : ndarray (N, n_raw)
    merge_map : dict  raw_idx -> target_idx
    n_target : int  number of target classes

    Returns
    -------
    Y_target : ndarray (N, n_target)
    """
    N = Y_raw.shape[0]
    Y_target = np.zeros((N, n_target), dtype=np.float32)
    for raw_idx, target_idx in merge_map.items():
        if raw_idx < Y_raw.shape[1]:
            Y_target[:, target_idx] = np.maximum(Y_target[:, target_idx], Y_raw[:, raw_idx])
    # Re-normalise rows so each event sums to 1 (handles merged overlapping labels)
    row_sums = Y_target.sum(axis=1, keepdims=True).clip(min=1e-12)
    Y_target = Y_target / row_sums
    return Y_target


# ---------------------------------------------------------------------------
# Derive variable list from setup.yaml (physics variables only, no flags)
# ---------------------------------------------------------------------------
def get_training_variables(setup_cfg):
    """Return the list of physics variables (exclude is_* flags)."""
    return [v for v in setup_cfg.get("training_variables", []) if not v.startswith("is_")]


def get_era_variables(setup_cfg):
    """Return the list of era flag variable names (is_20*)."""
    return [v for v in setup_cfg.get("training_variables", []) if v.startswith("is_20")]


def extract_era_features(df, era_names):
    """Return era one-hot array (n_events, n_eras) from the Nominal variables."""
    cols = [_col(Keys.NOMINAL, Keys.VARIABLES, v) for v in era_names]
    present = [n for n, c in zip(era_names, cols) if c in df.columns]
    cols = [_col(Keys.NOMINAL, Keys.VARIABLES, v) for v in present]
    return df[cols].values.astype(np.float32), present


# ---------------------------------------------------------------------------
# Learning-rate warmup callback
# ---------------------------------------------------------------------------
class WarmupSchedule(tf.keras.callbacks.Callback):
    """Linearly ramp LR from a small value to the target over `warmup_epochs`."""

    def __init__(self, target_lr, warmup_epochs):
        super().__init__()
        self.target_lr = target_lr
        self.warmup_epochs = warmup_epochs

    def on_epoch_begin(self, epoch, logs=None):
        if epoch < self.warmup_epochs:
            lr = self.target_lr * (epoch + 1) / self.warmup_epochs
            self.model.optimizer.learning_rate.assign(lr)


# ---------------------------------------------------------------------------
# Focal loss (focuses on hard-to-classify examples)
# ---------------------------------------------------------------------------
def categorical_focal_loss(gamma=2.0):
    """Focal loss for multiclass classification.

    FL(p_t) = -(1 - p_t)^gamma * log(p_t)
    When gamma=0, equivalent to standard cross-entropy.
    """
    def focal_loss(y_true, y_pred):
        y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0 - 1e-7)
        cross_entropy = -y_true * tf.math.log(y_pred)
        weight = tf.pow(1.0 - y_pred, gamma) * y_true
        loss = weight * cross_entropy
        return tf.reduce_sum(loss, axis=-1)
    return focal_loss


# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------
def _build_backbone(inputs, layer_sizes=(256, 256, 128), dropout=0.3):
    """Shared hidden layers for all classification schemes."""
    x = inputs
    for i, units in enumerate(layer_sizes):
        x = Dense(units, activation="relu", kernel_initializer="glorot_normal")(x)
        x = BatchNormalization()(x)
        # Slightly lower dropout for the last layer
        drop = dropout * 0.67 if i == len(layer_sizes) - 1 else dropout
        x = Dropout(drop)(x)
    return x


def build_model(n_physics, n_eras, n_classes, learning_rate=1e-3,
                layer_sizes=(256, 256, 128), dropout=0.3,
                focal_loss=False, focal_gamma=2.0):
    """
    Single-output multiclass NN (coarse or fine scheme) with era conditioning.
    """
    inp_physics = Input(shape=(n_physics,), name="physics_input")
    inp_era = Input(shape=(n_eras,), name="era_input")
    x = Concatenate()([inp_physics, inp_era])
    x = _build_backbone(x, layer_sizes=layer_sizes, dropout=dropout)
    out = Dense(n_classes, activation="softmax", kernel_initializer="glorot_normal", dtype="float32")(x)
    model = Model(inputs={"physics_input": inp_physics, "era_input": inp_era}, outputs=out)
    loss_fn = categorical_focal_loss(focal_gamma) if focal_loss else "categorical_crossentropy"
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss=loss_fn,
        weighted_metrics=["categorical_accuracy"],
    )
    return model


def build_hierarchical_model(
    n_physics, n_eras, n_coarse, n_fine, learning_rate=1e-3, coarse_loss_weight=0.3,
    layer_sizes=(256, 256, 128), dropout=0.3,
    focal_loss=False, focal_gamma=2.0,
):
    """
    Multi-output NN with a shared backbone, era conditioning, and two classification heads:
      * 'coarse': production-mode level (ggH, VBF, background)
      * 'fine':   individual STXS bins + background
    """
    inp_physics = Input(shape=(n_physics,), name="physics_input")
    inp_era = Input(shape=(n_eras,), name="era_input")
    x = Concatenate()([inp_physics, inp_era])
    x = _build_backbone(x, layer_sizes=layer_sizes, dropout=dropout)
    coarse_out = Dense(
        n_coarse, activation="softmax", name="coarse",
        kernel_initializer="glorot_normal", dtype="float32",
    )(x)
    fine_out = Dense(
        n_fine, activation="softmax", name="fine",
        kernel_initializer="glorot_normal", dtype="float32",
    )(x)
    model = Model(inputs={"physics_input": inp_physics, "era_input": inp_era}, outputs={"coarse": coarse_out, "fine": fine_out})
    loss_fn = categorical_focal_loss(focal_gamma) if focal_loss else "categorical_crossentropy"
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss={"coarse": loss_fn, "fine": loss_fn},
        loss_weights={"coarse": coarse_loss_weight, "fine": 1.0 - coarse_loss_weight},
        weighted_metrics=["categorical_accuracy"],
    )
    return model


# ---------------------------------------------------------------------------
# Balanced batch generator (like the existing balanced-batch approach)
# ---------------------------------------------------------------------------
class BalancedBatchGenerator(tf.keras.utils.Sequence):
    """
    Yields batches where every class contributes an equal number of events,
    sampled randomly with replacement from that class.

    For the hierarchical scheme, balancing is done on the *fine* labels
    and both coarse and fine label arrays are returned per batch.
    """

    def __init__(self, X_phys, X_era, Y, W, n_per_class, steps_per_epoch, rng,
                 Y_coarse=None):
        super().__init__()
        self.X_phys = X_phys
        self.X_era = X_era
        self.Y = Y          # fine (or single-output) labels
        self.W = W
        self.Y_coarse = Y_coarse  # only set for hierarchical
        self.n_classes = Y.shape[1]
        self.n_per_class = n_per_class
        self.steps = steps_per_epoch
        self.rng = rng
        self.class_indices = {
            c: np.where(np.argmax(Y, axis=1) == c)[0] for c in range(self.n_classes)
        }

    def __len__(self):
        return self.steps

    def __getitem__(self, _idx):
        indices = []
        for c in range(self.n_classes):
            pool = self.class_indices[c]
            if len(pool) == 0:
                continue
            idx = self.rng.choice(pool, size=self.n_per_class, replace=True)
            indices.append(idx)
        indices = np.concatenate(indices)
        self.rng.shuffle(indices)
        x_input = {"physics_input": self.X_phys[indices], "era_input": self.X_era[indices]}
        if self.Y_coarse is not None:
            return (
                x_input,
                {"coarse": self.Y_coarse[indices], "fine": self.Y[indices]},
                {"coarse": self.W[indices], "fine": self.W[indices]},
            )
        return x_input, self.Y[indices], self.W[indices]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()
    t0 = time.time()

    # ── GPU setup ────────────────────────────────────────────────────────
    strategy = setup_gpu(args.gpu, args.mixed_precision)

    np.random.seed(args.seed)
    tf.random.set_seed(args.seed)
    rng = np.random.RandomState(args.seed)

    # Output directory (channel-specific)
    out = Path(args.output_dir) / args.channel
    out.mkdir(parents=True, exist_ok=True)

    # ── Load setup config ────────────────────────────────────────────────
    with open(args.setup_config, "r") as f:
        setup_cfg = yaml.safe_load(f)

    raw_classes = get_all_raw_classes(setup_cfg)
    variable_names = get_training_variables(setup_cfg)
    era_variable_names = get_era_variables(setup_cfg)
    logger.info(f"Raw label classes from config ({len(raw_classes)}): {raw_classes}")
    logger.info(f"Training variables ({len(variable_names)}): {variable_names}")
    logger.info(f"Era conditioning variables ({len(era_variable_names)}): {era_variable_names}")
    logger.info(f"Channel: {args.channel}")
    logger.info(f"Classification scheme: {args.class_scheme}")

    scheme_result = build_class_scheme(raw_classes, args.class_scheme, channel=args.channel)
    hierarchical = args.class_scheme == "hierarchical"

    # ── Load fold data ───────────────────────────────────────────────────
    fold = args.fold
    ch = args.channel
    dataset_dir = Path(args.dataset_dir)

    # Per-process files contain channel info in filenames; filter by channel.
    # Combined files (fold0.feather) mix all channels and cannot be filtered.
    train_glob = sorted(dataset_dir.glob(f"__fold{fold}_training__{ch}_*.feather"))
    val_glob = sorted(dataset_dir.glob(f"__fold{fold}_validation__{ch}_*.feather"))
    full_glob = sorted(dataset_dir.glob(f"__fold{fold}__{ch}_*.feather"))

    if train_glob and val_glob:
        logger.info(f"Loading {len(train_glob)} training and {len(val_glob)} validation files for channel '{ch}'")
        df_train = pd.concat([pd.read_feather(str(f)) for f in train_glob], ignore_index=True)
        df_val = pd.concat([pd.read_feather(str(f)) for f in val_glob], ignore_index=True)
    elif full_glob:
        logger.info(f"Loading {len(full_glob)} full fold files for channel '{ch}' (75/25 split)")
        df_full = pd.concat([pd.read_feather(str(f)) for f in full_glob], ignore_index=True)
        n = len(df_full)
        idx = rng.permutation(n)
        split = int(0.75 * n)
        df_train = df_full.iloc[idx[:split]].reset_index(drop=True)
        df_val = df_full.iloc[idx[split:]].reset_index(drop=True)
        del df_full
    else:
        raise FileNotFoundError(
            f"No per-process fold data found for channel '{ch}' in {dataset_dir}. "
            f"Expected __fold{fold}[_training/_validation]__{ch}_*.feather"
        )

    # Restore MultiIndex columns (stored as tuples in feather)
    df_train.columns = pd.MultiIndex.from_tuples(df_train.columns)
    df_val.columns = pd.MultiIndex.from_tuples(df_val.columns)

    logger.info(f"Training set size: {len(df_train)}")
    logger.info(f"Validation set size: {len(df_val)}")

    # ── Extract arrays ───────────────────────────────────────────────────
    X_train, variable_names = extract_features(df_train, variable_names)
    X_val, _ = extract_features(df_val, variable_names)

    # ── Extract era conditioning ─────────────────────────────────────────
    E_train, era_variable_names = extract_era_features(df_train, era_variable_names)
    E_val, _ = extract_era_features(df_val, era_variable_names)
    logger.info(f"Era conditioning: {E_train.shape[1]} era flags present: {era_variable_names}")

    # ── Data quality checks ──────────────────────────────────────────────
    n_nan_train = np.isnan(X_train).sum()
    n_inf_train = np.isinf(X_train).sum()
    n_nan_val = np.isnan(X_val).sum()
    n_inf_val = np.isinf(X_val).sum()
    if n_nan_train > 0 or n_inf_train > 0:
        logger.warning(f"TRAINING features contain {n_nan_train} NaNs and {n_inf_train} Infs!")
        logger.warning("Replacing NaN/Inf with 0 — check your ntuples for corrupt branches")
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=0.0, neginf=0.0)
    if n_nan_val > 0 or n_inf_val > 0:
        logger.warning(f"VALIDATION features contain {n_nan_val} NaNs and {n_inf_val} Infs!")
        X_val = np.nan_to_num(X_val, nan=0.0, posinf=0.0, neginf=0.0)

    # Per-variable stats to spot problematic features
    for iv, vname in enumerate(variable_names):
        col = X_train[:, iv]
        if np.std(col) == 0:
            logger.warning(f"Variable '{vname}' has ZERO variance (constant) — consider removing it")
        elif np.std(col) > 1e6:
            logger.warning(f"Variable '{vname}' has very large std={np.std(col):.2e} — may dominate training")

    Y_train_raw, present_raw = extract_labels(df_train, raw_classes)
    Y_val_raw, _ = extract_labels(df_val, raw_classes)

    # Rebuild scheme based on actually present raw labels
    if set(present_raw) != set(raw_classes):
        logger.warning(f"Some raw classes missing in data. Present: {present_raw}")
        raw_classes = present_raw
        scheme_result = build_class_scheme(raw_classes, args.class_scheme, channel=args.channel)

    # ── Remap labels to the chosen scheme ────────────────────────────────
    if hierarchical:
        (coarse_classes, coarse_map), (fine_classes, fine_map) = scheme_result
        Y_train_coarse = remap_labels(Y_train_raw, coarse_map, len(coarse_classes))
        Y_val_coarse = remap_labels(Y_val_raw, coarse_map, len(coarse_classes))
        Y_train = remap_labels(Y_train_raw, fine_map, len(fine_classes))
        Y_val = remap_labels(Y_val_raw, fine_map, len(fine_classes))
        class_names = fine_classes  # primary class list for logging
        coarse_names = coarse_classes
        logger.info(f"Coarse classes ({len(coarse_classes)}): {coarse_classes}")
        logger.info(f"Fine classes ({len(fine_classes)}): {fine_classes}")
    else:
        target_classes, merge_map = scheme_result
        Y_train = remap_labels(Y_train_raw, merge_map, len(target_classes))
        Y_val = remap_labels(Y_val_raw, merge_map, len(target_classes))
        class_names = target_classes
        logger.info(f"Target classes ({len(class_names)}): {class_names}")

    del Y_train_raw, Y_val_raw

    # ── Label smoothing ──────────────────────────────────────────────────
    if args.label_smoothing > 0:
        eps = args.label_smoothing
        n_cls = Y_train.shape[1]
        logger.info(f"Applying label smoothing eps={eps} across {n_cls} classes")
        Y_train = Y_train * (1 - eps) + eps / n_cls
        Y_val = Y_val * (1 - eps) + eps / n_cls
        if hierarchical:
            n_coarse_cls = Y_train_coarse.shape[1]
            Y_train_coarse = Y_train_coarse * (1 - eps) + eps / n_coarse_cls
            Y_val_coarse = Y_val_coarse * (1 - eps) + eps / n_coarse_cls

    # ── Label sanity check ───────────────────────────────────────────────
    row_sums = Y_train.sum(axis=1)
    n_no_label = (row_sums < 0.5).sum()  # after normalisation, unlabelled rows sum to ~0
    n_multi_label = 0  # remapped labels are normalised, so check argmax consistency
    if n_no_label > 0:
        logger.warning(f"{n_no_label} training events have NO label (all zeros) — they contribute to loss but teach nothing")

    W_train = extract_weights(df_train)
    W_val = extract_weights(df_val)

    # ── Identify data events and their selection region ──────────────────
    # Anti-iso data (is_data=1, anti-iso region): jetFakes proxy — STAYS in training.
    # Iso data   (is_data=1, nominal/iso region): signal-region data — excluded from
    #   training and val-loss monitoring; scored by model.predict for data overlay in
    #   background score plots (requires `is_data: nominal` in setup.yaml selections).
    # Keys.CUT ("cut") is a tuple element distinct from Keys.ANTI_ISO_CUT ("anti_iso_cut")
    # so `Keys.CUT in col_tuple` correctly identifies only iso-cut columns.
    _data_col = _col(Keys.NOMINAL, Keys.VARIABLES, "is_data")
    _is_data_tr = (
        df_train[_data_col].values.astype(bool)
        if _data_col in df_train.columns
        else np.zeros(len(df_train), dtype=bool)
    )
    _is_data_va = (
        df_val[_data_col].values.astype(bool)
        if _data_col in df_val.columns
        else np.zeros(len(df_val), dtype=bool)
    )
    _in_iso_tr = np.zeros(len(df_train), dtype=bool)
    for c in [c for c in df_train.columns if Keys.CUT in c]:
        _in_iso_tr |= df_train[c].values.astype(bool)
    _in_iso_va = np.zeros(len(df_val), dtype=bool)
    for c in [c for c in df_val.columns if Keys.CUT in c]:
        _in_iso_va |= df_val[c].values.astype(bool)

    is_iso_data_train = _is_data_tr & _in_iso_tr
    is_iso_data_val   = _is_data_va & _in_iso_va
    mc_val            = ~_is_data_va   # MC-only mask for val loss and diagnostic plots

    logger.info(
        f"Training fold: {int(is_iso_data_train.sum())} iso data excluded; "
        f"{int(_is_data_tr.sum()) - int(is_iso_data_train.sum())} anti-iso data kept (jetFakes); "
        f"{int((~_is_data_tr).sum())} MC events"
    )
    logger.info(
        f"Validation fold: {int(is_iso_data_val.sum())} iso data (plot overlay); "
        f"{int(_is_data_va.sum()) - int(is_iso_data_val.sum())} anti-iso data; "
        f"{int((~_is_data_va).sum())} MC events"
    )
    del _is_data_tr, _in_iso_tr, _in_iso_va

    # Free DataFrames — all needed arrays have been extracted
    del df_train, df_val

    # ── Exclude iso-region data from training ─────────────────────────────
    # Anti-iso data (jetFakes proxy) remains in X_train.
    # X_val / E_val kept intact so model.predict can score iso data for plots.
    if is_iso_data_train.sum() > 0:
        logger.info(f"Removing {int(is_iso_data_train.sum())} iso data events from training")
        keep = ~is_iso_data_train
        X_train = X_train[keep]
        E_train = E_train[keep]
        Y_train = Y_train[keep]
        W_train = W_train[keep]
        if hierarchical:
            Y_train_coarse = Y_train_coarse[keep]
        del keep
    del is_iso_data_train

    # ── Weight diagnostics and fixes ─────────────────────────────────────
    n_neg_w = (W_train < 0).sum()
    n_zero_w = (W_train == 0).sum()
    n_nan_w = np.isnan(W_train).sum()
    if n_nan_w > 0:
        logger.warning(f"{n_nan_w} NaN weights found — setting to 0")
        W_train = np.nan_to_num(W_train, nan=0.0)
        W_val = np.nan_to_num(W_val, nan=0.0)
    if n_neg_w > 0:
        logger.warning(f"{n_neg_w}/{len(W_train)} training events have NEGATIVE weights ({100*n_neg_w/len(W_train):.1f}%)")
        if args.abs_weights:
            logger.info("Taking |weight| as requested by --abs-weights")
            W_train = np.abs(W_train)
            W_val = np.abs(W_val)
    if n_zero_w > 0:
        logger.warning(f"{n_zero_w} training events have ZERO weight")

    if args.clip_weights > 0:
        threshold = np.percentile(np.abs(W_train[W_train != 0]), args.clip_weights)
        n_clipped = (np.abs(W_train) > threshold).sum()
        logger.info(f"Clipping weights to {args.clip_weights}th percentile (|w| <= {threshold:.4f}), affects {n_clipped} events")
        W_train = np.clip(W_train, -threshold, threshold)
        W_val = np.clip(W_val, -threshold, threshold)

    # Normalize weights: scale so that mean |weight| = 1 for training stability
    mean_abs_w = np.mean(np.abs(W_train))
    if mean_abs_w > 0:
        W_train = W_train / mean_abs_w
        W_val = W_val / mean_abs_w

    # Per-class weight equalisation: rescale so each class has the same
    # mean |weight|.  Without this, physics cross-section differences make
    # background events dominate the loss even with balanced batches.
    if args.equalise_class_weights:
        logger.info("Equalising per-class mean |weight| across classes")
        y_idx_train = np.argmax(Y_train, axis=1)
        y_idx_val = np.argmax(Y_val, axis=1)
        for ci in range(Y_train.shape[1]):
            mask_tr = y_idx_train == ci
            mask_va = y_idx_val == ci
            if mask_tr.any():
                mean_w_cls = np.mean(np.abs(W_train[mask_tr]))
                if mean_w_cls > 0:
                    W_train[mask_tr] /= mean_w_cls
                    if mask_va.any():
                        W_val[mask_va] /= mean_w_cls

    # Per-era weight equalisation: rescale so each era has the same
    # mean |weight|. Without this, high-luminosity eras dominate training.
    if args.equalise_era_weights:
        logger.info("Equalising per-era mean |weight| across eras")
        for ei, era_name in enumerate(era_variable_names):
            # Training set
            mask_tr = E_train[:, ei] == 1
            if mask_tr.any():
                mean_w_era = np.mean(np.abs(W_train[mask_tr]))
                if mean_w_era > 0:
                    W_train[mask_tr] /= mean_w_era
            # Validation set
            mask_va = E_val[:, ei] == 1
            if mask_va.any():
                mean_w_era = np.mean(np.abs(W_val[mask_va]))
                if mean_w_era > 0:
                    W_val[mask_va] /= mean_w_era

    logger.info("Using cross-section weights from config (includes xsec, lumi, gen weights)")

    # Log weight statistics per class (fine / primary classes)
    def _log_class_stats(names, Y, W, tag=""):
        for i, name in enumerate(names):
            mask = np.argmax(Y, axis=1) == i
            if mask.any():
                w_cls = W[mask]
                n_neg_cls = (w_cls < 0).sum()
                logger.info(
                    f"  {tag}{name}: n={mask.sum()}, sum(w)={w_cls.sum():.2f}, "
                    f"mean(w)={w_cls.mean():.4f}, std(w)={w_cls.std():.4f}, "
                    f"min(w)={w_cls.min():.4f}, max(w)={w_cls.max():.4f}, "
                    f"neg_w={n_neg_cls}"
                )
            else:
                logger.warning(f"  {tag}{name}: EMPTY class — 0 training events!")

    _log_class_stats(class_names, Y_train, W_train)
    if hierarchical:
        _log_class_stats(coarse_names, Y_train_coarse, W_train, tag="[coarse] ")

    n_classes = Y_train.shape[1]
    n_vars = X_train.shape[1]
    n_eras = E_train.shape[1]
    logger.info(f"Input dimensions: {n_vars} physics variables + {n_eras} era conditions, {n_classes} fine classes")
    if hierarchical:
        logger.info(f"  + {len(coarse_names)} coarse classes")

    # Log per-class event counts
    for i, name in enumerate(class_names):
        mask_tr = np.argmax(Y_train, axis=1) == i
        mask_va = np.argmax(Y_val, axis=1) == i
        logger.info(f"  {name}: train={mask_tr.sum()}, val={mask_va.sum()}")

    # Log per-era event counts and weights
    logger.info("Era statistics:")
    for ei, era_name in enumerate(era_variable_names):
        mask_tr = E_train[:, ei] == 1
        mask_va = E_val[:, ei] == 1
        if mask_tr.any():
            w_tr = W_train[mask_tr]
            logger.info(
                f"  {era_name}: train_n={mask_tr.sum()}, train_sum(w)={w_tr.sum():.2f}, "
                f"train_mean(w)={w_tr.mean():.4f}, val_n={mask_va.sum()}"
            )
        else:
            logger.warning(f"  {era_name}: NO training events for this era!")

    # mc_val (MC-only, no data) used for val loss and diagnostic plots.
    # is_iso_data_val (iso/signal-region data) used as overlay in background score plots.

    # ── Preprocessing ────────────────────────────────────────────────────
    if args.preprocessing == "standard_scaler":
        scaler = preprocessing.StandardScaler().fit(X_train)
    elif args.preprocessing == "robust_scaler":
        scaler = preprocessing.RobustScaler().fit(X_train)
    elif args.preprocessing == "min_max_scaler":
        scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1)).fit(X_train)
    elif args.preprocessing == "identity":
        scaler = preprocessing.StandardScaler().fit(X_train)
        scaler.mean_[:] = 0.0
        scaler.scale_[:] = 1.0
    else:
        raise ValueError(f"Unknown preprocessing: {args.preprocessing}")

    X_train = scaler.transform(X_train).astype(np.float32)
    X_val = scaler.transform(X_val).astype(np.float32)

    scaler_path = out / f"fold{fold}_scaler.pickle"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    logger.info(f"Saved preprocessing to {scaler_path}")

    # Save class names and variable list for later inference
    meta = {
        "class_names": class_names,
        "variable_names": variable_names,
        "era_variable_names": era_variable_names,
        "channel": args.channel,
        "fold": fold,
        "preprocessing": args.preprocessing,
        "class_scheme": args.class_scheme,
    }
    if hierarchical:
        meta["coarse_class_names"] = coarse_names
    meta_path = out / f"fold{fold}_meta.yaml"
    with open(meta_path, "w") as f:
        yaml.dump(meta, f, default_flow_style=False)
    logger.info(f"Saved metadata to {meta_path}")

    # ── Build model ──────────────────────────────────────────────────────
    layer_sizes = tuple(int(x) for x in args.layers.split(","))
    logger.info(f"Network architecture: {layer_sizes}, dropout={args.dropout}, focal_loss={args.focal_loss}")
    with strategy.scope():
        if hierarchical:
            model = build_hierarchical_model(
                n_vars, n_eras, len(coarse_names), n_classes,
                learning_rate=args.learning_rate,
                coarse_loss_weight=args.coarse_loss_weight,
                layer_sizes=layer_sizes,
                dropout=args.dropout,
                focal_loss=args.focal_loss,
                focal_gamma=args.focal_gamma,
            )
        else:
            model = build_model(
                n_vars, n_eras, n_classes,
                learning_rate=args.learning_rate,
                layer_sizes=layer_sizes,
                dropout=args.dropout,
                focal_loss=args.focal_loss,
                focal_gamma=args.focal_gamma,
            )
    model.summary(print_fn=logger.info)

    # ── Callbacks ────────────────────────────────────────────────────────
    model_path = out / f"fold{fold}_model.keras"
    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=args.early_stopping,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            str(model_path),
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=max(args.early_stopping // 5, 5),
            min_lr=1e-6,
            verbose=1,
        ),
    ]
    if args.warmup_epochs > 0:
        callbacks.insert(0, WarmupSchedule(args.learning_rate, args.warmup_epochs))
        logger.info(f"LR warmup: {args.warmup_epochs} epochs to reach {args.learning_rate}")

    # ── Training ─────────────────────────────────────────────────────────
    t_train = time.time()

    # Validation data (dict inputs for physics + era conditioning)
    # TF validation dataset: MC-only (iso and anti-iso data both excluded from val loss
    # so early-stopping monitors a clean MC metric).  X_val / E_val left intact.
    val_batch_size = args.batch_size * 4
    _X_mc = X_val[mc_val]
    _E_mc = E_val[mc_val]
    _Y_mc = Y_val[mc_val]
    _W_mc = W_val[mc_val]
    _val_mc_inputs = {"physics_input": _X_mc, "era_input": _E_mc}
    if hierarchical:
        val_dataset = tf.data.Dataset.from_tensor_slices((
            _val_mc_inputs,
            {"coarse": Y_val_coarse[mc_val], "fine": _Y_mc},
            {"coarse": _W_mc, "fine": _W_mc},
        )).batch(val_batch_size)
    else:
        val_dataset = tf.data.Dataset.from_tensor_slices(
            (_val_mc_inputs, _Y_mc, _W_mc)
        ).batch(val_batch_size)
    del _X_mc, _E_mc, _Y_mc, _W_mc, _val_mc_inputs

    if args.balanced_batches:
        n_per_class = max(1, args.batch_size // n_classes)
        steps_per_epoch = max(1, len(X_train) // args.batch_size)
        gen = BalancedBatchGenerator(
            X_train, E_train, Y_train, W_train, n_per_class, steps_per_epoch, rng,
            Y_coarse=Y_train_coarse if hierarchical else None,
        )
        # Wrap generator in tf.data.Dataset to avoid iterator exhaustion
        sample_batch = gen[0]
        input_sig = {
            "physics_input": tf.TensorSpec(shape=(None, X_train.shape[1]), dtype=tf.float32),
            "era_input": tf.TensorSpec(shape=(None, E_train.shape[1]), dtype=tf.float32),
        }
        if isinstance(sample_batch[1], dict):
            output_sig = (
                input_sig,
                {k: tf.TensorSpec(shape=(None, v.shape[1] if v.ndim > 1 else None), dtype=tf.float32)
                 for k, v in sample_batch[1].items()},
                {k: tf.TensorSpec(shape=(None,), dtype=tf.float32)
                 for k in sample_batch[2]},
            )
        else:
            output_sig = (
                input_sig,
                tf.TensorSpec(shape=(None, Y_train.shape[1]), dtype=tf.float32),
                tf.TensorSpec(shape=(None,), dtype=tf.float32),
            )

        def _make_gen():
            while True:
                for i in range(steps_per_epoch):
                    yield gen[i]

        train_dataset = tf.data.Dataset.from_generator(
            _make_gen, output_signature=output_sig
        ).prefetch(tf.data.AUTOTUNE)

        history = model.fit(
            train_dataset,
            steps_per_epoch=steps_per_epoch,
            epochs=args.epochs,
            validation_data=val_dataset,
            callbacks=callbacks,
            verbose=2,
        )
    else:
        train_inputs = {"physics_input": X_train, "era_input": E_train}
        if hierarchical:
            history = model.fit(
                train_inputs,
                {"coarse": Y_train_coarse, "fine": Y_train},
                sample_weight={"coarse": W_train, "fine": W_train},
                batch_size=args.batch_size,
                epochs=args.epochs,
                validation_data=val_dataset,
                callbacks=callbacks,
                verbose=2,
            )
        else:
            history = model.fit(
                train_inputs,
                Y_train,
                sample_weight=W_train,
                batch_size=args.batch_size,
                epochs=args.epochs,
                validation_data=val_dataset,
                callbacks=callbacks,
                verbose=2,
            )

    t_end = time.time()
    logger.info(f"Training time: {t_end - t_train:.1f}s")
    logger.info(f"Total time: {t_end - t0:.1f}s")

    # ── Save final model (if not saved by checkpoint) ────────────────────
    if not model_path.exists():
        model.save(str(model_path))
        logger.info(f"Saved model to {model_path}")

    # ── Plotting helpers ──────────────────────────────────────────────────
    epochs_range = range(1, len(history.history["loss"]) + 1)

    def _plot_loss(loss_key, val_loss_key, title_suffix, file_suffix=""):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(epochs_range, history.history[loss_key], lw=2, label="Train loss", color='cornflowerblue')
        ax.plot(epochs_range, history.history[val_loss_key], lw=2, label="Val loss", color='orchid')
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Categorical Cross-Entropy")
        ax.set_title(f"STXS Multiclass NN - fold {fold} {title_suffix}")
        ax.legend()
        # ax.set_ylim(bottom=0)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(out / f"fold{fold}_loss{file_suffix}.{ext}")
        plt.close(fig)

    def _plot_acc(acc_key, val_acc_key, title_suffix, file_suffix=""):
        if acc_key not in history.history:
            return
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(epochs_range, history.history[acc_key], lw=2, label="Train acc", color='cornflowerblue')
        ax.plot(epochs_range, history.history[val_acc_key], lw=2, label="Val acc", color='orchid')
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Categorical Accuracy")
        ax.set_title(f"STXS Multiclass NN - fold {fold} {title_suffix}")
        ax.legend()
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(out / f"fold{fold}_accuracy{file_suffix}.{ext}")
        plt.close(fig)

    def _plot_scores(pred_scores, Y_true, names, n_cls, title_suffix, file_suffix=""):
        """Plot per-class score distributions, one subplot per predicted class.

        Each subplot shows histograms of the NN output score for that class,
        stacked by the true class identity of the events.
        """
        short = [n.replace("is_", "") for n in names]
        true_idx = np.argmax(Y_true, axis=1)
        winter = plt.get_cmap("winter")
        cool = plt.get_cmap("cool")
        raw_colors = (
            [winter(i / max(n_cls - 1, 1)) for i in range(n_cls // 2)]
            + [cool(i / max(n_cls - 1, 1)) for i in range(n_cls // 2, n_cls)]
        )
        # Desaturate by blending with white (alpha=0.6)
        colors = [tuple(c * 0.6 + 0.4 for c in rgba[:3]) + (1.0,) for rgba in raw_colors]
        ncols = min(4, n_cls)
        nrows = int(np.ceil(n_cls / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows))
        axes = np.atleast_2d(axes)
        for ci in range(n_cls):
            ax = axes[ci // ncols, ci % ncols]
            for ti in range(n_cls):
                mask = true_idx == ti
                if mask.sum() == 0:
                    continue
                ax.hist(
                    pred_scores[mask, ci],
                    bins=50, range=(0, 1),
                    histtype="step", lw=1.3,
                    label=short[ti], density=True,
                    color=colors[ti],
                )
            ax.set_xlabel(f"Score({short[ci]})")
            ax.set_ylabel("Density")
            ax.set_title(short[ci])
            ax.legend(fontsize=5, ncol=2, loc="upper center")
        # hide unused subplots
        for idx in range(n_cls, nrows * ncols):
            axes[idx // ncols, idx % ncols].set_visible(False)
        fig.suptitle(f"NN score distributions - fold {fold} {title_suffix}", y=1.02)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(out / f"fold{fold}_scores{file_suffix}.{ext}",
                        bbox_inches="tight")
        plt.close(fig)

    def _plot_confusion(y_true, y_pred, names, n_cls, title_suffix, file_suffix=""):
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true, y_pred, labels=list(range(n_cls)))
        cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)
        fig, ax = plt.subplots(figsize=(max(8, n_cls * 0.7), max(7, n_cls * 0.65)))
        im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(n_cls))
        ax.set_yticks(range(n_cls))
        short = [n.replace("is_", "") for n in names]
        ax.set_xticklabels(short, rotation=60, ha="right", fontsize=7)
        ax.set_yticklabels(short, fontsize=7)
        # Annotate each cell with the normalised value
        for i in range(n_cls):
            for j in range(n_cls):
                val = cm_norm[i, j]
                color = "white" if val > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=max(6, 10 - n_cls // 4), color=color)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title(f"Confusion Matrix (normalised) - fold {fold} {title_suffix}")
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        for ext in ("png", "pdf"):
            fig.savefig(out / f"fold{fold}_confusion{file_suffix}.{ext}")
        plt.close(fig)

    # ── Loss & accuracy curves ───────────────────────────────────────────
    if hierarchical:
        _plot_loss("loss", "val_loss", "(total)")
        _plot_loss("coarse_loss", "val_coarse_loss", "(coarse)", "_coarse")
        _plot_loss("fine_loss", "val_fine_loss", "(fine)", "_fine")
        _plot_acc("coarse_categorical_accuracy", "val_coarse_categorical_accuracy",
                  "(coarse)", "_coarse")
        _plot_acc("fine_categorical_accuracy", "val_fine_categorical_accuracy",
                  "(fine)", "_fine")
    else:
        _plot_loss("loss", "val_loss", f"({args.class_scheme})")
        _plot_acc("categorical_accuracy", "val_categorical_accuracy",
                  f"({args.class_scheme})")

    # ── Confusion matrices on validation set ─────────────────────────────
    # Predict on ALL validation events (MC + data) so data events get a score
    # for the background plots.  Confusion matrix and score distributions
    # use MC-only events (mc_val mask).
    preds = model.predict({"physics_input": X_val, "era_input": E_val}, batch_size=8192)
    if hierarchical:
        pred_coarse = preds["coarse"]
        pred_fine   = preds["fine"]
        _plot_confusion(
            np.argmax(Y_val_coarse[mc_val], axis=1), np.argmax(pred_coarse[mc_val], axis=1),
            coarse_names, len(coarse_names), "(coarse)", "_coarse",
        )
        _plot_confusion(
            np.argmax(Y_val[mc_val], axis=1), np.argmax(pred_fine[mc_val], axis=1),
            class_names, n_classes, "(fine)", "_fine",
        )
    else:
        _plot_confusion(
            np.argmax(Y_val[mc_val], axis=1), np.argmax(preds[mc_val], axis=1),
            class_names, n_classes, f"({args.class_scheme})",
        )

    # ── Score distributions on validation set (MC only) ──────────────────
    if hierarchical:
        _plot_scores(pred_coarse[mc_val], Y_val_coarse[mc_val], coarse_names, len(coarse_names),
                     "(coarse)", "_coarse")
        _plot_scores(pred_fine[mc_val], Y_val[mc_val], class_names, n_classes,
                     "(fine)", "_fine")
    else:
        _plot_scores(preds[mc_val], Y_val[mc_val], class_names, n_classes,
                     f"({args.class_scheme})")

    # ── Save validation arrays for Dumbledraw background score plot ──────
    bkg_cls_idx   = [i for i, n in enumerate(class_names)
                     if not (n.startswith("is_ggh") or n.startswith("is_vbf"))]
    bkg_cls_names = [class_names[i] for i in bkg_cls_idx]
    pred_fine     = preds["fine"] if hierarchical else preds
    npz_path      = out / f"fold{fold}_bkg_scores.npz"
    np.savez(
        npz_path,
        scores_val        = pred_fine.astype(np.float32),
        true_class_val    = np.argmax(Y_val, axis=1).astype(np.int32),
        weights_val       = W_val.astype(np.float32),
        is_data_val       = is_iso_data_val.astype(np.float32),  # iso-region data for plot overlay
        class_names       = np.array(class_names, dtype=object),
        bkg_class_indices = np.array(bkg_cls_idx, dtype=np.int32),
        bkg_class_names   = np.array(bkg_cls_names, dtype=object),
        channel           = np.array([ch], dtype=object),
        fold              = np.array([fold], dtype=np.int32),
    )
    logger.info(
        f"Saved background score arrays to {npz_path} — "
        f"render with: python trainings/plot_bkg_scores.py --input {npz_path} --era <era>"
    )

    logger.info("Done. Outputs written to %s", out)


if __name__ == "__main__":
    main()
