# flake8: noqa: E402
import os
import logging

logging.getLogger("numba").setLevel(logging.WARNING)
logging.getLogger("markdown_it").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO, format="| %(name)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

import torch
import localtts.utils as utils
from localtts.infer import infer, get_net_g
import gradio as gr
import webbrowser
import numpy as np
from localtts.config import config

net_g = None
hps = utils.get_hparams_from_file(config.webui_config.config_path)

device = config.webui_config.device
if device == "mps":
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


def generate_audio(
    slices,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    speaker,
    language,
):
    audio_list = []
    silence = np.zeros(hps.data.sampling_rate // 2, dtype=np.int16)
    version = hps.version  # if hasattr(hps, "version") else latest_version
    net_g = get_net_g(
        model_path=config.webui_config.model, version=version, device=device, hps=hps
    )
    with torch.no_grad():
        for piece in slices:
            audio = infer(
                piece,
                sdp_ratio=sdp_ratio,
                noise_scale=noise_scale,
                 noise_scale_w=noise_scale_w,
                length_scale=length_scale,
                sid=speaker,
                language=language,
                hps=hps,
                net_g=net_g,
                device=device,
            )
            audio16bit = gr.processing_utils.convert_to_16_bit_wav(audio)
            audio_list.append(audio16bit)
            audio_list.append(silence)  # 将静音添加到列表中
    return audio_list



def tts_fn(
    text: str,
    speaker,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    language,
):
    audio_list = []
    audio_list.extend(
        generate_audio(
           text.split("|"),
           sdp_ratio,
            noise_scale,
            noise_scale_w,
            length_scale,
            speaker,
            language,
        )
    )

    audio_concat = np.concatenate(audio_list)
    return "Success", (hps.data.sampling_rate, audio_concat)