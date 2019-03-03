import requests
import pprint
import parse_helper as ph

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
}


def parser(url_main):
    """

    :param url_page: url больницы
    :return:
    """
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    page = 2
    url_page = url_main
    while True:
        proxy = ph.get_proxy_https()
        "http://moszub.ru/clinics/stomatologicheskaya-poliklinika-65/?table=clinics&id=356&cp=1"
        r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content

        html = ph.get_html(r, 'html.parser')

        id = html.select_one("a.clinicorder").get("clinicid")
        url_page = url_main + "?table=clinics&id=" + id + "&cp=" + str(page)

        # if url_page.find("vrachi"):
        #     type = "doctor"
        # else:
        #     type = "clinic"
        # if(type is "clinic"):
        items = html.select("form.form_validate.form_direct")
        if(len(items) == 0):
            break
        for item in items:
            count += 1
            date = item.select_one("div.commentsdate").text.strip()
            date_block = date.split(".")
            day = date_block[0]
            month = date_block[1]
            year = date_block[2]
            date = year + "-" + month + "-" + day

            author_name = item.select_one("span.commentsguest").text.strip()

            emotion_text = item.select_one("div.avatar > span").get("title")
            if (emotion_text == "Мнение положительное"):
                emotion = "positive"
                count_positive_comments += 1

            elif (emotion_text =="Мнение отрицательное"):
                emotion = "negative"
                count_negative_comments += 1
            # # print(item)
            # response_block = item.select_one("div.replies__item-text")
            # # print(response_block)
            # if response_block is None:
            #     response = "no"
            # else:
            #     response = "yes"
            #
            response = "no"
            text = item.select_one("div.commentstext").text.strip()
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
    # parser("http://moszub.ru/clinics/ortodont-pro/")
    parser("http://moszub.ru/clinics/stomatologicheskaya-poliklinika-65/")