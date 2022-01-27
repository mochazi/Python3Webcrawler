from selenium import webdriver

PROXY='http://127.0.0.1:8080'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=127.0.0.1:8080")
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 专业模式


browser = webdriver.Chrome(executable_path=r'chromedriver.exe',options=chrome_options)#r 代表的是强制禁止转义

'''
本次爬取的课程地址：https://m.lizhiweike.com/channel2/1192275
'''

url = 'https://m.lizhiweike.com/channel2/1192275'
browser.get(url)#访问网站

