import itchat
import time
import requests
import json
from aip import AipSpeech
import change_audio_type
from pydub import AudioSegment
import os
import io
import base64
import random
import hashlib
from urllib.parse import quote
import string
import wave

# 图灵的URL
TU_LING_URL = "http://openapi.tuling123.com/openapi/api/v2"
# 百度的个人设置
APP_ID = '15093907'
API_KEY = 'joRbhzi0QaMym66UPvMuaU6z'
SECRET_KEY = 'kZqnlYeK3GAPKFRuzSVLHUCwfTl6mc8C'
# 配置AipSpeech
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def login():
    # 是否自动登录
    itchat.auto_login(hotReload=True)
    # itchat.login()


def get_tuling_word(user_name, user_word):
    # 组装请求参数
    # 因为userId不能接收太长的值  所以截取1-10
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": user_word
            }
        },
        "userInfo": {
            "apiKey": "270bfecc32ef452ab6596354a21f41fb",
            "userId": user_name[1:10]
        }
    }

    # 请求  post
    response = requests.post(TU_LING_URL, json=data).text

    # 解析返回数据
    json_obj = json.loads(response)

    # 获取到返回的值
    response_word = json_obj["results"][0]["values"]["text"]

    # 返回回去
    return response_word


# @itchat.msg_register('Text')
def text_replay(msg):
    global is_continue
    # 当消息不是自己发出的时候
    # 获取到该用户的用户名称
    from_user_name = msg['FromUserName']
    user_word = msg['Text']
    user_name = msg["User"]["UserName"]

    print(is_continue)
    print(from_user_name)
    print(user_word)

    if not from_user_name == myUserName:
        # 发送一条消息给文件助手
        # itchat.send_msg(
        #     u"[%s]收到好友@%s 的信息： %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['CreateTime'])),
        #                                 msg["User"]['NickName'],
        #                                 msg["Text"]), "filehelper")
        # 给文件管理助手发一条消息
        # itchat.send_msg("test222...", "filehelper")

        # 只有当全局变量为True
        if is_continue == True:
            return get_tuling_word(from_user_name, user_word)

    elif user_name == "filehelper":
        if user_word == "stop":
            is_continue = False
        elif user_word == "continue":
            is_continue = True


@itchat.msg_register(['Text', 'Picture', 'Recording'])
def all_replay(recv_msg):
    """
    包括  ：  文字 + 图片 + 语音
    :param recv_msg:  入参
    :return:
    """
    print(recv_msg)
    # 下载音频
    recv_msg['Text'](recv_msg['FileName'])
    # 将音频从mp3转为wav
    song = AudioSegment.from_mp3(recv_msg['FileName'])

    fileName = time.strftime("%Y%m%d%H%M%S", time.localtime())
    song.export(fileName + ".wav", format="wav")
    # clear_voice(recv_msg['FileName'], fileName)

    # # 识别本地文件
    # result = client.asr(get_file_content(fileName+".wav"), 'wav', 16000, {
    #     'dev_pid': 1536,
    # })

    tx_voice_to_word(fileName + ".wav")


def clear_voice(mp3_name, wav_name):
    fp = open(mp3_name, "rb")
    data = fp.read()
    fp.close()

    # 主要部分
    aud = io.BytesIO(data)
    sound = AudioSegment.from_file(aud, format='mp3')
    raw_data = sound._data
    # 写入到文件，验证结果是否正确。
    l = len(raw_data)
    f = wave.open(wav_name + ".wav", 'wb')
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(44100)
    # f.setnframes(l)
    f.writeframes(raw_data)
    f.close()


# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def logout():
    itchat.logout()


def test():
    # 测试用腾讯的语音识别
    fp = get_file_content("20181208130330.wav")

    params = {
        "app_id": "2110432857",
        "format": 1,
        "callback_url": "https://ai.qq.com",
        "speech": str(base64.b64encode(fp), encoding="UTF-8"),
        "time_stamp": int(time.time()),
        "nonce_str": str(random.randint(1, 3000)),
        "sign": "",
    }
    print(params)
    # sorted(d.items(), key=lambda x: x[1], reverse=True)
    params_sorted = sorted(params.items(), key=lambda x: x[0], reverse=False)
    strs = ""
    for x, y in params_sorted:
        if not y == "":
            strs = strs + x + "=" + str(y) + "&"
        # print(x, y)
    strs = strs + "app_key=" + "wi35kVZfoA0s42bL"
    print(strs)
    m = hashlib.md5()
    m.update(strs.encode("UTF-8"))
    md_out = m.hexdigest()
    md_out = md_out.upper()
    print(md_out)
    params["sign"] = md_out

    print(params)

    tx_url = 'https://api.ai.qq.com/fcgi-bin/aai/aai_wxasrlong'
    response = requests.post(tx_url, params).text
    print(response)


def curlmd5(src):
    m = hashlib.md5(src.encode('UTF-8'))
    # 将得到的MD5值所有字符转换成大写
    return m.hexdigest().upper()


def get_params(fileName):
    fp = get_file_content(fileName)
    # 请求时间戳（秒级），用于防止请求重放（保证签名5分钟有效）  
    t = time.time()
    time_stamp = str(int(t))
    # 请求随机字符串，用于保证签名不可预测  
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    # 应用标志，这里修改成自己的id和key  
    app_id = '2110432857'
    app_key = 'wi35kVZfoA0s42bL'
    params = {
        'app_id': app_id,
        'format': 1,
        # "callback_url": "http://4c2216ef.ngrok.io/callback",
        "speech": str(base64.b64encode(fp), encoding="UTF-8"),
        'time_stamp': time_stamp,
        'nonce_str': nonce_str
    }
    sign_before = ''
    # 要对key排序再拼接  
    for key in sorted(params):
        # 键值拼接过程value部分需要URL编码，URL编码算法用大写字母，例如%E8。quote默认大写。  
        sign_before += '{}={}&'.format(key, quote(str(params[key]), safe=''))

    # 将应用密钥以app_key为键名，拼接到字符串sign_before末尾  
    sign_before += 'app_key={}'.format(app_key)
    # 对字符串sign_before进行MD5运算，得到接口请求签名  
    sign = curlmd5(sign_before)
    params['sign'] = sign
    return params


def tx_voice_to_word(fileName):
    tx_url = "https://api.ai.qq.com/fcgi-bin/aai/aai_asr"
    response = requests.post(tx_url, get_params(fileName)).text
    print(response)


if __name__ == '__main__':
    # tx_url = 'https://api.ai.qq.com/fcgi-bin/aai/aai_wxasrlong'

    is_continue = False
    # 登录
    login()

    # 获取自己的UserName
    myUserName = itchat.get_friends(update=True)[0]["UserName"]
    itchat.run()
