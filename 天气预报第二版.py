import http.client
import json
import os
import random
import sys
import urllib
from datetime import datetime, date
from time import localtime

from requests import get, post
from zhdate import ZhDate


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():

    # appId
    # app_id = config["app_id"]
    app_id = "wx85fe515f01a962eb"
    # appSecret
    # app_secret = config["app_secret"]
    app_secret = "f8627cb23fb4662fc17baccdec1abb38"
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    print("测试",response)
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 最高最低温度
    max_temp,min_temp = max_min_temp(region)
    #体感温度
    feelslike = response["now"]["feelsLike"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    #风速
    wind_scale = response["now"]["windScale"]
    return weather, temp, max_temp, min_temp, feelslike, wind_dir, wind_scale

def max_min_temp(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    print("测试2", response)
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    max_min_temp_url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response = get(max_min_temp_url, headers=headers).json()
    print("测试", response['daily'][0])
    max_temp = response['daily'][0]['tempMax'] + u"\N{DEGREE SIGN}" + "C"
    min_temp = response['daily'][0]['tempMin'] + u"\N{DEGREE SIGN}" + "C"
    return max_temp, min_temp


def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day


def get_ciba():
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }
    r = get(url, headers=headers)
    note_en = r.json()["content"]
    note_ch = r.json()["note"]
    return note_ch, note_en



def send_message(to_user, access_token, region_name, weather, temp, max_temp, min_temp, feelslike, wind_dir,wind_scale, note_ch, note_en, lucky_):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather,
                "color": get_color()
            },
            "temp": {
                "value": temp,
                "color": get_color()
            },
            "max_temp": {
                "value": max_temp,
                "color": get_color()
            },
            "min_temp": {
                "value": min_temp,
                "color": get_color()
            },
            "feelslike": {
                "value": feelslike,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "wind_scale": {
                "value": wind_scale,
                "color": get_color()
            },
            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "note_en": {
                "value": note_en,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            },
            "lucky_": {
                "value":lucky_,
                "color":get_color()
            }
        }
    }
    # for key, value in birthdays.items():
    #     # 获取距离下次生日的时间
    #     birth_day = get_birthday(value["birthday"], year, today)
    #     if birth_day == 0:
    #         birthday_data = "\n今天{}生日哦，祝{}生日快乐！".format(value["name"], value["name"])
    #     else:
    #         birthday_data = "\n距离{}的生日还有{}天".format(value["name"], birth_day)
    #     # 将生日数据插入data
    #     data["data"][key] = {"value": birthday_data, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)
#星座运势
def lucky():
    lucky_API = "64baf8f39eb4ace7f6a137bbd7ff6ebd"
    astro = "双鱼座"
    if (lucky_API != "否"):
        conn = http.client.HTTPSConnection('api.tianapi.com')  # 接口域名
        params = urllib.parse.urlencode({'key': lucky_API, 'astro': astro})
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        conn.request('POST', '/star/index', params, headers)
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)
        data = "爱情指数：" + str(data["newslist"][1]["content"]) +"\n速配星座：" + str(data["newslist"][7]["content"]) +\
               "\n工作指数：" + str(data["newslist"][2]["content"]) + "\n今日概述：" + str(data["newslist"][8]["content"])
        return data
    else:
        return ""
if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, max_temp, min_temp, feelslike, wind_dir, wind_scale = get_weather(region)
    # note_ch = config["note_ch"]
    # 获取金山词霸中文版个人金句
    note_ch = get_ciba()[0]
    # note_en = config["note_en"]  获取自己设置的个人金句
    #获取金山词霸英文版个人金句
    note_en = get_ciba()[1]
    #星座运势
    lucky_ = lucky()

    if note_ch == "" and note_en == "":
        # 获取词霸每日金句
        note_ch, note_en = get_ciba()

    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, max_temp, min_temp, feelslike, wind_dir, wind_scale, note_en, note_ch, lucky_)
    os.system("pause")


# 模板内容
# {{date.DATA}}
# 地区：{{region.DATA}}
# 天气：{{weather.DATA}}
# 当前气温：{{temp.DATA}}
# 今天最高气温：{{max_temp.DATA}}
# 今天最低气温：{{min_temp.DATA}}
# 体感温度：{{feelslike.DATA}}
# 风向：{{wind_dir.DATA}}
# 风速：{{wind_scale.DATA}}
# 今天是我们恋爱的第{{love_day.DATA}}天
# {{birthday1.DATA}}
# {{birthday2.DATA}}
# {{note_en.DATA}}
# {{note_ch.DATA}}
#
# {{lucky_.DATA}}

#爱情指数: {{lover.DATA}}
#速配星座：{{constellation.DATA}}
#工作指数：{{work.DATA}}
#今日概述：{{today_text.DATA}}
