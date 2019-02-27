import requests
import pprint
import parse_helper as ph
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}


def parser(url_page):
    """
    Парсинг производится по HTML.
    :param url_page: ссылка на страницу или клинику
    :return:
    """
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    count = 0

    comment_list = []
    proxy = ph.get_proxy()
    r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content
    html = ph.get_html(r)
    items = html.select("ul.doc-main__feedbacks__list > li")
    for item in items:
        count += 1
        date = item.select_one("div.doc-main__feedbacks__item-date").text.strip()
        date_block = date.split(" ")
        day = date_block[0]
        month = ph.MonthRefactor(date_block[1])
        year = date_block[2]
        date = year + "-" + month + "-" + day

        author_name = item.select_one("a.permalink").text.strip()

        try:
            emotion_text = float(item.select_one("div.best__c-b-r-count.value").text.strip())
            if (emotion_text >= 4.5):
                emotion = "positive"
                count_positive_comments += 1

            elif (emotion_text <= 2):
                emotion = "negative"
                count_negative_comments += 1
            else:
                emotion = "neutral"
                count_neitral_comments += 1
        except Exception as e:
            emotion = None
            print(e)
        try:
            subcomments = html.select_one("div.comment-box")
            response = "yes"
        except:
            response = "no"

        text = item.select_one("div.doc-main__feedbacks__item-text.description").text.strip()
        url = url_page

        comment = {
            'author_name': author_name,
            'date': date,
            'emotion': emotion,
            'text': text,
            'response': response,
            'url': url
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
    parser("https://www.startsmile.ru/stomatologi/akhtanin_aleksandr_pavlovich.html")