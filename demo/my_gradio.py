import gradio as gr
import os
import tempfile
import tempfile
import anyio

from azure.cognitiveservices.speech import AudioDataStream, SpeechSynthesizer
import azure.cognitiveservices.speech as speechsdk

from src.api_tts import ApiTTS

from scipy.io import wavfile
from scipy.io.wavfile import write

import localtts.webui
from localtts.config import config
from localtts.infer import infer, get_net_g
from localtts.webui import tts_fn, generate_audio
import logging
from localtts.utils import get_hparams_from_file
import webbrowser
import localtts.utils as utils

logger = logging.getLogger(__name__)
net_g = None
hps = utils.get_hparams_from_file(config.webui_config.config_path)

device = config.webui_config.device
if device == "mps":
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


def api(text, api_type):
    _ApiTTS = ApiTTS()
    if api_type == 'ms':
        _ApiTTS.change_api('ms')
    elif api_type == 'iflytek':
        _ApiTTS.change_api('iflytek')
    return _ApiTTS.synthesize(text)


def create_app():
    app = gr.Blocks()
    if config.webui_config.debug:
        logger.info("Enable DEBUG-LEVEL log")
        logging.basicConfig(level=logging.DEBUG)
    hps = get_hparams_from_file(config.webui_config.config_path)
    # 若config.json中未指定版本则默认为最新版本
    version = hps.version  # if hasattr(hps, "version") else latest_version
    net_g = get_net_g(
        model_path=config.webui_config.model, version=version, device=device, hps=hps
    )
    speaker_ids = hps.data.spk2id
    speakers = list(speaker_ids.keys())
    languages = ["ZH"]
    with app:
        gr.Markdown("# <center>🌟 - TTS-Core </center>")
        with gr.Tab("⚡ API TTS"):
            with gr.Row():
                with gr.Column():
                    api_type = gr.Dropdown(choices=[
                        'ms', 'iflytek'], label='请选择模型')

                with gr.Column():
                    inp_text = gr.Textbox(
                        label="请填写您想生成的文本",
                        placeholder="想说却还没说的 还很多 攒着是因为想写成歌", lines=5)
                    btn_text = gr.Button("拟声", variant="primary")

                with gr.Column():
                    inp1 = gr.Audio(type="filepath",
                                    label="TTS Result", interactive=False)
            btn_text.click(api, [inp_text, api_type], inp1)

        with gr.Tab("⚡ Local-Model TTS"):
            with gr.Row():
                with gr.Column():
                    text = gr.TextArea(
                        label="输入文本内容",
                        placeholder="""
                            可以用'|'分割长段实现分句生成。
                            """,
                    )
                    speaker = gr.Dropdown(
                        choices=speakers, value=speakers[0], label="选择说话人"
                    )
                    sdp_ratio = gr.Slider(
                        minimum=0, maximum=1, value=0.2, step=0.1, label="SDP/DP混合比"
                    )
                    noise_scale = gr.Slider(
                        minimum=0.1, maximum=2, value=0.6, step=0.1, label="感情"
                    )
                    noise_scale_w = gr.Slider(
                        minimum=0.1, maximum=2, value=0.8, step=0.1, label="音素长度"
                    )
                    length_scale = gr.Slider(
                        minimum=0.1, maximum=2, value=1.0, step=0.1, label="语速"
                    )
                    language = gr.Dropdown(
                        choices=languages, value=languages[0], label="选择语言"
                    )
                    btn = gr.Button("生成音频！", variant="primary")
                    text_output = gr.Textbox(label="状态信息")
                    audio_output = gr.Audio(label="输出音频")
            btn.click(
                tts_fn,
                inputs=[
                    text,
                    speaker,
                    sdp_ratio,
                    noise_scale,
                    noise_scale_w,
                    length_scale,
                    language,
                ],
                outputs=[text_output, audio_output],
            )
    return app


def main():
    app = create_app()
    print("推理页面已开启!")
    webbrowser.open(f"http://127.0.0.1:{config.webui_config.port}")
    app.launch(share=config.webui_config.share, server_port=config.webui_config.port)


if __name__ == "__main__":
    main()
