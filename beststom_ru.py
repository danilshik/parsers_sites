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

def beststom_ru(url_page, type):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    url_test = url_page + "otzyvy/"
    if type is "doctor":
        url_test = url_page
    page = 0
    is_no_first = None
    url_new = None
    while True:
        if(is_no_first):
            url_new = url_test + "?p=" + str(page)
        else:
            url_new = url_test
        is_no_first = True
        proxy = ph.get_proxy_http()
        r = requests.get(url_new, proxies=proxy[0], auth=proxy[1], headers=headers).content
        html = ph.get_html(r, 'html.parser')
        page += 1
        items = html.select("div.b-comments-list > div")
        if len(items) == 0:
            break
        print(len(items))

        for index, item in enumerate(items):
            try:
                date_block = item.select_one("div.b-date").text.strip()
                date = date_block.split(".")
                day = date[0]
                month = date[1]
                year = date[2]
                date = year + "-" + month + "-" + day
            except:
                date = None

            author_name = item.select_one("div.b-name").text.strip()
            emotion_block = item.get("class")[1]
            if emotion_block.find("positive")!= -1:
                emotion = "positive"
                count_positive_comments += 1
            elif emotion_block.find("negative")!= -1:
                emotion = "negative"
                count_negative_comments += 1
            elif emotion_block.find("neutral")!= -1:
                emotion = "neutral"
                count_neitral_comments += 1
            text = ph.clear_specials_symbols(item.select_one("div.b-comment-txt > p").text.strip())
            # response_block = item.select_one("div.fos_comment_comment_replies > div")
            # if response_block is None:
            #     response = "no"
            # else:
            #     response = "yes"

            response = None
            if date is None:
                hash = ph.get_md5_hash(author_name + text)
            else:
                hash = ph.get_md5_hash(author_name + date + text)
            url = url_page
            comment = {
                'author_name': author_name,
                'date': date,
                'emotion': emotion,
                'text': text,
                'response': response,
                'url': url,
                'hash': hash
            }
            print(comment)
            count += 1
            comment_list.append(comment)
        if type is "doctor":
            break
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
    # beststom_ru("https://msk.beststom.ru/stomatologi/gorbunov_andrey_2/", "doctor")
    beststom_ru("https://msk.beststom.ru/clinics/detskaja_stomatologija_dental_fentezi_home_m_vdnh/", "clinic")
    # beststom_ru("https://msk.beststom.ru/clinics/sovremennyj_stomatologicheskij_kompleks_akademika_anohina_9/", "clinic")