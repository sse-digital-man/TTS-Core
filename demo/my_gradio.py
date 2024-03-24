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


def api(text, api_type):
    _ApiTTS = ApiTTS()
    if api_type == 'ms':
        _ApiTTS.change_api('ms')
    elif api_type == 'iflytek':
        _ApiTTS.change_api('iflytek')
    _ApiTTS.synthesize(text)


def create_app():
    app = gr.Blocks()

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
                input_text = gr.Textbox(
                    lines=5, placeholder="想说却还没说的 还很多 攒着是因为想写成歌",
                    label="填写您想生成的文本")

                btn_edge = gr.Button("一键开启真实拟声吧", variant="primary")
                output_text = gr.Textbox(label="输出文本", visible=False)
                output_audio = gr.Audio(type="filepath", label="Edge TTS真实拟声")
    return app


def main():
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
