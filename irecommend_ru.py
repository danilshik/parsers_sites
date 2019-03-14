import requests
import pprint
import parse_helper as ph
from urllib.parse import urljoin


url_site = "https://irecommend.ru"

def irecomment_ru(url_page):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
    }
    cookie = {
        'ss_uid':'15525040324004156'

    }
    proxy = ph.get_proxy_http()
    r = requests.get(url_page, headers=headers, proxies=proxy[0], auth=proxy[1], cookies=cookie).content
    html = ph.get_html(r, 'html.parser')
    a_list = html.select("a.more")
    for a in a_list:
        href = urljoin(url_site, a.get("href"))

        r = requests.get(href, headers=headers, proxies=proxy[0], auth=proxy[1], cookies=cookie).content
        html_new = ph.get_html(r, 'html.parser')
        date_block = html_new.select_one("span.dtreviewed").text.strip().split(" ")
        day = date_block[0]
        if len(day) == 1:
            day = "0" + day
        month = ph.MonthRefactor(date_block[1])
        year = date_block[2]
        date = year + "-" + month + "-" + day
        author_name = html_new.select_one("strong.reviewer > a").text.strip()
        emotion_text = float(html_new.select_one('meta[itemprop="ratingValue"]').get("content"))
        if (emotion_text >= 4):
            emotion = "positive"
            count_positive_comments += 1

        elif (emotion_text < 3):
            emotion = "negative"
            count_negative_comments += 1
        else:
            emotion = "neutral"
            count_neitral_comments += 1
        response_block = html_new.select_one("div.cmntreply-items > div")
        if response_block is None:
            response = "no"
        else:
            response = "yes"
        text = ph.clear_specials_symbols(html_new.select_one("div.description.hasinlineimage").text.strip())
        comment = {
            'author_name': author_name,
            'date': date,
            'emotion': emotion,
            'text': text,
            'response': response,
            'url': href,
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
    irecomment_ru("https://irecommend.ru/content/tsentr-ortodontii-ulybnis-malekseevskaya-moskva")