from parsers.parser import Parser

from bs4 import BeautifulSoup


class HtmlParser(Parser):

    def parse(self, text):
        """
        Parses html text and extracts field values
        :param data: html text (page)
        :return: a dictionary where key is one
        of  fields and value is this field's value
        """

        data = {}

        soup = BeautifulSoup(text, features='lxml')

        # Your code here: find an appropriate html element
        data['Name'] = soup.find('h1', {'class': 'section-title'}).text.split(' ')[2]
        id = soup.find('td', text='Hero League').findParent('tr').get('id')
        data['Place'] = int(soup.find('tr', {'id': id}).find('span').text.split(' ')[1])
        id = soup.find('td', text='Total Games Played').findParent('tr').get('id')
        data['Total games'] = int(soup.find('tr', {'id': id}).findAll('td')[1].text)
        id = soup.find('td', text='Overall Win Percent').findParent('tr').get('id')
        data['Win %'] = float(soup.find('tr', {'id': id}).findAll('td')[1].text.split(' ')[0])

        for i in range(9):
            lst = soup.find('tr', {'id': '__' + str(i)}).findAll('td')
            data[lst[0].find('span').text + ' games'] = int(lst[1].text.replace(',', ''))
            data[lst[0].find('span').text + ' win %'] = float(lst[2].text.split(' ')[0])

        return data
