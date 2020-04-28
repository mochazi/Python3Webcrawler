#Python3.7 
#encoding = utf-8

import requests,re,json
from bs4 import BeautifulSoup
from urllib import parse

KEYWORD = parse.quote('python')

base = 'https://item.jd.com'
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
	'Connection':'keep-alive',
	#参考链接:https://search.jd.com/Search?keyword=python&enc=utf-8&wq=python
}


def get_index(url):
	#一开始的请求页面

	session = requests.Session()
	session.headers = headers
	html = session.get(url)
	html.encoding = 'GBK'
	soup = BeautifulSoup(html.text,'lxml')
	items = soup.select('li.gl-item')


	for item in items:
		inner_url = item.select('li.gl-item .gl-i-wrap .p-img a')[0].get('href')
		print(inner_url)	
		inner_url = parse.urljoin(base,inner_url)#转成URL格式
	
		item_id = get_id(inner_url)

		#评论数
		comm_num = get_comm_num(inner_url)
		inner_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv6501&productId=11993134&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'

		#获取评论
		if comm_num>0:
			get_comm(inner_url,comm_num,item_id)
	



def get_comm(url,comm_num,item_id ):

	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
	}
	good_comments = ''  #存放结果
	#获取评论

	pages = comm_num//10
	if pages>99:
		pages = 99

	for page in range(0,pages):
		comment_url = 'https://sclub.jd.com/comment/productPageComments.action?'\
					'callback=fetchJSON_comment98vv4&productId={}&score=0'\
					'&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'.format(item_id,page)
	
		json_decoder = requests.get(comment_url,headers=headers).text
		try:
			if json_decoder:
				start = json_decoder.find('{"productAttr":null,')

				end = json_decoder.find(',"afterDays":0}]}')+len(',"afterDays":0}]}')
			
				content = json.loads(json_decoder[start:end])
				
				comments = content['comments']
				
				for c in comments:
					comm = c['content']
					good_comments+="{}|".format(comm)
					
				print(good_comments)
		except Exception as e:
			print(e)

	print(item_id,good_comments)

def get_shop_info(url):#获取商品信息
	shop_data = {}
	html = requests.get(url,headers = headers)
	soup = BeautifulSoup(html.text,'lxml')
	try:
		shop_name = soup.select('div.mt h3 a')
	except Exception as e:
		raise e

def get_index_lists(html):#获取索引列表
	html.encoding = 'utf8'
	soup = BeautifulSoup(html.text,'lxml')
	lis = soup.find_all('li',attrs = {"class":"gl-item"})
	for li in lis:
		number = li.find('div',attrs = {"class":"p-commit"}).strong
		print(number)

def get_comm_num(url):#获取评论数量
	
	item_id = get_id(url)
	comm_url = 'https://club.jd.com/comment/productCommentSummaries.action?'\
			'referenceIds={}&callback=jQuery3096445'.format(item_id)
	comment = requests.get(comm_url,headers = headers).text
	start = comment.find('{"CommentsCount":')#起始
	end = comment.find('"PoorRateStyle":0}]}')+len('"PoorRateStyle":0}]}')#结尾
	try:
		content = json.loads(comment[start:end])['CommentsCount']#取出json
	except:
		return 0
	comm_num = content[0]['CommentCount']
	return comm_num


def get_id(url):#匹配id
	id = re.compile('\d+')
	res = id.findall(url)
	return res[0]


if __name__ == '__main__':

	for i in range(1,30,2):
		url = 'https://search.jd.com/Search?'\
		'keyword={}&page={}'.format(KEYWORD,i)
		get_index(url)


