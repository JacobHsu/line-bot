import requests
from bs4 import BeautifulSoup

def get_page_number(content):
    #/bbs/Beauty/index{2435}.html
    start_index = content.find('index')
    end_index = content.find('.html')
    page_number = content[start_index + 5: end_index]
    return int(page_number) + 1

def craw_page(res):
    soup_ = BeautifulSoup(res.text, 'html.parser')
    article_seq = []
    for r_ent in soup_.find_all(class_="r-ent"):
        try:
            # 先得到每篇文章的篇url
            link = r_ent.find('a')['href']
            if link:
                # 確定得到url再去抓 標題 以及 推文數
                title = r_ent.find(class_="title").text.strip()
                rate = r_ent.find(class_="nrec").text
                url = 'https://www.ptt.cc' + link
                if rate:
                    rate = 100 if rate.startswith('爆') else rate
                    rate = -1 * int(rate[1]) if rate.startswith('X') else rate
                else:
                    rate = 0
                # 比對推文數
                push_rate = 20  # 推文數
                if int(rate) >= push_rate:
                    article_seq.append({
                        'title': title,
                        'url': url,
                        'rate': rate,
                    })
        except Exception as e:
            print('已被刪除', e)
    return article_seq

def ptt_beauty():
    rs = requests.session()
    res = rs.get('https://www.ptt.cc/bbs/Beauty/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    all_page_url = soup.select('.btn.wide')[1]['href']
    start_page_id = get_page_number(all_page_url)

    index_list = []
    article_list = []
    for page in range(start_page_id, start_page_id - 2, -1):
        page_url = 'https://www.ptt.cc/bbs/Beauty/index{}.html'.format(page) 
        index_list.append(page_url)

    while index_list:
        index = index_list.pop(0)
        print(index)
        res = rs.get(index, verify=False)
        article_list = craw_page(res)

    content = ''
    for article in article_list:
        data = ' {}\n{}\n\n'.format( article.get('title', None), article.get('url', None))
        content += data
 
    return content