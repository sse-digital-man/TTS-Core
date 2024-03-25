"""
版本管理、兼容推理及模型加载实现。
版本说明：
    1. 版本号与github的release版本号对应，使用哪个release版本训练的模型即对应其版本号
    2. 请在模型的config.json中显示声明版本号，添加一个字段"version" : "你的版本号"
特殊版本说明：
    1.1.1-fix： 1.1.1版本训练的模型，但是在推理时使用dev的日语修复
    1.1.1-dev： dev开发
    2.0：当前版本
"""
import torch
import localtts.commons as commons
from localtts.text import cleaned_text_to_sequence, get_bert
from localtts.text.cleaner import clean_text
import localtts.utils as utils

from localtts.models import SynthesizerTrn
from localtts.text.symbols import symbols

# 当前版本信息
latest_version = "2.0"

def get_net_g(model_path: str, version: str, device: str, hps):
        # 当前版本模型 net_g
    net_g = SynthesizerTrn(
        len(symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model,
    ).to(device)
    _ = net_g.eval()
    _ = utils.load_checkpoint(model_path, net_g, None, skip_optimizer=True)
    return net_g


def get_text(text, language_str, hps, device):
    # 在此处实现当前版本的get_text
    norm_text, phone, tone, word2ph = clean_text(text, language_str)
    phone, tone, language = cleaned_text_to_sequence(phone, tone, language_str)

    if hps.data.add_blank:
        phone = commons.intersperse(phone, 0)
        tone = commons.intersperse(tone, 0)
        language = commons.intersperse(language, 0)
        for i in range(len(word2ph)):
            word2ph[i] = word2ph[i] * 2
        word2ph[0] += 1
    bert_ori = get_bert(norm_text, word2ph, language_str, device)
    del word2ph
    assert bert_ori.shape[-1] == len(phone), phone

    if language_str == "ZH":
        bert = bert_ori
        ja_bert = torch.zeros(1024, len(phone))
        en_bert = torch.zeros(1024, len(phone))
    else:
        raise ValueError("language_str should be ZH")

    assert bert.shape[-1] == len(
        phone
    ), f"Bert seq len {bert.shape[-1]} != {len(phone)}"

    phone = torch.LongTensor(phone)
    tone = torch.LongTensor(tone)
    language = torch.LongTensor(language)
    return bert, ja_bert, en_bert, phone, tone, language


def infer(
    text,
    sdp_ratio,
    noise_scale,
    noise_scale_w,
    length_scale,
    sid,
    language,
    hps,
    net_g,
    device,
):

    version = hps.version
    # 在此处实现当前版本的推理
    bert, ja_bert, en_bert, phones, tones, lang_ids = get_text(
        text, language, hps, device
    )
    with torch.no_grad():
        x_tst = phones.to(device).unsqueeze(0)
        tones = tones.to(device).unsqueeze(0)
        lang_ids = lang_ids.to(device).unsqueeze(0)
        bert = bert.to(device).unsqueeze(0)
        ja_bert = ja_bert.to(device).unsqueeze(0)
        en_bert = en_bert.to(device).unsqueeze(0)
        x_tst_lengths = torch.LongTensor([phones.size(0)]).to(device)
        del phones
        speakers = torch.LongTensor([hps.data.spk2id[sid]]).to(device)
        audio = (
            net_g.infer(
                x_tst,
                x_tst_lengths,
                speakers,
                tones,
                lang_ids,
                bert,
                ja_bert,
                en_bert,
                sdp_ratio=sdp_ratio,
                noise_scale=noise_scale,
                noise_scale_w=noise_scale_w,
                length_scale=length_scale,
            )[0][0, 0]
            .data.cpu()
            .float()
            .numpy()
        )
        del x_tst, tones, lang_ids, bert, x_tst_lengths, speakers, ja_bert, en_bert
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return audio
