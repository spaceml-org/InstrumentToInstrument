#!/bin/bash

set -o xtrace

EPOCHS=100
LIMIT_VAL_BATCHES=1000

# MISSING EXPERIMENTS

## MSG to GOES
# 1-channel: 3.9um Channel
# A_bands="[3920.0]"
# B_bands="[3890.0]"

# INPUT_DIM_A=1
# INPUT_DIM_B=1

# FILTER_DAYTIME=False

# wandb_name="MSG-GOES16-3000m-1ch-3.9um"
# python itipy/train/geo_to_geo.py \
#     --config-name msg-to-goes.yaml \
#     data.A_bands="$A_bands" \
#     data.B_bands="$B_bands" \
#     data.filter_daytime=$FILTER_DAYTIME \
#     model.input_dim_a=$INPUT_DIM_A \
#     model.input_dim_b=$INPUT_DIM_B \
#     logging.wandb_name="$wandb_name" \
#     training.epochs=$EPOCHS \
#     training.limit_val_batches=$LIMIT_VAL_BATCHES \
#     seed=2408


## MSG to HIMAWARI
# 1-channel: 3.9um Channel
# A_bands="[3920.0]"
# B_bands="[3900.0]"

# INPUT_DIM_A=1
# INPUT_DIM_B=1

# FILTER_DAYTIME=False

# wandb_name="MSG-HIMAWARI8-3000m-1ch-3.9um"
# python itipy/train/geo_to_geo.py \
#     --config-name msg-to-himawari.yaml \
#     data.A_bands="$A_bands" \
#     data.B_bands="$B_bands" \
#     data.filter_daytime=$FILTER_DAYTIME \
#     model.input_dim_a=$INPUT_DIM_A \
#     model.input_dim_b=$INPUT_DIM_B \
#     logging.wandb_name="$wandb_name" \
#     training.epochs=$EPOCHS \
#     training.limit_val_batches=$LIMIT_VAL_BATCHES \
#     seed=2408

## HIMAWARI to MSG

# 1-channel: 3.9um Channel
# A_bands="[3900.0]"
# B_bands="[3920.0]"

# INPUT_DIM_A=1
# INPUT_DIM_B=1

# FILTER_DAYTIME=False

# wandb_name="HIMAWARI8-MSG-3000m-1ch-3.9um"
# python itipy/train/geo_to_geo.py \
#     --config-name himawari-to-msg.yaml \
#     data.A_bands="$A_bands" \
#     data.B_bands="$B_bands" \
#     data.filter_daytime=$FILTER_DAYTIME \
#     model.input_dim_a=$INPUT_DIM_A \
#     model.input_dim_b=$INPUT_DIM_B \
#     logging.wandb_name="$wandb_name" \
#     training.epochs=$EPOCHS \
#     training.limit_val_batches=$LIMIT_VAL_BATCHES \
#     seed=2408

# 2-channel: Water Vapor Channels
A_bands="[6200.0, 7300.0]"
B_bands="[6250.0, 7350.0]"

INPUT_DIM_A=2
INPUT_DIM_B=2

FILTER_DAYTIME=False

wandb_name="HIMAWARI8-MSG-3000m-2ch-6.2-7.3um"
python itipy/train/geo_to_geo.py \
    --config-name himawari-to-msg.yaml \
    data.A_bands="$A_bands" \
    data.B_bands="$B_bands" \
    data.filter_daytime=$FILTER_DAYTIME \
    model.input_dim_a=$INPUT_DIM_A \
    model.input_dim_b=$INPUT_DIM_B \
    logging.wandb_name="$wandb_name" \
    training.epochs=$EPOCHS \
    training.limit_val_batches=$LIMIT_VAL_BATCHES \
    seed=908

# 5-channel: All infrared channels
A_bands="[8600.0, 9600.0, 10400.0, 12400.0, 13300.0]"
B_bands="[8700.0, 9660.0, 10800.0, 12000.0, 13400.0]"

INPUT_DIM_A=5
INPUT_DIM_B=5

FILTER_DAYTIME=False

wandb_name="HIMAWARI8-MSG-3000m-5ch-8.4-13.3um"
python itipy/train/geo_to_geo.py \
    --config-name himawari-to-msg.yaml \
    data.A_bands="$A_bands" \
    data.B_bands="$B_bands" \
    data.filter_daytime=$FILTER_DAYTIME \
    model.input_dim_a=$INPUT_DIM_A \
    model.input_dim_b=$INPUT_DIM_B \
    logging.wandb_name="$wandb_name" \
    training.epochs=$EPOCHS \
    training.limit_val_batches=$LIMIT_VAL_BATCHES \
    seed=42

## GOES to MSG

seeds=(611 1502 2906 100 123 40)

# 2-channel: Water Vapor Channels

for seed in "${seeds[@]}"; do

    echo "Running for seed: $seed"

    # 2-channel: Water Vapor Channels
    A_bands="[6170.0, 7340.0]"
    B_bands="[6250.0, 7350.0]"

    INPUT_DIM_A=2
    INPUT_DIM_B=2

    FILTER_DAYTIME=False

    wandb_name="GOES16-MSG-3000m-2ch-6.2-7.3um"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-msg.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES \
        seed=$seed