from selenium import webdriver

PROXY='http://127.0.0.1:8080'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=127.0.0.1:8080")
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 专业模式


browser = webdriver.Chrome(executable_path=r'chromedriver.exe',options=chrome_options)#r 代表的是强制禁止转义

'''
本次爬取的课程地址：https://appdgjqmn6j1714.h5.xiaoeknow.com/v1/course/video/v_61ceb0f8e4b05006f9c4214e
'''

url = 'https://appdgjqmn6j1714.h5.xiaoeknow.com/v1/course/video/v_61ceb0f8e4b05006f9c4214e'
browser.get(url)#访问网站

