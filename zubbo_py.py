import requests
import pprint
import parse_helper as ph
import random
import time
from urllib.parse import urljoin
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
        }

url_site = "https://msk.stom-firms.ru/"

def zubbo_ru(url_page):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []

    proxy = ph.get_proxy_https()
    r = requests.get(url_page, proxies=proxy[0], auth=proxy[1], headers=headers).content
    html = ph.get_html(r, 'html.parser')

    items = html.select("div.fos_comment_thread_comments > div")
    for index, item in enumerate(items):
        date = item.select_one("div.metadata").text.strip()
        index = date.find(",")
        date = date[index:].split(" ")
        day = date[1]
        if len(day) == 1:
            day = "0" + day
        month = ph.MonthRefactor(date[2][:-1])
        year = "2018"
        date = year + "-" + month + "-" + day

        author_name = item.select_one("strong.author_name").text.strip()
        emotion = None
        text = ph.clear_specials_symbols(item.select_one("div.fos_comment_comment_body").text.strip())
        response_block = item.select_one("div.fos_comment_comment_replies > div")
        if response_block is None:
            response = "no"
        else:
            response = "yes"

        url = url_page
        comment = {
            'author_name': author_name,
            'date': date,
            'emotion': emotion,
            'text': text,
            'response': response,
            'url': url,
            'hash': ph.get_md5_hash(author_name + date + text)
        }
        print(comment)
        count += 1
        comment_list.append(comment)

    statistic = {
        'count': count,
        'positive': count_positive_comments,
        'negative': count_negative_comments,
        'neutral': count_neitral_comments
    }
    main_dict = {
        'statistic': statistic,
        'comments': comment_list
    }

    pprint.pprint(main_dict)
    return main_dict



if __name__ == '__main__':
    zubbo_ru("http://zubbo.ru/moskva/stomatologii/stomatologija-diamed-m-schelkovskaja--532")