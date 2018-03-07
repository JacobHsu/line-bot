from flask import Flask, request, abort
import configparser
import requests
import json
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



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "蘋果即時新聞":
        content = apple_news()
    elif event.message.text == "近期熱門廢文":  
        content = ptt_hot()  
    elif event.message.text == "近期上映電影":  
        content = movie()
    elif event.message.text == "今日匯率":  
        content = currencylayer()        
    else:
        content = event.message.text + ' by bot'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=content))


if __name__ == "__main__":
    app.run()