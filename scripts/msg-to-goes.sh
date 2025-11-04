#!/bin/bash

set -o xtrace

EPOCHS=100
LIMIT_VAL_BATCHES=1000

# 2-channel: Visible Channels (daytime only)
declare -A variables_and_bands_2ch=(
    ["2ch-0.64-0.87um"]="[640.0, 870.0]" # Visible channels
)
A_bands="[640.0, 810.0]"
B_bands="[640.0, 870.0]"

INPUT_DIM_A=2
INPUT_DIM_B=2

FILTER_DAYTIME=True

for variable in "${!variables_and_bands_2ch[@]}"; do
    bands=${variables_and_bands_2ch[$variable]}
    wandb_name="MSG-GOES16-3000m-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name msg-to-goes.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 1-channel: Near-IR Channels (daytime only)
declare -A variables_and_bands_1ch=(
    ["1ch-1.6um"]="[1610.0]"
)
A_bands="[1640.0]"
B_bands="[1610.0]"

FILTER_DAYTIME=True

INPUT_DIM_A=1
INPUT_DIM_B=1

for variable in "${!variables_and_bands_1ch[@]}"; do
    bands=${variables_and_bands_1ch[$variable]}
    wandb_name="MSG-GOES16-3000m-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name msg-to-goes.yaml \
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
    ["1ch-3.9um"]="[3890.0]"
)
A_bands="[3920.0]"
B_bands="[3890.0]"

INPUT_DIM_A=1
INPUT_DIM_B=1

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_1ch[@]}"; do
    bands=${variables_and_bands_1ch[$variable]}
    wandb_name="MSG-GOES16-3000m-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name msg-to-goes.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 2-channel: Water Vapor Channels
declare -A variables_and_bands_2ch=(
    ["2ch-6.2-7.3um"]="[6170.0, 7340.0]" # Water vapor channels
)
A_bands="[6250.0, 7350.0]"
B_bands="[6170.0, 7340.0]"

INPUT_DIM_A=2
INPUT_DIM_B=2

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_2ch[@]}"; do
    bands=${variables_and_bands_2ch[$variable]}
    wandb_name="MSG-GOES16-3000m-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name msg-to-goes.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 5-channel: All infrared channels
declare -A variables_and_bands_5ch=(
     ["5ch-8.4-13.3um"]="[8440.0, 9610.0, 10330.0, 12270.0, 13270.0]"
)

A_bands="[8700.0, 9660.0, 10800.0, 12000.0, 13400.0]"
B_bands="[8440.0, 9610.0, 10330.0, 12270.0, 13270.0]"

INPUT_DIM_A=5
INPUT_DIM_B=5

FILTER_DAYTIME=False

for variable in "${!variables_and_bands_5ch[@]}"; do
    bands=${variables_and_bands_5ch[$variable]}
    wandb_name="MSG-GOES16-3000m-${variable}"
    python itipy/train/geo_to_geo.py \
        --config-name msg-to-goes.yaml \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done
