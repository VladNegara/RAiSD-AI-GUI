#!/bin/bash

eval "$(conda shell.bash hook)" # conda must already be on PATH.

GENERATE_TRAINING_DATA=1
TRAIN_CNN_MODEL=1
GENERATE_TEST_DATA=1
TEST_CNN_MODEL=1
SCAN_DATASET=1
CLEANUP_ALL=0

TRAINING_NEUTRAL=datasets/train/msneutral1_100sims.out
TRAINING_SWEEP=datasets/train/msselection1_100sims.out

TEST_NEUTRAL=datasets/test/msneutral1_10sims.out
TEST_SWEEP=datasets/test/msselection1_10sims.out

# Create training data
if [ "$GENERATE_TRAINING_DATA" -eq 1 ]; then
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTR -f -frm -bin -O
./RAiSD-AI -n TrainingDataBINRAWPOS -I $TRAINING_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTR -f -bin -O 
fi

# Train CNN model (FASTER-NN-G)
if [ "$TRAIN_CNN_MODEL" -eq 1 ]; then
conda activate raisd-ai
./RAiSD-AI -n FASTER-NN-G-PT-BINRAWPOS -I RAiSD_Images.TrainingDataBINRAWPOS -f -op MDL-GEN -O -frm -e 10 -g 2 -arc FASTER-NN-G
conda deactivate
fi

# Create test data
if [ "$GENERATE_TEST_DATA" -eq 1 ]; then
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_NEUTRAL -L 100000 -its 50000 -op IMG-GEN -icl neutralTE -f -frm -bin -O
./RAiSD-AI -n TestDataBINRAWPOS -I $TEST_SWEEP -L 100000 -its 50000 -op IMG-GEN -icl sweepTE -f -bin -O
fi

# Test CNN model (FASTER-NN-G, classification only)
if [ "$TEST_CNN_MODEL" -eq 1 ]; then
conda activate raisd-ai
./RAiSD-AI -n FASTER-NN-G-PT-BINRAWPOS-ModelTest -mdl RAiSD_Model.FASTER-NN-G-PT-BINRAWPOS -f -op MDL-TST -I RAiSD_Images.TestDataBINRAWPOS -clp 2 sweepTR=sweepTE neutralTR=neutralTE
conda deactivate
fi

# Scan using CNN model (FASTER-NN-G, detection mode)
if [ "$SCAN_DATASET" -eq 1 ]; then
conda activate raisd-ai

# Scan neutral dataset to obtain FPR thresholds at 0.05
./RAiSD-AI -n FASTER-NN-G-PT-BINRAWPOS-SCAN-NEUTRAL -mdl RAiSD_Model.FASTER-NN-G-PT-BINRAWPOS -f -op SWP-SCN -I $TEST_NEUTRAL -L 100000 -frm -G 100 -pcs 1 sweepTR -O -k 0.05 

# Get thresholds
fprThresholdMU=$(grep " mu " RAiSD_Info.FASTER-NN-G-PT-BINRAWPOS-SCAN-NEUTRAL | grep min | awk -F: '{print $2}' | awk '{print $1}')
echo $fprThresholdMU
fprThresholdPCL0=$(grep " sweepTR" RAiSD_Info.FASTER-NN-G-PT-BINRAWPOS-SCAN-NEUTRAL | grep min | awk -F: '{print $2}' | awk '{print $1}')
echo $fprThresholdPCL0

# Scan dataset
./RAiSD-AI -n FASTER-NN-G-PT-BINRAWPOS-SCAN-SWEEP -mdl RAiSD_Model.FASTER-NN-G-PT-BINRAWPOS -f -op SWP-SCN -I $TEST_SWEEP -L 100000 -frm -T 50000 -d 1000 -G 100 -pcs 1 sweepTR -O -l 2 mu=$fprThresholdMU pcl0=$fprThresholdPCL0 

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
