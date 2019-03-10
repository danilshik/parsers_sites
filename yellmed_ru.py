import requests
import pprint
import parse_helper as ph

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0'}


def yellmed_ru(url_page):
    """

    :param url_page: url больницы или врача
    :return:
    """
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    proxy = ph.get_proxy_http()
    r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content
    html = ph.get_html(r, 'lxml')
    if url_page.find("vrachi") != -1:
        type = "doctor"
    else:
        type = "clinic"
    if(type is "clinic"):
        items = html.select("div.comment")
        for item in items:
            count += 1
            try:
                date = item.select_one("div.comment__date").text.strip()
                date_block = date.split(" ")
                day = date_block[0]
                month = ph.MonthRefactor(date_block[1])
                year = date_block[2]
                date = year + "-" + month + "-" + day
            except:
                date = None

            author_name = item.select_one("div.comment__author-name").text.strip()
            try:
                emotion_text = float(item.select_one("div.rating").get("data-rating"))
                if (emotion_text >= 4):
                    emotion = "positive"
                    count_positive_comments += 1

                elif (emotion_text < 3):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except Exception as e:
                emotion = None
                print(e)
            # # print(item)
            # response_block = item.select_one("div.replies__item-text")
            # # print(response_block)
            # if response_block is None:
            #     response = "no"
            # else:
            #     response = "yes"
            #
            response = "no"
            text = ph.clear_specials_symbols(item.select_one("div.comment__text").text.strip())
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
    elif(type is "doctor"):

        items = html.select("div.doctor-reviews > div.doctor-reviews__item")
        for item in items:
            count += 1
            try:
                date = item.select_one("div.doctor-reviews__publ-time").text.strip()
                date_block = date.split(" ")
                day = date_block[0]
                month = ph.MonthRefactor(date_block[1])
                year = date_block[2]
                date = year + "-" + month + "-" + day
            except:
                date = None
            # print(item)
            author_name = item.select_one('span[itemprop="name"]').text.strip()
            try:
                emotion_text = float(item.select_one("div.rating").get("data-rating"))
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
            # # print(item)
            # response_block = item.select_one("div.replies__item-text")
            # # print(response_block)
            # if response_block is None:
            #     response = "no"
            # else:
            #     response = "yes"
            #
            response = "no"
            text = item.select_one("blockquote.doctor-reviews__review-text").text.strip()
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
    yellmed_ru("https://yellmed.ru/medicinskie-centry/klinika-k-31")
    # yellmed_ru("https://yellmed.ru/vrachi/Kremnev_Uriy")
    # yellmed_ru("https://yellmed.ru/vrachi/Goludeva_Galina")