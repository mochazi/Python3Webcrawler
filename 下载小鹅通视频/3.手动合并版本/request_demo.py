# python 3.7
import mitmproxy.http,json,os,shutil
from bs4 import BeautifulSoup
from mitmproxy import ctx
from pathlib import Path
from Crypto.Cipher import AES

'''
本次爬取的课程地址：https://appdgjqmn6j1714.h5.xiaoeknow.com/v1/course/video/v_61ceb0f8e4b05006f9c4214e?type=2&pro_id=p_61cc408ee4b0a91144afda88&is_redirect=1
'''

# 生成python修复文件
repair_file_py = r'''

"此文件用于保存密钥，请不要执行代码"

import os

from Crypto.Cipher import AES

# 获取当前路径
current_filename = os.getcwd().replace('\\','/') 

# 修复文件连接
new_repair_file_txt = current_filename + '/修复文件/' + 'repair_file.txt'

# 开始修复文件
def decrypt_file():

    global new_repair_file_txt

    before_content = None

    key = {}

    mode = AES.MODE_CBC

    # 获取 AES 解密对象
    cryptos = AES.new(key, mode)

    # 创建修复文件
    repair_filename = current_filename + '/修复文件'
    if not os.path.exists(repair_filename):
        os.makedirs(repair_filename)

    with open('not_finish_file.txt','r',encoding='utf-8') as f1:

        # 读取第一行
        line = f1.readline()

        # 逐行读取
        while line:
            # 获取 还没被解密的 ts 视频的路径
            not_finish_file_line = line.split(' ')[1].replace('\n','').replace("'",'').replace('\\','/')
            print(not_finish_file_line)

            with open(not_finish_file_line,'rb') as f:  # 解密之前
                before_content = f.read()

            # 写入 修复文件
            new_repair_filename = repair_filename + '/' + not_finish_file_line.split('/')[-1]
            print(new_repair_filename)
            with open(new_repair_filename,'wb') as f:  # 解密之后
                f.write(cryptos.decrypt(before_content))

            new_repair_file_txt = repair_filename + '/' + 'repair_file.txt'

            # 确保不重复
            with open(new_repair_file_txt,'a+',encoding='utf-8') as f3:  # 解密之后
                with open(new_repair_file_txt,'r',encoding='utf-8') as f4:
                    if str(new_repair_filename) not in f4.read():
                        f3.write("file '%s'\n" % str(new_repair_filename))

            line = f1.readline()

# 使用 not_finish_file.txt 合成视频
def compose_file():
    
    cmd = "ffmpeg.exe -f concat -safe 0 -i " + new_repair_file_txt  + " -c copy 1.修复视频.mp4"
    print(cmd)
    # 设置UTF-8编码
    os.system('CHCP 65001')
    os.system(cmd.replace('/','\\'))

decrypt_file()
compose_file()
'''

# 生成python合成文件
merge_file_py = r'''

"此文件用于合成视频"

import os

mp4_filename = '%s'

cmd = '%s'

# 如果合成的视频已经存在，先删除，再执行
if os.path.exists(mp4_filename):
    os.remove(mp4_filename)

    # 设置UTF-8编码
    os.system('CHCP 65001')
    os.system(cmd.replace('/','\\'))
    print('[警告]：文件路径 {}'.format(mp4_filename))
    print('[警告]：文件被覆盖了，由于该文件之前已存在过')
else:
    os.system('CHCP 65001')
    os.system(cmd.replace('/','\\'))
    print('[成功]：文件路径 {}'.format(mp4_filename))
    print('[成功]：合并完毕')
'''

cryptos = None    # AES解密
filename = None   # 下载视频路径
current_filename = os.getcwd().replace('\\','/') # 获取当前路径
result_filename = current_filename + '/合成的视频' # 获取 ffmepg合成视频后的路径
title = None # 标题
finish_file_flag = False # 标记是否存在 还没被解密的 ts 视频

class Counter:

    def __init__(self):
        self.Referer = 'https://appdgjqmn6j1714.h5.xiaoeknow.com'
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
        global cryptos,filename,result_filename,repair_file_py,title,finish_file_flag,merge_file_py

        # 注入 JavaScript 
        # 启动就能点击播放器
        if 'v_61ceb0f8e4b05006f9c4214e' in flow.request.url:
            
            # 确保匹配 HTML
            if 'text/html' in flow.response.headers.get('content-type'):
                
                try:
                    print('尝试执行JS控制播放器代码')
                    javascript_text = '''
                        // 视频播放速度
                        const playbackRate = 16;
                        
                        function start_video(){
                            
                            // 确保修改了视频播放速度
                            while(document.querySelector('video').playbackRate != playbackRate ){
                                
                                // 点击播放器
                                document.querySelector('div.iconfont.playButton.icon-icon_play').click();

                                // 设置视频重头播放
                                document.querySelector('video').currentTime = 0;

                                // 设置视频自动播放
                                document.querySelector('video').autoplay = true;

                                // 设置视频播放速度
                                document.querySelector('video').playbackRate = playbackRate;

                                // 设置视频静音
                                document.querySelector('video').muted = true

                                // 开始播放
                                document.querySelector('video').play();
                            } 
                        };

                        // 使用递归，异步等待，确保video标签会出现
                        function waitForElementToDisplay(selector, time) {

                            // video标签出现后，异步等待 1 秒
                            if(document.querySelector(selector)!=null) {
                                
                                console.log('获取成功video');
                                setTimeout(
                                    ()=>{
                                        start_video();
                                    },1000
                                ); 
                                
                                return;
                            }
                            else {
                                setTimeout( ()=> {
                                    waitForElementToDisplay(selector, time);
                                }, time);
                            }
                        }

                        // 每过 1 秒检查video标签 是否出现
                        waitForElementToDisplay('video',1000)                            
                    '''

                    # 获取 BeautifulSoup 对象
                    soup = BeautifulSoup(flow.response.text, 'lxml')

                    # 生成一个script节点
                    script_tag = soup.new_tag('script', type='text/javascript')

                    # 往script节点写入内容
                    script_tag.string = javascript_text

                    # 在当前 HTML 最后一个script节点  向后插入一个节点
                    soup.select('script')[-1].insert_after(script_tag)

                    # 修改当前 HTML 全部内容
                    flow.response.text = str(soup)
                except:
                    pass

        # 设置 AES解密模式
        mode = AES.MODE_CBC

        # 获取课程标题
        if 'get_goods_info_business' in flow.request.url:
            
            # 加载 JSON 对象
            json_data = json.loads(flow.response.text)

            # 获取当前视频标题
            title = json_data['data']['goods_name'].replace(' ','')

            # 如果没有文件夹，就创建文件夹
            filename = current_filename + '/下载成功的视频/{}'.format(title)
            if not os.path.exists(filename):
                os.makedirs(filename)
                
            if not os.path.exists(result_filename):
                os.makedirs(result_filename)
     
        # 匹配密钥
        if 'get_video_key.php' in flow.request.url:
            
            print('\n当前密钥：{}'.format(str(flow.response.content)))

            # 将密钥 写入 修复文件
            repair_file_py = repair_file_py.format(str(flow.response.content))
            cryptos = AES.new(flow.response.content, mode)

        # 解密 ts 文件
        if '.ts' in flow.request.url:
            
            print('-'*50)
            print('\n[当前解密对象]：{}\n'.format(cryptos))

            # 拼接当前视频保存路径
            m3u8_ts_filename = filename + '/start={}end={}.ts'.format(flow.request.query.get('start'),flow.request.query.get('end'))
            print('[当前视频]：{} [保存路径]：{}\n'.format(title,m3u8_ts_filename))
         
            # 用于合成
            m3u8_finish_file_filename = filename + '/finish_file.txt'

            # 确定最后一个分片
            start_data = flow.request.query.get('start')
            end_data = flow.request.query.get('end')
            result_data = start_data + end_data

            # 获取成功密钥，再解密
            if cryptos != None:
                
                
                # 保存 解密好的 ts
                with open(m3u8_ts_filename,'wb') as f:
                    f.write(cryptos.decrypt(flow.response.content))


                # 写入 解密成功 标记文件
                with open(m3u8_finish_file_filename,'a+',encoding='utf-8') as f1:
                    with open(m3u8_finish_file_filename,'r',encoding='utf-8') as f2:
                        
                        # 如果文件为空，同时又存在最后一片，将不写入
                        if result_data in m3u8_ts_filename and f2.read()=='':
                            pass

                        # 防止重复，确保路径没问题
                        elif m3u8_ts_filename not in f2.read():
                            f1.write("file '{}'\n".format(m3u8_ts_filename))

                ffmpeg_filename = filename + '/ffmpeg.exe'
                shutil.copyfile('ffmpeg.exe', ffmpeg_filename)

                # 优化版 生成python合成文件
                mp4_filename = result_filename + '/' + filename.split('/')[-1] + '.mp4'
                cmd = 'ffmpeg.exe -f concat -safe 0 -i "' + m3u8_finish_file_filename + '" -c copy "' + result_filename + '/' + filename.split('/')[-1] + '.mp4"'

                if mp4_filename and cmd:
                    
                    try:
                        merge_file_py = merge_file_py % (str(mp4_filename),str(cmd)) 
                    except:
                        pass

                    # 开始生成python合成文件
                    merge_file = filename + '/merge.py'
                    with open(merge_file,'w',encoding='utf-8') as f:
                        f.write(merge_file_py)

                # 生成修复python文件
                repair_file = filename + '/repair.py'
                with open(repair_file,'w',encoding='utf-8') as f:
                    f.write(repair_file_py)
            else:
                
                # 标记是否存在 还没被解密的 ts 视频
                finish_file_flag = True

                # 保存 还没被解密的 ts 视频
                with open(m3u8_ts_filename,'wb') as f:
                    f.write(flow.response.content)
                
                # 用于合成
                m3u8_not_finish_file__filename = filename + '/not_finish_file.txt'
                with open(m3u8_not_finish_file__filename,'a+',encoding='utf-8') as f:
                    f.write("file '{}'\n".format(m3u8_ts_filename))
                

addons = [
    Counter()
]