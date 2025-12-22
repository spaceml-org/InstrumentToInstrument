#!/bin/bash

set -o xtrace

# Delete the tmp-data folder
rm -rf /home/anna.jungbluth/tmp-data/himawari
rm -rf /home/anna.jungbluth/tmp-data/goes

EPOCHS=100

# 1-channel:
# declare -A variables_and_bands_1ch=(
#     ["1ch-3.9um"]="[3890.0]"
# )
# A_bands="[3900.0]"
# B_bands="[3890.0]"

# INPUT_DIM_A=1
# INPUT_DIM_B=1

# FILTER_DAYTIME=False
# LIMIT_VAL_BATCHES=1000 # reset to full val set, since daytime filtering reduces val set size

# for variable in "${!variables_and_bands_1ch[@]}"; do
#     bands=${variables_and_bands_1ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

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
#     # ["3ch-10.3-12.4um"]="[10330.0,11190.0,12400.0]"  # 3 main windows - using parentheses
#     # ["3ch-6.2-7.3um"]="[6170.0,6930.0,7340.0]" # Water vapor channels
#     # ["3ch-0.47-0.87um"]="[470.0,640.0,870.0]" # Visible channels
#     ["3ch-1.6-3.9um"]="[1610.0,2250.0,3890.0]" # NIR channels
# )
# A_bands="[1600.0,2300.0,3900.0]"
# B_bands="[1610.0,2250.0,3890.0]"

# INPUT_DIM_A=3
# INPUT_DIM_B=3

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=1000 # reset to full val set, since daytime filtering reduces val set size

# for variable in "${!variables_and_bands_3ch[@]}"; do
#     bands=${variables_and_bands_3ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
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

# 6-channel: All infrared channels
# declare -A variables_and_bands_6ch=(
#      ["6ch-8.4-13.3um"]="[8440.0, 9610.0, 10330.0, 11190.0, 12270.0, 13270.0]"
# )

# INPUT_DIM_A=6
# INPUT_DIM_B=6

# for variable in "${!variables_and_bands_6ch[@]}"; do
#     bands=${variables_and_bands_6ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

# 3/4-channel: All visible + near-IR channels (daytime only)
# declare -A variables_and_bands_3ch=(
#     ["4ch-0.47-0.87um"]="[470.0, 640.0, 870.0]"
# )

# A_bands="[470.0, 510.0, 640.0, 860.0]"
# B_bands="[470.0, 640.0, 870.0]"

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

# INPUT_DIM_A=4
# INPUT_DIM_B=3

# for variable in "${!variables_and_bands_3ch[@]}"; do
#     bands=${variables_and_bands_3ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

# 6-channel: All visible + near-IR channels (daytime only)
# declare -A variables_and_bands_6ch=(
#     ["6ch-0.47-3.9um"]="[470.0, 640.0, 870.0, 1380.0, 1610.0, 2250.0]"
# )

# A_bands="[470.0, 510.0, 640.0, 860.0, 1600.0,2300.0]"
# B_bands="[470.0, 640.0, 870.0, 1380.0, 1610.0, 2250.0]"

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

# INPUT_DIM_A=6
# INPUT_DIM_B=6

# for variable in "${!variables_and_bands_6ch[@]}"; do
#     bands=${variables_and_bands_6ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

# 3/4-channel:

# declare -A variables_and_bands_3ch=(
#     ["4|3ch-0.47-0.87um"]="[470.0, 640.0, 870.0]"
# )
# A_bands="[470.0, 510.0, 640.0, 860.0]"
# B_bands="[470.0, 640.0, 870.0]"

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

# INPUT_DIM_A=4
# INPUT_DIM_B=3

# LAMBDA_RECONSTRUCTION_ID=0
# LAMBDA_CONTENT_ID=0

# for variable in "${!variables_and_bands_3ch[@]}"; do
#     bands=${variables_and_bands_3ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         +model.lambda_reconstruction_id=$LAMBDA_RECONSTRUCTION_ID \
#         +model.lambda_content_id=$LAMBDA_CONTENT_ID \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done


# 2-channel: All visible + near-IR channels (daytime only)
# declare -A variables_and_bands_2ch=(
#     ["2ch-1.6-2.2um"]="[1610.0, 2250.0]"
# )
# A_bands="[1600.0, 2300.0]"
# B_bands="[1610.0, 2250.0]"

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

# INPUT_DIM_A=2
# INPUT_DIM_B=2

# # LAMBDA_RECONSTRUCTION_ID=0
# # LAMBDA_CONTENT_ID=0

# for variable in "${!variables_and_bands_2ch[@]}"; do
#     bands=${variables_and_bands_2ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

# 5-channel: All visible + near-IR channels (daytime only)
declare -A variables_and_bands_5ch=(
    ["5ch-0.47-2.2um"]="[470.0, 640.0, 870.0, 1610.0, 2250.0]"
)
A_bands="[470.0, 640.0, 860.0, 1600.0, 2300.0]"
B_bands="[470.0, 640.0, 870.0, 1610.0, 2250.0]"

FILTER_DAYTIME=True
LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

INPUT_DIM_A=5
INPUT_DIM_B=5

# LAMBDA_RECONSTRUCTION_ID=0
# LAMBDA_CONTENT_ID=0

for variable in "${!variables_and_bands_5ch[@]}"; do
    bands=${variables_and_bands_5ch[$variable]}
    wandb_name="HIM8-GOES16-${variable}"
    python itipy/train/geo_to_geo.py \
        data.A_bands="$A_bands" \
        data.B_bands="$B_bands" \
        data.filter_daytime=$FILTER_DAYTIME \
        model.input_dim_a=$INPUT_DIM_A \
        model.input_dim_b=$INPUT_DIM_B \
        logging.wandb_name="$wandb_name" \
        training.epochs=$EPOCHS \
        training.limit_val_batches=$LIMIT_VAL_BATCHES
done

# 6-channel: All visible + near-IR channels (daytime only)
# declare -A variables_and_bands_6ch=(
#     ["6ch-0.47-2.2um"]="[470.0, 640.0, 870.0, 1380.0, 1610.0, 2250.0]"
# )
# A_bands="[470.0, 510.0, 640.0, 860.0, 1600.0, 2300.0]"
# B_bands="[470.0, 640.0, 870.0, 1380.0, 1610.0, 2250.0]"

# FILTER_DAYTIME=True
# LIMIT_VAL_BATCHES=null # reset to full val set, since daytime filtering reduces val set size

# INPUT_DIM_A=6
# INPUT_DIM_B=6

# LAMBDA_RECONSTRUCTION_ID=0
# LAMBDA_CONTENT_ID=0

# for variable in "${!variables_and_bands_6ch[@]}"; do
#     bands=${variables_and_bands_6ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$A_bands" \
#         data.B_bands="$B_bands" \
#         data.filter_daytime=$FILTER_DAYTIME \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         +model.lambda_reconstruction_id=$LAMBDA_RECONSTRUCTION_ID \
#         +model.lambda_content_id=$LAMBDA_CONTENT_ID \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS \
#         training.limit_val_batches=$LIMIT_VAL_BATCHES
# done

# 9-channel: All infrared channels
# declare -A variables_and_bands_9ch=(
#     ["9ch-6.9-13.3um"]="[6170.0,6930.0,7340.0,8440.0,9610.0,10330.0,11190.0,12270.0,13270.0]"
# )

# INPUT_DIM_A=9
# INPUT_DIM_B=9

# for variable in "${!variables_and_bands_9ch[@]}"; do
#     bands=${variables_and_bands_9ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS
# done

# 16-channel: All channels channels

# declare -A variables_and_bands_16ch=(
#     ["16ch-0.47-13.3um"]="[470.0, 640.0, 870.0, 1380.0, 1610.0, 2250.0, 3890.0, 6170.0, 6930.0, 7340.0, 8440.0, 9610.0, 10330.0, 11190.0, 12270.0, 13270.0]"
# )

# INPUT_DIM_A=16
# INPUT_DIM_B=16

# for variable in "${!variables_and_bands_16ch[@]}"; do
#     bands=${variables_and_bands_16ch[$variable]}
#     wandb_name="HIM8-GOES16-${variable}"
#     python itipy/train/geo_to_geo.py \
#         data.A_bands="$bands" \
#         data.B_bands="$bands" \
#         model.input_dim_a=$INPUT_DIM_A \
#         model.input_dim_b=$INPUT_DIM_B \
#         logging.wandb_name="$wandb_name" \
#         training.epochs=$EPOCHS
# done

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
