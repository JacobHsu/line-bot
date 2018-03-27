import requests
from bs4 import BeautifulSoup
import datetime

def truemovie():
    target_url = 'http://www.truemovie.com/tairelease.htm'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'Big5'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""

    today = datetime.datetime.now()
    tableid= int(today.month) +115
    week = int( int(today.day) /5 ) -1

    for index, data in enumerate(soup.select('#table'+str(tableid)+' td a')):
        movie = data.text.replace('\n', '').replace('\u3000', '').replace(" ", "").replace('\t', '').replace('\r', '')                            
        if(index%5 == week): 
           title = movie
           link = "http://www.truemovie.com/" + data['href']
           content += '{}\n{}\n'.format(title, link)
    return content
    
def atmovies():
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