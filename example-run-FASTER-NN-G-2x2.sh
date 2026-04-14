#!/bin/bash

eval "$(conda shell.bash hook)" # conda must already be on PATH.

GENERATE_TRAINING_DATA=1
TRAIN_CNN_MODEL=1
GENERATE_TEST_DATA=1
TEST_CNN_MODEL=1
SCAN_DATASET=1
CLEANUP_ALL=0

TRAINING_NEUTRAL=datasets/train/recombination_hotspot/ms_neutral_no_rechot.ms
TRAINING_SWEEP=datasets/train/recombination_hotspot/ms_sweep_no_rechot.ms
TRAINING_NEUTRAL_RECOMBINATION_HOTSPOT=datasets/train/recombination_hotspot/ms_neutral_rechotPos0.5.ms
TRAINING_SWEEP_RECOMBINATION_HOTSPOT=datasets/train/recombination_hotspot/mbs_sweep_rechot_Pos0.5_overlap.ms

TEST_NEUTRAL=datasets/train/recombination_hotspot/ms_neutral_no_rechot.ms
TEST_SWEEP=datasets/train/recombination_hotspot/ms_sweep_no_rechot.ms
TEST_NEUTRAL_RECOMBINATION_HOTSPOT=datasets/train/recombination_hotspot/ms_neutral_rechotPos0.5.ms
TEST_SWEEP_RECOMBINATION_HOTSPOT=datasets/train/recombination_hotspot/mbs_sweep_rechot_Pos0.5_overlap.ms

# Unzip recombination_hotspot files first
RECHOT_PATH=datasets/train/recombination_hotspot
if [ "$GENERATE_TRAINING_DATA" -eq 1 ]; then
for f in "$RECHOT_PATH"/*.zip; do
  [ -e "$f" ] || continue
  unzip "$f" -d "$RECHOT_PATH"
done
fi

# Create training data
if [ "$GENERATE_TRAINING_DATA" -eq 1 ]; then
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -bin -O 
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -bin -O 
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_NEUTRAL_RECOMBINATION_HOTSPOT -L 100000 -its 50000 -op IMG-GEN -icl neutralTRhotspot -f -bin -O 
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_SWEEP_RECOMBINATION_HOTSPOT -L 100000 -its 50000 -op IMG-GEN -icl sweepTRhotspot -f -bin -O -b 
fi

# Train CNN model (FASTER-NN-G)
if [ "$TRAIN_CNN_MODEL" -eq 1 ]; then
conda activate raisd-ai
./RAiSD-AI -n FASTER-NN-G2x2-PT-BINRAWPOS -I RAiSD_Images.TrainingDataBINRAWPOS -f -op MDL-GEN -O -frm -e 10 -g 2 -arc FASTER-NN-G -cl4 label00=neutralTR label01=sweepTR label10=neutralTRhotspot label11=sweepTRhotspot -cl4_1x_label recomb-hotspot -cl4_x1_label selective-sweep
conda deactivate
fi

# Create test data
if [ "$GENERATE_TEST_DATA" -eq 1 ]; then
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -bin -O
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -bin -O
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_NEUTRAL_RECOMBINATION_HOTSPOT -L 100000 -its 50000 -op IMG-GEN -icl neutralTEhotspot -f -bin -O
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_SWEEP_RECOMBINATION_HOTSPOT -L 100000 -its 50000 -op IMG-GEN -icl sweepTEhotspot -f -bin -O -b
fi

# Test CNN model (FASTER-NN-G, classification only)
if [ "$TEST_CNN_MODEL" -eq 1 ]; then
conda activate raisd-ai
./RAiSD-AI -n FASTER-NN-G2x2-PT-BINRAWPOS-ModelTest -mdl RAiSD_Model.FASTER-NN-G2x2-PT-BINRAWPOS -f -op MDL-TST -I RAiSD_Images.TestDataBINRAWPOS -clp 4 sweepTR=sweepTE neutralTR=neutralTE neutralTRhotspot=neutralTEhotspot sweepTRhotspot=sweepTEhotspot
conda deactivate
fi

# Scan using CNN model (FASTER-NN-G, detection mode)
if [ "$SCAN_DATASET" -eq 1 ]; then
conda activate raisd-ai

# Scan neutral dataset to obtain FPR thresholds at 0.05
./RAiSD-AI -n FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-NEUTRAL -mdl RAiSD_Model.FASTER-NN-G2x2-PT-BINRAWPOS -f -op SWP-SCN -I $TEST_NEUTRAL -L 100000 -frm -G 100 -pcs 2 sweepTR sweepTRhotspot -O -k 0.05 

# Get thresholds
fprThresholdMU=$(grep " mu " RAiSD_Info.FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-NEUTRAL | grep min | awk -F: '{print $2}' | awk '{print $1}')
echo $fprThresholdMU
fprThresholdPCL0=$(grep " recomb-hotspot " RAiSD_Info.FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-NEUTRAL | grep min | awk -F: '{print $2}' | awk '{print $1}')
echo $fprThresholdPCL0
fprThresholdPCL1=$(grep " selective-sweep " RAiSD_Info.FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-NEUTRAL | grep min | awk -F: '{print $2}' | awk '{print $1}')
echo $fprThresholdPCL1

# Scan dataset with sweep, no rechotspot, report sweep stats
./RAiSD-AI -n FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-SWEEP -mdl RAiSD_Model.FASTER-NN-G2x2-PT-BINRAWPOS -f -op SWP-SCN -I $TEST_SWEEP -L 100000 -frm -T 50000 -d 1000 -G 100 -pcs 2 sweepTR sweepTRhotspot -O -l 3 mu=$fprThresholdMU pcl0=$fprThresholdPCL0 pcl1=$fprThresholdPCL1 

# Scan dataset with sweep, no rechotspot, report rechotspot stats
./RAiSD-AI -n FASTER-NN-G2x2-PT-BINRAWPOS-SCAN-SWEEP -mdl RAiSD_Model.FASTER-NN-G2x2-PT-BINRAWPOS -f -op SWP-SCN -I $TEST_SWEEP_RECOMBINATION_HOTSPOT -L 100000 -frm -T 50000 -d 1000 -G 100 -pcs 2 sweepTR sweepTRhotspot -O -l 3 mu=$fprThresholdMU pcl0=$fprThresholdPCL0 pcl1=$fprThresholdPCL1 -b

conda deactivate
fi

if [ "$CLEANUP_ALL" -eq 1 ]; then
rm RAiSD_Info.*
rm RAiSD_Plot.*
rm RAiSD_Report.*
rm -r RAiSD_Grid.*
rm -r RAiSD_Images.*
rm -r RAiSD_Model.*
fi
