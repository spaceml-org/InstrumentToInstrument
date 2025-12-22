#!/bin/bash

set -o xtrace

EPOCHS=100
LIMIT_VAL_BATCHES=1000

# 3-channel: Visible Channels (daytime only)
declare -A variables_and_bands_3ch=(
    ["3ch-0.47-0.87um"]="[470.0,640.0,860.0]" # Visible channels
)
A_bands="[470.0, 640.0, 870.0]"
B_bands="[470.0, 640.0, 860.0]"

INPUT_DIM_A=3
INPUT_DIM_B=3

FILTER_DAYTIME=True

for variable in "${!variables_and_bands_3ch[@]}"; do
    bands=${variables_and_bands_3ch[$variable]}
    wandb_name="GOES16-HIM8-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-himawari.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 2-channel: Near-IR Channels (daytime only)
declare -A variables_and_bands_2ch=(
    ["2ch-1.6-2.2um"]="[1610.0, 2300.0]"
)
A_bands="[1600.0, 2250.0]"
B_bands="[1610.0, 2300.0]"

FILTER_DAYTIME=True

INPUT_DIM_A=2
INPUT_DIM_B=2

for variable in "${!variables_and_bands_2ch[@]}"; do
    bands=${variables_and_bands_2ch[$variable]}
    wandb_name="GOES16-HIM8-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-himawari.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 1-channel:
declare -A variables_and_bands_1ch=(
    ["1ch-3.9um"]="[3900.0]"
)
A_bands="[3890.0]"
B_bands="[3900.0]"

INPUT_DIM_A=1
INPUT_DIM_B=1

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_1ch[@]}"; do
    bands=${variables_and_bands_1ch[$variable]}
    wandb_name="GOES16-HIM8-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-himawari.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 3-channel: Water Vapor Channels
declare -A variables_and_bands_3ch=(
    ["3ch-6.2-7.3um"]="[6200.0, 6900.0, 7300.0]" # Water vapor channels
)
A_bands="[6170.0, 6930.0, 7340.0]"
B_bands="[6200.0, 6900.0, 7300.0]"

INPUT_DIM_A=3
INPUT_DIM_B=3

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_3ch[@]}"; do
    bands=${variables_and_bands_3ch[$variable]}
    wandb_name="GOES16-HIM8-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-himawari.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 6-channel: All infrared channels
declare -A variables_and_bands_6ch=(
     ["6ch-8.6-13.3um"]="[8600.0, 9600.0, 10400.0, 11200.0, 12400.0, 13300.0]"
)

A_bands="[8440.0, 9610.0, 10330.0, 11190.0, 12270.0, 13270.0]"
B_bands="[8600.0, 9600.0, 10400.0, 11200.0, 12400.0, 13300.0]"

INPUT_DIM_A=6
INPUT_DIM_B=6

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_6ch[@]}"; do
    bands=${variables_and_bands_6ch[$variable]}
    wandb_name="GOES16-HIM8-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name goes-to-himawari.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done
