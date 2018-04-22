import requests
from bs4 import BeautifulSoup

def books():
	target_url = 'http://www.books.com.tw/web/ebook/?loc=menu_0_001'
	rs = requests.session()
	res = rs.get(target_url, verify=False)
	soup = BeautifulSoup(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('.mod_b.type02_l006 a'), 0):
	    if index == 1:
	        title = data.text
	        link = data['href']
	        content += '博客來66元: {}\n{}\n'.format(title, link)
	        return content
	return content

def kobo():
	target_url = 'https://www.kobo.com/tw/zh'
	rs = requests.session()
	res = rs.get(target_url, verify=False)
	soup = BeautifulSoup(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('#99 a img'), 0):
		title = data['title']
		link = target_url
		content += '樂天今日99: {}\n{}\n'.format(title, link)
		return content
	return content

def taaze():
	target_url = 'https://www.taaze.tw/container.html?t=14&k=01&d=00'
	rs = requests.session()
	res = rs.get(target_url, verify=False)
	soup = BeautifulSoup(res.text, 'html.parser')
	content = ""
	for index, data in enumerate(soup.select('.linkA a'), 0):
	    if index == 0:
	        title = data.text
	        link = data['href']
	        content += '讀冊5折: {}\n{}\n'.format(title, link)
	        return content
	return content