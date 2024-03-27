import argparse
import sys

sys.path.insert(0, ".")  # if executed within smhtt_ul
sys.path.insert(0, "..")  # if executed within smhtt_ul/misc_helper

from config.shapes.file_names import files

parser = argparse.ArgumentParser(description='Create a list of samples for SM HTT UL analysis')
parser.add_argument('--channel', nargs='+', type=str, help='Channel(s): mm, mt, et, em, tt')
parser.add_argument('--era', nargs='+', type=str, help='Era(s): 2018, 2017, 2016preVFP, 2016postVFP')
parser.add_argument('--output', type=str, default='samples.txt', help='Output file name')
option = parser.parse_args()

print(f"Selected years: {option.era}")
print(f"Selected channels: {option.channel}")

if __name__ == "__main__":
    used_files = []
    for era in option.era:
        for ch in option.channel:
            for processes in files[era][ch]:
                used_files += files[era][ch][processes]
    used_files = sorted(list(set(used_files)))

    with open(option.output, 'w') as f:
        f.write("\n".join(used_files))

    print(f"{len(used_files)} samples is saved in {option.output}")
