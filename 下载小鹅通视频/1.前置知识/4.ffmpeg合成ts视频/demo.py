import os

'''
    路径常识：
    \ 不能在Linux
    / 能够跨平台
    推荐使用 / 路径  
'''

print('\\') 
print('/')

# 遍历文件夹	
for dirpath,dirnames,files in os.walk('./素材'):

    # 获取有多少个文件
    print(files)

    # 将文件名排序好
    # list_data = [ int(data.replace('.ts','')) for data in files]
    # list_data.sort()
    # print(list_data)

    # 开始写入文件
    # for index in list_data:

    #     # 写入
    #     with open('file.txt','a+',encoding='utf-8') as f1:
            
    #         # 读取
    #         with open('file.txt','r',encoding='utf-8') as f2:
                
    #             # 获取当前绝对路径
    #             current_filename = os.getcwd().replace('\\','/')

    #             # 文件名
    #             filename = current_filename + '/素材/{}.ts'.format(index)

    #             # 如果该文件名不在里面，就写入
    #             if filename not in f2.read():
    #                 f1.write("file '{}'\n".format(filename))


# 设置UTF-8编码，让命令行支持中文编码
# cmd = 'ffmpeg.exe -f concat -safe 0 -i file.txt -c copy out.mp4"'
# os.system('CHCP 65001')
# os.system(cmd.replace('/', '\\'))

    


