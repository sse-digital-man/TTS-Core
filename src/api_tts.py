# TODO 实现API调用
import json

# NOTE Every API Object accept ApiTTS.config to init itself


class ApiTTS:
    def __init__(self, config_path="../config/tts_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.api_list = list(self.config.get("api").keys())
        self.api = None

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    # TODO Construct the corresponding object according to api_name in api_list
    # PERF： Use the object pool to save the generated objects
    def change_api(self, api_name):
        pass

    def synthesize(self, text):
        self.api.synthesize(text)
