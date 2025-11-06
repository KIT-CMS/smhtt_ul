import sys
import argparse
import numpy as np
import ROOT

def main():
    parser = argparse.ArgumentParser(
        description="For each already existing systematic shift histogram, add an extra ±10/% /scaled variation."
    )
    parser.add_argument("--input", required=True, help="Input ROOT file containing the shift histograms")
    parser.add_argument("--output", required=True, help="Output ROOT file with the extra up/down histograms added")
    parser.add_argument("--process", required=True, help="Signal process name (e.g. EMB_DM1011_PT20_40)")
    parser.add_argument("--minshift", type=float, default=-20.0, help="Minimum shift value (default: -20.0)")
    parser.add_argument("--maxshift", type=float, default=20.0, help="Maximum shift value (default: 20.0)")
    parser.add_argument("--step", type=float, default=0.1, help="Step size (default: 0.1)")
    parser.add_argument("--scaleup", type=float, default=1.1, help="Extra scaling factor for the up variation (default: 1.1)")
    parser.add_argument("--scaledown", type=float, default=0.9, help="Extra scaling factor for the down variation (default: 0.9)")
    parser.add_argument("--scaleTES", type=float, default=0.01, help="Extra scaling factor for the TES variation (default: 0.01)")
    args = parser.parse_args()

    # First, copy the complete original root file
    copy_success = ROOT.TFile.Cp(args.input, args.output)
    if not copy_success:
        print(f"Error: Failed to copy {args.input} to {args.output}")
        sys.exit(1)
    print(f"Copied original file {args.input} to {args.output}")
    
    # Open the copied file for modification
    fout = ROOT.TFile.Open(args.output, "UPDATE")
    if not fout or fout.IsZombie():
        print(f"Error: Unable to open output file {args.output}")
        sys.exit(1)

    # The histograms are stored in a subdirectory.
    directory_name = "mt_" + args.process
    dir_obj = fout.Get(directory_name)
    if not dir_obj:
        print(f"Error: directory '{directory_name}' not found in the file")
        sys.exit(1)

    # Loop over the systematic shifts.
    shifts = np.arange(args.minshift, args.maxshift + args.step/10.0, args.step)
    for shift in shifts:
        shift_str = format(shift, ".1f")
        
        if shift_str == "-0.0":
            shift_str = "0.0"
        # Build the full histogram name e.g. EMB_DM1011_PT20_40_20.0
        hist_name = "EMB_" + args.process + "_" + shift_str
        h_nom = dir_obj.Get(hist_name)
        if not h_nom:
            # Skip if histogram not found.
            breakpoint()
            continue

        # Clone to create extra up and down versions.
        h_up = h_nom.Clone(hist_name + "_Custom_simple_shiftUp")
        h_down = h_nom.Clone(hist_name + "_Custom_simple_shiftDown")
        nbins = h_nom.GetNbinsX() + 2    # include underflow/overflow
        
        # Linear tau energy scale uncertainty
        x0 = h_nom.GetMean()  # Reference value (e.g., mean of the distribution)
        a = args.scaleTES  # Slope of the shift (1% per unit of x)
        for bin_idx in range(0, nbins):
            content = h_nom.GetBinContent(bin_idx)
            # TES shift:
            x = h_nom.GetBinCenter(bin_idx)
            delta = a * (x - x0)  # Linear shift
            h_up.SetBinContent(bin_idx, content * (1 + delta))
            h_down.SetBinContent(bin_idx, content * (1 - delta))
            
            # Simple shift:
            # h_up.SetBinContent(bin_idx, content * args.scaleup)
            # h_down.SetBinContent(bin_idx, content * args.scaledown)
        # Change directory to the correct one and write the histograms there
        fout.cd(directory_name)
        h_up.Write()
        h_down.Write()
        print(f"Added variations for {hist_name}: up={h_up.GetName()}, down={h_down.GetName()}")

    fout.Close()
    print("Output file written:", args.output)

if __name__=="__main__":
    main()