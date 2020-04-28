#Python3.7 
#encoding = utf-8

import requests,time,json
from bs4 import BeautifulSoup

headers ={
	'Referer':'https://www.kuaidaili.com/free/inha/1/',
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
	#参考链接:https://www.kuaidaili.com/free/inha/1/
}


def get_ip(url):#访问网站
	html = requests.get(url,headers = headers)
	if html.status_code==200:
		time.sleep(2)
		print('[INFO]正在爬取...')
		parse_html(html.text)
	else:
		print("[ERROR]错误",url)

def parse_html(html):#获取ip信息
	soup = BeautifulSoup(html,'lxml')
	ips = soup.select('.table tbody tr')
	for line in ips:
		ip = line.select_one('td').text
		port = line.select('td')[1].text
		print('[INFO]获取IP:{}  Port:{}'.format(ip,port))

		address = 'http://{}:{}'.format(ip,port)#构造ip访问
		proxies = {
			'http':address,
			'https':address,
		}
		verify_ip(proxies)

def verify_ip(proxies):#验证ip能否被用

	try:	
		html = requests.get('http://www.baidu.com',proxies = proxies,timeout = 3)#连接测试
		print('[SUCC]可用代理：{}'.format(proxies))
		write_json(proxies)
	except:
		print("[ERROR]代理超时不可用:{}".format(proxies))


def write_json(row):#写入文本

	with open('ip_pool.json','a+',encoding='utf-8') as f:
		json.dump(row,f)
		f.write('\n')


def read_json():#读取文件
	
	with open('ip_pool.json','r',encoding='utf-8') as f:
	 	
	 	for i in f.readlines():
	 		content = json.loads(i.strip())
	 		print(content)		


if __name__ == '__main__':

	for i in range(15,25):
		url = 'https://www.kuaidaili.com/free/inha/{}/'.format(i)
		get_ip(url)

	print('目前验证成功的IP')
	read_json()