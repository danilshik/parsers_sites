
import requests
import pprint
import json
import parse_helper as ph

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}


def parser(id, type, url_page):
    """

    :param id: id специалиста или организации. Можно взять в элементе div с классом star-rating-svg в параметре data-org-id
    :param type: или doctor или clinic
    :param url_page страница,
    :return:
    """

    is_last = False
    # Cчетчики
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    count = 0
    comment_list = []
    comment_id_list = []

    if id is None:
        raise Exception("Не указан id")


    if type is "clinic":
        item_name = "org"
    elif type is "doctor":
        item_name = "specialist"
    else:
        raise Exception("Указан неправильный type")

    while is_last != True:
        proxy = ph.get_proxy()
        params = {'last_ids[]': comment_id_list}
        r = requests.request("GET", "https://www.kleos.ru/comment/0/operation?mode=getlist&item_id=" + str(id) + "&item_name=" + item_name + "&comment_cnt=1000000",
                             headers=headers, params=params, proxies=proxy[0], auth=proxy[1]).content
        html = ph.get_html(r, 'lxml')
        json_text = json.loads(html.select_one("p").text)
        html_json = ph.get_html(json_text["html"], 'lxml')
        if(json_text["is_last"] == True):
            is_last = True
        items = html_json.select("body > div.comment-item")
        print("Количество отзывов:", len(items))
        for item in items:
            count += 1
            subcomments = item.select("div.comment-item")
            if(len(subcomments) > 0):
                response = "yes"
            else:
                response = "no"
            comment_id = item.get("data-id")
            comment_id_list.append(comment_id)
            left_block = item.select_one("div.left-content > div")
            spans = left_block.select("span")

            date = spans[0].text.strip().replace(".", "-")

            author_name = spans[1].text.strip()

            try:
                emotion_text = float(left_block.select_one("div.star-rating-svg").get("data-initial-rating"))
                if(emotion_text >= 4.5):
                    emotion = "positive"
                    count_positive_comments += 1

                elif(emotion_text <= 2):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except:
                emotion = None

            text = item.select_one("div.comment-text.padding-coment").text.strip()


            comment = {
                'author_name': author_name,
                'date': date,
                'emotion': emotion,
                'text': text,
                'response': response,
                'url': url_page
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

    pprint.pprint(main_dict)
    return main_dict




if __name__ == '__main__':
    parser(7493, "clinic", "url")