#Python3.7 
#encoding = utf-8

import requests,json,re,os,traceback,datetime,aiohttp,asyncio
from uuid import uuid4
from urllib import parse
from concurrent.futures import ThreadPoolExecutor

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Referer':'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&pv=&ic=0&nc=1&z=&hd=&latest=&copyright=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&sid=&word=%E5%88%9D%E9%9F%B3%E6%9C%AA%E6%9D%A5',
    #参考链接:https://image.baidu.com/
    #请在此处填写你的 Cookie
}

tasks = []

def get_html(url):

    try:
        html = requests.get(url,headers=headers)
        json_data = html.text.replace('\\','')#去除JSON数据多余的\
        json_data = json.loads(json_data)
        parse_json(json_data)

    except json.decoder.JSONDecodeError:
     
        #去除"fromPageTitle"键值的双引号异常
        fromPageTitle = r'"fromPageTitle":"(.*?)",'
        json_data = replace_data(fromPageTitle,json_data)

        #去除"fromPageTitle"键值的双引号异常
        fromPageTitle = r'"fromPageTitleEnc":"(.*?)",'
        json_data = replace_data(fromPageTitle,json_data)

        json_data = json.loads(json_data)
        write_error(url,flag='已经成功处理')
        parse_json(json_data)

    except Exception:
        write_error(url,flag='未能成功处理')

#解析JSON获取图片URL
def parse_json(json_data):
    list_data = json_data['data']
    for data in list_data[:-1]:
        image_name = data["fromPageTitleEnc"]
        for image_data in data["replaceUrl"]:
            image_url = image_data['ObjURL']
            tasks.append(download(image_url,image_name))
            
#下载图片
async def download(image_url,image_name):

    black_image = b'GIF89a\x04\x00\x08\x00\x91\x02\x00\xff\xff\xff\x00\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x02\x00,\x00\x00\x00\x00\x04\x00\x08\x00\x00\x02\x05\x94\x8f\xa9\x8b\x05\x00;'

    filename = './百度图片/下载好的图片'
    if not os.path.exists(filename):
        os.makedirs(filename)

    print("[INFO]{} 正在下载图片：{}".format(datetime.datetime.now(),image_name))

    async with aiohttp.ClientSession(headers = headers) as session:
        async with session.get(image_url) as html:
            
            uuid_id = uuid4()
            image_file_name = '{}/{}.jpg'.format(filename,uuid_id)
            
            #筛选掉异常的黑色图片、查询不到的图片
            if black_image not in await html.read() and b'<!DOCTYPE html>' not in await html.read():
            
                with open(image_file_name,'wb') as f:
                    f.write(await html.read())
        
                with open('./百度图片/图片映射表.json','a+',encoding='utf-8') as f:
                    json_data = json.dumps(dict(image_name = image_name,id=str(uuid_id)),ensure_ascii=False)
                    f.write(json_data + '\n')

#用正则删除双引号异常
def replace_data(re_compile,json_data):
    re_data = re.compile(re_compile)
    for i in re_data.findall(json_data):
        data = i.replace('"','').replace("\\'",'')
        json_data = json_data.replace(i,data)
    return json_data

#写入异常
def write_error(url,flag=None):

    with open('./百度图片/错误日志.txt','a+',encoding='utf-8') as f:
        f.write('JSON异常是否处理成功：{}\n'.format(flag))
        f.write('异常时间：{}\n'.format(datetime.datetime.now()))
        f.write('异常URL：{}\n'.format(url))
        f.write(traceback.format_exc() + '\n')

if __name__ == "__main__":

    loop = asyncio.get_event_loop()#创建异步编程
    name = parse.quote('初音未来')
    
    with ThreadPoolExecutor(max_workers = 2) as t:
        #翻页30
        for i in range(30,120,30):
            url = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592'\
                    '&is=&fp=result&queryWord={}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&hd=&latest='\
                    '&copyright=&word={}&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1'\
                    '&fr=&expermode=&force=&pn={}&rn=30'.format(name,name,i)
            t.submit(get_html,url)

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()#程序关闭