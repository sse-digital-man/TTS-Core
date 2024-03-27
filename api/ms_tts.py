import os
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream
from datetime import datetime

from src import api_tts
from src.interface import ConfigurableModel, GenerativeModel


# 定义 MSApi 类，继承自 ConfigurableModel 和 GenerativeModel
class MSApi(ConfigurableModel, GenerativeModel):
    def __init__(self, ApiTTS):
        self.file_name = None  # 初始化文件名和路径
        self.speech_file_path = None
        self.api_config = ApiTTS.api_config  # 获取API配置信息
        self._initialize()

    def _initialize(self):
        # 从API配置中获取MS语音合成相关的配置信息
        ms_api_config = self.api_config['ms_tts']
        self.subscription_key = ms_api_config['ms_tts_api_secret']
        self.region = ms_api_config['ms_tts_region']
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key, region=self.region)

    def synthesize(self, text, output_dir=r'..\out'):

        speech_config = self.speech_config

        speech_config.speech_synthesis_voice_name = 'zh-CN-XiaohanNeural'

        # 生成语音文件名和路径
        self.file_name = f'{datetime.now().strftime("MS_TTS-%Y%m%d%H%M%S")}.wav'
        self.speech_file_path = os.path.join(output_dir, self.file_name)

        # 文件输出
        audio_config = speechsdk.audio.AudioOutputConfig(filename=self.speech_file_path)

        # 创建语音合成器对象，设置语音合成的配置和输出
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)

        # 调用语音合成器进行语音合成，并获取合成结果
        speech_synthesis_result = speech_synthesizer.speak_text_async(
            text).get()

        # 根据合成结果的原因进行相应的处理
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            stream = AudioDataStream(speech_synthesis_result)
            stream.save_to_wav_file(self.speech_file_path)
            print(f"Speech synthesized for text: {text}")
            print(f"File saved at: {self.speech_file_path}")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(
                cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(
                        cancellation_details.error_details))
                    print(
                        "Did you set the speech resource key and region values?")
        return self.speech_file_path


'''
if __name__ == '__main__':
    # Example usage
    test_api_tts = api_tts.ApiTTS()
    synthesizer = MSApi(test_api_tts)
    text_to_synthesize = "感谢来到直播间的粉丝们，我直播时间一般是10点到12点..."
    synthesizer.synthesize(text_to_synthesize)
'''