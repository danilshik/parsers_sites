import requests
import pprint
import parse_helper as ph
import random
import time


def mydentist_ru(url_page):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
    }
    proxy = ph.get_proxy_http()
    r = requests.get(url_page, headers=headers, proxies=proxy[0], auth=proxy[1]).content
    html = ph.get_html(r, 'lxml')
    items = html.select("div.ci_reviews_list > ul > li")
    print(len(items))
    for index, item in enumerate(items):
        date_block = item.select_one("div.ci_review_datatime").text.strip().split(".")
        day = date_block[0]
        month = date_block[1]
        year = "20" + date_block[2]
        date = year + "-" + month + "-" + day
    #
        author_name = item.select_one("div.ci_review_owner_name").text.strip()

        emotion_text = float(item.select_one("div.ci_review_rating_mark").text.strip())
        if (emotion_text >= 4):
            emotion = "positive"
            count_positive_comments += 1

        elif (emotion_text < 3):
            emotion = "negative"
            count_negative_comments += 1
        else:
            emotion = "neutral"
            count_neitral_comments += 1
    #         # # print(item)
    #         response_block = item.select_one("div.feedback-answer.text-data.feedback-firmAnswer ")
    #         # print(response_block)
    #         if response_block is None:
    #             response = "no"
    #         else:
    #             response = "yes"
        response = "no"
        text = ph.clear_specials_symbols(item.select_one("div.ci_review_content").text.strip())
    #
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
    #
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
    # mydentist_ru("https://mydentist.ru/msk/clinic/38269/")
    mydentist_ru("https://mydentist.ru/msk/doctor/35077/")