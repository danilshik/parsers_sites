import requests
import pprint
import parse_helper as ph
import random
import time
headers = {'User-Agent': 'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)'}
def prodoctorov_ru(id, type, url_page):
    """

    :param id: ID у больницы можно взять в ссылке, например https://prodoctorov.ru/moskva/lpu/9155-klinika-sovremennoy-mediciny/otzivi/, Id =9155; для докторов Id не трубуется
    :param type: тип
    :param url_page: страница
    :return:
    """

    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    proxy = ph.get_proxy_http()
    items_list = []
    if type is "doctor":

        r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content
        html = ph.get_html(r, 'html.parser')
        items = html.select('tr[itemprop="review"]')
        for item in items:
            items_list.append(item)
        print("Количество:", len(items))

    elif type is "clinic":
        #Получение первых 20 отзывов
        r = requests.request("GET", url_page, proxies=proxy[0], auth=proxy[1]).content
        html = ph.get_html(r, 'html.parser')
        items = html.select('table.rates > tr')
        print("Количество:", len(items))
        for item in items:
            items_list.append(item)


        page = 1
        while True:
            random_number = random.randint(3, 10)
            time.sleep(random_number)
            url_request = "https://prodoctorov.ru/ajax/lpu/" + str(id) + "/doctors_rates/?page=" +str(page)
            r = requests.request("GET", url_request, proxies=proxy[0], auth=proxy[1]).content
            html = ph.get_html(r, 'html.parser')
            items = html.select('table.rates > tr')
            print("Количество:", len(items))
            if(len(items) == 0):
                break
            else:
                for item in items:
                    items_list.append(item)
            page +=1

    print(len(items_list))
    for item in items_list:

        date = item.select_one("div.datetime").get("content")
        try:
            author_name = item.select_one('div[itemprop="author"]').text.strip()
        except:
            author_name = item.select_one("div.patient_mobile").text.strip()

        emotion_text = item.get("class")
        for em_text in emotion_text:
            if em_text =="positive_rate":
                emotion = "positive"
                count_positive_comments += 1
                break
            elif em_text == "neutral_rate":
                emotion = "neutral"
                count_neitral_comments += 1
                break
            elif em_text == "negative_rate":
                emotion = "negative"
                count_negative_comments += 1
                break
        response_block = item.select_one("div.moder")
        if response_block is None:
            response = "no"
        else:
            response = "yes"
        try:
            text_comment2 = item.select_one("p.comment2").text.strip() + " "
        except:
            text_comment2 = ""
        try:
            text_comment = item.select_one("p.comment").text.strip() + " "
        except:
            text_comment = ""

        try:
            text_plus = "Плюсы: " + item.select_one("p.comment_plus").text.strip() + " "
        except:
            text_plus = ""

        try:
            text_minus = "Минусы :" + item.select_one("p.comment_minus").text.strip() + " "
        except:
            text_minus = ""

        text = ph.clear_specials_symbols(text_plus + text_minus + text_comment + text_comment2)

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
    # return main_dict



if __name__ == '__main__':
    prodoctorov_ru(None, "clinic","https://prodoctorov.ru/moskva/lpu/21042-hospis-2/")
    # prodoctorov_ru(9155, "clinic","https://prodoctorov.ru/moskva/lpu/9155-klinika-sovremennoy-mediciny/otzivi/")