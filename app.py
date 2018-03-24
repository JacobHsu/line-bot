from flask import Flask, request, abort
import configparser
import requests
import json
from bs4 import BeautifulSoup
import maps
import movie

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage,
)

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def apple_news():
    target_url = 'http://www.appledaily.com.tw/realtimenews/section/new/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rtddt a'), 0):
        if index == 3:
            return content

        link = data['href']
        content += '{}\n\n'.format(link)
    return content

def ptt_hot():
    target_url = 'http://disp.cc/b/PttHot'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('#list div.row2 div span.listTitle')):
        if index <= 13:
            continue
        title = data.text
        link = "http://disp.cc/b/" + data.find('a')['href']
        if data.find('a')['href'] == "796-59l9": #[公告]
            break
        content += '{}\n{}\n\n'.format(title, link)
    return content

def currencylayer():
    target_url = 'http://apilayer.net/api/live?access_key='+config['currencylayer']['Access_Key']+'&currencies=TWD,JPY,CNY'
    response = requests.get(target_url)
    data = response.text
    parsed = json.loads(data)
    rates = parsed['quotes']
    content = ""
    for currency, rate in rates.items():
        content += currency+"="+str(rate)+"\n"
    return content[:-1]

def currency():
    target_url = 'http://rate.bot.com.tw/Pages/Static/UIP003.zh-TW.htm'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rate-content-sight.text-right.print_hide')):
        if index == 1: 
            content += '美金(USD)'+data.text+"\n"
            print('美金(USD)' , data.text)
        elif index == 15:
            content += '日圓(JPY)'+data.text+"\n"
            print('日圓(JPY)' , data.text)
        elif index == 37:
            content += '人民幣(CNY)'+data.text
            print('人民幣(CNY)' , data.text)
    return content

def pm25():
    target_url = 'http://opendata2.epa.gov.tw/AQX.json'
    response = requests.get(target_url)
    data = response.text
    results = json.loads(data)
    content = results[3]['SiteName'] + ' PM2.5: '+ results[3]['PM2.5'] + ',狀態: ' + results[3]['Status']
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if event.message.text == "蘋果即時新聞":
        content = apple_news()
    elif event.message.text == "近期熱門廢文":  
        content = ptt_hot()  
    elif event.message.text == "本週新片":  
        content = movie.truemovie()
    elif event.message.text == "開演":  
        content = movie.atmovies()
    elif event.message.text == "今日即期匯率":  
        content = currency()
    elif event.message.text == "吃什麼":  
        content = maps.randombysearch()
    elif( len(event.message.text) == 4 and event.message.text.isdigit() ):
        content = 'https://goodinfo.tw/StockInfo/StockDividendSchedule.asp?STOCK_ID='+ event.message.text
    elif( len(event.message.text) == 2 and event.message.text.isdigit() ):
        content = ''
    elif event.message.text == "USD":  
        content = currencylayer()
    elif event.message.text == "空氣":  
        content = pm25()      
    else:
        content =  event.message.text + ' by bot'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=content))


@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    lat = event.message.latitude
    lng = event.message.longitude
    content = maps.nearbysearch(lat,lng) 
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=content))

if __name__ == "__main__":
    app.run()