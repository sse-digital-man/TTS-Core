import base64
import json
import uuid
import requests
from datetime import datetime
import os

from src.interface import ConfigurableModel, GenerativeModel


class VolcanoAPI(ConfigurableModel, GenerativeModel):
    def __init__(self, ApiTTS):
        self.file_name = None  # 初始化文件名和路径
        self.speech_file_path = None
        self.api_config = ApiTTS.api_config  # 获取API配置信息
        self._initialize()

    def _initialize(self):
        volcano_api_config = self.api_config['volcano_tts']
        self.appid = volcano_api_config['volcano_tts_app_id']
        self.access_token = volcano_api_config['volcano_tts_access_token']
        self.cluster = "volcano_tts"
        self.voice_type = "BV700_V2_streaming"
        self.host = "openspeech.bytedance.com"
        self.api_url = f"https://{self.host}/api/v1/tts"
        self.header = {"Authorization": f"Bearer;{self.access_token}"}

    def synthesize(self, text, output_dir=r'..\out'):
        request_json = {
            "app": {
                "appid": self.appid,
                "token": "access_token",
                "cluster": self.cluster
            },
            "user": {
                "uid": "388808087185088"
            },
            "audio": {
                "voice_type": self.voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"
            }
        }

        try:
            self.file_name = f"{datetime.now().strftime('VOLCANO_TTS-%Y%m%d%H%M%S')}.mp3"
            self.speech_file_path = os.path.join(output_dir, self.file_name)
            print(self.speech_file_path)

            resp = requests.post(self.api_url, json.dumps(request_json), headers=self.header)
            if "data" in resp.json():
                data = resp.json()["data"]
                file_to_save = open(self.speech_file_path, "wb")
                file_to_save.write(base64.b64decode(data))
        except Exception as e:
            print(f"Error occurred: {e}")
        return self.speech_file_path

'''
if __name__ == '__main__':
    test_api_tts = api_tts.ApiTTS()
    volcano_tts = VolcanoAPI(test_api_tts)
    text_to_synthesize = "感谢来到直播间的粉丝们，我直播时间一般是10点到12点，大家记得准时来哦，我们每天都有福利哒。"
    volcano_tts.synthesize(text_to_synthesize)
'''