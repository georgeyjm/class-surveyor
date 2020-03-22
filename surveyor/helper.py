import os
from datetime import datetime
from pathlib import Path

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


def get_export_file(file_format):
    '''Returns the file path and filename of the exported feedbacks file.'''

    root_dir = Path(os.path.dirname(os.path.realpath(__file__))).parents[0]
    exports_dir = root_dir / 'exports/'
    exports_dir.mkdir(parents=True, exist_ok=True)
    time_str = datetime.now().strftime('%Y%m%d%H%M%S')
    suffix = {'excel': 'xlsx', 'csv': 'csv'}.get(file_format, 'xlsx')
    filename = 'Feedbacks - {}.{}'.format(time_str, suffix)
    filepath = (exports_dir / filename).as_posix() # should be root_dir not exports_dir here

    return filepath, filename

