#Python3.7 
#encoding = utf-8

import execjs,requests,time

class User():#获取用户密码加密

    def __init__(self,user_id,user_password):

        self.user_id = user_id
        self.user_password = user_password
        self.session = requests.session()
        self.session.headers = {
            'Referer':'https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=https%3A%2F%2Ftemp.163.com%2Fspecial%2F00804C4H%2F&cf=urs_style_2019.css%3Ft%3D20190527&MGID=1590637061742.5342&wdaId=&pkid=MODXOXd&product=163',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
            #请在此处输入你的Cookie
            #参考链接 https://www.163.com/
        }

    def get_pw(self):

        with open('pw.js','r',encoding='utf-8') as f:
            content = f.read()
      
        js_data = execjs.compile(content)#编译js
        pw = js_data.call('get_pw',self.user_password)#调用get_pw函数
        return pw

    def get_rtid(self):

        with open('rtid.js','r',encoding='utf-8') as f:
            content = f.read()
   
        js_data = execjs.compile(content)#编译js
        rtid = js_data.call('get_rtid')#调用get_rtid函数
        return rtid

    def get_tk(self,rtid):

        url = 'https://dl.reg.163.com/dl/gt'

        params = {
            'un':self.user_id,
            'pkid':'MODXOXd',
            'pd':'163',
            'channel':'0',
            'topURL':'https://www.163.com/',
            'rtid':rtid,
            'nocache':int(time.time()*1000),
        }

        html = self.session.get(url,params = params).json()
        return html['tk']

    def get_login(self,pw,rtid,tk):

        url = 'https://dl.reg.163.com/dl/l'


        data = {
            'channel':'0',
            'd':'10',
            'domains':"163.com",
            'l':'0',
            'pd':"163",
            'pkid':"MODXOXd",
            'pw':pw,
            'pwdKeyUp':'1',
            'rtid':rtid,
            't':int(time.time()*1000),
            'tk':tk,
            'topURL':"https://www.163.com/",
            'un':self.user_id,
        }

        html = self.session.post(url,json = data).json()#传递JSON
        return html


if __name__ == "__main__":
    
    user = User('请输入你的账号','请输入你的密码')
    pw = user.get_pw()#获取pw
    rtid = user.get_rtid()#获取rtid

    tk = user.get_tk(rtid)#获取tk

    login = user.get_login(pw,rtid,tk)
    print(login)

    
