# -*- coding: utf-8 -*-
# QQ 本地账号数据分析
# by: @Wormwaker
# 感谢：https://github.com/sun589/QQkey_Tool

from urlextract import URLExtract
import html
import requests
import psutil
from threading import Thread
import traceback
from datetime import datetime
import time
import random
import os
import sys
import re
import json

VERSION = "v1.0"
SPIDER_MORE = False	# 是否获取更多信息 (!!PRIVACY WARNING!!)
SAFEMODE = True		# 是否开启安全模式，启用后将隐去部分信息

def procprint(*args, **kwargs):
    print("\033[37m[*] " + str(*args) + "\033[0m", file=sys.stderr, **kwargs)
def errprint(*args, **kwargs):
    print("\033[91m[-] " + str(*args) + "\033[0m", file=sys.stderr, **kwargs)
def warnprint(*args, **kwargs):
    print("\033[33m[!] " + str(*args) + "\033[0m", file=sys.stderr, **kwargs)
def sucprint(*args, **kwargs):
    print("\033[92m[+] " + str(*args) + "\033[0m", file=sys.stderr, **kwargs)

def parse_timestamp(ts):
    dt_object = datetime.fromtimestamp(ts)
    
    formatted_date = dt_object.strftime('%Y/%m/%d %H:%M:%S')
    
    day_of_week = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][dt_object.weekday()]
    
    # 返回最终结果字符串
    return f"{formatted_date} {day_of_week}"

def exist_process(name):
    name_lower = name.lower()
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == name_lower:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # 如果进程在访问时终止或权限不足等异常情况发生，跳过该进程
            continue
    
    # 如果没有找到匹配的进程，则返回False
    return False

def spider_phone_by_qq(qq : str):
    # time.sleep(1.0)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"}
    try:
        resp = requests.get("https://api.xywlapi.cc/qqapi", params={"qq": qq}, headers=headers, timeout=5)
        # _type = resp.headers.get('Content-Type', '')
        # if 'application/json' in _type:
        data = resp.json()
        if data.get("status") == 200:
            phone = data.get("phone", "-/-")
            phonediqu = data.get("phonediqu", "-/-")
            return f"\033[32m{phone}\t\t\033[36m{phonediqu}", phone
        else:
            return "\033[32m-/-\t\t\033[36m-/-", ""
        # else:
        #     return "\033[32mTYPE IS " + str(_type)
    except Exception as e:
        return "\033[32m" + str(e), ""
    
def spider_microblog_by_phone(phone : str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"}
    try:
        resp = requests.get("https://api.xywlapi.cc/wbphone", params={"phone": phone}, headers=headers, timeout=5)
        # _type = resp.headers.get('Content-Type', '')
        # if 'application/json' in _type:
        data = resp.json()
        if data.get("status") == 200:
            id = data.get("id", "-/-")
            return f"\033[33m{id}"
        else:
            return "\033[33m-/-"
        # else:
        #     return "\033[32mTYPE IS " + str(_type)
    except Exception as e:
        return "\033[33m" + str(e)
    
def nick_name(name):
    if not name:
        return ""
    if ' ' in name:
        name = " ".join(name.split(' ')[1:])
    return str(name[0] + "*" * (len(name) - 1))

def print_friend_item(item, j, spiderMore = False):
    try:
        if spiderMore:
            phoneinfo, phone = spider_phone_by_qq(str(item["uin"]))
            wbinfo = spider_microblog_by_phone(phone)
        else:
            phoneinfo = "\033[32m(off)\t\t\033[36m(off)"
            wbinfo = "\033[33m(off)"

        if SAFEMODE:
            _name = nick_name(str(html.unescape(item["name"])))
        else:
            _name = str(html.unescape(item["name"]))

        print("\033[37m" + str(j) 
            + "\t\033[95m" + _name
            + "\t\t\t\033[91m" + str(item["uin"]) 
            + "\t" + phoneinfo + "\t" + wbinfo
            + "\033[90m\n\t\t\t\t\t\t" + item["img"]
              + "\033[0m", end='')
        print()
    except Exception as e:
        print("ERROR: " + str(e))
        traceback.print_exc()
    
login_data = [
    {
        "proxy_url": "https://qzs.qq.com/qzone/v6/portal/proxy.html",
        "daid": "5",
        "hide_title_bar": "1",
        "low_login": "0",
        "qlogin_auto_login": "1",
        "no_verifyimg": "1",
        "link_target": "blank",
        "appid": "549000912",
        "style": "22",
        "target": "self",
        "s_url": "https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone",
        "pt_qr_app": "手机QQ空间",
        "pt_qr_link": "https://z.qzone.com/download.html",
        "self_regurl": "https://qzs.qq.com/qzone/v6/reg/index.html",
        "pt_qr_help_link": "https://z.qzone.com/download.html",
        "pt_no_auth": "0"
    },
    {
        "pt_disable_pwd": "1",
        "appid": "715030901",
        "hide_close_icon": "1",
        "daid": "73",
        "pt_no_auth": "1",
        "s_url": "https://qun.qq.com/"
    },
    # {"u1":"https://wx.mail.qq.com/list/readtemplate?name=login_page.html","s_url":None},
    {
        "target": "self",
        "appid": "522005705",
        "daid": "4",
        "s_url": "https://wx.mail.qq.com/list/readtemplate?name=login_jump.html",
        "style": "25",
        "low_login": "1",
        "proxy_url": "https://mail.qq.com/proxy.html",
        "need_qr": "0",
        "hide_border": "1",
        "border_radius": "0",
        "self_regurl": "https://reg.mail.qq.com",
        "app_id": "11005?t=regist",
        "pt_feedback_link": "http://support.qq.com/discuss/350_1.shtml",
        "css": "https://res.mail.qq.com/zh_CN/htmledition/style/ptlogin_input_for_xmail.css",
        "enable_qlogin": "0"
    },
    {
        "appid": "8000201",
        "style": "20",
        "s_url": "https://vip.qq.com/loginsuccess.html",
        "maskOpacity": "60",
        "daid": "18",
        "target": "self"
    },
    # {"u1":"https://www.weiyun.com/?adtag=ntqqmainpanel","s_url":None},
    {
        "appid": "527020901",
        "daid": "372",
        "low_login": "0",
        "qlogin_auto_login": "1",
        "s_url": "https://www.weiyun.com/web/callback/common_qq_login_ok.html?login_succ",
        "style": "20",
        "hide_title": "1",
        "target": "self",
        "link_target": "blank",
        "hide_close_icon": "1",
        "pt_no_auth": "1"
    },
    {
        "style": "40",
        "appid": "1600001573",
        "s_url": "https://accounts.qq.com/homepage#/",
        "daid": "761",
        "hide_close_icon": "0"
    },
    {
        "appid": "10000101",
        "s_url": "https://qqshow.qq.com/manage/myCreation",
        "hide_close_icon": "1"
    },
    {
        "s_url": "https://huifu.qq.com/recovery/index.html?frag=1",
        "style": "20",
        "appid": "715021417",
        "daid": "768",
        "proxy_url": "https://huifu.qq.com/proxy.html"
    },
    {"u1": "https://docs.qq.com/desktop/?tdsourcetag=s_ntpcqq_panel_app", "s_url": None},
    {
        "daid": "377",
        "style": "11",
        "appid": "716027613",
        "target": "self",
        "pt_disable_pwd": "1",
        "s_url": "https://connect.qq.com/login_success.html",
        "t": str(time.time())
    },
    {
        "appid": "501038301",
        "target": "self",
        "s_url": "https://im.qq.com/loginSuccess"
    }
]

clientkey = ""
uin = ""
nickname = ""
self_cookie = {}
pt_local_token = ""
pt_login_sig = ""
qzone_skey = ""
qzone_pskey = ""
mail_pskey = ""
qun_skey = ""
qun_pskey = ""

def bkn(skey):
    t,n,o = 5381,0,len(skey)

    while n < o:
        t += (t << 5) + ord(skey[n])
        n += 1

    return t & 2147483647

def get_base_info(mute = False):
    global clientkey, uin, nickname, pt_local_token, pt_login_sig, qzone_skey, qzone_pskey, mail_pskey, qun_skey, qun_pskey
    session = requests.session()
    try:
        if not mute:
            procprint("正在获取 pt_local_token...")
        login_htm = session.get("https://xui.ptlogin2.qq.com/cgi-bin/xlogin?s_url=https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone")
        q_cookies = requests.utils.dict_from_cookiejar(login_htm.cookies)
        pt_local_token = q_cookies.get("pt_local_token")
        pt_login_sig = q_cookies.get("pt_login_sig")

        if not mute:
            sucprint(f"pt_local_token={pt_local_token}")
            sucprint(f"pt_local_sig={pt_login_sig}")

        params = {"callback":"ptui_getuins_CB",
                "r":"0.8987470931280881",
                "pt_local_tk":pt_local_token}
        cookies = {"pt_local_token":pt_local_token,
                "pt_login_sig":pt_login_sig}
        headers = {"Referer":"https://xui.ptlogin2.qq.com/",
                "Host":"localhost.ptlogin2.qq.com:4301",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"}
    except Exception as e:
        errprint(f"获取pt_local_token时发生错误,原因:{e}")
        input()
        sys.exit(0)
    try:
        if not mute:
            procprint("正在获取本机登录QQ号..")
        get_uin = session.get("https://localhost.ptlogin2.qq.com:4301/pt_get_uins",params=params,cookies=cookies,headers=headers).text
        uin_list = re.findall(r'\[([^\[\]]*)\]', get_uin)[0]
        split_list = list(map(lambda i:i if i[0] == '{' else '{'+i,uin_list.split(',{')))
        uin = None
        nickname = None
        if len(split_list) > 1:
            warnprint("检测到您正在多开QQ,将使用第一个QQ号获取")
            uin_list = json.loads(json.loads(json.dumps(split_list[0]))) # Json库我爱你loads后返回str还要再loads一次 凸(艹皿艹 )
            uin = uin_list.get("uin")
            nickname = uin_list.get("nickname")
        else:
            uin = json.loads(uin_list).get('uin')
            nickname = json.loads(uin_list).get('nickname')

        if not mute:
            sucprint(f"uin={uin}\n[+] nickname={nickname}")

        clientkey_params = {"clientuin":uin,
                            "r":"0.14246048393632815",
                            "pt_local_tk":pt_local_token,
                            "callback":"__jp0"}
        
        if not mute:
            procprint("正在获取 clientkey...")
        clientkey_get = session.get("https://localhost.ptlogin2.qq.com:4301/pt_get_st",cookies=cookies,headers=headers,params=clientkey_params)
        clientkey_cookies = requests.utils.dict_from_cookiejar(clientkey_get.cookies)
        clientkey = clientkey_cookies.get("clientkey")
        if not clientkey:
            warnprint("未获取到 clientkey,请尝试稍后重启工具获取!")
        else:
            if not mute:
                sucprint(f"clientkey={clientkey}")
    except Exception as e:
        errprint(f"获取clientkey发生错误,请检查是否开启QQ!")
        input()
        sys.exit(0)
    try:
        if not mute:
            procprint("正在获取QQ空间 & QQ邮箱登录地址 & Skey...")
        qzone_params = {
            "u1":"https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone",
            "clientuin":uin,
            "pt_aid":"549000912",
            "keyindex":"19",
            "pt_local_tk":pt_local_token,
            "pt_3rd_aid":"0",
            "ptopt":"1",
            "style":"40",
            "daid":"5"
        }
        qzone_jump_cookies = {
            "clientkey":clientkey,
            "clientuin":uin,
            "pt_local_token":pt_local_token
        }
        headers = {"Referer": "https://xui.ptlogin2.qq.com/",
                "Host": "ssl.ptlogin2.qq.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"}
        qzone_url = session.get("https://ssl.ptlogin2.qq.com/jump",params=qzone_params,cookies=cookies,headers=headers)
        qzone_cookies = requests.utils.dict_from_cookiejar(qzone_url.cookies)
        qzone_skey = qzone_cookies.get("skey")
        extractor = URLExtract()
        qzone_url = extractor.find_urls(qzone_url.text)[0]
        pskey = session.get(qzone_url,allow_redirects=False)
        pskey_cookies = requests.utils.dict_from_cookiejar(pskey.cookies)
        qzone_pskey = pskey_cookies.get("p_skey")
        qzone_url = f"https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin={uin}&clientkey={clientkey}&u1=https://user.qzone.qq.com/{uin}/infocenter&keyindex=19"

        if not mute:
            sucprint(f"qzone_skey={qzone_skey}")
            sucprint(f"qzone_pskey={qzone_pskey}")
            sucprint(f"qzone_url={qzone_url}")

        mail_params = {
            "u1":"https://graph.qq.com/oauth2.0/login_jump",
            "clientuin":uin,
            "pt_aid":"716027609",
            "keyindex":"19",
            "pt_local_tk":pt_local_token,
            "pt_3rd_aid":"102013353",
            "ptopt":"1",
            "style":"40",
            "daid":"383"
        }
        mail_cookies = {
            "clientkey":str(clientkey),
            "clientuin":str(uin),
            "pt_local_token":str(pt_local_token),
            "pt_login_sig":str(pt_login_sig)
        }
        mail_url = session.get("https://ssl.ptlogin2.qq.com/jump",params=mail_params,cookies=mail_cookies,headers=headers)
        mail_cookies = requests.utils.dict_from_cookiejar(mail_url.cookies)
        mail_url = extractor.find_urls(mail_url.text)[0]
        pskey = session.get(mail_url,allow_redirects=False)
        pskey_cookies = requests.utils.dict_from_cookiejar(pskey.cookies)
        mail_pskey = pskey_cookies.get("p_skey")
        mail_url = f"https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin={uin}&clientkey={clientkey}&u1=https://wx.mail.qq.com/list/readtemplate?name=login_page.html&keyindex=19"

        if not mute:
            sucprint(f"mail_pskey={mail_pskey}")
            sucprint(f"mail_url={mail_url}")

        qun_params = {
        "clientuin":str(uin),
        "keyindex":"19",
        "pt_aid":"715030901",
        "daid":"73",
        "u1":"https://qun.qq.com/",
        "pt_local_tk":str(pt_local_token),
        "pt_3rd_aid":"0",
        "ptopt":"1",
        "style":"40"
    }
        qun_cookies = {
            "clientkey":str(clientkey),
            "clientuin":str(uin),
            "pt_local_token":str(pt_local_token),
            "pt_login_sig":str(pt_login_sig)
        }
        qun_res = session.get("https://ssl.ptlogin2.qq.com/jump",params=qun_params,cookies=qun_cookies,headers=headers)
        qun_url = extractor.find_urls(qun_res.text)[0]
        qun_cookie = requests.utils.dict_from_cookiejar(qun_res.cookies)
        qun_info_cookies = session.get(qun_url,allow_redirects=False).cookies
        qun_skey = qun_info_cookies.get("skey")
        qun_pskey = qun_info_cookies.get("p_skey")
        if not mute:
            sucprint(f"qun_url={qun_url}")
    except Exception as e:
        errprint(f"获取QQ空间&QQ邮箱地址时出现错误,原因:{e}")
        input()
        sys.exit(0)
    if not mute:
        print("\033[95m****************** 基础信息 ******************\033[0m")
        print(f"\033[94muin = \033[92m{uin}")
        print(f"\033[94mnickname =\033[91m {nickname}")
        if SAFEMODE:
            print(f"\033[94mclientkey =\033[93m {nick_name(clientkey)}")
            print(f"\033[94mqzone_skey =\033[96m {nick_name(qzone_skey)}")
            print(f"\033[94mqzone_pskey =\033[93m {nick_name(qzone_pskey)}")
            print(f"\033[94mmail_pskey =\033[96m {nick_name(mail_pskey)}")
            print(f"\033[94mqun_skey =\033[93m {nick_name(qun_skey)}")
            print(f"\033[94mqun_pskey =\033[96m {nick_name(qun_pskey)}")
            print(f"\033[94mqzone_url =\033[33m {nick_name(qzone_url)}")
            print(f"\033[94mmail_url = \033[37m{nick_name(mail_url)}")
            print(f"\033[94mqun_url = \033[33m{nick_name(qun_url)}\033[0m")
        else:
            print(f"\033[94mclientkey =\033[93m {clientkey}")
            print(f"\033[94mqzone_skey =\033[96m {qzone_skey}")
            print(f"\033[94mqzone_pskey =\033[93m {qzone_pskey}")
            print(f"\033[94mmail_pskey =\033[96m {mail_pskey}")
            print(f"\033[94mqun_skey =\033[93m {qun_skey}")
            print(f"\033[94mqun_pskey =\033[96m {qun_pskey}")
            print(f"\033[94mqzone_url =\033[33m {qzone_url}")
            print(f"\033[94mmail_url = \033[37m{mail_url}")
            print(f"\033[94mqun_url = \033[33m{qun_url}\033[0m")
        print("\033[95m****************** 感谢使用 ******************\033[0m")

def get_g_tk(p_skey):
    t = 5381
    for i in p_skey:
        t += (t << 5) + ord(i)
    return t & 2147483647

def load_skey_by_clientkey(data):

    global uin, skey, pskey, g_tk, self_cookie

    login_data, uin, clientkey = data
    try:
        print("login_data: " + str(login_data))
        session = requests.session()
        if login_data['s_url']:
            login_htm = session.get(
                "https://xui.ptlogin2.qq.com/cgi-bin/xlogin",params=login_data)
            print("URL: " + login_htm.url)
            q_cookies = requests.utils.dict_from_cookiejar(login_htm.cookies)
            print("Cookies: " + str(q_cookies))
            pt_local_token = q_cookies.get("pt_local_token")
            headers = {"Referer": "https://xui.ptlogin2.qq.com/",
                        "Host": "ssl.ptlogin2.qq.com",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"}
            params = {
                "u1": login_data['s_url'],
                "clientuin": uin,
                "pt_aid": login_data['appid'],
                "keyindex": "19",
                "pt_local_tk": pt_local_token,
                "pt_3rd_aid": "0",
                "ptopt": "1",
                "style": "40"
            }
            if login_data.get("daid"): params['daid'] = login_data.get("daid")
            cookies = {
                "clientkey": clientkey,
                "clientuin": str(uin),
                "pt_local_token": pt_local_token
            }
            login_res = session.get("https://ssl.ptlogin2.qq.com/jump",params=params,cookies=cookies,headers=headers)
        else:
            login_res = session.get(f"https://ssl.ptlogin2.qq.com/jump?ptlang=1033&clientuin={uin}&clientkey={clientkey}&u1={login_data['u1']}&keyindex=19",allow_redirects=False)
        if login_data['s_url']:
            extracter = URLExtract()
            print("* Text: -----------------------------------")
            print(login_res.text)
            print("* -----------------------------------------")
            urls = extracter.find_urls(login_res.text)
            print("* Urls: " + str(urls))
            url = urls[0]
        else:
            url = login_res.headers['Location']

        login_url = url

        uin = login_res.cookies.get_dict().get('uin')
        print("UIN: " + uin)
        cookies = requests.utils.dict_from_cookiejar(login_res.cookies)
        r2 = requests.get(url, cookies=cookies, allow_redirects=False)
        targetCookies = requests.utils.dict_from_cookiejar(r2.cookies)
        skey = requests.utils.dict_from_cookiejar(r2.cookies).get('skey')
        pskey = requests.utils.dict_from_cookiejar(r2.cookies).get('p_skey')
        if not skey:
            raise Exception("Skey not found!")
        self_cookie = targetCookies
        
        if 'qzone' in login_data.get("s_url"):
            g_tk = get_g_tk(skey)
        else:
            g_tk = ''
        sucprint("登录成功！")
    except Exception as e:
        errprint("登录失败! " + str(e))

def get_friend_list(g_tk, uin, pskey, skey):
    Cookies = {
        "p_skey": pskey,
        "uin": str(uin),
        "skey": skey,
        "p_uin": str(uin)
    }
    headers = {
        "Referer": f"https://user.qzone.qq.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Origin": "https://user.qzone.qq.com"
    }
    data = {
                "uin":str(uin)[1:],
                "do":"1",
                "rd":f"0.{time.time()}",
                "fupdate":"1",
                "clean":"1",
                "g_tk":g_tk
            }
    try:
        res = requests.get("https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi", params=data, cookies=Cookies, headers=headers, json=data, data=data).text[10:-2]
        # print(res)
        friend_list = json.loads(res).get("data").get("items_list")
    except Exception as e:
        errprint("错误：" + str(e))

    try:
        print("\033[95m***************************** 好友列表 *****************************\033[0m")
        print("\033[95m序号\t昵称\t\t\tQQ号\t\t\t手机号\t\t手机地区\t\t微博ID\t\t头像地址   \033[0m")

        j = 0

        for i in friend_list:
            # try:

            # Thread(target=print_friend_item, args=(i, j)).start() 频率太高会被封ip的
            print_friend_item(i, j, SPIDER_MORE)
            
            # except:
            #     # print("ERROR: " + str(e))
            #     traceback.print_exc()
            #     break
            j += 1
        print("\033[95m***************************** 显示完毕 *****************************\033[0m")

        # with open("friend_list.csv",'w',encoding='utf-8-sig',newline='') as f:
        #     csv_f = csv.writer(f)
        #     csv_f.writerow(['名称','QQ号','头像地址'])
        #     for i in friend_list:
        #         csv_f.writerow([i['name']+"\t",str(i['uin'])+"\t",i['img']])
        # sucprint("已保存至friend_list.csv!")
    # except PermissionError:
    #     errprint("请关闭正在打开 friend_list.csv 的文件!")

    except Exception as e:
        errprint("未知错误! " + str(e))

group_list = []

def get_group_list(bkn, cookies):
    url = 'https://qun.qq.com/cgi-bin/qun_mgr/get_group_list'
    print(f"url={url}, bkn={bkn}, cookies={cookies}")
    data = {'bkn': bkn}
    qun_lis = requests.post(url,data = data, cookies = cookies).json()

    gn_width = 40  # 根据实际内容调整
    gc_width = 18  # 根据实际内容调整
    owner_width = 30  # 根据实际内容调整

    try:
        if qun_lis.get('create') != 0:
            print("\033[95m***************** 你创建的群 *****************\033[0m")
            print("\033[33m群名\t\t\033[34m群号\t\t\033[31m群主\033[0m")
            for i in qun_lis['create']:
                print(f"\033[33m{str(html.unescape(i['gn'])):<{gn_width}}\033[0m" +
                      f"\033[34m{str(i['gc']):<{gc_width}}\033[0m" +
                      f"\033[31m{str(i['owner']):<{owner_width}}\033[0m")
                group_list.append([i['gc'], i['gn']])
            print()
        if qun_lis.get('manage') != 0:
            print("\033[95m***************** 你管理的群 *****************\033[0m")
            print("\033[33m群名\t\t\033[34m群号\t\t\033[31m群主\033[0m")
            for i in qun_lis['manage']:
                print(f"\033[33m{str(html.unescape(i['gn'])):<{gn_width}}\033[0m" +
                      f"\033[34m{str(i['gc']):<{gc_width}}\033[0m" +
                      f"\033[31m{str(i['owner']):<{owner_width}}\033[0m")
                group_list.append([i['gc'], i['gn']])
            print()
        if qun_lis.get('join') != 0:
            print("\033[95m***************** 你加入的群 *****************\033[0m")
            print("\033[33m群名\t\t\033[34m群号\t\t\033[31m群主\033[0m")
            for i in qun_lis['join']:
                print(f"\033[33m{str(html.unescape(i['gn'])):<{gn_width}}\033[0m" +
                      f"\033[34m{str(i['gc']):<{gc_width}}\033[0m" +
                      f"\033[31m{str(i['owner']):<{owner_width}}\033[0m")
                group_list.append([i['gc'], i['gn']])
            print()
        print("\033[95m********************************************\033[0m")
    except Exception as e:
        errprint("错误：" + str(e))

def get_group_member_list(bkn, qid, qname):
    data = {
        "st":"0",
        "start":"0",
        "end":"9",
        "sort":"1",
        "group_id":str(qid),
        "gc":str(qid)
    }
    headers = {
        "Referer": "https://web.qun.qq.com/mannounce/index.html?_wv=1031&_bid=148",
        "Host": "qun.qq.com",
        "Origin": "https://qun.qq.com"
    }
    Cookies = {
        "p_skey": pskey,
        "uin": str(uin),
        "skey": skey,
        "p_uin": str(uin),
        "ptui_loginuin":str(uin)
    }
    l = []
    start = 0
    end = 9
    while True:
        attempt = 1
        time.sleep(random.randint(1, 3))
        res = requests.post(f"https://qun.qq.com/cgi-bin/qun_mgr/search_group_members?bkn={bkn}&ts=1702901784527", 
                            cookies=Cookies, data=data, headers=headers).json()
        try:
            # print(f"res: {str(res)}")

            for i in res['mems']:
                # l.append(str(i))
                # print(l,[str(i['nick'])+'\t',str(i['uin'])+'\t'])
                # if [str(i['nick']),str(i['uin'])] in l:
                #     break
                # l.append([str(i['nick']),str(i['uin'])])
                if i in l:
                    continue
                l.append(i)
            start += 10
            end += 10
            data['start'], data['end'] = str(start), str(end)
        except Exception as e:
            if "malicious" in str(e):  
                # {ec: 99997, errcode: 0, em: "anti-malicious [errcode:99997:0]"}
                if attempt >= 2:
                    errprint("重试次数已达上限！正在取消操作")
                    break
                errprint("请求速度过快，被拒绝 :( 正在重试...")
                attempt += 1
                time.sleep(3)
            else:
                errprint("ERROR：" + str(e))
                break
    try:
        nickname_width = 40
        qq_width = 20
        timestamp_width = 30

        print("\033[34m****************************************************")
        print("\033[37m群聊：\033[92m" + html.unescape(qname) + " - \033[31m" + str(qid))
        print("\033[33m昵称\t\t身份\t\tQQ 号\t\t群昵称\t\t加入时间\t\t发言时间\t\tQ 龄\t\tflag\t\trm\t\ttags")

        # print("\033[97m" + str(l))
        if l:
            for mem in l:
                line = ""
                if 'nick' in mem:
                    line += f"\033[93m{str(html.unescape(mem['nick'])):<{nickname_width}}"
                if 'role' in mem:
                    line += f"\033[34m{str(mem['role']):<{6}}"
                if 'uin' in mem:
                    line += f"\033[31m{str(mem['uin']):<{qq_width}}"
                if 'card' in mem:
                    if len(mem['card']) == 0:
                        mem['card'] = "-/-"
                    line += f"\033[94m{str(html.unescape(mem['card'])):<{nickname_width}}"
                if 'join_time' in mem:
                    line += f"\033[32m{parse_timestamp(mem['join_time']):<{timestamp_width}}"
                if 'last_speak_time' in mem:
                    line += f"\033[33m{parse_timestamp(mem['last_speak_time']):<{timestamp_width}}"
                if 'qage' in mem:
                    line += f"\033[90m{str(mem['qage']):<{7}}"
                if 'flag' in mem:
                    line += f"\033[37m{str(mem['flag']):<{7}}"
                if 'rm' in mem:
                    line += f"\033[90m{str(mem['rm']):<{7}}"
                if 'tags' in mem:
                    line += f"\033[37m{str(mem['tags']):<{7}}"

                print(line + "\033[0m")
            
    except Exception as e:
        errprint("错误：" + str(e))
    print("\033[34m****************************************************")

def test():
    print("""\033[93m
888       888        d8888 8888888b.  888b    888 8888888 888b    888  .d8888b.  
888   o   888       d88888 888   Y88b 8888b   888   888   8888b   888 d88P  Y88b 
888  d8b  888      d88P888 888    888 88888b  888   888   88888b  888 888    888 
888 d888b 888     d88P 888 888   d88P 888Y88b 888   888   888Y88b 888 888        
888d88888b888    d88P  888 8888888P"  888 Y88b888   888   888 Y88b888 888  88888 
88888P Y88888   d88P   888 888 T88b   888  Y88888   888   888  Y88888 888    888 
8888P   Y8888  d8888888888 888  T88b  888   Y8888   888   888   Y8888 Y88b  d88P 
888P     Y888 d88P     888 888   T88b 888    Y888 8888888 888    Y888  "Y8888P88 
   
          \033[0m""")
    print("\033[91m[!] 警告：这可能会侵犯你的隐私，请谨慎使用！\033[0m")
    print("\033[91m[!] 如果拒绝访问你的QQ信息，请在\033[92m三秒内\033[91m退出程序!!\033[94m（你可以按下Ctrl+C）\033[0m")
    if SAFEMODE:
        print("\033[92m[+] 安全模式已开启，将隐去部分信息\033[0m")
    time.sleep(3)

    get_base_info()
    # --------------------------------------------
    # 1. 空间
    load_skey_by_clientkey((login_data[0], uin, clientkey))

    # g_tk = get_g_tk(qzone_skey)
    # pskey = qzone_pskey
    # skey = qzone_skey
    get_friend_list(g_tk, uin, pskey, skey)

    # --------------------------------------------
    # 2. 群
    get_base_info(True)
    load_skey_by_clientkey((login_data[1], uin, clientkey))
    get_group_list(bkn(skey), self_cookie)

    procprint("获取群成员信息中...")
    get_base_info(True)
    load_skey_by_clientkey((login_data[1], uin, clientkey))
    for grp in group_list:
        get_group_member_list(bkn(skey), grp[0], grp[1])

    os.system("pause")
    os._exit(0)

def print_menu():
    print("\033[94m----------------------------------\033[0m")
    print("\033[93m输入数字选择功能：\033[0m")
    print("\033[95m[0] 展示所有信息\033[0m")
    print("\033[95m[1] 账号基本信息\033[0m")
    print("\033[95m[2] 好友列表\033[0m")
    print("\033[95m[3] 群列表\033[0m")
    print("\033[95m[4] 群成员列表\033[0m")
    print("\033[95m[5] 指定群成员列表\033[0m")
    print("\033[95m[6] 退出\033[0m")
    print("\033[94m----------------------------------\033[0m")

def enter_menu():
    print_menu()
    s = input("\033[97m> \033[37m")
    if s == "0":
        test()
    elif s == "1":
        get_base_info()
    elif s == "2":
        get_base_info(True)
        load_skey_by_clientkey((login_data[0], uin, clientkey))
        get_friend_list(g_tk, uin, pskey, skey)
    elif s == "3":
        get_base_info(True)
        load_skey_by_clientkey((login_data[1], uin, clientkey))
        get_group_list(bkn(skey), self_cookie)
    elif s == "4":
        get_base_info(True)
        load_skey_by_clientkey((login_data[1], uin, clientkey))
        for grp in group_list:
            get_group_member_list(bkn(skey), grp[0], grp[1])
    elif s == "5":
        get_base_info(True)
        load_skey_by_clientkey((login_data[1], uin, clientkey))
        get_group_member_list(bkn(skey), input("\033[37m输入群号：\033[0m"), "")
    elif s == "6":
        os._exit(0)
    else:
        print("\033[91m[!] 错误：无效的输入\033[0m\n")


if __name__ == '__main__':
    print("\033[36m----------------------------------\033[0m")
    print("\033[37mQQInspector " + VERSION + "\033[0m")
    print("\033[37m       by @Wormwaker\033[0m")
    print("\033[36m----------------------------------\033[0m")
    os.system("title QQInspector " + VERSION + " - by @Wormwaker")
    
    if not exist_process("QQ.exe"):
        print("\033[91m[!] 错误：请先运行并登录QQ！\033[0m")
        os._exit(0)

    get_base_info(True)
    while True:
        enter_menu()