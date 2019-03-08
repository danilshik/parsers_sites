import requests
import pprint
import parse_helper as ph

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0'
}

def moscow_stomatologija_su(url_page):
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    proxy = ph.get_proxy_https()
    url_page = url_page + "/otzyvy"
    r = requests.request("GET",url_page, proxies=proxy[0], auth=proxy[1]).content
    html = ph.get_html(r, 'html.parser')
    items = html.select("div.p20 > div.otziv")
    print(len(items))
    for item in items:
        try:
            date = item.select_one("div.clinic_otziv_name > a > span").text.strip().split(" ")[2]
        except AttributeError:
            date = item.select_one("div.clinic_otziv_name > span").text.strip().split(" ")[2]
        date_block = date.split(".")
        day = date_block[0]
        month = date_block[1]
        year = date_block[2]
        date = year + "-" + month + "-" + day
        try:
            author_name = item.select_one('span[itemprop = "author"] > a').text.strip()
        except AttributeError:
            try:
                author_name = item.select_one('span[itemprop = "author"] > span').text.strip()
            except:
                try:
                    author_name = item.select_one('div.otziv_body > span').text.strip()
                except:
                    author_name = item.select_one('div.otziv_body > a').text.strip()
        try:
            emotion_text = float(item.select_one("div.vote_number").text.strip())
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
        try:
            response_block = item.select_one("div.otziv_.otvet > div").text
            response = "yes"
        except:
            response = "no"

        text = ph.clear_specials_symbols(item.select_one("div.otziv_text").text.strip())

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

    pprint.pprint(main_dict)
    return main_dict



if __name__ == '__main__':
    moscow_stomatologija_su("http://moscow.stomatologija.su/klinika/stomatologiya-mendeleev")
    # moscow_stomatologija_su("http://moscow.stomatologija.su/doctor/koryakin-artem-sergeevich")