import requests
import pprint
import parse_helper as ph

def like_doctor_ru(id, type, url):
    """

    :param id: Идентификатор больницы или доктора. Можно взять у meta property="og:image" в content =  https://like.doctor/uploads/clinics/724/6724.jpeg, значит id = 6724:
    :param type:
    :param url:
    :return:
    """
    count = 0
    count_positive_comments = 0
    count_negative_comments = 0
    count_neitral_comments = 0
    comment_list = []
    page = 0
    while True:
        headers = {
            'Host': 'like.doctor',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://like.doctor/sankt-peterburg/kliniki/stomatologiya',
            'Connection': 'keep-alive',
            'Cookie': '__cfduid=d01dd1125c1868e9fb31064316ebca6611551725500; _ym_uid=1552415289968903118; _ym_d=1552415289; _ga=GA1.2.515682993.1552415289; _fbp=fb.1.1552415288794.1260102438; PHPSESSID=eqcrsm9bedpmuhh8umvh609jr7; _csrf=4882f54cd0a41e2c6e648b141daab848ae5f43d210d6682d28f5fe677f22a8e6a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22k4k8GzeyreESj8joaeWVu1bDAK7Su_cD%22%3B%7D; _ym_visorc_48769385=w; _ym_isad=2; _gid=GA1.2.1658319103.1552595455; _gat_gtag_UA_118564471_1=1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers',
            'X-Requested-With': 'XMLHttpRequest'
        }


        url_test = "https://like.doctor/service/more-posts"
        proxy = ph.get_proxy_http()
        if type is "clinic":
            data_post ={
                'nextpage': page,
                'perpage':'10',
                'data[city_id]':'false',
                'data[type]':'1',
                'data[user_id]':'false',
                'data[doctor_id]':'false',
                'data[lector_id]':'false',
                'data[event_id]':'false',
                'data[education_id]	':'false',
                'data[service_id]':'false',
                'data[speciality_id]':'false',
                'data[clinic_id][]':id,
                'data[include_clinic_info]':id,
                'data[temp]':'0',
                'data[show]	':'1',
                'data[additional_data][no_clinic_name]':'true'
            }
        elif type is "doctor":
            data_post = {
                'nextpage': page,
                'perpage': '10',
                'data[city_id]': 'false',
                'data[type]': '1',
                'data[user_id]': 'false',
                'data[doctor_id]': id,
                'data[lector_id]': 'false',
                'data[event_id]': 'false',
                'data[education_id]	': 'false',
                'data[service_id]': 'false',
                'data[speciality_id]': 'false',
                'data[clinic_id][]': 'false',
                'data[include_clinic_info]': 'false',
                'data[temp]': '0',
                'data[show]	': '1',
                'data[additional_data][no_clinic_name]': 'true'
            }
        json = requests.post(url_test, data=data_post, headers=headers, proxies=proxy[0], auth=proxy[1]).json()
        print(json)
        html_json = json["html"]
        html = ph.get_html(html_json, 'html.parser')
        print("Pagination:", str(page), url_test)
        items = html.select('div[itemprop="review"]')
        print(len(items))
        if len(items) == 0:
            break
        for index, item in enumerate(items):
            date = item.select_one("span.date").get("content")

            author_name = item.select_one('a[itemprop="author"]').text.strip()
            try:
                emotion_text = float(item.select_one("span.rating__wrap ").text.strip())
                if (emotion_text >= 4):
                    emotion = "positive"
                    count_positive_comments += 1

                elif (emotion_text <= 3):
                    emotion = "negative"
                    count_negative_comments += 1
                else:
                    emotion = "neutral"
                    count_neitral_comments += 1
            except:
                emotion = None
            response_block = item.select_one("div.wrapper-sub-comments > div")
            if response_block is None:
                response = "no"
            else:
                response = "yes"
            text = ph.clear_specials_symbols(item.select_one('p[itemprop="reviewBody"]').text.strip())
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
    # like_doctor_ru(6724, "clinic", "https://like.doctor/sankt-peterburg/kliniki/stomatologiya-noviy-vek-na-prosvescheniya")
    like_doctor_ru(29071, "doctor", "https://like.doctor/sankt-peterburg/vrachi/bugaev-sergey-sergeevich")