from openai import OpenAI
import os
import random
from datetime import datetime

from src.interface import ConfigurableModel, GenerativeModel


class OpenAIAPI(ConfigurableModel, GenerativeModel):
    def __init__(self, ApiTTS):
        self.file_name = None  # 初始化文件名和路径
        self.speech_file_path = None
        self.api_config = ApiTTS.api_config  # 获取API配置信息
        self._initialize()

    def _initialize(self):
        # 从API配置中获取MS语音合成相关的配置信息
        openai_config = self.api_config['openai_tts']
        self.api_key = openai_config['openai_tts_api_key']
        self.voice = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.client = OpenAI(api_key=self.api_key, base_url='https://api.chatanywhere.tech/v1')

    def synthesize(self, input_text, output_dir=r'..\out'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        v = self.voice[1]
        self.file_name = f"{datetime.now().strftime('OPENAI_TTS-%Y%m%d%H%M%S')}.mp3"
        self.speech_file_path = os.path.join(output_dir, self.file_name)
        print(self.speech_file_path)

        # TTS API调用
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=v,
            input=input_text,
        )

        response.stream_to_file(self.speech_file_path)
        return self.speech_file_path

'''
if __name__ == '__main__':
    # Example usage
    test_api_tts = api_tts.ApiTTS()
    openai_tts = OpenAIAPI(test_api_tts)
    input_text = "感谢来到直播间的粉丝们，我直播时间一般是10点到12点，大家记得准时来哦，我们每天都有福利哒。"
    openai_tts.synthesize(input_text)
'''