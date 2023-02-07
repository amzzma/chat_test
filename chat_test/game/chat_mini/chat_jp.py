# -*- coding:utf-8 -*-

import os
import time
import utils
import commons
import hashlib
from pyChatGPT import ChatGPT
from pydub import AudioSegment
from winsound import PlaySound
from text import text_to_sequence
from models import SynthesizerTrn
from scipy.io.wavfile import write
from torch import no_grad, LongTensor


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def get_cleaned(text, symbols: list):
    list1 = list(text)
    n = 0
    for i in symbols:
        n += list1.count(i)
    # print(n, len(text))
    if len(text) == 0:
        return False
    elif n / len(text) >= 0.9:
        return True
    else:
        return False


def get_content(path: str):
    if os.path.exists(f'{path}'):
        with open(f'{path}', mode='r', encoding='utf-8') as f:
            ct = ''
            for i in f:
                ct += ''.join(i)
        return ct
    else:
        time.sleep(2)
        get_content(path)


def write_content(path: str, content: str):
    if os.path.exists(rf'{path}'):
        with open(f'{path}', mode='w', encoding='utf-8') as f:
            f.write(f'{content}')
    else:
        time.sleep(2)
        get_content(path)


def trans_audio_type(filepath, input_audio_type, output_audio_type):
    song = AudioSegment.from_file(filepath, input_audio_type)
    song.export(f'../audio/output.{output_audio_type}', format=f'{output_audio_type}')


def check_md5(file_path):
    obj = hashlib.md5()
    with open(file_path, encoding='utf-8') as f:
        for i in f:
            obj.update(i.encode('utf-8'))
    result = obj.hexdigest()
    return result


def generate_sound(input_string):
    model = input('Path of a VITS model: ')
    config = input('Path of a config file: ')

    hps_ms = utils.get_hparams_from_file(config)
    n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    # speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
    n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    symbols = hps_ms.symbols

    net_g_ms = SynthesizerTrn(
        n_symbols,
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=n_speakers,
        **hps_ms.model)
    _ = net_g_ms.eval()

    utils.load_checkpoint(model, net_g_ms)

    assert n_symbols != 0, '请确认config的symbols'
    text = input_string
    length_scale = 1  # 语速
    noise_scale = 0.667  # 噪声参数
    noise_scale_w = 0.8  # 噪声参数偏差
    cleaned = get_cleaned(text, symbols)
    stn_tst = get_text(text, hps_ms, cleaned=cleaned)
    speaker_id = speakerID

    # out_path = input('Path to save: ')
    out_path = '../audio/output.wav'

    with no_grad():
        x_tst = stn_tst.unsqueeze(0)
        x_tst_lengths = LongTensor([stn_tst.size(0)])
        sid = LongTensor([speaker_id])
        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                               noise_scale_w=noise_scale_w, length_scale=length_scale)[0][
            0, 0].data.cpu().float().numpy()
    try:
        write(out_path, hps_ms.data.sampling_rate, audio)
        print('Successfully saved!')
    except:
        print('ERROR')


if __name__ == "__main__":
    choose = input('使用chatGPT输入C，使用本地文本语音合成按W（请确认修改好了script）：')
    assert choose in ['c', 'C', 'w', 'W'], '输入有误'
    speakerID = eval(input('输入角色id：'))

    if choose == ('c' or 'C'):
        session_token = input("Copy your token of ChatGPT:")
        api = ChatGPT(session_token)
        st = get_content('..audio/start_time.txt')
        print('You can start your communication')
        if 'T' in st:  # 判断前端是否准备好
            while True:
                resp = api.send_message(get_content('../audio/words.txt'))
                answer = resp["message"].replace('\n', '')  # 获得回复
                generate_sound(answer)  # 合成语音
                trans_audio_type('../audio/output.wav', 'wav', 'ogg')  # 转换音频格式为ren'py可读
                write_content('../audio/output.txt', answer)  # 写入回复
                write_content('..audio/success_time_B.txt', 'T')  # 将完成的信号写入对应文档
                words_md5 = check_md5('../audio/words.txt')

                while True:
                    if words_md5 != check_md5('../audio/words.txt'):  # 判断保存words的文档内容是否改变
                        break
                    else:
                        time.sleep(3)
                        continue

    elif choose == ('w' or 'W'):
        st = get_content('..audio/start_time.txt')
        print('You can start your communication')
        if 'T' in st:
            generate_sound(get_content('../audio/words.txt'))
            trans_audio_type('../audio/output.wav', 'wav', 'ogg')
            write_content('../audio/success_time_B.txt', 'T')
            md5_zhi = check_md5('../audio/words.txt')
            while True:
                if md5_zhi != check_md5('../audio/words.txt'):
                    break
                else:
                    time.sleep(1)
                    continue

    # PlaySound(r'..\audio\output.wav', flags=1)  # 播放音频
