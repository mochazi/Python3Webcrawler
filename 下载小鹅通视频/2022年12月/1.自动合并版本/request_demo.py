# python 3.7.9
import mitmproxy.http,json,os,m3u8,requests,base64
from mitmproxy import ctx
from pathlib import Path

'''
    解密参考文章: https://www.52pojie.cn/thread-1689801-1-1.html
    m3u8下载器GitHub地址: https://github.com/nilaoda/N_m3u8DL-CLI

    旧版课程: https://appjkyl58fl2930.h5.xiaoeknow.com/p/course/column/p_5c483e6305292_C1LfcA9T?type=3
    新版课程: https://app0mupqpv04212.h5.xiaoeknow.com/p/course/column/p_6226f0d0e4b02b82585244ba?type=3

    本次爬取的课程地址: https://app0mupqpv04212.h5.xiaoeknow.com/p/course/column/p_6226f0d0e4b02b82585244ba?type=3
'''

userid = None # 用户uid
filename = None   # 下载视频路径
current_filename = os.getcwd().replace('\\','/') # 获取当前路径
ts_url = None # ts文件下载地址
title = None # 标题
m3u8_obj = None # m3u8对象
m3u8_content = None # m3u8密钥

class Counter:

    def __init__(self):
        self.Referer = 'https://app0mupqpv04212.h5.xiaoeknow.com/p/course/column/p_6226f0d0e4b02b82585244ba?type=3'
        self.Cookie = '请填写你的Cooie'
        self.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
        self.headers = {
            'Referer':self.Referer,
            'Cookie':self.Cookie,
            'UserAgent':self.UserAgent
        }

    def request(self, flow: mitmproxy.http.HTTPFlow):

        # 所有请求插入协议头
        flow.request.headers['Referer'] = self.Referer
        flow.request.headers['Cookie'] = self.Cookie

    def response(self, flow: mitmproxy.http.HTTPFlow):
        
        # 导入全局变量
        global filename,title,userid,ts_url,m3u8_obj,m3u8_content


        # 获取课程标题
        if 'xe.course.business.core.info.get' in flow.request.url:
            
            # 加载 JSON 对象
            json_data = json.loads(flow.response.text)

            # 获取当前视频标题
            title = json_data['data']['resource_name'].replace(' ','')

            print(f'[当前标题] {title}')

            # 如果没有文件夹，就创建文件夹
            filename = current_filename + '/下载成功的视频/{}'.format(title)
            if not os.path.exists(filename):
                os.makedirs(filename)
            
            if not os.path.exists(current_filename+'/m3u8'):
                os.makedirs(current_filename+'/m3u8')

        if 'xe.course.business.composite_info.get' in flow.request.url:
            
            # 加载 JSON 对象
            json_data = json.loads(flow.response.text)

            # 获取userid
            userid = json_data['data']['user_info']['user_id'].replace(' ','')

            print(f'[用户ID] {userid}')

        # 匹配 m3u8
        if '.m3u8' in flow.request.url:
            
            if userid != None and filename != None:

                # 加载 m3u8 对象
                m3u8_obj = m3u8.loads(flow.response.text)

                # 添加用户userid
                m3u8_obj.keys[0].uri = m3u8_obj.keys[0].uri + f'&uid={userid}'

                # 获取m3u8密钥 URL
                m3u8_key_url = m3u8_obj.keys[0].uri

                # 获取解密参数（第一次解密）
                # print(m3u8_key_url)
                m3u8_content = requests.get(url=m3u8_key_url,headers=self.headers).content

                # 基于用户userid解密（第二次解密）
                rsp_data = m3u8_content
                userid_bytes = bytes(userid.encode(encoding='utf-8'))
                result_list = []
                for index in range(0, len(rsp_data)):
                    result_list.append(
                        rsp_data[index] ^ userid_bytes[index])
                m3u8_content = bytes(result_list)

                # 最终密钥
                m3u8_content = base64.b64encode(bytes(result_list)).decode()
                print(f'[m3u8密钥] {m3u8_content}')

            else:
                print(f'[当前标题] {title}')
                print(f'[用户ID] {userid}')
                print('[错误] 没有用户id || 没有标题')


        if '.ts' in flow.request.url:
            
            video_url = flow.request.url

            print('[开始下载视频]------------------')
            # print(f'video_url: {video_url}')

            # 获取ts文件下载域名（前缀）
            start_url = video_url.split('/')[:-1]

            # 获取ts文件下载域名（后缀）
            end_url = video_url.split('/')[-1].split('?')
            end_url[0] = '{ts_url}'

            # 后缀塞入前缀
            start_url.append('&'.join(end_url))
            
            # 生成 ts文件下载地址
            ts_url = '/'.join(start_url)

            # 添加 ts 链接地址
            for tmp_data in m3u8_obj.segments:

                # 插入
                if ts_url != None:
                    tmp_data.uri = ts_url.format(ts_url=tmp_data.uri)
                else:
                    print(f'[错误] ts_url is None')

            m3u8_filename = f'./m3u8/{title}.m3u8'
            m3u8_obj.dump(m3u8_filename)

            # 确保m3u8文件存在
            if os.path.exists(m3u8_filename):

                if os.path.exists(f'{filename}/{title}.mp4'):
                    print(f'[停止下载警告] 已经存在 {filename}/{title}.mp4')

                elif m3u8_content == None:
                    print(f'[m3u8密钥] {m3u8_content}')
                    print('[错误] 没有m3u8密钥')

                else:
                    cmd = f'N_m3u8DL-CLI_v3.0.2.exe "{m3u8_filename}" --workDir "{filename}" --saveName "{title}" --useKeyBase64 "{m3u8_content}"'
                    print(cmd)
                    os.system('CHCP 65001')
                    os.system(cmd)
                
            else:
                print('[错误]m3u8文件生成失败')


addons = [
    Counter()
]