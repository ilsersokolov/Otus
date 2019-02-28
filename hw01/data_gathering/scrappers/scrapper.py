import logging
import requests
import time
import re
import os
from bs4 import BeautifulSoup

logger = logging.getLogger('gathering.scrapper')


class Scrapper(object):
    """
    Class scrap hotslog.com and eject pages to storage
    """
    def __init__(self, skip_objects=None, delay=3):
        self.skip_objects = skip_objects
        self.user_ids_file = 'users.txt'
        self.delay = delay

    def _get_user_ids(self):
        """
        Create users list from Master league
        """
        logger.info('Get Users IDs')
        url = r'https://www.hotslogs.com/Rankings?Region=2&GameMode=4&League=Master'
        user_ids = []

        with requests.session() as s:
            r = s.get(url)
            soup = BeautifulSoup(r.text, features="lxml")
            pages_total = int(soup.find('div', {'class': "rgWrap rgInfoPart"}).findAll('strong')[1].text)
            users_total = int(soup.find('div', {'class': "rgWrap rgInfoPart"}).findAll('strong')[0].text)
            loaded_pages = []

            cur_page = 1
            for t in range(int(pages_total / 10) + 1):
                pages = soup.find('div', {'class': "rgWrap rgNumPart"}).findAll('a')
                for page in pages:
                    if page.get('title') == 'Previous Pages':
                        continue
                    try:
                        if int(page.text) in loaded_pages:  # page.text may be '...'
                            continue
                    except ValueError:
                        pass
                    if page.get('class') is None:  # not current page eq 1,11,21, etc. Becouse already loaded
                        viewstate = soup.find('input', {'id': "__VIEWSTATE"}).get('value')
                        viewstategenerator = soup.find('input', {'id': "__VIEWSTATEGENERATOR"}).get('value')
                        eventvalidation = soup.find('input', {'id': "__EVENTVALIDATION"}).get('value')
                        eventargument = ''
                        eventagent = re.split(r"'", page.get('href'))[1]
                        parm = {"__VIEWSTATE": viewstate, "__VIEWSTATEGENERATOR": viewstategenerator,
                                "__EVENTVALIDATION": eventvalidation,
                                '__EVENTTARGET': eventagent, '__EVENTARGUMENT': eventargument}
                        r = s.post(url, data=parm)
                        soup = BeautifulSoup(r.text, features="lxml")
                    if page.text == '...':
                        continue
                    logger.info('page: {} of {}'.format(page.text, pages_total))
                    loaded_pages.append((int(page.text)))
                    # extract users from page
                    user_ids_table = soup.findAll('tr')
                    for i in range(3, len(user_ids_table)):
                        user_ids.append(user_ids_table[i].find('td').text)
                    logger.info('{} of {}'.format(len(user_ids), users_total))
                    logger.debug('Last ID: {}'.format(user_ids[-1]))
                    cur_page += 1
                    time.sleep(self.delay)

        with open(self.user_ids_file, 'w') as output_file:
            output_file.write(';'.join(user_ids))

        logger.info('total: {} users, {} pages'.format(len(user_ids), cur_page))
        assert len(user_ids) == users_total
        assert cur_page - 1 == pages_total

    def scrap_process(self, storage, update=False):
        """
        scrap hotslog.com and eject pages to storage
        :param storage: reference to Storage class
        :param update: enable if need update info about user
        """
        logger.info('Start scrapping')

        # get users list
        if not os.path.exists(self.user_ids_file):
            self._get_user_ids()
        with open(self.user_ids_file, 'r') as f:
            user_ids = f.read().split(';')
        user_total = len(user_ids)

        data = {}
        user_done = []
        if not os.path.exists(storage.file_name) or update:
            storage.write_data(data)
        else:
            storage.read_data()
            user_done = storage.user_ids

        url = r'https://www.hotslogs.com/Player/Profile?PlayerID='
        eventagent = 'tl00$MainContent$DropDownGameMode'  # for Hero League
        eventargument = '"type":1,"index":2,"text":"Hero%20League","value":"4"}'  # for Hero League
        cs = '{"enabled":true,"logEntries":[],"selectedIndex":2,"selectedText":"Hero%20League","selectedValue":"4"}'

        last_percent = -1
        with requests.session() as s:
            for i, user in enumerate(user_ids):
                if user in user_done:
                    continue
                user_done.append(user)
                logger.debug('get user {}'.format(user))
                percent = int(i / user_total * 100)
                url_user = url + user
                r = s.get(url_user)
                # extract parameters to get new page
                soup = BeautifulSoup(r.text, features="lxml")
                viewstate = soup.find('input', {'id': "__VIEWSTATE"}).get('value')
                viewstategenerator = soup.find('input', {'id': "__VIEWSTATEGENERATOR"}).get('value')
                eventvalidation = soup.find('input', {'id': "__EVENTVALIDATION"}).get('value')
                ctl31_tsm = soup.find('input', {'id': "ctl31_TSM"}).get('value')
                parm = {"__VIEWSTATE": viewstate, "__VIEWSTATEGENERATOR": viewstategenerator,
                        "__EVENTVALIDATION": eventvalidation, '__EVENTTARGET': eventagent,
                        '__EVENTARGUMENT': eventargument, 'ctl31_TSM': ctl31_tsm,
                        'ctl00_MainContent_DropDownGameMode_ClientState': cs}
                # delay excludes ban
                time.sleep(self.delay)
                # request new page
                r = s.post(url_user, data=parm)
                data[user] = r.text
                # some info and save part of data
                if percent != last_percent:
                    logger.info(f'{percent}% done')
                    storage.append_data(data)
                    data = {}
                    last_percent = percent
                time.sleep(self.delay)

        storage.append_data(data)

        logger.info('Scrapping done')
