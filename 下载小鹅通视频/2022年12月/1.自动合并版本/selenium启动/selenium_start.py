# python 3.7.9
from selenium import webdriver

PROXY='http://127.0.0.1:8080'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=127.0.0.1:8080")
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 专业模式


browser = webdriver.Chrome(executable_path=r'chromedriver.exe',options=chrome_options)#r 代表的是强制禁止转义

'''
本次爬取的课程地址: https://app0mupqpv04212.h5.xiaoeknow.com/p/course/column/p_6226f0d0e4b02b82585244ba?type=3
'''

url = 'https://app0mupqpv04212.h5.xiaoeknow.com/p/course/column/p_6226f0d0e4b02b82585244ba?type=3'
browser.get(url)#访问网站

