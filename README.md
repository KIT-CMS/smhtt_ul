# mssm-htt-legacy-analysis
In this repository all software necessary for the MSSM HTT Legacy analysis starting from flat n-tuple level is stored.
The software uses the ntuple_processor code included as submodule of the main repository.
The software is written in python3 and uses RDataFrames.
Since currently there is no software stack containing these packages, a local installation of ROOT with PyROOT support for python3 is used.

## Checkout instructions
The repository includes all necessary packages as submodules. Thus, a simple recursive clone of the repository should be sufficient.
```bash
git clone git@github.com:mburkart/mssm-htt-legacy-analysis.git --recursive
```

## Producing shapes
In order to run the shape production, the correct ROOT version needs to be sourced. For this a utility script is provided under `utils/setup_root.sh`. There is a top-level script for the shape production that allows to run the shape production locally or to write out a `.pkl` containing a list of all created computational graphs for the different samples. Each of these created graphs can then be executed independently. 
### Shapes for control plots and GoF tests
The top-level script allows the creation of shapes for the actual analysis, control plots and GoF tests through the command line arguments `--control-plots` and `--skip-systematic-variations`. For the production of input shapes for the GoF tests the `--control-plots` option is sufficient. For control plots the `--skip-systematic-variations` option needs to be set as well. The command for the production of control plots is:
```bash
source utils/setup_root.sh

python shapes/produce_shapes.py --channels tt --output-file control_shapes-2017-tt --directory /ceph/mburkart/Run2Legacy/ntuples_mssm_04_27/2017/ntuples/ --tt-friend-directory /ceph/mburkart/Run2Legacy/ntuples_mssm_04_27/2017/friends/{SVFit,FakeFactors}/ --era 2017 --num-processes 4 --num-threads 3 --optimization-level 1 --control-plots --skip-systematic-variaitons
```

### Analysis shapes
Local production of shapes for control plots and GoF shapes for single channels is possible since they only need a small subset of the processes used in the analysis. For the actual analysis, this is not feasible since a large number of signal files needs to be processed as well. Therefore, a submit script for the analysis jobs is provided. Since the creation of the graphs takes quite some time it is not recommended to try to submit multiple channels and a large subset of the processes simultaneously. Thus, a split of the processes is provided in the submit script and even the submission of single processes is possible. The submit script will create the graphs locally and writes them to a file. Afterwards, it sets up the directories for the submission and the submission files. The commands for the submission are then printed to standard output. 

Before submitting the jobs it is recommended to create a directory on `/ceph` for the outputs and a second direcory where the log files will be written to on the `/work` machine. These directories can then be symlinked into the repository structure via
```bash
ln -s /path/to/ceph/directory output
ln -s /path/to/work/directory log
```

To submit the shapes for the 2017 data-taking period the recommended way to invoke the script is:
```bash
for CHANNEL in et mt tt em
do
  for PROCESSES in backgrounds sm_signals mssm_ggh_split[1-5] mssm_bbh_split{1,2}
  do
    bash submit/submit_shape_production.sh 2017 $CHANNEL $PROCESSES singlegraph
  done
done
```
This will create single core jobs for all pipelines except the nominal ones which will submitted as multicore jobs running the computational graph multithreaded on 8 cores.

The outputs of the jobs will be written to `output/shapes/analysis_unit_graphs-2017-$CHANNEL-<processes>/output-single_graph_job-analysis_unit_graphs-2017-$CHANNEL-<processes>-<graph_number>.root` where `<processes>` is the expanded subset of graphs of the submitted jobs and `<graph_number>` the number of the processed graph. The outputs can then be merged using the `hadd` command and further processed to obtain the input shapes for combine. This is done with two additional scripts. The first one estimates the shapes of derived processes like the fake factor method and the QCD multijet background from the created histograms and the second script converts the shapes to the format expected by combine.
```bash
source utils/setup_root.sh

python shapes/do_estimations.py -e 2017 -i /path/to/merged/inputs --emb-tt
python shapes/convert_to_synced_shapes.py -e 2017 -i /path/to/merged/inputs -o output/shapes/2017-m_sv_puppi-synced_shapes --variable-selection m_sv_puppi --num-processes 12
hadd output/shapes/2017-m_sv_puppi-synced-shapes/2017-mt-synced-MSSM.root output/shapes/2017-m_sv_puppi-synced-shapes/2017-mt-synced-MSSM*.root
```
These shapes can then be used as input to the [analysis repository](https://github.com/KIT-CMS/MSSMvsSMRun2Legacy/).

## General structure
ToDo

## Remarks on the structure of the ntuple-processor submodule
ToDo

