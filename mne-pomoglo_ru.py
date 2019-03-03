import requests
import pprint
import parse_helper as ph

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
}


def parser(url_page):
    """

    :param url_page: url больницы
    :return:
    """
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []

    is_pagination = True

    last = None
    page = 1
    while is_pagination:
        proxy = ph.get_proxy()
        r = requests.request("GET", url_page + "?page=" + str(page), proxies=proxy[0], auth=proxy[1]).content
        html = ph.get_html(r, 'html.parser')
        print("Pagination:", str(page))
        # if url_page.find("vrachi"):
        #     type = "doctor"
        # else:
        #     type = "clinic"
        # if(type is "clinic"):
        items = html.select("div.company-reviews-list-item ")
        for index, item in enumerate(items):


            date = item.select_one("div.company-reviews-list-item-date").text.strip().split("\t")[-1]
            print(date)
            date_block = date.split(".")
            day = date_block[0]
            month = date_block[1]
            year = "20" + date_block[2]
            date = year + "-" + month + "-" + day

            author_name = item.select_one("div.company-reviews-list-item-name").text.strip()
            try:
                emotion_text = float(item.select_one("span.company-reviews-list-item-firstline-rating-stars.rating-autostars").get("data-rating"))
                if (emotion_text >= 4.5):
                    emotion = "positive"
                    count_positive_comments += 1

                elif (emotion_text <= 2):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except:
                emotion = None
            # # print(item)
            response_block = item.select_one("div.company-reviews-list-item-full-link")
            # print(response_block)
            if response_block is None:
                response = "no"
            else:
                response = "yes"
            text = item.select_one("div.company-reviews-list-item-text-message").text.strip()

            #Конструкция для проверки первого сообщений на предудщей страницы с этой
            if index == 0:
                if text == last:
                    is_pagination = False
                    break
                else:
                    last = text

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
    parser("http://mne-pomoglo.ru/invitro-medicinskiy-centr")