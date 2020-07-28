#Python3.7 
#encoding = utf-8

from urllib import parse
import asyncio,aiohttp,os,time,requests
from bs4 import BeautifulSoup#爬虫解析库
from boook_db import Book,sess
from concurrent.futures import ThreadPoolExecutor

tasks = []

headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
	'Referer':'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=40&type=T',
	#参考链接 https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=0&type=T
}


def get_html(url):

	
	html = requests.get(url,headers = headers)

	if html.status_code==200:
		
		parse_html(html.text)
	else:
		print('错误')

def parse_html(html):

	soup =BeautifulSoup(html,'lxml')#选择解析器
	books = soup.select('li.subject-item')#选择文章

	for book in books:

		try:#防错机制

			title = book.select_one('.info h2 a').text.strip().replace(' ','').replace('\n','')#选择书名并去除空格
			info = book.select_one('.subject-item .info div.pub').text.strip().replace(' ','').replace('\n','')#选择作者
			star = book.select_one('.rating_nums').text.strip().replace(' ','').replace('\n','')#选择评分
			pl = book.select_one('.pl').text.strip().replace(' ','').replace('\n','')#选择评价
			introduce = book.select_one('.info p').text.strip().replace(' ','').replace('\n','')#选择书本简介
			img = book.select_one('.nbg img')['src']#获取图片url

			tasks.append(dowmload(title,img))#异步编程
			print(title,info,star,pl,img)
			print(introduce)
			print('-'*50)

		#插入数据库
			book_data = Book(
				title = title,
				info = info,
				star = star,
				pl = pl,
				introduce = introduce,
			)
			sess.add(book_data)
			sess.commit()
		except Exception as e:#发生任何错误返回
			print(e)
			sess.rollback()#事务回滚


async def dowmload(title,url):#保存封面图片

	if not os.path.exists('./豆瓣读书/doubanImg'):#检查有没有文件夹并创建
		os.makedirs('./豆瓣读书/doubanImg')

	async with aiohttp.ClientSession(headers = headers) as session:
		async with session.get(url) as html:		
			with open('./豆瓣读书/doubanImg/{}.jpg'.format(title),'wb')as f:
				f.write(await html.content.read())
	
if __name__ == '__main__':

	loop = asyncio.get_event_loop()
	with ThreadPoolExecutor(max_workers = 2) as t:
		for i in range(0,100,20):#翻页参数为20
			url = 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start={}&type=T'.format(i)
			t.submit(get_html,url)
	loop.run_until_complete(asyncio.wait(tasks))
	loop.close()#程序关闭


