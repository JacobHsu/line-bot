from flask import Flask, request, abort
import configparser
import requests
import json
import random
from bs4 import BeautifulSoup


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
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

def movie():
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('ul.filmNextListAll a')):
        if index == 5:
            return content
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        content += '{}\n{}\n'.format(title, link)
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


def nearbysearch():
    rand = random.random()*0.01
    point  = ("%.6f" % rand)
    lat = int(25) + float(point)
    rand = random.randint(450000,630000)
    print(rand)
    lng = "121." + str(rand)
    print(lat,lng)
    target_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&radius=500&type=restaurant&key='+config['places_api']['YOUR_API_KEY']
    response = requests.get(target_url)
    data = response.text
    parsed = json.loads(data)
    restaurant = parsed['results']
    if restaurant == []:
        print('nearbysearch')
        return str(lat)+","+str(lng)+"請重新搜尋"
    content = ""
    for index, data in enumerate(restaurant): 
        if index < 5:
            name = data['name'].replace(" ",'%20')
            print(name)
            content += 'https://www.google.com.tw/search?q='+str(name)+"\n"
    return content[:-1]

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
    elif event.message.text == "近期上映電影":  
        content = movie()
    elif event.message.text == "今日即期匯率":  
        content = currency()
    elif event.message.text == "吃什麼":  
        content = nearbysearch()
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


if __name__ == "__main__":
    app.run()