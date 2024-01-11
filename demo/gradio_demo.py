import gradio as gr
import os
import tempfile
from openai import OpenAI
import tempfile
import anyio


# Set an environment variable for key
# os.environ['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

# client = OpenAI() # add api_key

from scipy.io import wavfile
from scipy.io.wavfile import write

from speechbrain.pretrained import SpectralMaskEnhancement

enhance_model = SpectralMaskEnhancement.from_hparams(
    source="speechbrain/metricgan-plus-voicebank",
    savedir="pretrained_models/metricgan-plus-voicebank",
)

knn_vc = torch.hub.load('bshall/knn-vc', 'knn_vc', prematched=True,
                        trust_repo=True, pretrained=True, device='cpu')

language_dict = tts_order_voice


async def text_to_speech_edge(text, language_code):
    voice = language_dict[language_code]
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_path = tmp_file.name

    await communicate.save(tmp_path)

    return "语音合成完成：{}".format(text), tmp_path


def voice_change(audio_in, audio_ref):
    samplerate1, data1 = wavfile.read(audio_in)
    samplerate2, data2 = wavfile.read(audio_ref)
    write("./audio_in.wav", samplerate1, data1)
    write("./audio_ref.wav", samplerate2, data2)

    query_seq = knn_vc.get_features("./audio_in.wav")
    matching_set = knn_vc.get_matching_set(["./audio_ref.wav"])
    out_wav = knn_vc.match(query_seq, matching_set, topk=4)
    torchaudio.save('output.wav', out_wav[None], 16000)
    noisy = enhance_model.load_audio(
        'output.wav'
    ).unsqueeze(0)
    enhanced = enhance_model.enhance_batch(noisy, lengths=torch.tensor([1.]))
    torchaudio.save('enhanced.wav', enhanced.cpu(), 16000)
    return 'enhanced.wav'


def tts(text, model, voice, api_key):
    if len(text) > 300:
        raise gr.Error('您输入的文本字符多于300个，请缩短您的文本')
    if api_key == '':
        raise gr.Error('Please enter your OpenAI API Key')
    else:
        try:
            client = OpenAI(api_key=api_key)

            response = client.audio.speech.create(
                model=model,  # "tts-1","tts-1-hd"
                voice=voice,  # 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
                input=text,
            )

        except Exception as error:
            # Handle any exception that occurs
            raise gr.Error(
                "An error occurred while generating speech. Please check your API key and try again.")
            print(str(error))

    # Create a temp file to save the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(response.content)

    # Get the file path of the temp file
    temp_file_path = temp_file.name

    return temp_file_path


app = gr.Blocks()

with app:
    gr.Markdown("# <center>🌟 - TTS-Core </center>")
    with gr.Tab("🤗 Local-Model TTS"):
        with gr.Row(variant='panel'):
            api_key = gr.Textbox(
                type='password', label='OpenAI API Key', placeholder='请在此填写您的OpenAI API Key')
            model = gr.Dropdown(choices=[
                                'tts-1', 'tts-1-hd'], label='请选择模型（tts-1推理更快，tts-1-hd音质更好）', value='tts-1')
            voice = gr.Dropdown(choices=[
                                'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], label='请选择一个说话人', value='alloy')
        with gr.Row():
            with gr.Column():
                inp_text = gr.Textbox(
                    label="请填写您想生成的文本（中英文皆可）", placeholder="想说却还没说的 还很多 攒着是因为想写成歌", lines=5)
                btn_text = gr.Button("一键开启真实拟声吧", variant="primary")

            with gr.Column():
                inp1 = gr.Audio(type="filepath",
                                label="OpenAI TTS真实拟声", interactive=False)
                inp2 = gr.Audio(type="filepath",
                                label="请上传AI变声的参照音频（决定变声后的语音音色）")
                btn1 = gr.Button("一键开启AI变声吧", variant="primary")
            with gr.Column():
                out1 = gr.Audio(type="filepath", label="AI变声后的专属音频")
            btn_text.click(tts, [inp_text, model, voice, api_key], inp1)
            btn1.click(voice_change, [inp1, inp2], out1)
    with gr.Tab("⚡ Edge TTS"):
        with gr.Row():
            input_text = gr.Textbox(
                lines=5, placeholder="想说却还没说的 还很多 攒着是因为想写成歌", label="请填写您想生成的文本（中英文皆可）")
            default_language = list(language_dict.keys())[15]
            language = gr.Dropdown(choices=list(
                language_dict.keys()), value=default_language, label="请选择文本对应的语言")
            btn_edge = gr.Button("一键开启真实拟声吧", variant="primary")
            output_text = gr.Textbox(label="输出文本", visible=False)
            output_audio = gr.Audio(type="filepath", label="Edge TTS真实拟声")

        with gr.Row():
            inp_vc = gr.Audio(
                type="filepath", label="请上传AI变声的参照音频（决定变声后的语音音色）")
            btn_vc = gr.Button("一键开启AI变声吧", variant="primary")
            out_vc = gr.Audio(type="filepath", label="AI变声后的专属音频")

        btn_edge.click(text_to_speech_edge, [input_text, language], [
                       output_text, output_audio])
        btn_vc.click(voice_change, [output_audio, inp_vc], out_vc)

    gr.Markdown(
        "### <center>注意❗：请不要生成会对个人以及组织造成侵害的内容，此程序仅供科研、学习及个人娱乐使用。Get your OpenAI API Key [here](https://platform.openai.com/api-keys).</center>")
    gr.HTML('''
        <div class="footer">
                    <p>🌊🏞️🎶 - 江水东流急，滔滔无尽声。 明·顾璘
                    </p>
        </div>
    ''')

app.launch(show_error=True)
