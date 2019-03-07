import requests
import pprint
import parse_helper as ph
import re
import json
import random
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}


def spr_ru(id):
    """

    :param id: id больницы, можно взять из ссылки у сетей и В кнопке оставить отзыв в методе onclick
    у одиночных поликлиник, например document.location.href='//www.spr.ru/forum_adding.php?id_top=11&id_firm_forum=107473'
    id = 107473
    :return:
    """

    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    proxy = ph.get_proxy_http()
    type_comments = ["positive" , "negative"]
    for type_comment in type_comments:
        page_count = 0
        while True:
            url_page = "https://www.spr.ru/js/zzz_next.php?id_top=11&id_firm=" + str(id) + "&view11=" + str(page_count)
            if type_comment == "positive":
                id_top = "&id_top=11"
            elif type_comment == "negative":
                id_top = "&id_top=1"
            url_page = url_page + id_top
            random_number = random.randint(1, 3)
            time.sleep(random_number)
            r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content

            #Разбор вручную
            r_text = re.search(r'".*"', str(r, "windows-1251")).group(0)
            r_text = r_text[1:-1] #"Отсекание кавычек"
            r_text = r_text.replace('\\', '')
            r_text = r_text.replace('&lt;', '<')
            r_text = r_text.replace('&gt;', '>')
            r_text = r_text.replace('&quot;', '"')
            html = ph.get_html(r_text, 'lxml')

            href_list = []
            a_list = html.select("a.zagolovok")
            if len(a_list) == 0:
                break
            for a in a_list:
                href = "https:" + a.get("href")
                href_list.append(href)
                print("Ссылка на отзыв:", href)
            for href in href_list:
                random_number = random.randint(1, 4)
                time.sleep(random_number)
                r = requests.get(href, proxies=proxy[0], auth=proxy[1]).content
                html_comment = ph.get_html(r,  "html.parser")
                img = html_comment.select_one("#leftside > img")
                emotion_text = img.get("title")
                if emotion_text == "Это положительный отзыв":
                    emotion = "positive"
                    count_positive_comments += 1
                elif emotion_text == "Это отрицательный отзыв":
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = " neutral"
                    count_neitral_comments += 1

                text = html_comment.select_one("#leftside > span").text.strip()
                response_text = html_comment.select_one('#leftside > table[style="width:100%;"]')
                if response_text is None:
                    response = "no"
                else:
                    response = "yes"


                try:
                    date = html_comment.select_one('#leftside > table > tr > td > div.archive > nobr > span').text.strip().split(" ")[0]
                    date_block = date.split("-")
                    day = date_block[2]
                    month = date_block[1]
                    year = date_block[0]
                    date = year + "-" + month + "-" + day
                except:
                    date = None

                author_name = html_comment.select_one('#leftside > span[style = "font-weight:bold;"]').text.strip()

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
                comment_list.append(comment)
                count += 1
            page_count += 20
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
    #
    pprint.pprint(main_dict)
    return main_dict




if __name__ == '__main__':
    spr_ru(107473)