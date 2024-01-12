import os
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import AudioDataStream
from datetime import datetime
from src.interface import ConfigurableModel, GenerativeModel
# from src.api_tts import ApiTTS


class MSApi(ConfigurableModel, GenerativeModel):
    def __init__(self, ApiTTS):
        self.api_config = ApiTTS.api_config
        self._initialize()

    def _initialize(self):
        ms_api_config = self.api_config['ms_tts']
        self.subscription_key = ms_api_config['ms_tts_api_secret']
        self.region = ms_api_config['ms_tts_region']
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key, region=self.region)

    def synthesize(self, text, output_dir=r'..\out'):
        speech_config = self.speech_config
        speech_config.speech_synthesis_voice_name = 'zh-CN-XiaohanNeural'

        file_name = f'{datetime.now().strftime("%Y%m%d%H%M%S")}.wav'
        speech_file_path = os.path.join(output_dir, file_name)

        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(
            text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            stream = AudioDataStream(speech_synthesis_result)
            stream.save_to_wav_file(speech_file_path)
            print(f"Speech synthesized for text: {text}")
            print(f"File saved at: {speech_file_path}")
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


if __name__ == '__main__':
    # Example usage
    api_tts = api_tts.ApiTTS()
    synthesizer = MSApi(api_tts)
    text_to_synthesize = "感谢来到直播间的粉丝们，我直播时间一般是10点到12点..."
    synthesizer.synthesize(text_to_synthesize)
