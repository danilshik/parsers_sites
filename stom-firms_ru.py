import requests
import pprint
import parse_helper as ph
import random
import time
from urllib.parse import urljoin


url_site = "https://msk.stom-firms.ru/"

def stom_firms_ru(firm_id, branch_id):
    """

    :param firm_id: Идентификатор больницы, можно взять в большинстве ссылок, например /clinics.php?i=3063&open=photos   id = 3063
    :param branch_id: Идентификатор филиала для получения отзывов только по филиалу, Id можно найти в фильтрах, например <option value="138"></option> id = 138
    :return:
    """
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    page = 1
    while True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Host': 'www.stom-firms.ru',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.stom-firms.ru/clinics.php?i=' + str(firm_id) + '&page=' + str(page),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }


        url_test = "https://msk.stom-firms.ru/p_firmFeedbacks_feedbacksList_items_view"
        proxy = ph.get_proxy_http()
        if branch_id is not None:
            data_post ={
                'page': page,
                'limit' : '20',
                'addGroupPositive': firm_id,
                # 'addGroupPositiveFirmId': firm_id,
                'distrust[]' : ['affiliated', 'ip', 'contacts', 'rude', 'spam', 'constructive', 'non_feedback', 'client_doesnt_exist', 'resolved'],
                'groupId' : firm_id,
                'firmId' : branch_id

            }
        else:
            data_post = {
                'page' : page,
                'limit': '20',
                'addGroupPositive': firm_id,
                # 'addGroupPositiveFirmId': firm_id,
                'distrust[]': ['affiliated', 'ip', 'contacts', 'rude', 'spam', 'constructive', 'non_feedback',
                               'client_doesnt_exist', 'resolved'],
                'groupId' : firm_id


            }
        r = requests.post(url_test, data=data_post, proxies=proxy[0], auth=proxy[1], headers=headers).json()
        print(r)
        html_json = r["html"]
        html = ph.get_html(html_json, 'html.parser')
        print("Pagination:", str(page), url_test)
        items = html.select("div.feedback-item")
        if len(items) == 0:
            break
        for index, item in enumerate(items):
            date = item.select_one("span.metadata-date").text.strip().split(" ")[0]
            date_block = date.split(".")
            day = date_block[0]
            month = date_block[1]
            year = date_block[2]
            date = year + "-" + month + "-" + day

            author_name = item.select_one("div.feedback-wrapper > a").get("alt")
            # try:
            #     emotion_text = float(item.select_one("span.company-reviews-list-item-firstline-rating-stars.rating-autostars").get("data-rating"))
            #     if (emotion_text >= 4.5):
            #         emotion = "positive"
            #         count_positive_comments += 1
            #
            #     elif (emotion_text <= 2):
            #         emotion = "negative"
            #         count_negative_comments += 1
            #     else:
            #         emotion = "neutral"
            #         count_neitral_comments += 1
            # except:
            emotion = None
            response_block = item.select_one("div.feedback-answer.text-data.feedback-firmAnswer> div.answer-text").text.strip()
            print(response_block)
            if response_block =="":
                response = "no"
            else:
                response = "yes"
            text = ph.clear_specials_symbols(item.select_one("div.text").text.strip())

            url = urljoin(url_site, item.select_one('a.avatar').get("href"))
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
        page += 1

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
    # stom_firms_ru(683, None)
    # stom_firms_ru(683, 913)
    stom_firms_ru(9941, None)