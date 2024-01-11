from local_tts import LocalTTS
from api_tts import ApiTTS
from enum import Enum


class tts_type(Enum):
    API = 1
    LOCAL = 2


class TTSController:
    def __init__(self, config_path='../config/tts_config.json'):
        self.api_tts = ApiTTS(config_path=config_path)
        self.local_tts = LocalTTS(config_path=config_path)
        self.tts_type = tts_type.API

    def generate_speech(self, text):
        if self.tts_type == tts_type.API:
            return self.api_tts.synthesize(text)
        elif self.tts_type == tts_type.LOCAL:
            return self.local_tts.synthesize(text)

    def llm_interface(self, text):
        # Interface provided to the LLM, receiving text input and returning voice files or real-time voice streams
        return self.generate_speech(text)


# 示例用法
if __name__ == "__main__":
    tts_controller = TTSController()

    text_input = "Hello, this is a test."
    speech_output = tts_controller.llm_interface(text_input)

    print("Generated Speech:", speech_output)
