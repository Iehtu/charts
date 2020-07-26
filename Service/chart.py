import datetime
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from jinja2 import Environment, FileSystemLoader
from selenium.webdriver.firefox.options import Options

class ChartCrawler(object):
    CHARTS_URL = 'https://www.officialcharts.com/charts/singles-chart/{date}'
    YOUTUBE_URL_TEMPLATE = '<iframe width="560" height="315" src="{url}"' \
                           ' frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope;' \
                           ' picture-in-picture" allowfullscreen></iframe>'
    YOUTUBE_URL_QUERY = 'https://www.youtube.com/results?search_query={artist} {title}'

    def __init__(self, day: int, month: int, year: int):
        date = datetime.datetime(year=year, month=month, day=day)
        url = self.CHARTS_URL.format(date=date.strftime("%Y%m%d"))
        self.bs = BeautifulSoup(requests.get(url).text, 'html.parser')
        self.result = []
        options = Options()
        options.headless = True
        self.webdriver = webdriver.Firefox(executable_path='./bin/geckodriver.exe', options=options)
        self.file_path = "{day}{month}{year}.html".format(day = day, month=month, year=year)

    def __del__(self):
        self.webdriver.close()

    def parse(self, limit: int = 5):
        tas = self.bs.find_all("div", class_='title-artist')
        num = 0
        self.result.clear()
        for ta in tas:

            num += 1
            artist = ta.find("div", class_='artist').getText(strip=True)
            title = ta.find("div", class_='title').getText(strip=True)
            href = self.get_youtube_clip(artist=artist, title=title).replace('watch?v=', 'embed/')
            self.result.append(dict(pos=num,
                                    artist=artist,
                                    title=title,
                                    href=self.YOUTUBE_URL_TEMPLATE.format(url=href)))

            if num >= limit:
                return

    def get_youtube_clip(self, artist: str, title: str):
        self.webdriver.get(self.YOUTUBE_URL_QUERY.format(artist=artist, title=title))
        time.sleep(1)
        elem = self.webdriver.find_element_by_id(id_='video-title')
        if elem is not None:
            href = elem.get_attribute('href')
        else:
            href = ''

        return href

    def get_result(self):
        return self.result

    def get_html_result(self) -> str:
        env = Environment(loader=FileSystemLoader('./templates'))
        template = env.get_template('chart_template.html')
        return template.render(rows=self.result)

    def save_html_to_file(self):
        f = open('./chart_results/{filename}'.format(filename = self.file_path), 'w', encoding='UTF-8')
        f.write(self.get_html_result())
        f.close()


