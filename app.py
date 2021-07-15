import os
import requests
import time
import json
import random
import time
from weather import *
from get_photo import *
from contents import determine_contents
from crawler import *
from deal_db import * # for record the weather.
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from line_token import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

# TODO: 新增各地景點美食，晚餐吃甚麼，圖搜功能，
# 波波發胖('https://www.popdaily.com.tw/food/778598?utm_source=facebook-popyummy&utm_medium=post&utm_campaign=icecream&utm_content=link-20200904&fbclid=IwAR1ETXsqlFtaklvsRs9de4cH0A3ev5Ye00qLQwLs5yENILeWgp_yETGBR2')
# 短網址功能
app = Flask(__name__)

CAT=channel_access_token()
CS=channel_secret()
# Channel Access Token
line_bot_api = LineBotApi(CAT)
# Channel Secret
handler = WebhookHandler(CS)

# covid 19 reminder~
@app.route("/covid19_clock", methods =['GET'])
def covid19_clock():
    id_list=[]
    id_list=push_weather_id()
    covid_message = covid_reminder()
    print(id_list)
    for i in range(len(id_list)):
        try:
            profile = line_bot_api.get_profile(id_list[i])
            message = "哈囉 "+profile.display_name+" ~~~ \n"
            message += "劉大帥來報疫情狀況囉!\n今日"
            message += covid_message
            message += "\n希望三級趕快結束T_T"
        except:
            message = "出BUG辣!!! 請通知開發者，或是利用表單通知QQ\n"
        time.sleep(0.5)
        try:
            print(message)
            line_bot_api.push_message(id_list[i],TextSendMessage(text=message))
        except:
            print("push message failed")
    return 'OK'

# beauty crawler ~
@app.route("/beauty_crawler", methods =['GET'])
def beauty_clock():
    try:
        beauty_crawler()
    except:
        print("The beauty crawler die....")
    return 'OK'


@app.route("/weather_clock", methods =['GET'])
def weather_clock():
    id_list=[]
    location_list=[]

    id_list=push_weather_id()
    location_list = push_location_id()
    print(id_list)
    print(location_list)
    for i in range(len(id_list)):
        try:
            profile = line_bot_api.get_profile(id_list[i])
            message = "哈囉 "+profile.display_name+" ~~~ \n"
            message += "劉大帥來報氣象囉!\n"
            message += determine_littleTown(location_list[i])
        except:
            message = location_list[i]+"出BUG辣!!! 請通知開發者，或是利用表單通知QQ\n"
            if(location_list[i] == '彰化縣'):
                message = "哈囉 "+profile.display_name+" ~~~ \n"
                message += "劉大帥來報氣象囉!\n"
                message = determine_littleTown('彰化縣')
        time.sleep(0.5)
        try:
            print(message)
            line_bot_api.push_message(id_list[i],TextSendMessage(text=message))
        except:
            print("push message failed")
    return 'OK'


# 監聽所有來自 /callback 的 Post Request

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body

    print(body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# broadcast


@app.route("/broadcast_function/<string:broadcast_text_str>")
def broadcast_message(broadcast_text_str):
    line_bot_api.broadcast(TextSendMessage(text=broadcast_text_str))
    return 'OK'

# 處理訊息

# breakfast

def breakfast_EatWhat():
    breakfast_list = ['宮保雞丁麵', '蘿蔔糕', '黑胡椒鐵板麵', '蘑菇鐵板麵',
                      '烤三明治', '火腿蛋吐司', '豬肉蛋吐司', '薯餅蛋吐司', '熱狗蛋吐司', '燻雞蛋吐司', '厚片吐司', '三明治', '燒餅油條', '蔥抓餅', '煎餃', '中式飯糰', '御飯糰', '牛肉麵(南部人的習慣)', '炒麵(台中人)', '粥', '肉燥飯(台南、高雄)', '油飯',
                      '大腸麵線/蚵仔麵線', '肉鬆蛋餅', '起司蛋餅', '薯餅蛋餅', '鮪魚蛋餅', '早餐店漢堡', '火腿蛋堡', '起司蛋堡', '卡啦雞腿堡', '豬肉滿福堡(麥當勞)', '薯餅', '香雞滿福堡(麥當勞)', '青蔬滿福堡(麥當勞)', '火腿蛋堡(麥當勞)', '吉事蛋堡(麥當勞)', '比利時鬆餅', '麥當勞鬆餅']
    return random.choice(breakfast_list)

# lunch and dinner

def lunch_EatWhat():
    lunch_list = ['全家便利超商', '炒飯', '炒麵', '咖喱飯', '牛肉麵',
                  '鍋貼', '水餃', '麻醬麵', '炸醬麵', '焢肉飯', '泡麵', '陽春麵', '丼飯', '麥當勞', '迴轉壽司', '火鍋', '涼麵', '烤肉飯', '一般的便當', '7-11', '新加坡料理', '燒臘便當', '肯德基', '拿玻里', '披薩', '永和豆漿', '美式炸雞', '涮涮鍋', '麻辣鍋', '壽喜燒', '生魚片', '石鍋拌飯', '韓式炸雞', '銅盤烤肉', '好市多餐廳', '牛排', '義大利麵', '拉麵', '滷肉飯']
    return random.choice(lunch_list)

# drink 
def drink_what():
    drink_list = ['烏龍綠茶','特級綠茶', '錫蘭紅茶' ,'極品菁茶' ,'原鄉四季' ,'特選普洱', '翡翠烏龍' ,'嚴選高山茶','太妃鴛鴦奶茶', '珍珠奶茶' ,'波霸奶茶', '錫蘭奶紅' ,'烏龍奶茶' ,'特級奶綠' ,'仙草凍奶茶' ,'椰果奶茶' ,'布丁奶茶' ,'暗黑水晶奶茶' ,'粉圓奶茶' ,'蜂蜜奶茶','芝麻奶茶'
    ,'多多綠茶','冰淇淋紅茶']
    return random.choice(drink_list)



@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    today = time.strftime('%m/%d').lstrip('0')
    if (event.message.text == "6"):  # flex
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "bubble",
                "hero": {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "action": {
                            "type": "uri",
                            "uri": "http://linecorp.com/"
                        }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                            {
                                "type": "text",
                                "text": "Justin Cafe",
                                "weight": "bold",
                                "size": "xl"
                            },
                        {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "lg",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "Place",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": "Miraina Tower, 4-1-6 Shinjuku, Tokyo",
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            }
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "Time",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": "10:00 - 23:00",
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            }
                                        ]
                                    }
                                ]
                        },
                        {
                                "type": "box",
                                "layout": "baseline",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "icon",
                                        "size": "sm",
                                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                                    },
                                    {
                                        "type": "icon",
                                        "size": "sm",
                                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                                    },
                                    {
                                        "type": "icon",
                                        "size": "sm",
                                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                                    },
                                    {
                                        "type": "icon",
                                        "size": "sm",
                                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                                    },
                                    {
                                        "type": "icon",
                                        "size": "sm",
                                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                                    },
                                    {
                                        "type": "text",
                                        "text": "4.0",
                                        "size": "sm",
                                        "color": "#999999",
                                        "margin": "md",
                                        "flex": 0
                                    }
                                ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                            {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "CALL",
                                    "uri": "https://linecorp.com"
                                }
                            },
                        {
                                "type": "button",
                                "style": "link",
                                "height": "sm",
                                "action": {
                                    "type": "uri",
                                    "label": "WEBSITE",
                                    "uri": "https://linecorp.com"
                                }
                            },
                        {
                                "type": "spacer",
                                "size": "sm"
                            }
                    ],
                    "flex": 0
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
        return 0
    if (event.message.text == "PTT"):
        flex_message = FlexSendMessage(
            alt_text='PTT看板',
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://i.imgur.com/KlLvT2z.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": "https://linecorp.com"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "action": {
                        "type": "uri",
                        "uri": "https://linecorp.com"
                    },
                    "contents": [
                        {
                            "type": "text",
                            "text": "PTT看板",
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "八卦版熱門文章",
                                        "text": "八卦"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "最近省錢版在省啥",
                                        "text": "省錢"
                                    }
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "     ~~~~~~其他看板增加中~~~~~~",
                            "wrap": True,
                            "color": "#aaaaaa",
                            "size": "xxs"
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
        return 0

    if (event.message.text == "你是誰"):  # 你是誰
        message = TextSendMessage(text='哈囉! 我是劉大帥')
        line_bot_api.reply_message(event.reply_token, message)
        return 0
    if (event.message.text == "發送訊息"):
        message = TextSendMessage(text='系統正在試著發送訊息....')
        line_bot_api.reply_message(event.reply_token, message)
        line_bot_api.push_message('U91415c29ac7b4f1e1128df71692903c3',TextSendMessage(text='這是我主動發送的訊息優><'))
        
    if (event.message.text == "提醒天氣"): # record the weather.
        messaage = TextSendMessage(text='準備來記錄天氣囉~\n請輸入"記錄天氣 地點"\nExample: 記錄天氣 汐止區')
        line_bot_api.reply_message(event.reply_token, messaage)
        return 0
    if (event.message.text[0:4] == "記錄天氣" or event.message.text[0:4] == "紀錄天氣"):
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)

        messaage = TextSendMessage(text=profile.display_name+'您好，你要記錄天氣的地區是'+event.message.text[5:])
        line_bot_api.reply_message(event.reply_token, messaage)
        push_msg=prepare_record(profile.user_id,profile.display_name,event.message.text[5:])
        line_bot_api.push_message(profile.user_id,TextSendMessage(text=push_msg))
        return 0
    if (event.message.text == "我是誰"):  # 我是誰
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        # print(profile.display_name)
        your_name = profile.display_name
        if(user_id == 'U669964f8d90416b0387cf99efd8bb0a4'):
            your_name = "我媽咪"
        elif(user_id == 'U91415c29ac7b4f1e1128df71692903c3'):
            your_name = "我ㄉ把拔"
        your_location=find_setting_weather(profile.user_id)
        message = TextSendMessage(text=("你是"+your_name
                                        +"\n你的user_id為"+str(user_id)
                                        +"\n你的天氣設定為"+your_location
                                        ))
        line_bot_api.reply_message(event.reply_token, message)

        return 0
    if (event.message.text == "八卦"):  # 八卦
        message = gossiping()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == "貓咪"): # 回傳貓咪照片
        preview,original=get_cat()
    
        image_message = ImageSendMessage(
        original_content_url=original,
        preview_image_url=original
    )
        line_bot_api.reply_message(
        event.reply_token, image_message)
        return 0
    if (event.message.text == "狗狗"): # 回傳dog照片
        preview,original=get_dog()
        image_message = ImageSendMessage(
        original_content_url=original,
        preview_image_url=original
    )
        line_bot_api.reply_message(
        event.reply_token, image_message)
        return 0
    if (event.message.text == "省錢"):  # 省錢
        message = LIM()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == "兆偉女友" or event.message.text == "抽"):  # 兆偉女友照片合輯
        original = beauty_sql(sex = 'female')
        image_message = ImageSendMessage(
        original_content_url=original,
        preview_image_url=original
    )
        line_bot_api.reply_message(
        event.reply_token, image_message)
        return 0
    if (event.message.text == "兆偉男友" or event.message.text == "抽男"):  # 兆偉男友照片合輯
        original = beauty_sql(sex = 'male')
        image_message = ImageSendMessage(
        original_content_url=original,
        preview_image_url=original
    )
        line_bot_api.reply_message(
        event.reply_token, image_message)
        return 0
    if(event.message.text == '今日疫情' or event.message.text == '今天疫情'):
        covid_message = covid_reminder()
        message = "劉大帥來報疫情狀況囉!\n今日"
        message += covid_message
        message += "\n希望三級趕快結束T_T"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '今日番號'):
        message = av_recommand()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '@王兆偉'):
        message = '上線啦幹'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '兆偉網路'):
        message = '媽的王兆偉7414'
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '早餐吃什麼'):
        message = breakfast_EatWhat()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '晚餐吃什麼'):
        message = lunch_EatWhat()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '飲料喝什麼'):
        message = drink_what()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '午餐吃什麼'):
        message = lunch_EatWhat()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0
    if (event.message.text == '臺北行政區'):
        flex_message = FlexSendMessage(
            alt_text='臺北行政區',
            contents=determine_contents(event.message.text)
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
        return 0
    if (event.message.text == '新北行政區'):
        flex_message = FlexSendMessage(
            alt_text='新北行政區',
            contents=determine_contents(event.message.text)
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
        return 0
    if (event.message.text == "台灣地圖"):
        flex_message = FlexSendMessage(
            alt_text='台灣地圖',
            contents=determine_contents(event.message.text)
        )
        line_bot_api.reply_message(
            event.reply_token, flex_message)
        return 0
    if (event.message.text[3:5] == '天氣'):

        Little_Town = ''

        NewTaipeiList = ['板橋區', '新莊區', '中和區', '永和區', '土城區', '樹林區', '三峽區',
                         '鶯歌區', '三重區', '蘆洲區', '五股區', '泰山區', '林口區', '八里區', '淡水區', '三芝區', '石門區',
                         '金山區', '萬里區', '汐止區', '瑞芳區', '貢寮區', '平溪區', '雙溪區', '新店區', '深坑區', '石碇區', '坪林區', '烏來區']
        TaipeiList = ['中正區', '大同區', '中山區', '松山區', '大安區',
                      '萬華區', '信義區', '士林區', '北投區', '內湖區', '南港區', '文山區']
        KeeLungList = ['仁愛區', '中正區', '信義區', '中山區', '安樂區', '暖暖區', '七堵區']
        if event.message.text[0:3] in NewTaipeiList:
            city = '新北市'
            Little_Town = event.message.text[0:3]

        elif event.message.text[0:3] in TaipeiList:
            city = '臺北市'
            Little_Town = event.message.text[0:3]
        else:
            city = event.message.text[0:3]  # 城市
            if (city == '台南市'):
                city = '臺南市'
            elif city == '台東縣':
                city = '臺東縣'
            elif city == '台中市':
                city = '臺中市'

        print(city)
        message = weather(city, Little_Town)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message))
        return 0

    if (event.message.text == '功能'):
        flex_message = FlexSendMessage(
            alt_text='功能選單',
            contents={
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/3sAcfuN.jpg",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                            "action": {
                                "type": "uri",
                                "uri": "http://linecorp.com/"
                            },
                            "backgroundColor": "#FFFFFF"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "功能選單",
                                    "weight": "bold",
                                    "size": "xl",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "選擇你要的(`・ω・´)",
                                    "margin": "md"
                                }
                            ],
                            "action": {
                                "type": "uri",
                                "label": "View detail",
                                "uri": "http://linecorp.com/",
                                "altUri": {
                                    "desktop": "http://example.com/page/123"
                                }
                            }
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "你是誰?",
                                        "text": "你是誰"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "我是誰?",
                                        "text": "我是誰"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "設定天氣鬧鐘~",
                                        "text": "提醒天氣"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "PTT看板",
                                        "text": "PTT"
                                    },
                                    "height": "sm"
                                }
                            ],
                            "flex": 0
                        },
                        "styles": {
                            "footer": {
                                "separator": True
                            }
                        }
                    }
                ]
            }
        )
        line_bot_api.reply_message(
            event.reply_token, flex_message)
        return 0
    elif (event.message.text== "目錄"):
        flex_message = FlexSendMessage(
            alt_text='目錄',
            contents={
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/YPRHpxV.jpg",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                            "action": {
                                "type": "uri",
                                "uri": "http://linecorp.com/"
                            },
                            "backgroundColor": "#FFFFFF"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目錄",
                                    "weight": "bold",
                                    "size": "xl",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "請選擇",
                                    "margin": "md"
                                }
                            ],
                            "action": {
                                "type": "uri",
                                "label": "View detail",
                                "uri": "http://linecorp.com/",
                                "altUri": {
                                    "desktop": "http://example.com/page/123"
                                }
                            }
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "看偶有甚麼功能",
                                        "text": "功能"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "今天的天氣系安抓",
                                        "text": "台灣地圖"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type":"uri",
                                        "label":"許願功能><",
                                        "uri":"https://www.surveycake.com/s/ZZDP6",
                                        "altUri":{
                                            "desktop":"https://www.surveycake.com/s/ZZDP6"
                                        }
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "uri",
                                        "label": "把我分享給你所~~~~有的朋友",
                                        "uri": "https://line.me/R/nv/recommendOA/@502ohwly",
                                        "altUri": {
                                            "desktop": "https://line.me/R/nv/recommendOA/@502ohwly"
                                        }
                                    },
                                    "height": "sm"
                                }
                            ],
                            "flex": 0
                        },
                        "styles": {
                            "footer": {
                                "separator": True
                            }
                        }
                    },
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://i.imgur.com/yqzlgsV.jpg",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                            "action": {
                                "type": "uri",
                                "uri": "http://linecorp.com/"
                            },
                            "backgroundColor": "#FFFFFF"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "吃啥選單",
                                    "weight": "bold",
                                    "size": "xl",
                                    "margin": "md"
                                },
                                {
                                    "type": "text",
                                    "text": "欸你肚子餓就來一點",
                                    "margin": "md"
                                }
                            ],
                            "action": {
                                "type": "uri",
                                "label": "View detail",
                                "uri": "http://linecorp.com/",
                                "altUri": {
                                    "desktop": "http://example.com/page/123"
                                }
                            }
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "早餐吃得飽",
                                        "text": "早餐吃什麼"
                                    },
                                    "height": "sm"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "午餐吃得好",
                                        "text": "午餐吃什麼"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "飲料喝什麼",
                                        "text": "飲料喝什麼"
                                    }
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "晚餐吃到飽",
                                        "text": "晚餐吃什麼"
                                    },
                                    "height": "sm"
                                }
                                
                            ],
                            "flex": 0
                        },
                        "styles": {
                            "footer": {
                                "separator": True
                            }
                        }
                    }
                ]
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
