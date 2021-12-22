from typing import List
import requests,json,csv,os,re
from uuid import uuid4
from urllib import parse

'''主域名'''
DOMAIN_URL = 'https://book.douban.com'

'''
    协议头
    user-agent（必填）
    Referer（有就填，没有不填）
    Cookie（有账号登录就填，没有不填）
'''
HEADERS = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
    'Referer':'https://book.douban.com/',
    'Cookie':'填写你的Cookie'
}

'''结果去重集合'''
RESULT_SET_DATA = set()


class ReFind():

    def __init__(self,text):

        '''去除所有空格、换行'''
        self.text = re.sub('\s+','',text)

    
     
    '''
        【链式调用】传入指定正则表达式，获取第一个结果文本
        params:
            compile: str --> 指定正则表达式
            re_type：RegexFlag --> 匹配模式
        return: ReFind --> 实例化对象本身，方便进行链式调用
    '''
    def add_search(self,compile:str,re_type=re.I|re.S):

        self.text = re.compile(compile,re_type).search(self.text).group()
        
        return self
    
    '''
        传入指定正则表达式，返回所有查询结果
        params:
            compile: str --> 指定正则表达式
            re_type：RegexFlag --> 匹配模式
        return: List[str] --> 正则匹配成功的结果
    '''
    def find_all(self,compile:str,re_type=re.I|re.S) -> List[str]:

        return re.compile(compile,re_type).findall(self.text)



    '''
        打印当前文本
        return: str --> 当前对象的文本
    '''
    def print(self) -> str:
        print(self.text)



'''
    获取book的tag链接
    params:
        parse_number: int --> 爬取几个tag链接，默认全部

    return: List[str] --> 确定爬取几个tag链接
'''
def get_book_tag_url(split_number:int=None) -> List[str]:

    html = requests.get(url=DOMAIN_URL,headers=HEADERS)
 
    tag_url_list_data = [ 
            DOMAIN_URL+ parse.quote(tag_url)
            for tag_url in (
                    ReFind(html.text)
                    .add_search(r'<ulclass="hot-tags-col5s".*?<!--doubanadbegin-->')
                    .find_all(r'<li><ahref="(/tag/.*?)"class="tag">.*?</a></li>')
                )
        ]

    if split_number:
        tag_url_list_data = tag_url_list_data[:split_number]

    return tag_url_list_data


'''
    解析tag_url，进行翻页后，获取book的内容
    params:
        tag_url_list_data: List[str] --> book的tag链接
        parse_number: int --> 翻页参数，默认爬取3页
        write_type: bool --> 是否写入json文件
    return：List[dict] --> 爬取成功book的内容
'''
def parse_book_url_info(
    tag_url_list_data:List[str],
    parse_number:int=3,
    write_json_type:bool=True,
    write_csv_type:bool=True,
    write_image_type:bool=True
) -> List[dict]:

    book_info_list_data = []

    for tag_url in tag_url_list_data:

        # 开始翻页，每20算一页
        for parse in range(0,parse_number*20+1,20):
            
            # 翻页URL
            parse_url = f'{tag_url}?start={parse}'
            
            html = requests.get(url=parse_url,headers=HEADERS)

            # 选择书本
            books = (
                    ReFind(html.text)
                    .find_all(r'<liclass="subject-item".*?</li>')
                )

            for book in books:

                # 选择书本链接
                book_url = (
                    ReFind(book)
                    .find_all(r'<h2class=""><ahref="(.*?)".*?</a></h2>')
                )[0]

                # 选择书名
                title = (
                    ReFind(book)
                    .find_all(r'<h2class=""><ahref=.*?>(.*?)</a></h2>')
                )[0].strip().replace(' ','').replace('\n','')

                # 选择作者
                info = (
                    ReFind(book)
                    .find_all(r'<divclass="pub">(.*?)</div>')
                )[0].strip().replace(' ','').replace('\n','')

                # 选择评分
                star = (
                    ReFind(book)
                    .find_all(r'<spanclass="rating_nums">(.*?)</span>')
                )[0].strip().replace(' ','').replace('\n','')

                # 选择评价
                pl = (
                    ReFind(book)
                    .find_all(r'<spanclass="pl">(.*?)</span>')
                )[0].strip().replace(' ','').replace('\n','')

                # 选择书本简介
                introduce = (
                    ReFind(book)
                    .find_all(r'<p>(.*?)</p>')
                )[0].strip().replace(' ','').replace('\n','')


                # 获取图片URL
                image_url =(
                    ReFind(book)
                    .find_all(r'<img.*?src="(.*?)".*?>')
                )[0]

                book_info_result = dict(
                    书本链接=book_url,
                    书名=title,
                    作者=info,
                    评分=star,
                    评价=pl,
                    书本简介=introduce,
                    图片链接=image_url
                )

                '''生成结果hash值'''
                result_hash_data = hash(json.dumps(book_info_result,ensure_ascii=False))

                if result_hash_data not in RESULT_SET_DATA:

                    '''加入去重集合'''
                    RESULT_SET_DATA.add(result_hash_data)

                    if write_image_type:
                        write_image_book_info(
                            image_url=image_url,
                            image_name=title,
                            headers=HEADERS
                        )

                    # 检查是否写入json文件
                    if write_json_type:
                        write_json_book_info(book_info_result)

                    # 检查是否写入csv文件
                    if write_csv_type:
                        write_csv_book_info(
                            headers=[key for key,value in book_info_result.items()],
                            book_info=[value for key,value in book_info_result.items()]
                        )

                    print(book_info_result)

                    book_info_list_data.append(book_info_result)

    return book_info_list_data


'''
    保存图片，生成图片映射JSON文件
    params:
        image_url：str --> 图片链接
        image_name：str --> 图片名字
        headers: dict --> 协议头
'''
def write_image_book_info(image_url:str,image_name:str,headers:dict):

    '''确保图片文件名不重复'''
    uuid_id = uuid4()

    filename = './保存图片/图片'

    image_file_name = f'{filename}/{uuid_id}.jpg'

    image_map_file_name = f'./保存图片/image_map_data.json'

    '''如果不存在文件夹则创建'''
    if not os.path.exists(filename):
        os.makedirs(filename)

    html = requests.get(url=image_url,headers=headers)

    '''写入图片'''
    with open(image_file_name,'wb') as f:

        f.write(html.content)
    
    '''保存图片映射JSON文件'''
    with open(image_map_file_name,'a+',encoding='utf-8') as f:

        f.write(json.dumps(dict(image_name=image_name,uuid=str(uuid_id),image_url=image_url),ensure_ascii=False)+'\n')



'''
    将book的内容，写入json文件
    params:
        book_info: dict --> 爬取成功book的内容
'''
def write_json_book_info(book_info:dict):

    with open('book_info.json','a+',encoding='utf-8') as f:

        '''
            json.dumps() 将dict对象转成str对象，json就是str对象
            ensure_ascii=False 让json显示中文编码
        '''
        f.write(json.dumps(book_info,ensure_ascii=False)+'\n')



'''
    将book的内容，写入csv文件（带表头）
    params:
        headers：list --> CSV表头
        book_info: list --> 爬取成功book的内容
'''
def write_csv_book_info(headers:list,book_info:list):

    '''
        跨平台问题：
            写入csv 因为Windows有点BUG
            writerows()写入会出现空行
            所以加入newline=''
            没有出现这种情况则不需要
    '''

    '''
        检查是否创建了CSV文件
        没有则生成带有表头的CSV文件
    '''
    if not os.path.exists('book_info.csv'): 

        with open('book_info.csv','a+',encoding='utf-8',newline='') as f:

             f_csv = csv.writer(f)
             f_csv.writerow(headers)



    '''
        逐行开始写入CSV
    '''
    with open('book_info.csv','a+',encoding='utf-8',newline='') as f:

        f_csv = csv.writer(f)
        f_csv.writerow(book_info) #逐行插入

if __name__ == '__main__':

    book_tag_url = get_book_tag_url(1)
 
    book_url_info = parse_book_url_info(book_tag_url)