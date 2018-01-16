import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver


class MALParser(object):
    def __init__(self, mal_profile):
        self.mal_profile = mal_profile
        self.url = self.mal_profile.url
        self.anime_list = self.mal_profile.anime_list
        self.anime_titles = self.mal_profile.anime_titles
        self.anime_scores = self.mal_profile.anime_scores
        self.anime_urls = self.mal_profile.anime_urls
        self.parser = 'lxml'
        self.df_filename = 'title.csv'

    def parse_modern_anime_list(self):
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get(self.url)
        scroll_pause_time = 4
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_scroll_height = driver.execute_script("return document.body.scrollHeight")
            if new_scroll_height == scroll_height:
                break
            scroll_height = new_scroll_height

        soup = BeautifulSoup(driver.page_source, self.parser)
        for tr_tag in soup.find_all('tr', class_='list-table-data'):
            for anime_title_td_tag in tr_tag.find_all('td', class_='data title clearfix'):
                self.anime_urls.append(''.join(['https://myanimelist.net', anime_title_td_tag.a.get('href')]))
                self.anime_titles.append(anime_title_td_tag.a.string)
            for score_td_tag in tr_tag.find_all('td', class_='data score'):
                try:
                    self.anime_scores.append(int(score_td_tag.a.string.strip()))
                except ValueError:
                    self.anime_scores.append(0)

    def parse_classic_anime_list(self):
        driver = webdriver.Chrome('chromedriver.exe')
        driver.get(self.url)
        scroll_pause_time = 4
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_scroll_height = driver.execute_script("return document.body.scrollHeight")
            if new_scroll_height == scroll_height:
                break
            scroll_height = new_scroll_height

        soup = BeautifulSoup(driver.page_source, self.parser)
        for anchor_tag in soup.find_all('a', class_='animetitle'):
            try:
                self.anime_scores.append(int(anchor_tag.parent.next_sibling.next_sibling.string.strip()))
            except ValueError:
                self.anime_scores.append(0)
            self.anime_urls.append(''.join(['https://myanimelist.net', anchor_tag.get('href')]))
            [self.anime_titles.append(span_tag.string) for span_tag in anchor_tag.find_all('span')]

    def parse_modern_anime_list_without_driver(self):
        """Not using web driver, thus faster than standard modern anime list parser,
         but only works with approximately 300 entries."""
        get_request = requests.get(self.url)
        data = get_request.text
        soup = BeautifulSoup(data, self.parser)

        table_tags = (soup.find_all('table', class_='list-table'))
        table_items = list(map(lambda x: x['data-items'], table_tags))
        pattern = r'{.+?"score":(.+?).+?"anime_title":"(.+?)".+?"anime_url":"(.+?)".+?}+?'
        matches = re.findall(pattern, table_items[0])
        self.anime_scores = list(map(lambda x: int(x), [match[0] for match in matches]))
        self.anime_titles = list(map(lambda x: x, [match[1] for match in matches]))
        self.anime_urls = list(map(lambda x: ''.join(['https://myanimelist.net', x]),
                                   [match[2].replace('\\', '') for match in matches]))

    def parse_anime_page(self, url):
        get_request = requests.get(url)
        data = get_request.text
        soup = BeautifulSoup(data, self.parser)
        span_tags = soup.find_all('span', class_='dark_text')
        required_colons = ('English:', 'Type:', 'Episodes:', 'Studios:', 'Source:', 'Genres:', 'Score:')
        parsed_colons = []
        for tag in span_tags:
            if tag.string in required_colons:
                parsed_colons.append(tag.string)
                if tag.next_sibling.next_sibling:
                    self.anime_list.setdefault(tag.string.strip(':'), []).append(tag.next_sibling.next_sibling.string)
                else:
                    self.anime_list.setdefault(tag.string.strip(':'), []).append(tag.next_sibling.strip())
        lost_colons = set(required_colons) - set(parsed_colons)
        [self.anime_list.setdefault(item.strip(':'), []).append('NaN') if lost_colons else '' for item in lost_colons]

    def create_anime_list(self):
        for url in self.anime_urls:
            self.parse_anime_page(url)
        self.anime_list['Personal score'] = self.anime_scores
        for index, value in enumerate(self.anime_list['English']):
            if value == 'NaN':
                self.anime_list['English'][index] = self.anime_titles[index]
        anime_data_frame = pd.DataFrame(self.anime_list)
        anime_data_frame.to_csv(self.df_filename, index=False)
