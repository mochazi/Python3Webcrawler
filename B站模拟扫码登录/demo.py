# Python3.7
# encoding=utf-8

import requests,time,json,os
import qrcode   # 生成二维码
import cv2 as cv # 读取二维码图片
from concurrent.futures import ThreadPoolExecutor

'''
    需要安装第三方库：
    pip install qrcode==7.3
    pip install opencv-python==4.5.3.56
'''

headers = {
    'referer':'https://passport.bilibili.com/login',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36x-requested-with: XMLHttpRequest'
}

class Login():

    def __init__(self):
        self.oauthKey = ''
        self.qrcodeURL = ''
        self.session = requests.Session()
        self.session.headers = headers

    # 获取二维码图片地址
    def getQRcode(self):
        
        html = self.session.get('https://passport.bilibili.com/qrcode/getLoginUrl')
        if html.json()['status'] == True:
            self.oauthKey = html.json()['data']['oauthKey']
            self.qrcodeURL = html.json()['data']['url']
            return True
        return False

    # 利用 opencv 读取图片
    @staticmethod
    def showQRCode(url):
        qrCode = qrcode.QRCode()
        qrCode.add_data(url)
        qrCode = qrCode.make_image()
        qrCode.save('qrCode.png')
        img = cv.imread('qrCode.png',1)
        cv.imshow('Login',img)
        cv.waitKey()

    # 开始登录
    def login(self):

        # 创建另一个线程，展示二维码图片
        thread_pool = ThreadPoolExecutor(max_workers=2)
        if self.getQRcode():
            thread_pool.submit(self.showQRCode,self.qrcodeURL)
        
        # 不断检查二维码是否确认登录
        while True:
            time.sleep(1)
            data = {
                'oauthKey':self.oauthKey,
                'gourl':'https://www.bilibili.com/'
            }

            html = self.session.post('https://passport.bilibili.com/qrcode/getLoginInfo',headers=headers,data=data)

            if html.json()['data'] == -4: # 还没扫码
                pass
            elif html.json()['data'] == -2: # 二维码过期，需要重新生成
                self.getQRcode()
                thread_pool.submit(self.showQRCode,self.qrcodeURL)
            elif html.json()['data'] == -5: # 已经扫码，等待确认
                pass
            else:
                break
        
        # 解析 cookie
        cookieRaw = html.json()['data']['url'].split('?')[1].split('&')
        cookies = {}
        for cookie in cookieRaw:
            key,value = cookie.split('=')
            if key != 'gourl' and key != 'Expires':
                cookies[key] = value
        print(json.dumps(cookies))
        os._exit(0)

if __name__ == '__main__':
    login = Login()
    login.login()
