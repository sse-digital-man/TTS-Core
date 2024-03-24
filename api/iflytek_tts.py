import hashlib
import hmac
import os
from time import mktime
from src.interface import ConfigurableModel, GenerativeModel
import websocket
import json
import _thread as thread
import os
import ssl
import base64
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from datetime import datetime
import wave

# 定义一些常量，用于标识音频帧的状态
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


# 定义 IflytekApi 类，继承自 ConfigurableModel 和 GenerativeModel
class IflytekApi(ConfigurableModel, GenerativeModel):
    def __init__(self, ApiTTS):
        self.file_name = None  # 初始化文件名和路径
        self.speech_file_path = None
        self.api_config = ApiTTS.api_config  # 获取API配置信息
        self._initialize()

    def _initialize(self):
        # 从API配置中获取讯飞语音合成相关的配置信息
        iflytek_api_config = self.api_config['xf_tts']
        self.xf_tts_app_id = iflytek_api_config['xf_tts_app_id']
        self.xf_tts_api_secret = iflytek_api_config['xf_tts_api_secret']
        self.xf_tts_api_key = iflytek_api_config['xf_tts_api_key']

    def synthesize(self, text, output_dir=r'..\out'):
        # 创建 WebSocket 参数对象
        ws_param = Ws_Param(
            APPID=self.xf_tts_app_id,
            APISecret=self.xf_tts_api_secret,
            APIKey=self.xf_tts_api_key,
            Text=text
        )
        # 生成语音文件名和路径
        self.file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}.pcm'
        self.speech_file_path = os.path.join(output_dir, self.file_name)

        # 定义接收 WebSocket 消息的回调函数
        def on_message(ws, message):
            try:
                message = json.loads(message)
                code = message["code"]
                sid = message["sid"]
                audio = message["data"]["audio"]
                audio = base64.b64decode(audio)
                status = message["data"]["status"]
                # print(message)
                # 根据状态处理音频数据
                if status == 2:
                    print("ws is closed")
                    ws.close()
                if code != 0:
                    errMsg = message["message"]
                    print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
                else:
                    with open(self.speech_file_path, 'ab') as f:
                        f.write(audio)

            except Exception as e:
                print("receive msg,but parse exception:", e)

        # 定义 WebSocket 错误回调函数
        def on_error(ws, error):
            print("### error:", error)

        # 定义 WebSocket 关闭回调函数
        def on_close(ws):
            print("### closed ###")

        # 创建 WebSocket 客户端对象并运行
        ws_client = WebSocketClient(
            ws_param, on_message, on_error, on_close)
        ws_client.run()
        # 将生成的 PCM 文件转换为 WAV 文件
        pcm2wav(self.speech_file_path, replace_suffix(self.speech_file_path, '.pcm', '.wav'))


def replace_suffix(original_string, old_suffix, new_suffix):
    parts = original_string.rsplit(old_suffix, 1)
    if len(parts) == 2:
        return parts[0] + new_suffix
    else:
        return original_string


# 定义将 PCM 文件转换为 WAV 文件的函数
def pcm2wav(pcm_file, wav_file, channels=1, bits=16, sample_rate=16000):
    # 打开 PCM 文件
    pcmfile = open(pcm_file, 'rb')

    # 读取 PCM 文件的参数
    frames = os.path.getsize(pcm_file)

    # 创建一个 WAV 文件
    wavfile = wave.open(wav_file, 'wb')

    # 设置 WAV 文件的参数
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(bits // 8)
    wavfile.setframerate(sample_rate)
    wavfile.setnframes(frames)

    # 写入 WAV 文件
    wavfile.writeframes(pcmfile.read(frames))

    # 关闭文件
    pcmfile.close()
    wavfile.close()


# 定义 WebSocket 参数类
class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {
            "aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(
            base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        # 使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        # self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'

        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(
            signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 定义 WebSocket 客户端类
class WebSocketClient:
    def __init__(self, ws_param, on_message_callback, on_error_callback, on_close_callback):
        self.ws_param = ws_param
        self.ws_url = self.ws_param.create_url()
        self.on_message_callback = on_message_callback
        self.on_error_callback = on_error_callback
        self.on_close_callback = on_close_callback

    # 运行 WebSocket 客户端
    def run(self):
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message_callback,
            on_error=self.on_error_callback,
            on_close=self.on_close_callback
        )
        ws.on_open = self.on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    # WebSocket 连接打开时的回调函数
    def on_open(self, ws):
        def run(*args):
            data = {
                "common": self.ws_param.CommonArgs,
                "business": self.ws_param.BusinessArgs,
                "data": self.ws_param.Data,
            }
            data = json.dumps(data)
            print("------>开始发送文本数据")
            ws.send(data)
            if os.path.exists('./out/iflytek_demo.pcm'):
                os.remove('./out/iflytek_demo.pcm')

        thread.start_new_thread(run, ())
