from api.ms_tts import MSApi
from api.iflytek_tts import IflytekApi
from api.openai_tts import OpenAIAPI
from api.volcano_tts import VolcanoAPI
from local_tts import LocalTTS
from api_tts import ApiTTS
from enum import Enum
from queue import Queue



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

class AudioQueueManager:
    def __init__(self):
        self.queue = Queue()

    def add_to_queue(self, item):
        self.queue.put(item)

    def get_from_queue(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

    def get_all_items(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        return items
    
# 示例用法
if __name__ == "__main__":
    tts_controller = TTSController()
    audio_manager = AudioQueueManager()

    test_api_tts = ApiTTS()
    synthesizer = IflytekApi(test_api_tts)

    text_input = "Hello, this is a test."
    speech_output = synthesizer.synthesize(text_input)

    # speech_output = tts_controller.llm_interface(text_input)

    audio_manager.add_to_queue(speech_output)
    
    print("Generated Speech:", speech_output)
