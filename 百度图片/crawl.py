#Python3.7 
#encoding = utf-8

import requests,asyncio,aiohttp,os,time
from urllib import parse
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor

tasks = []

headers = {
	'Referer':'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1585789312844_R&pv=&ic=&nc=1&z=&hd=&latest=&copyright=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&hs=2&sid=&word=miku',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
	#请填写你的Cookie
}

session = requests.session()#保存登录状态
session.headers = headers

def get_html(url):#访问网页

	s= time.time()
	html = session.get(url)

	if html.status_code == 200:#状态码
		
		parse_html(html.json())

	else:
		print('访问网页错误')

	print('\n\n'+'*'*40+'\n\n')
	print('程序耗时了：  {}  秒'.format(time.time()-s))#输出程序耗时
	print('\n\n'+'*'*40+'\n\n')


def parse_html(html):#解析网页

	data = html['data']

	for i in data:
		try:
			img = i['middleURL']
			print(img)
			tasks.append(download(img))
		except Exception as e:
			print(e)


async def download(img_url):

	filename = '下载好的图片'
	if not os.path.exists(filename):
		os.makedirs(filename)

	async with aiohttp.ClientSession(headers = headers) as session:
		async with session.get(img_url) as html:

			with open('./{}/{}.jpg'.format(filename,uuid4()),'wb') as f:
				f.write(await html.content.read())




if __name__ == '__main__':

	loop = asyncio.get_event_loop()#创建异步编程

	name = parse.quote('初音未来')#有需要的可以添加一个input，让用户输入

	with ThreadPoolExecutor(max_workers = 2) as t:
		for i in range(30,270,30):
			url = 'https://image.baidu.com/search/acjson?tn=resultjson_com'\
				'&ipn=rj&ct=201326592&is=&fp=result&queryWord={}'\
				'&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic='\
				'&hd=&latest=&copyright=&word={}&s=&se=&tab=&width='\
				'&height=&face=0&istype=2&qc=&nc=1&fr=&expermode='\
				'&force=&pn={}&rn=30'.format(name,name,i)
			t.submit(get_html,url)

	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()#程序关闭


