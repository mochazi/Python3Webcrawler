#Python3.7 
#encoding = utf-8

import requests, re
from lxml import etree
from urllib import parse
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from db import sess, House

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
    'referer':'https://fs.zu.fang.com/house-a0617/i32/',
    #参考链接 https://zu.fang.com/house-a01
    #请填写你的Cookie
}

session = requests.session()  #保持会话状态，不必重复请求
session.headers = headers


#获取str中的数字
def get_number(text):
    number = re.compile('\d+')
    return number.findall(text)[0]


#获取页面的page数目
def get_pages(html):
    soup = etree.HTML(html.text)
    pages = soup.xpath("//div[@class='fanye']/span/text()")
    number = get_number(pages[0])
    if number:
        return int(number)
    return None


def get_house_data(url, *args):
    headers = {
        'Connection': 'keep-alive',  #常链接
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
        'Referer': 'https://fs.zu.fang.com/house-a0617/i33/',
        #参考链接 https://zu.fang.com/house-a01
        #请填写你的Cookie
    }

    loca_url = re.compile("<td>(.*?)</td>")  #获取跳转链接
    xiangqing_url = re.compile('location.href="(.*?)"')

    session = requests.session()  #长连接   保持会话
    session.headers = headers

    url = 'http://search.fang.com/captcha-854085290c4833ba19/redirect?h=' + url

    html = session.get(url)

    one_url = xiangqing_url.findall(html.text)[-1]  #第一次跳转
    html = session.get(one_url)

    two_url = xiangqing_url.findall(html.text)[-1]  #第二次跳转
    html = session.get(two_url)

    soup = etree.HTML(html.text)
    xiangqing = soup.xpath('//div[@class="fyms_con floatl gray3"]/text()')
    xiangqing = '|'.join(xiangqing)
    print('block:{}\t标题:{}\t租金:{}详情:{}'.format(args[0], args[2], args[1],xiangqing))

    s = sess()
    try:
        house = House(block=args[0],
                      title=args[2],
                      rent=args[1],
                      data=xiangqing)

        s.add(house)
        s.commit()
        print('commit')
    except Exception as e:
        print('rollback', e)
        s.rollback()


#获取页面信息
def get_data_next(url):
    html = session.get(url)
    soup = etree.HTML(html.text)
    dls = soup.xpath("//div[@class='houseList']/dl")
    block = soup.xpath("//span[@class='selestfinds']/a/text()")
    rfss = soup.xpath("//input[@id='baidid']/@value")[0]
    for dl in dls:
        try:
            title = dl.xpath('dd/p/a/text()')[0]
            rent = dl.xpath("dd/div/p/span[@class='price']/text()")[0]
            href = parse.urljoin('https://zu.fang.com',
                                 dl.xpath('dd/p/a/@href')[0])  #拼接链
            get_house_data(href, block, rent, title)
        except IndexError as e:
            print('dl error', e)


#获取页面
def get_data(html):
    pages = get_pages(html)
    if not pages:
        pages = 1
    urls = [
        'https://zu.fang.com/house-a01/i3%d/' % i for i in range(1, pages + 1)
    ]

    with ProcessPoolExecutor(max_workers=2) as t:

        for url in urls:
            t.submit(get_data_next, url)


#进入首页
def get_index(url):
    html = session.get(url, headers=headers)
    if html.status_code == 200:
        get_data(html)
    else:
        print('请求页面{}出错'.format(url))


def main():
    urls = ['https://zu.fang.com/house-a0{}/'.format(i) for i in range(1, 17)]
    with ProcessPoolExecutor(max_workers=2) as p:
        for url in urls:
            p.submit(get_index, url)


if __name__ == '__main__':
    main()
    session.close()
