import configparser
import requests
from bs4 import BeautifulSoup
import json
import random

config = configparser.ConfigParser()
config.read("config.ini")

def randombysearch():
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
        return "請重新搜尋"
    content = "傳送位置資訊\n可以得到更精準的推薦喔 􀀅 \n"
    for index, data in enumerate(restaurant): 
        if index < 5:
            name = data['name'].replace(" ",'%20')
            print(name)
            content += 'https://www.google.com.tw/search?q='+str(name)+"\n"
    return content[:-1]

def nearbysearch(lat,lng):
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