from Crypto.Cipher import AES

# 设置模式
mode = AES.MODE_CBC

key = b'V\x9dH\x1e:\xe6g\x10\x11l\xd7\xab\xd5\xd3\xc1\xbc'

'''
    生成解密对象
    key：密钥
    mode：解密模式
    iv：偏移量
'''
cryptos = AES.new(key=key,mode=mode,iv=b'0000000000000000')

with open('before.ts','rb') as f:   # 解密前
    with open('after.ts','wb') as f2:   # 解密后
        f2.write(cryptos.decrypt(f.read()))
