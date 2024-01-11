import json

# NOTE Every LocalTTS Object accept LocalTTS.config to init itself


class LocalTTS:
    def __init__(self, config_path="../config/tts_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.model_list = list(self.config.get("model").keys())
        self.model = None

    def _load_config(self):
        with open(self.config_path, 'r') as file:
            return json.load(file)

    # TODO Construct the corresponding object according to model_name in model_list
    # PERF： Use the object pool to save the generated objects
    def change_model(self, model_name):
        pass

    def synthesize(self, text):
        self.model.synthesize(text)
