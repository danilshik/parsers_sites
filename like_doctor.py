import requests
import pprint
import parse_helper as ph
import random
import time


url_site = "https://msk.stom-firms.ru/"

def like_doctor_ru(firm_id):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    page = 0
    while True:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Referer': 'https://www.stom-firms.ru/clinics.php?i=' + str(firm_id) + '&page=' + str(page),
            'X-Requested-With': 'XMLHttpRequest'
        }


        url_test = "https://like.doctor/service/more-posts"
        proxy = ph.get_proxy_http()
        data_post ={
            'nextpage': page,
            'perpage': 10,
            'data[clinic_id][]':firm_id
        }
        json = requests.post(url_test, data=data_post, headers=headers, proxies=proxy[0], auth=proxy[1])
        print(json)
        break
        # html_json = r["html"]
        # html = ph.get_html(html_json, 'html.parser')
        # # print(html_json)
        # print("Pagination:", str(page), url_test)
        # # if url_page.find("vrachi"):
        # #     type = "doctor"
        # # else:
        # #     type = "clinic"
        # # if(type is "clinic"):
        # items = html.select("div.feedback-item")
        # if len(items) == 0:
        #     break
    #     for index, item in enumerate(items):
    #         date = item.select_one("span.metadata-date").text.strip().split(" ")[0]
    #         date_block = date.split(".")
    #         day = date_block[0]
    #         month = date_block[1]
    #         year = date_block[2]
    #         date = year + "-" + month + "-" + day
    #
    #         author_name = item.select_one("div.feedback-wrapper > a").get("alt")
    #         # try:
    #         #     emotion_text = float(item.select_one("span.company-reviews-list-item-firstline-rating-stars.rating-autostars").get("data-rating"))
    #         #     if (emotion_text >= 4.5):
    #         #         emotion = "positive"
    #         #         count_positive_comments += 1
    #         #
    #         #     elif (emotion_text <= 2):
    #         #         emotion = "negative"
    #         #         count_negative_comments += 1
    #         #     else:
    #         #         emotion = "neutral"
    #         #         count_neitral_comments += 1
    #         # except:
    #         emotion = None
    #         # # print(item)
    #         response_block = item.select_one("div.feedback-answer.text-data.feedback-firmAnswer ")
    #         # print(response_block)
    #         if response_block is None:
    #             response = "no"
    #         else:
    #             response = "yes"
    #         text = ph.clear_specials_symbols(item.select_one("div.text").text.strip())
    #
    #         url = urljoin(url_site, item.select_one('a.avatar').get("href"))
    #         comment = {
    #             'author_name': author_name,
    #             'date': date,
    #             'emotion': emotion,
    #             'text': text,
    #             'response': response,
    #             'url': url,
    #             'hash': ph.get_md5_hash(author_name + date + text)
    #         }
    #         print(comment)
    #         count += 1
    #         comment_list.append(comment)
    #     page += 1
    #
    # statistic = {
    #     'count': count,
    #     'positive': count_positive_comments,
    #     'negative': count_negative_comments,
    #     'neutral': count_neitral_comments
    # }
    # main_dict = {
    #     'statistic': statistic,
    #     'comments': comment_list
    # }
    #
    # pprint.pprint(main_dict)
    # return main_dict



if __name__ == '__main__':
    like_doctor_ru(7241)