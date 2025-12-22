import numpy as np

# default split configuration for the datamodule
SPLITS_DICT = {
    "train": {
        "years": np.arange(2004, 2025).tolist(),
        "months": np.arange(1, 13).tolist(),
        "days": np.arange(2, 23).tolist(),
    },
    "val": {
        "years": np.arange(2004, 2025).tolist(),
        "months": np.arange(1, 13).tolist(),
        "days": np.arange(24, 32).tolist(),
    },
}

MSG_CHANNELS = [
    "VIS006",
    "VIS008",
    "IR_016",
    "IR_039",
    "IR_087",
    "IR_097",
    "IR_108",
    "IR_120",
    "IR_134",
    "WV_062",
    "WV_073",
]
GOES_CHANNELS = [
    "CMI_C01",
    "CMI_C02",
    "CMI_C03",
    "CMI_C04",
    "CMI_C05",
    "CMI_C06",
    "CMI_C07",
    "CMI_C08",
    "CMI_C09",
    "CMI_C10",
    "CMI_C11",
    "CMI_C12",
    "CMI_C13",
    "CMI_C14",
    "CMI_C15",
    "CMI_C16",
]
HIMAWARI_CHANNELS = [
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "B11",
    "B12",
    "B13",
    "B14",
    "B15",
    "B16",
]

CHANNELS = {
    "msg": MSG_CHANNELS,
    "goes": GOES_CHANNELS,
    "himawari": HIMAWARI_CHANNELS,
}

MSG_WAVELENGTHS = [
    640.0,
    810.0,
    1640.0,
    3920.0,
    6250.0,
    7350.0,
    8700.0,
    9660.0,
    10800.0,
    12000.0,
    13400.0,
]

GOES_WAVELENGTHS = [
    470.0,
    640.0,
    870.0,
    1380.0,
    1610.0,
    2250.0,
    3890.0,
    6170.0,
    6930.0,
    7340.0,
    8440.0,
    9610.0,
    10330.0,
    11190.0,
    12270.0,
    13270.0,
]

HIMAWARI_WAVELENGTHS = [
    470.0,
    510.0,
    640.0,
    860.0,
    1600.0,
    2300.0,
    3900.0,
    6200.0,
    6900.0,
    7300.0,
    8600.0,
    9600.0,
    10400.0,
    11200.0,
    12400.0,
    13300.0,
]

WAVELENGTHS = {
    "himawari": HIMAWARI_WAVELENGTHS,
    "goes": GOES_WAVELENGTHS,
    "msg": MSG_WAVELENGTHS,
}
