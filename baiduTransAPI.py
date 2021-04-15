#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8

import http.client
import hashlib
import time
import urllib
import random
import json

def splitStr(inStr):
    transStrArray = []
    outStrArray = []
    if len(inStr) < 800:
        transStrArray.append(inStr)
    else:
        temp_transArray = inStr.split(".")
        temp_transStr = ""
        i = 0
        for temp_transy in  temp_transArray:
            i+=1
            temp_transStr = temp_transStr + temp_transy+". "
            if len(temp_transStr) > 1000:
                transStrArray.append(temp_transStr)
                temp_transStr = ""
            elif i == len(temp_transArray):
                transStrArray.append(temp_transStr)
    return transStrArray

def translate(q):
    appid = '20200625000505843'  # 填写你的appid
    secretKey = 'UTH1H8QuyhEUWl7FcJM3'  # 填写你的密钥
    myurl = '/api/trans/vip/translate'
    fromLang = 'auto'  # 原文语种
    toLang = 'zh'  # 译文语种

    httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
    time.sleep(1.5)
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
    try:
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        #print(result)
        resultStr = result['trans_result'][0]['dst']
    except Exception as e:
        print(e)
        return q
    finally:
        if httpClient:
            httpClient.close()
    #print(resultStr)
    return resultStr

def transText(inputStr):
    temp_list = splitStr(inputStr)
    output = ""
    for temp in temp_list:
        time.sleep(1)
        output = output + translate(temp)
    return output



