from bs4 import BeautifulSoup

'''
    BeautifulSoup修改文档树-官方文档：https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#id45
'''

with open('before.html','r',encoding='utf-8') as f:
    
    soup = BeautifulSoup(f.read(), 'lxml')


    # 创建 HTML 的 script 节点
    script_tag = soup.new_tag('script', type='text/javascript')
    script_tag.string = "alert('靓仔')"
    # print(script_tag)

    # 获取最后一个 script 节点，向后插入
    print('[插入前] 最后一个节点：{}'.format(soup.select('script')[-1]))
    soup.select('script')[-1].insert_after(script_tag)
    print('[插入后] 最后一个节点：{}'.format(soup.select('script')[-1]))

    with open('after.html','w',encoding='utf-8') as f:
        f.write(soup.prettify()) # 格式化写入
    
    # print(soup)