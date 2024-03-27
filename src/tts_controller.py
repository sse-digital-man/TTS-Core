from local_tts import LocalTTS
from api_tts import ApiTTS
from enum import Enum
from queue import Queue


class TTS_TYPE(Enum):
    API = 1
    LOCAL = 2


class TTSController:
    def __init__(self, config_path='../config/tts_config.json'):
        self.api_tts = ApiTTS(config_path=config_path)
        self.local_tts = LocalTTS(config_path=config_path)
        self.tts_type = TTS_TYPE.API

    def generate_speech(self, text):
        if self.tts_type == TTS_TYPE.API:
            return self.api_tts.synthesize(text)
        elif self.tts_type == TTS_TYPE.LOCAL:
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
    test_api_tts.change_api('iflytek')

    text_input = "Hello, this is a test."
    speech_output = test_api_tts.synthesize(text_input)

    audio_manager.add_to_queue(speech_output)

    print("Generated Speech:", speech_output)
