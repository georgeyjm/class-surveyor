import requests
from bs4 import BeautifulSoup


def ykps_auth(username, password):
    '''Authenticates the given credentials through Powerschool.'''

    url = 'https://powerschool.ykpaoschool.cn/guardian/home.html'
    form_data = {
        'account': username,
        'ldappassword': password,
        'pw': 'surveyor'
    }

    try:
        req = requests.post(url, data=form_data, timeout=5)
        soup = BeautifulSoup(req.text, 'html.parser')
        name = soup.select('#userName > span')[0].get_text().strip()
        ret = 0
    except Exception as e:
        name = str(e)
        ret = -1

    return ret, name
