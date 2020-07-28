#Python3.7 
#encoding = utf-8

import requests,os,json,math,threading
from urllib import parse
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from db import SQLsession,Song

headers = {
	'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
	'referer':'https://y.qq.com/portal/singer_list.html',
	#参考链接 https://y.qq.com/portal/singer_list.html#page=1&index=1&
}

lock = threading.Lock()
session = SQLsession()

def myProcess():
	#把歌手按照首字母分为27类
	with ProcessPoolExecutor(max_workers = 2) as p:#创建27个进程
		for i in range(1,28):#28
			p.submit(get_singer_mid,i)
	
def get_singer_mid(index):
	#index =  1-----27
	#打开歌手列表页面，找出singerList,找出所有歌手的数目,除于80,构造后续页面获取page歌手
	#找出mid, 用于歌手详情页

	data = '{"comm":{"ct":24,"cv":0},"singerList":{"module":"Music.SingerListServer"'\
			',"method":"get_singer_list","param":{"area":-100,"sex":-100,"genre":-100,'\
			'"index":%s,"sin":0,"cur_page":1}}}'%(str(index))

	url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getUCGI0432880619182503'\
		'&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&out'\
		'Charset=utf-8&notice=0&platform=yqq.json&needNewCode=0'\
		'&data={}'.format(parse.quote(data))
	
	html = requests.get(url).json()
	total = html['singerList']['data']['total']#多少个歌手
	pages = int(math.floor(int(total)/80))
	thread_number = pages

	Thread = ThreadPoolExecutor(max_workers = thread_number)

	sin = 0
	#分页迭代每一个字母下的所有页面歌手
	for page in range(1,pages+2):
		data = '{"comm":{"ct":24,"cv":0},"singerList":{"module":"Music.SingerListServer",'\
				'"method":"get_singer_list","param":{"area":-100,"sex":-100,"genre":-100,"'\
				'index":%s,"sin":%d,"cur_page":%s}}}'%(str(index),sin,str(page))
		
		url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getUCGI0432880619182503'\
			'&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&out'\
			'Charset=utf-8&notice=0&platform=yqq.json&needNewCode=0'\
			'&data={}'.format(parse.quote(data))

		html = requests.get(url,headers = headers).json()
		
		sings = html['singerList']['data']['singerlist']

		for sing in sings:

			singer_name = sing['singer_name']
			mid = sing['singer_mid']

			Thread.submit(get_singer_data,mid = mid,
							singer_name = singer_name,)
		sin+=80



#获取歌手信息
def get_singer_data(mid,singer_name):
	#获取歌手mid,进入歌手详情页，也就是每一个歌手歌曲所在页面
	#找出歌手的歌曲信息页

	params = '{"comm":{"ct":24,"cv":0},"singerSongList":{"method":"GetSingerSongList",'\
			'"param":{"order":1,"singerMid":"%s","begin":0,"num":10},'\
			'"module":"musichall.song_list_server"}}'%str(mid)

	url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getSingerSong9513357793133783&'\
			'g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8'\
			'&notice=0&platform=yqq.json&needNewCode=0*&data={}'.format(parse.quote(params))

	html = requests.session()
	content = html.get(url,headers = headers).json()

	songs_num = content['singerSongList']['data']['totalNum']


	for a in range(0,songs_num,100):

		params = '{"comm":{"ct":24,"cv":0},"singerSongList":{"method":"GetSingerSongList",' \
					'"param":{"order":1,"singerMid":"%s","begin":%s,"num":%s},' \
					'"module":"musichall.song_list_server"}}' % (str(mid), int(a),int(songs_num))

		url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getSingerSong9513357793133783&' \
				'g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8' \
				'&notice=0&platform=yqq.json&needNewCode=0*&data={}'.format(parse.quote(params))

		html = requests.session()
		content = html.get(url, headers=headers).json()

		datas = content['singerSongList']['data']['songList']

		for d in datas:
			sing_name = d['songInfo']['title']
			songmid = d['songInfo']['mid']
			try:
				lock.acquire()#锁上
				session.add(Song(song_name = sing_name,
									song_singer = singer_name,
									song_mid = songmid))
				session.commit()
				lock.release()#解锁
				print('commit')
			except:
				session.rollback()
				print('rollbeak')

			print('歌手名字：{}\t歌曲名字：{}\t歌曲ID：{}'.format(singer_name,sing_name,mid))
			download(songmid,sing_name,singer_name)

def download(songmid,sing_name,singer_name):
	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
		'Referer':'https://y.qq.com/n/yqq/singer/000aHmbL2aPXWH.html',
	}


	data = '{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch",'\
			'"param":{"guid":"5746584900","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer",'\
			'"method":"CgiGetVkey","param":{"guid":"5746584900","songmid":["%s"],"songtype":[0],'\
			'"uin":"3262637034","loginflag":1,"platform":"20"}},"comm":{"uin":3262637034,"format":"json","ct":24,"cv":0}}'%str(songmid)


	url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?-=getplaysongvkey17693804549459324'\
		'&g_tk=5381&loginUin=3262637034&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8'\
		'&notice=0&platform=yqq.json&needNewCode=0&data={}'.format(parse.quote(data))

	html = requests.get(url,headers = headers)

	try:
		purl = html.json()['req_0']['data']['midurlinfo'][0]['purl']

		url = 'http://ws.stream.qqmusic.qq.com/{}'.format(purl)

		html = requests.get(url,headers = headers)
		html.encoding = 'utf-8'

		sing_file_name = '{} -- {}'.format(sing_name,singer_name)

		filename = './旧版QQ音乐(仍可用)/歌曲'

		if not os.path.exists(filename):
			os.makedirs(filename)
	
		with open('./旧版QQ音乐(仍可用)/歌曲/{}.m4a'.format(sing_file_name),'wb') as f:
			print('\n正在下载{}歌曲.....\n'.format(sing_file_name))
			f.write(html.content)
		
	except:
		print('查询权限失败，或没有查到对应的歌曲')



if __name__ == '__main__':
	myProcess()