from bs4 import BeautifulSoup
import requests
import pprint
from datetime import *
import parse_helper as ph

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
           'X-Requested-With': 'XMLHttpRequest'}

def parser(url_main, id):
    """

    :param url_main: Ссылка на страницу
    :param id: идентификатор больницы или доктора, в случае значения None, определяется по html-странице
    :return:
    """
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    count = 0
    comment_list = []

    if id is None:
        r = requests.request("GET", url_main).content
        html = ph.get_html(r)
        id = html.select_one("div.comments-section.service-feedbacks.service-box-white.js-togglable-content.js-reviews-module.js-corpservice-block").get("data-owner-id")

    url_page = "https://spb.zoon.ru/js.php?area=service&action=CommentList&owner[]=organization&owner[]=prof&organization=" + id + "&limit=10000"
    json = requests.request("GET", url_page).json()
    print(json)
    html = ph.get_html(json["list"])
    print(html)

    items = html.select('body > li')
    print(len(items))
    for item in items:
        count += 1

        block_data_emotion = item.select_one('span.gray')

        date = block_data_emotion.text.split("\n")[-1].strip()
        date_block = date.split(" ")
        day = date_block[0]
        if(len(day) == 1):
            day = "0" + day
        month = ph.MonthRefactor(date_block[1])
        if(date_block[2].isdigit()):
            year = date_block[2]
        else:
            year = str(datetime.now().year)

        date = year + "-" + month + "-" + day

        author_name = item.get("data-author")

        try:
            emotion_text = block_data_emotion.select('span.star-item > span[style="width: 100%; display: block;"]')
            if(len(emotion_text) == 0):
                emotion = None
            elif (len(emotion_text) >= 4.5):
                emotion = "positive"
                count_positive_comments += 1

            elif((len(emotion_text) <= 2) and (len(emotion_text) != 0)):
                emotion = "negative"
                count_negative_comments += 1
            else:
                emotion = "neutral"
                count_neitral_comments += 1
        except Exception as e:
            emotion = None
            print(e)
        response_block = item.select_one("ul.list-reset.subcomments > li")
        if response_block is None:
            response = "no"
        else:
            response = "yes"

        text = item.select_one("div.js-comment-short-text").text.strip()
        text = text.replace("\xa0", " ")

        comment = {
            'author_name': author_name,
            'date': date,
            'emotion': emotion,
            'text': text,
            'response': response,
            'url': url_main
        }
        print(comment)
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

    # pprint.pprint(main_dict)
    return main_dict



if __name__ == '__main__':
    # parser("https://spb.zoon.ru/medical/stomatologiya_stellit_na_ulitse_lyoni_golikova/?zutm_source=zbd&zutm_medium=none", "503c4c343c72dd7d70000024")
    parser("https://spb.zoon.ru/medical/klinika_kosmetologii_i_stomatologii_mediestetik_comfort_na_leninskom_prospekte/", "50230d843c72dd4077000000")