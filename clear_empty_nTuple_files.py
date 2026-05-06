import os
import ROOT
from tqdm import tqdm

# Suppress the spam of ROOT error messages in the terminal while scanning
ROOT.gErrorIgnoreLevel = ROOT.kFatal 

base_dir = "/ceph/jvoss/CROWN/ntuples/sda_v12_16_04_26_v2"
bad_files_count = 0
bad_file_names = []
print(f"Scanning directory: {base_dir}")
print("Looking for corrupted or empty ROOT files...")

def _file_name(file_path):
    file_name = file_path.split("/")[-1]
    return file_name

del_flag = False

print(f"\nFound empty/broken files are getting deleted: {del_flag}\n")

for root_dir, dirs, files in tqdm(os.walk(base_dir), total=len(list(os.walk(base_dir))), desc="Scanning files"):
    for file in files:
        if not file.endswith(".root"):
            continue
            
        file_path = os.path.join(root_dir, file)
        
        # Check 1: Is it literally 0 bytes?
        if os.path.getsize(file_path) == 0:
            print(f"Deleting 0-byte file: {file_path}")
            if del_flag:
                os.remove(file_path)
            bad_file_names += (_file_name(file_path),)
            bad_files_count += 1
            continue
            
        # Check 2: Does it fail to open or is it a Zombie?
        try:
            f = ROOT.TFile.Open(file_path, "READ")
            if not f or f.IsZombie():
                print(f"Deleting corrupted (Zombie) file: {file_path}")
                if f:
                    f.Close()
                if del_flag:
                    os.remove(file_path)
                bad_file_names += (_file_name(file_path),)
                bad_files_count += 1
                continue
            
            # Check 3: Was it improperly closed (Recovered) or does it have zero keys?
            if f.TestBit(ROOT.TFile.kRecovered) or len(f.GetListOfKeys()) == 0:
                print(f"Deleting recovered/empty-key file: {file_path}")
                f.Close()
                if del_flag:
                    os.remove(file_path)
                bad_file_names += (_file_name(file_path),)
                bad_files_count += 1
                continue

            # File is good
            f.Close()
        
        except OSError:
            # Newer ROOT versions throw an OSError when a file is severely corrupted/empty
            print(f"Deleting unopenable file (raised OSError): {file_path}")
            if del_flag:
                os.remove(file_path)
            bad_file_names += (_file_name(file_path),)
            bad_files_count += 1
            
        except Exception as e:
             # Catch any other weird PyROOT exceptions just to be safe
            print(f"Deleting unopenable file ({e}): {file_path}")
            if del_flag:
                os.remove(file_path)
            bad_file_names += (_file_name(file_path),)
            bad_files_count += 1

print(f"\nScan complete. Deleted {bad_files_count} corrupted/empty files.\n")
print("\n\nList of deleted files:")
for name in bad_file_names:
    print(f"  - {name}")