## Training Dataset Creation

  1. Produce a configuration file using the required `--collect-config-only` and `--config-output-file` options with `shapes/produce_shapes.py`. This bypasses shape creation, collecting only weights and cuts used for shapes creation.
  2. Run `adjust_config.py` to modify the raw configuration from the previous step. This script renames processes and removes SMHtt-specific ones (marked in the file accordingly). Adapt this step for other use cases if necessary. If your configuration lacks systematic variations, you can omit the `nest_and_categorize_uncertainties` step before saving the modified config.
  3. Using a configuration from `adjust_config.py`, `create_training_dataset.py` generates a pandas DataFrame for training. This involves three per-process steps:
     1. The `ROOTToPlain` section offers a **general tool** to create a consolidated pandas DataFrame (or a combined ROOT RDataFrame) from various ROOT ntuples and friend files. This process uses defined filters, and specified columns for data extraction that can also be provided independent of the created configuration file in step 2.
     2. Apply `ProcessDataFrameManipulation` procedure to create a pandas DataFrame with a multi-level column structure. This part can also accept functions compatible with pandas pipe chains (e.g., `exemplary_remove_cut_regions`, `exemplary_custom_selection`).
     3. Generate folds based on a user-defined condition that are applied splitting the process DataFrame into multiple ones.

      Subsequently, folds from all processes are merged. `NaN` values are handled as per the `CombinedDataFrameManipulation` documentation (see `fill_nans_in_weight_like`, `fill_nans_in_shift_like`, `fill_nans_in_nominal_additional`). Finally, all folds are saved.
