import uproot
import numpy as np
import argparse
import os
import logging
import shutil
import ROOT

from config.logging_setup_configs import setup_logging

logger = setup_logging(logger=logging.getLogger(__name__))


def modify_jetfakes_systematics(file_path, factor=2.0):
    """
    Modifies specific jetFakes systematic uncertainty histograms in a ROOT file.
    This version uses a safe two-file approach to prevent freezing issues.

    Only modifies jetFakes systematics that contain '_non_closure_' in their name.

    Args:
        file_path (str): The path to the ROOT file to be modified.
        factor (float): The multiplication factor for the uncertainty.
    """
    ROOT.gROOT.SetBatch(True)

    if not os.path.exists(file_path):
        logger.error(f"File not found at {file_path}")
        return

    # Define path for the temporary output file
    temp_file_path = file_path + ".tmp"

    root_file_in = None
    root_file_out = None

    try:
        # Open the original file for reading
        root_file_in = ROOT.TFile.Open(file_path, "READ")
        if not root_file_in or root_file_in.IsZombie():
            logger.error(f"Failed to open input ROOT file: {file_path}")
            return

        # Create a new temporary file for writing
        root_file_out = ROOT.TFile.Open(temp_file_path, "RECREATE")
        if not root_file_out or root_file_out.IsZombie():
            logger.error(f"Failed to create temporary ROOT file: {temp_file_path}")
            return

        logger.info(f"Reading from {file_path} and writing to {temp_file_path}")

        # Iterate over all top-level directories in the input file
        for key in root_file_in.GetListOfKeys():
            obj = key.ReadObj()
            if not isinstance(obj, ROOT.TDirectory):
                continue

            in_dir = obj
            dir_name = in_dir.GetName()

            # Create the same directory in the output file
            out_dir = root_file_out.mkdir(dir_name)
            logger.info(f"Processing directory: {dir_name}")

            nominal_hist = in_dir.Get("jetFakes")
            if not nominal_hist:
                logger.warning(f"No 'jetFakes' nominal found in {dir_name}. Copying all contents as-is.")

            # Now, iterate through all objects in the input directory
            for item_key in in_dir.GetListOfKeys():
                item_obj = item_key.ReadObj()
                item_name = item_obj.GetName()

                # Condition to check if this is a histogram we need to modify
                is_target_systematic = all(
                    [
                        item_name.startswith("jetFakes_"),
                        (item_name.endswith("Up") or item_name.endswith("Down")),
                        ("_non_closure_" in item_name and "Stat1Sigma" in item_name) or
                        any(
                            subit in item_name for subit in [
                                # ml derived part only the stat part
                                # "ff_QCD",
                                # "ff_Wjets",
                                # "ff_ttbar",
                                # ---
                                "ff_QCDStat",
                                "ff_WjetsStat",
                                "ff_ttbarStat",
                                # ---
                                # "fractions_QCD",
                                # "fractions_Wjets",
                                # "fractions_ttbar",
                                "fractions_StatStat",
                                # ---
                                # "QCD_DR_SR_correction",
                                "QCD_DR_SR_correctionStat",
                                # ---
                                # "Wjets_DR_SR_correction",
                                "Wjets_DR_SR_correctionStat",
                                # ---
                            ]
                        )
                    ]
                )

                # Set the current directory in the output file for writing
                out_dir.cd()

                if is_target_systematic and nominal_hist:
                    logger.info(f"  - Modifying: {item_name}")
                    syst_hist = item_obj

                    # Stretch each bin away from the nominal by a factor,
                    # preserving the per-bin sign of the original variation.
                    new_syst_hist = syst_hist.Clone(item_name)
                    for bin_idx in range(new_syst_hist.GetNcells()):
                        nominal_val = nominal_hist.GetBinContent(bin_idx)
                        syst_val = syst_hist.GetBinContent(bin_idx)
                        delta = syst_val - nominal_val
                        new_syst_hist.SetBinContent(bin_idx, nominal_val + factor * delta)

                    new_syst_hist.Write()
                    del new_syst_hist  # Clean up temporary clone to prevent memory issues
                else:
                    item_obj.Write()  # If it's not a target systematic, just copy it to the new file

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        # Clean up if something went wrong
        if root_file_in:
            root_file_in.Close()
        if root_file_out:
            root_file_out.Close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return

    # Finalize and replace
    logger.info("Finalizing files...")
    root_file_in.Close()
    root_file_out.Close()

    # Replace the original file with the new, modified one
    os.replace(temp_file_path, file_path)
    logger.info(f"Successfully modified and overwritten {file_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Modify specific 'non_closure' jetFakes systematics in a ROOT file using a safe two-file method."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Input ROOT file to be modified."
    )
    parser.add_argument(
        "-f", "--factor", type=float, default=2.0, help="Multiplication factor for the systematic difference (default: 2.0)."
    )

    args = parser.parse_args()

    # Create a one-time backup before running the script.
    backup_path = args.input + ".bak"
    if not os.path.exists(backup_path):
        try:
            logger.info(f"Creating a one-time backup at: {backup_path}")
            shutil.copy(args.input, backup_path)
        except Exception as e:
            logger.error(f"Could not create backup file. Aborting. Error: {e}")
            exit()
    else:
        logger.info(f"Backup file already exists at {backup_path}. Skipping backup.")

    modify_jetfakes_systematics(args.input, args.factor)
