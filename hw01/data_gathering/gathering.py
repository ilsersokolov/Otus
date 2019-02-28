"""
ЗАДАНИЕ

Выбрать источник данных и собрать данные по некоторой предметной области.

Цель задания - отработать навык написания программ на Python.
В процессе выполнения задания затронем области:
- организация кода в виде проекта, импортирование модулей внутри проекта
- unit тестирование
- работа с файлами
- работа с протоколом http
- работа с pandas
- логирование

Требования к выполнению задания:

- собрать не менее 1000 объектов

- в каждом объекте должно быть не менее 5 атрибутов
(иначе просто будет не с чем работать.
исключение - вы абсолютно уверены что 4 атрибута в ваших данных
невероятно интересны)

- сохранить объекты в виде csv файла

- считать статистику по собранным объектам


Этапы:

1. Выбрать источник данных.

Это может быть любой сайт или любое API

Примеры:
- Пользователи vk.com (API)
- Посты любой популярной группы vk.com (API)
- Фильмы с Кинопоиска
(см. ссылку на статью ниже)
- Отзывы с Кинопоиска
- Статьи Википедии
(довольно сложная задача,
можно скачать дамп википедии и распарсить его,
можно найти упрощенные дампы)
- Статьи на habrahabr.ru
- Объекты на внутриигровом рынке на каком-нибудь сервере WOW (API)
(желательно англоязычном, иначе будет сложно разобраться)
- Матчи в DOTA (API)
- Сайт с кулинарными рецептами
- Ebay (API)
- Amazon (API)
...

Не ограничивайте свою фантазию. Это могут быть любые данные,
связанные с вашим хобби, работой, данные любой тематики.
Задание специально ставится в открытой форме.
У такого подхода две цели -
развить способность смотреть на задачу широко,
пополнить ваше портфолио (вы вполне можете в какой-то момент
развить этот проект в стартап, почему бы и нет,
а так же написать статью на хабр(!) или в личный блог.
Чем больше у вас таких активностей, тем ценнее ваша кандидатура на рынке)

2. Собрать данные из источника и сохранить себе в любом виде,
который потом сможете преобразовать

Можно сохранять страницы сайта в виде отдельных файлов.
Можно сразу доставать нужную информацию.
Главное - постараться не обращаться по http за одними и теми же данными много раз.
Суть в том, чтобы скачать данные себе, чтобы потом их можно было как угодно обработать.
В случае, если обработать захочется иначе - данные не надо собирать заново.
Нужно соблюдать "этикет", не пытаться заддосить сайт собирая данные в несколько потоков,
иногда может понадобиться дополнительная авторизация.

В случае с ограничениями api можно использовать time.sleep(seconds),
чтобы сделать задержку между запросами

3. Преобразовать данные из собранного вида в табличный вид.

Нужно достать из сырых данных ту самую информацию, которую считаете ценной
и сохранить в табличном формате - csv отлично для этого подходит

4. Посчитать статистики в данных
Требование - использовать pandas (мы ведь еще отрабатываем навык использования инструментария)
То, что считаете важным и хотели бы о данных узнать.

Критерий сдачи задания - собраны данные по не менее чем 1000 объектам (больше - лучше),
при запуске кода командой "python3 -m gathering stats" из собранных данных
считается и печатается в консоль некоторая статистика

Код можно менять любым удобным образом
Можно использовать и Python 2.7, и 3

Зачем нужны __init__.py файлы
https://stackoverflow.com/questions/448271/what-is-init-py-for

Про документирование в Python проекте
https://www.python.org/dev/peps/pep-0257/

Про оформление Python кода
https://www.python.org/dev/peps/pep-0008/


Примеры сбора данных:
https://habrahabr.ru/post/280238/

Для запуска тестов в корне проекта:
python3 -m unittest discover

Для запуска проекта из корня проекта:
python3 -m gathering gather
или
python3 -m gathering transform
или
python3 -m gathering stats


Для проверки стиля кода всех файлов проекта из корня проекта
pep8 .

"""

import logging

import sys

from scrappers.scrapper import Scrapper
from storages.file_storage import FileStorage

from parsers.html_parser import HtmlParser
import numpy as np
import pandas as pd
from itertools import islice

# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
SCRAPPED_FILE = 'scrapped_data.zip'
TABLE_FORMAT_FILE = 'data.csv'
LOG_FILE = 'gathering.log'

#logger settings
log_formatter = logging.Formatter(FORMAT)
logger = logging.getLogger('gathering')
logger.setLevel(logging.INFO)

fh = logging.FileHandler(LOG_FILE)
fh.setFormatter(log_formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(log_formatter)
logger.addHandler(ch)


def gather_process():
    """
    Scrap hotslog.com data to storage
    """
    logger.info("gather")
    storage = FileStorage(SCRAPPED_FILE)
    scrapper = Scrapper()
    scrapper.scrap_process(storage)


def convert_data_to_table_format():
    """
    extract data from storage to csv
    """
    logger.info("transform")

    storage = FileStorage(SCRAPPED_FILE)
    data = storage.read_data()
    hp = HtmlParser()
    result = []
    # data = dict(islice(data.items(), 10))
    total_ids = len(data)
    num = 1
    old_percent = -1
    for id, html in data.items():
        percent = int(num * 100 / total_ids)
        if percent > old_percent:
            logger.info('{}% done'.format(percent))
            old_percent = percent
        try:
            dt = hp.parse(html)
        except Exception as ex:
            logger.error('error at user id = {}'.format(id))
            raise ex
        dt['id'] = int(id)
        num += 1
        result.append(dt)
    user_data = pd.DataFrame(result)
    cols = list(user_data)
    cols.insert(0, cols.pop(cols.index('Win %')))
    cols.insert(0, cols.pop(cols.index('Total games')))
    cols.insert(0, cols.pop(cols.index('Name')))
    cols.insert(0, cols.pop(cols.index('Place')))
    cols.insert(0, cols.pop(cols.index('id')))
    user_data = user_data.ix[:, cols]
    user_data.set_index('id', inplace=True)
    user_data.to_csv(TABLE_FORMAT_FILE, index=False)


def stats_of_data():
    """
    extract some statistics from csv
    """
    logger.info("stats")

    user_data = pd.read_csv(TABLE_FORMAT_FILE, index_col=False)
    user_data.set_index('id', inplace=True)
    print(user_data.describe())
    print('Как зависит % побед от числа игр?')
    print(user_data.groupby(pd.cut(user_data['Win %'],np.arange(45,67,1)))['Total games'].median())
    print('Как зависит % побед от числа игр за класс Ambusher?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Ambusher games'].median())
    print('Как зависит % побед от числа игр за класс Bruiser?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Bruiser games'].median())
    print('Как зависит % побед от числа игр за класс Burst Damage?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Burst Damage games'].median())
    print('Как зависит % побед от числа игр за класс Healer?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Healer games'].median())
    print('Как зависит % побед от числа игр за класс Siege?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Siege games'].median())
    print('Как зависит % побед от числа игр за класс Support?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Support games'].median())
    print('Как зависит % побед от числа игр за класс Sustained Damage?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Sustained Damage games'].median())
    print('Как зависит % побед от числа игр за класс Tank?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Tank games'].median())
    print('Как зависит % побед от числа игр за класс Utility?')
    print(user_data.groupby(pd.cut(user_data['Win %'], np.arange(45, 66, 1)))['Utility games'].median())


if __name__ == '__main__':
    logger.info("Work started")

    if sys.argv[1] == 'gather':
        gather_process()

    elif sys.argv[1] == 'transform':
        convert_data_to_table_format()

    elif sys.argv[1] == 'stats':
        stats_of_data()

    logger.info("work ended")
