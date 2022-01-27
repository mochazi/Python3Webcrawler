# python 3.7
import mitmproxy.http,json,os,requests
from mitmproxy import ctx
from pathlib import Path

'''
本次爬取的课程地址：https://m.lizhiweike.com/channel2/1192275
'''

cookie = '请填写你的Cooie'
filename = None   # 下载视频路径
current_filename = os.getcwd().replace('\\','/') # 获取当前路径
title = None # 标题

class Counter:

    def __init__(self):
        self.Referer = 'https://m.lizhiweike.com/channel2/1192275'
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
        self.headers = {
            'Referer':self.Referer,
            'Host':'m.lizhiweike.com',
            'User-Agent':self.UserAgent
        }

    def request(self, flow: mitmproxy.http.HTTPFlow):

        # 所有请求插入协议头
        flow.request.headers['Referer'] = self.Referer
   
    def response(self, flow: mitmproxy.http.HTTPFlow):
        
        # 导入全局变量
        global filename,title,current_filename,cookie

        if 'lecture' in flow.request.url and 'info' in flow.request.url:

            # 加载 JSON 对象
            json_data = json.loads(flow.response.text)

            try:
                # 获取当前视频标题
                title = json_data['data']['share_info']['share_title'].replace(' ','')
            except:
                pass

        # 获取课程标题
        if 'qcvideo' in flow.request.url:
            
            # 加载 JSON 对象
            json_data = json.loads(flow.response.text)

            # 获取视频URL
            video_url = json_data['data']['play_list'][0]['url']

            print(f'【信息】当前视频标题：{title}，视频mp4链接：{video_url}')
            
            # 如果没有文件夹，就创建文件夹
            filename = current_filename + '/下载成功的视频/'
            if not os.path.exists(filename):
                os.makedirs(filename)
            
            # 生产mp4存放路径
            mp4_filename_path = f'{filename}{title}.mp4'
            
            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
                'referer':'https://m.lizhiweike.com/channel2/1192275',
                'Cookie':cookie
            }

            # 下载视频
            html = requests.get(url=video_url,headers=headers)
            with open(mp4_filename_path,'wb') as f:
                f.write(html.content)

addons = [
    Counter()
]