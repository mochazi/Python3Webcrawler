#Python3.7 
#encoding = utf-8

import time, math,random,hashlib
import requests

def get_html(name):

    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'


    ts = math.floor(time.time() * 1000)
    salt = ts + int(random.random() * 10)

    sign = hashlib.md5(("fanyideskweb" + name + str(salt) +"Nw(nmmbP%A-r6U3EUn]Aj").encode('utf-8')).hexdigest()
    bv = hashlib.md5(("5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36").encode('utf-8')).hexdigest()

    data = {
        'i': name,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': salt,
        'sign': sign,
        'ts': ts,
        'bv': bv,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CLICKBUTTION',
    }

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
        'Referer': 'http://fanyi.youdao.com/',
        #参考链接:http://fanyi.youdao.com/
        #请在此处填写你的 Cookie
    }


    html = requests.post(url, headers=headers, data=data)#有需要的可以改成session写法
    # print(html.json())
    print('正在执行有道翻译程序:')
    print('翻译的词:{}'.format(html.json()['translateResult'][0][0]['src']))
    print('翻译结果:{}'.format(html.json()['translateResult'][0][0]['tgt']))

if __name__ == "__main__":
    
    name = '靓仔'
    
    get_html(name)