import json
from api.ms_tts import MSApi
from api.iflytek_tts import IflytekApi
from api.openai_tts import OpenAIAPI
from api.volcano_tts import VolcanoAPI


# NOTE Every API Object accept ApiTTS.config to init itself


class ApiTTS:
    def __init__(self, config_path="../config/tts_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.api_config = self.config.get("api")
        self.api_list = list(self.config.get("api").keys())
        self.api = MSApi(self)

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    # TODO Construct the corresponding object according to api_name in api_list
    # PERF： Use the object pool to save the generated objects
    def change_api(self, api_name):
        if api_name == 'ms':
            self.api = MSApi(self)
        elif api_name == 'iflytek':
            self.api = IflytekApi(self)
        elif api_name == 'openai':
            self.api = OpenAIAPI(self)
        elif api_name == 'volcano':
            self.api = VolcanoAPI(self)

    def synthesize(self, text):
        self.api.synthesize(text)
