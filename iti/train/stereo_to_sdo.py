import logging
import os

from sunpy.visualization.colormaps import cm

from iti.data.editor import RandomPatchEditor, SliceEditor, BrightestPixelPatchEditor
from iti.train.model import DiscriminatorMode

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

import torch
from torch.utils.data import DataLoader

from iti.data.dataset import SDODataset, StorageDataset, STEREODataset
from iti.callback import PlotBAB, PlotABA, HistoryCallback, ProgressCallback, SaveCallback
from iti.trainer import Trainer, loop

base_dir = "/gss/r.jarolim/iti/stereo_v7"

stereo_path = "/gss/r.jarolim/data/stereo_iti2021_prep"
stereo_converted_path = '/gss/r.jarolim/data/converted/stereo_1024'
sdo_path = "/gss/r.jarolim/data/ch_detection"
sdo_valid_path = "/gss/r.jarolim/data/sdo/valid"

prediction_dir = os.path.join(base_dir, 'prediction')
os.makedirs(prediction_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(base_dir, "info_log")),
        logging.StreamHandler()
    ])

# Init Model
trainer = Trainer(4, 4, upsampling=2, discriminator_mode=DiscriminatorMode.CHANNELS, lambda_diversity=0,
                  norm='in_rs_aff')
trainer.cuda()
start_it = trainer.resume(base_dir)

# Init Dataset

sdo_dataset = SDODataset(sdo_path, resolution=4096, patch_shape=(1024, 1024), months=list(range(11)))
sdo_converted_path = '/gss/r.jarolim/data/converted/sdo_4096'
sdo_dataset = StorageDataset(sdo_dataset,
                             sdo_converted_path,
                             ext_editors=[SliceEditor(0, -1),
                                          RandomPatchEditor((512, 512))])

stereo_dataset = StorageDataset(STEREODataset(stereo_path, months=list(range(11))),
                                stereo_converted_path,
                                ext_editors=[BrightestPixelPatchEditor((256, 256)), RandomPatchEditor((128, 128))])

sdo_valid = StorageDataset(SDODataset(sdo_valid_path, resolution=4096, patch_shape=(1024, 1024), months=[11, 12]),
                           sdo_converted_path, ext_editors=[RandomPatchEditor((512, 512)), SliceEditor(0, -1)])
stereo_valid = StorageDataset(STEREODataset(stereo_path, patch_shape=(1024, 1024), months=[11, 12]),
                              stereo_converted_path, ext_editors=[RandomPatchEditor((128, 128))])

sdo_iterator = loop(DataLoader(sdo_dataset, batch_size=1, shuffle=True, num_workers=8))
stereo_iterator = loop(DataLoader(stereo_dataset, batch_size=1, shuffle=True, num_workers=8))

# Init Plot Callbacks
history = HistoryCallback(trainer, base_dir)
progress = ProgressCallback(trainer)
save = SaveCallback(trainer, base_dir)

plot_settings_A = [
    {"cmap": cm.sdoaia171, "title": "SECCHI 171", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia193, "title": "SECCHI 195", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia211, "title": "SECCHI 284", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia304, "title": "SECCHI 304", 'vmin': -1, 'vmax': 1},
]
plot_settings_B = [
    {"cmap": cm.sdoaia171, "title": "AIA 171", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia193, "title": "AIA 193", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia211, "title": "AIA 211", 'vmin': -1, 'vmax': 1},
    {"cmap": cm.sdoaia304, "title": "AIA 304", 'vmin': -1, 'vmax': 1},
]

log_iteration = 1000

aba_callback = PlotABA(stereo_valid.sample(4), trainer, prediction_dir, log_iteration=log_iteration,
                       plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)

bab_callback = PlotBAB(sdo_valid.sample(4), trainer, prediction_dir, log_iteration=log_iteration,
                       plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B)

full_disk_aba_callback = PlotABA(STEREODataset(stereo_path).sample(4),
                                 trainer, prediction_dir, log_iteration=log_iteration, batch_size=1,
                                 plot_settings_A=plot_settings_A, plot_settings_B=plot_settings_B,
                                 plot_id='FULL_ABA')

aba_callback.call(0)
bab_callback.call(0)
full_disk_aba_callback.call(0)

callbacks = [history, progress, save, aba_callback, bab_callback, full_disk_aba_callback]

# Start training
for it in range(start_it, int(1e8)):
    if it > 100000:
        trainer.gen_ab.eval()  # fix running stats
        trainer.gen_ba.eval()  # fix running stats
    x_a, x_b = next(stereo_iterator), next(sdo_iterator)
    x_a, x_b = x_a.float().cuda().detach(), x_b.float().cuda().detach()
    #
    trainer.discriminator_update(x_a, x_b)
    trainer.generator_update(x_a, x_b)
    torch.cuda.synchronize()
    #
    for callback in callbacks:
        callback(it)