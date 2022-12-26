import m3u8

'''
    m3u8 官方文档：https://github.com/globocom/m3u8
'''
with open(r'demo.m3u8','r',encoding='utf-8') as f:

    # 解析 m3u8
    dict_data = m3u8.parse(f.read())
    print(dict_data)

    # 获取键值
    # print(dict_data.keys())

    # 获取 m3u8 分片地址
    # for data in dict_data['segments']:
    #     print(data['uri'])
    #     start = data['uri'].split('?')[1].split('&')[0]
    #     end = data['uri'].split('?')[1].split('&')[1]
    #     print(start + end)


    # 获取 m3u8 加密地址
    # for data in dict_data['keys']:
    #     print(data['uri'])


