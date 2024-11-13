#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# cron "30 4 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('天翼云盘签到');

# #!/usr/bin/python3
# # -- coding: utf-8 --
# # @Time : 2023/4/4 9:23
# #作者：https://www.52pojie.cn/thread-1231190-1-1.html
# # -------------------------------
# # cron "30 4 * * *" script-path=xxx.py,tag=匹配cron用
# # const $ = new Env('天翼云盘签到');
#


import time
import re
import json
import base64
import hashlib
import urllib.parse, hmac
import rsa
import requests
import random
import os
import notify
response = requests.get("https://mkjt.jdmk.xyz/mkjt.txt")
response.encoding = 'utf-8'
txt = response.text
print(txt)

# 变量 ty_username（手机号）,ty_password（密码）
ty_username = os.getenv("ty_username").split('&')
ty_password = os.getenv("ty_password").split('&')

BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")

B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

s = requests.Session()

print(f"{' ' * 10}꧁༺ 天翼༒云盘 ༻꧂\n")
for i in range(len(ty_username)):
    
    print(f'\n----------- 🍺账号【{i + 1}/{len(ty_username)}】执行🍺 -----------\n')
    def int2char(a):
        return BI_RM[a]
    def b64tohex(a):
        d = ""
        e = 0
        c = 0
        for i in range(len(a)):
            if list(a)[i] != "=":
                v = B64MAP.index(list(a)[i])
                if 0 == e:
                    e = 1
                    d += int2char(v >> 2)
                    c = 3 & v
                elif 1 == e:
                    e = 2
                    d += int2char(c << 2 | v >> 4)
                    c = 15 & v
                elif 2 == e:
                    e = 3
                    d += int2char(c)
                    d += int2char(v >> 2)
                    c = 3 & v
                else:
                    e = 0
                    d += int2char(c << 2 | v >> 4)
                    d += int2char(15 & v)
        if e == 1:
            d += int2char(c << 2)
        return d


    def rsa_encode(j_rsakey, string):
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        result = b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
        return result


    def calculate_md5_sign(params):
        return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()


    def login(ty_username, ty_password):

        print(f"📱：{ty_username[0]}")
        # https://m.cloud.189.cn/login2014.jsp?redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html
        url = ""
        urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
        s = requests.Session()
        r = s.get(urlToken)
        pattern = r"https?://[^\s'\"]+"  # 匹配以http或https开头的url
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            url = match.group()  # 获取匹配的字符串
            # print(url)  # 打印url
        else:  # 如果没有找到匹配
            print("没有找到url")

        r = s.get(url)
        # print(r.text)
        pattern = r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\""  # 匹配id为j-tab-login-link的a标签，并捕获href引号内的内容
        match = re.search(pattern, r.text)  # 在文本中搜索匹配
        if match:  # 如果找到匹配
            href = match.group(1)  # 获取捕获的内容
            # print("href:" + href)  # 打印href链接
        else:  # 如果没有找到匹配
            print("没有找到href链接")

        r = s.get(href)
        captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
        paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        s.headers.update({"lt": lt})

        username = rsa_encode(j_rsakey, ty_username[i])
        password = rsa_encode(j_rsakey,ty_password[i])
        url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
            'Referer': 'https://open.e.189.cn/',
        }
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username}",
            "password": f"{{RSA}}{password}",
            "validateCode": "",
            "captchaToken": captchaToken,
            "returnUrl": returnUrl,
            "mailSuffix": "@189.cn",
            "paramId": paramId
        }
        r = s.post(url, data=data, headers=headers, timeout=5)
        if (r.json()['result'] == 0):
            #print(r.json()['msg'])
            msg = r.json()['msg']
            print(f"☁️登陆：{msg}")
        else:
            print(r.json()['msg'])
        redirect_url = r.json()['toUrl']
        r = s.get(redirect_url)
        return s


    def main():
        s = login(ty_username, ty_password)
        rand = str(round(time.time() * 1000))
        surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
        url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
        url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN'
        url3 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_2022_FLDFS_KJ&activityId=ACT_SIGNIN'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        response = s.get(surl, headers=headers)
        netdiskBonus = response.json()['netdiskBonus']
        if (response.json()['isSign'] == "false"):
            print(f"☁️签到：获得天翼云盘{netdiskBonus}M空间")
            res1 = f"☁️签到：获得天翼云盘{netdiskBonus}M空间"
        else:
            print(f"☁️签到：获得天翼云盘{netdiskBonus}M空间")
            res1 = f"☁️签到：获得天翼云盘{netdiskBonus}M空间"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
            "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
            "Host": "m.cloud.189.cn",
            "Accept-Encoding": "gzip, deflate",
        }
        response = s.get(url, headers=headers)
        #print(response.json())
        try:
            if "天翼云盘" in json.loads(response.text)["prizeName"]:
                description = response.json()['prizeName']
                print(f"☁️抽奖：获得{description}")
                res2 = f"☁️抽奖：获得{description}"
        except Exception as e:
            if "sessionKey" in json.loads(response.text)["errorMsg"]:
                print(f"☁️抽奖：已获取抽奖奖励")
                res2 = ""

        time.sleep(random.randint(10, 10))    
        response = s.get(url2, headers=headers)
        #print(response.json())
        try:
            if "天翼云盘" in json.loads(response.text)["prizeName"]:
                description = response.json()['prizeName']
                print(f"☁️抽奖：获得{description}")
                res3 = f"☁️抽奖：获得{description}"
        except Exception as e:
            if "sessionKey" in json.loads(response.text)["errorMsg"]:
                print(f"☁️抽奖：已获取抽奖奖励")
                res3 = ""

        time.sleep(random.randint(10, 10))    
        response = s.get(url3, headers=headers)
        #print(response.json())
        try:
            if "天翼云盘" in json.loads(response.text)["prizeName"]:
                description = response.json()['prizeName']
                print(f"☁️抽奖：获得{description}")
                res4 = f"☁️抽奖：获得{description}"
        except Exception as e:
            if "sessionKey" in json.loads(response.text)["errorMsg"]:
                print(f"☁️抽奖：已获取抽奖奖励")
                res4 = ""
        message = res1+res2+res3+res4
        
        message = res1
        #notify.send('title', 'message')


    def lambda_handler(event, context):  # aws default
        main()


    def main_handler(event, context):  # tencent default
        main()


    def handler(event, context):  # aliyun default
        main()


    if __name__ == "__main__":
        #time.sleep(random.randint(5, 30))
        main()
        print(f'\n----------- 🎊 执 行  结 束 🎊 -----------')