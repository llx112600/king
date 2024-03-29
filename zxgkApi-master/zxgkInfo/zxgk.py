import requests
import re
import os
import random
from lxml import etree
from aip import AipOcr
from django.db.models import Q
import time
from .models import *
from .config import APP_ID, API_KEY, SECRET_KEY, HEADERS

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

session = requests.session()


def get_captche_id():
    url = "http://zxgk.court.gov.cn/zhzxgk/index_form.do"
    response = requests.request("GET", url, headers=HEADERS)
    result = re.search(r'var captchaId = \'(.*)\';', response.text)
    print(result)
    if result:
        print(result.group(1))
        captchaid = result.group(1)
        return captchaid


def recognize_image(captchaid):
    url = "http://zxgk.court.gov.cn/zhzxgk/captcha.do"
    querystring = {"captchaId": captchaid, "random": random.uniform(0, 1)}
    if os.path.exists('captcha.jpg'):
        os.remove('captcha.jpg')
    try:
        response = session.request("GET", url, headers=HEADERS, timeout=6, params=querystring)
        if response.text:
            with open('captcha.jpg', 'wb') as f:
                f.write(response.content)
        else:
            print("retry, response.text is empty")
    except Exception as ee:
        print(ee)

        # 识别
    def get_file_content(filepath):
        with open(filepath, 'rb') as fp:
            return fp.read()

    image = get_file_content('captcha.jpg')
    # 识别结果
    api_result = client.basicGeneral(image)
    print(api_result)
    try:
        if api_result['words_result'][0]:
            code = api_result['words_result'][0]['words']
            print(code)
            os.remove('captcha.jpg')
            return {'j_captcha': code, 'captchaId': captchaid}
    except Exception as e:
        print(e)
        return {'j_captcha': '1111', 'captchaId': captchaid}


def zxgk_list(cardnum, captchaid, current_page=1):
    result = recognize_image(captchaid)
    url = "http://zxgk.court.gov.cn/zhzxgk/newsearch"
    payload = {
        'currentPage': current_page,
        'searchCourtName': '全国法院（包含地方各级法院）',
        'selectCourtId': '0',
        'selectCourtArrange': '1',
        'pname': '',
        'cardNum': cardnum,
        'j_captcha': result.get('j_captcha'),
        'countNameSelect': '',
        'captchaId': result.get('captchaId')
    }

    response = session.request("POST", url, data=payload, headers=HEADERS)
    while "验证码错误" in response.text:
        time.sleep(1)
        result = recognize_image(captchaid)
        try:
            payload['j_captcha'] = result.get('j_captcha')
        except Exception as e:
            print(e)
        response = session.request("POST", url, data=payload, headers=HEADERS)
    else:
        temps = re.search('1/\\d{1,4}', response.text).group()
        max_page = int(temps.replace('1/', ''))
        print("共{}页数据".format(max_page))
        for page in range(1, max_page + 1):
            print("*" * 100)
            print("正在爬取关键词{}第{}页数".format(cardnum, page))
            print("*" * 100)
            payload['currentPage'] = page
            response = session.request("POST", url, data=payload, headers=HEADERS)
            while "验证码错误" in response.text:
                result = recognize_image(captchaid)
                payload['j_captcha'] = result.get('j_captcha')
                response = session.request("POST", url, data=payload, headers=HEADERS)
            else:
                html = etree.HTML(response.text)
                trs = html.xpath('//table/tbody/tr')
                for tr in trs[1:]:
                    tds = tr.xpath('.//td/text()')
                    print(tds)
                    name = tds[1]
                    case_no = tds[3]
                    print(name, result.get('j_captcha'), case_no, captchaid)
                    zxgk_detail(name, cardnum, result.get('j_captcha'), case_no, captchaid)
                    time.sleep(1)


def zxgk_detail(pname, cardnum, j_captcha_newdel, casecode_newdel, captchaid_newdel):
    url = "http://zxgk.court.gov.cn/zhzxgk/newdetail?pnameNewDel={}&" \
          "cardNumNewDel={}&j_captchaNewDel={}&caseCodeNewDel={}&captchaIdNewDel=" \
          "{}".format(pname, cardnum, j_captcha_newdel, casecode_newdel, captchaid_newdel)
    print(url)
    response = requests.request("GET", url, headers=HEADERS)
    html = etree.HTML(response.text.encode('utf-8', 'ignore'))
    while "验证码错误" in response.text:
        print("验证码错误，正在重试")
        result = recognize_image(captchaid_newdel)
        zxgk_detail(pname, cardnum, result.get('j_captcha'), casecode_newdel, captchaid_newdel)
    else:
        bzxr_trs = html.xpath('//table[@id="bzxr"]/tr')
        if bzxr_trs:
            print("被执行人")
            try:
                name = html.xpath('//td[@id="pnameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                name = ''
            try:
                card_id = html.xpath('//td[@id="partyCardNumDetail"]/text()')[0]
                if card_id:
                    card_id = cardnum
            except Exception as e:
                print(e)
                card_id = ''
            try:
                sexy = html.xpath('//td[@id="Detail"]/text()')[0]
            except Exception as e:
                print(e)
                sexy = ''
            try:
                court = html.xpath('//td[@id="execCourtNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                court = ''
            try:
                case_time = html.xpath('//td[@id="caseCreateTimeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_time = ''
            try:
                case_code = html.xpath('//td[@id="caseCodeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_code = ''
            try:
                target = html.xpath('//td[@id="execMoneyDetail"]/text()')[0]
            except Exception as e:
                print(e)
                target = ''

            Bzxr.objects.update_or_create(courtName=court, caseCode=case_code,
                                          execMoney=target, regDate=case_time, sexy=sexy,
                                          person_id=Person.objects.filter(Q(cardNum=card_id) & Q(iname=name))[0].id)

        zb_trs = html.xpath('//table[@id="zb"]/tr')

        if zb_trs:
            print("终本案件")

            try:
                case_code = html.xpath('//td[@id="ahDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_code = ''

            try:
                name = html.xpath('//td[@id="xmDetail"]/text()')[0]
            except Exception as e:
                print(e)
                name = ''

            try:
                sexy = html.xpath('//td[@id="xmDetail"]/../following-sibling::tr/td[2]/text()')[0]
            except Exception as e:
                print(e)
                sexy = ''

            try:
                card_id = html.xpath('//td[@id="sfzhmDetail"]/text()')[0]
                if card_id:
                    card_id = cardnum
            except Exception as e:
                print(e)
                card_id = ''

            try:
                court = html.xpath('//td[@id="zxfymcDetail"]/text()')[0]
            except Exception as e:
                print(e)
                court = ''

            try:
                case_time = html.xpath('//td[@id="larqDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_time = ''

            try:
                final_date = html.xpath('//td[@id="jarqDetail"]/text()')[0]
            except Exception as e:
                print(e)
                final_date = ''

            try:
                target = html.xpath('//td[@id="sqzxbdjeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                target = ''

            try:
                money = html.xpath('//td[@id="swzxbdjeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                money = ''

            ZhongBen.objects.update_or_create(caseCode=case_code, regDate=case_time, courtName=court, execMoney=target,
                                              finalDate=final_date, sexy=sexy, unperformMoney=money,
                                              person_id=Person.objects.filter(Q(cardNum=card_id) & Q(iname=name))[0].id)

        xgl_trs = html.xpath('//table[@id="xgl"]/tr')

        if xgl_trs:
            print("限制消费人员")

            try:
                name = html.xpath('//td[@id="inameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                name = ''

            try:
                sexy = html.xpath('//td[@id="sexDetail"]/text()')[0]
            except Exception as e:
                print(e)
                sexy = ''

            try:
                card_id = html.xpath('//td[@id="cardNumDetail"]/text()')[0]
                if card_id:
                    card_id = cardnum
            except Exception as e:
                print(e)
                card_id = ''

            try:
                court = html.xpath('//td[@id="courtNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                court = ''

            try:
                area = html.xpath('//td[@id="areaNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                area = ''

            try:
                case_code = html.xpath('//td[@id="caseCodeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_code = ''

            try:
                case_time = html.xpath('//td[@id="regDateDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_time = ''

            Xgl.objects.update_or_create(courtName=court, regDate=case_time, caseCode=case_code,
                                         areaName=area, sexy=sexy, person_id=Person.objects.filter(Q(cardNum=card_id) & Q(iname=name))[0].id)

        sx_trs = html.xpath('//table[@id="sx"]/tr')

        if sx_trs:
            print("失信被执行人")
            try:
                name = html.xpath('//td[@id="inameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                name = ''

            try:
                sexy = html.xpath('//td[@id="sexDetail"]/text()')[0]
            except Exception as e:
                print(e)
                sexy = ''

            try:
                card_id = html.xpath('//td[@id="cardNumDetail"]/text()')[0]
                if card_id:
                    card_id = cardnum
            except Exception as e:
                print(e)
                card_id = ''

            try:
                court = html.xpath('//td[@id="courtNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                court = ''

            try:
                area = html.xpath('//td[@id="areaNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                area = ''

            try:
                gist_id = html.xpath('//td[@id="gistIdDetail"]/text()')[0]
            except Exception as e:
                print(e)
                gist_id = ''

            try:
                case_time = html.xpath('//td[@id="regDateDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_time = ''

            try:
                case_code = html.xpath('//td[@id="caseCodeDetail"]/text()')[0]
            except Exception as e:
                print(e)
                case_code = ''

            try:
                gist_unit = html.xpath('//td[@id="gistUnitDetail"]/text()')[0]
            except Exception as e:
                print(e)
                gist_unit = ''

            try:
                duty = html.xpath('//td[@id="dutyDetail"]/text()')[0]
            except Exception as e:
                print(e)
                duty = ''

            try:
                performance = html.xpath('//td[@id="performanceDetail"]/text()')[0]
            except Exception as e:
                print(e)
                performance = ''

            try:
                disrupt_typename = html.xpath('//td[@id="disruptTypeNameDetail"]/text()')[0]
            except Exception as e:
                print(e)
                disrupt_typename = ''

            try:
                publish_date = html.xpath('//td[@id="publishDateDetail"]/text()')[0]
            except Exception as e:
                print(e)
                publish_date = ''

            ShiXin.objects.update_or_create(areaName=area, caseCode=case_code, courtName=court,
                                            disruptTypeName=disrupt_typename, duty=duty, sexy=sexy,
                                            gistId=gist_id, gistUnit=gist_unit, performance=performance,
                                            publishDate=publish_date, regDate=case_time, person_id=Person.objects.filter(Q(cardNum=card_id) & Q(iname=name))[0].id
                                            )
