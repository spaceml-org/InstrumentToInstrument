#!/bin/bash

set -o xtrace

# Delete the tmp-data folder
rm -rf /home/anna.jungbluth/tmp-data/himawari
rm -rf /home/anna.jungbluth/tmp-data/goes

EPOCHS=100

# Single-channel experiments (thermal IR only - 24/7 available)
# Define dictionary of variables and corresponding bands
# declare -A variables_and_bands=(
    # ["1ch-8.4um"]="[8440.0]"     # IR window - less water vapor interference
    # # ["1ch-9.6um"]="[9610.0]"     # Ozone absorption - stratospheric info
    # ["1ch-10.4um"]="[10330.0]"   # Clean IR - atmospheric window
    # ["1ch-11.2um"]="[11190.0]"   # Primary IR window - most common
    # # ["1ch-12.4um"]="[12400.0]"   # Dirty IR - split window reference
    # ["1ch-13.3um"]="[13270.0]"   # CO2 absorption - cloud top height
# )
# INPUT_DIM_A=1
# INPUT_DIM_B=1
#
# for variable in "${!variables_and_bands[@]}"; do
#     bands=${variables_and_bands[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands=$bands \
#         data.B_bands=$bands \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name=$wandb_name \
#         training.epochs=$EPOCHS
#     # Delete the tmp-data folder
#     # rm -rf /home/anna.jungbluth/tmp-data/himawari
#     # rm -rf /home/anna.jungbluth/tmp-data/goes
# done

# 3-channel: Atmospheric windows + CO2
# declare -A variables_and_bands_3ch=(
#     ["3ch-10.3-12.4um"]="[10330.0,11190.0,12400.0]"  # 3 main windows - using parentheses
#     # ["3ch-8.4-13.3um"]="[8440.0,11190.0,13270.0]"   # Wide spectral coverage - using parentheses
# )

# INPUT_DIM_A=3
# INPUT_DIM_B=3

# for variable in "${!variables_and_bands_3ch[@]}"; do
#     bands=${variables_and_bands_3ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS
# done

# 5-channel: Atmospheric windows + CO2
# declare -A variables_and_bands_5ch=(
#     ["5ch-9.6-13.3um"]="[9610.0,10330.0,11190.0,12400.0,13270.0]"  # 5 main windows - using parentheses
# )

# INPUT_DIM_A=5
# INPUT_DIM_B=5

# for variable in "${!variables_and_bands_5ch[@]}"; do
#     bands=${variables_and_bands_5ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS
# done

# 9-channel: All infrared channels
declare -A variables_and_bands_9ch=(
    ["9ch-6.9-13.3um"]="[6170.0,6930.0,7340.0,8440.0,9610.0,10330.0,11190.0,12270.0,13270.0]"
)

INPUT_DIM_A=9
INPUT_DIM_B=9

for variable in "${!variables_and_bands_9ch[@]}"; do
    bands=${variables_and_bands_9ch[$variable]}
    wandb_name="HIM8-GOES16-${variable}"
    python itipy/train/geo_to_geo.py \
        data.A_bands="$bands" \
        data.B_bands="$bands" \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS
done

# # Delete the tmp-data folder
# rm -rf /home/anna.jungbluth/tmp-data/himawari
# rm -rf /home/anna.jungbluth/tmp-data/goes

# # 6-channel: All thermal IR (complete)
# declare -A variables_and_bands_6ch=(
#     ["6ch-8.4-13.3um"]="[8440.0,9610.0,10330.0,11190.0,12400.0,13270.0]"  # Complete thermal set - using parentheses
# )

# INPUT_DIM_A=6
# INPUT_DIM_B=6

# for variable in "${!variables_and_bands_6ch[@]}"; do
#     bands=${variables_and_bands_6ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name"
    # Delete the tmp-data folder
    # rm -rf /home/anna.jungbluth/tmp-data/himawari
    # rm -rf /home/anna.jungbluth/tmp-data/goes
# done

# # Delete the tmp-data folder
# rm -rf /home/anna.jungbluth/tmp-data/himawari
# rm -rf /home/anna.jungbluth/tmp-data/goes
