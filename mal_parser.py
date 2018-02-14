import re
import time
from concurrent import futures
import requests
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
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
        driver.quit()

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
        driver.quit()

    def parse_modern_anime_list_without_driver(self):
        """Faster. Works with approximately 300 entries."""
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
        time.sleep(3)
        try:
            request = requests.get(url)
            if request.status_code == 200:
                html = request.text
                strainer = SoupStrainer('div')
                soup = BeautifulSoup(html, self.parser, parse_only=strainer)
                span_tags = soup.find_all('span', class_='dark_text')
                required_colons = ('Type:', 'Episodes:', 'Studios:', 'Source:', 'Genres:', 'Score:')
                colons = list(filter(lambda x: x.text in required_colons, span_tags))
                for tag in colons:
                    if tag.next_sibling.next_sibling:
                        self.anime_list.setdefault(tag.text.strip(':'), []).append(tag.next_sibling.next_sibling.text)
                    else:
                        self.anime_list.setdefault(tag.text.strip(':'), []).append(str(tag.next_sibling.strip()))
                print(f'{url} processed.')
            else:
                print(request)
                time.sleep(4)
                self.parse_anime_page(url)
        except Exception as e:
            print(e)

    def create_anime_list(self):
        with futures.ThreadPoolExecutor(max_workers=5) as e:
            e.map(self.parse_anime_page, self.anime_urls)
        self.anime_list['Personal score'] = self.anime_scores
        self.anime_list['Title'] = self.anime_titles

    def export_anime_list_to_csv(self, filename):
        anime_data_frame = pd.DataFrame(self.anime_list)
        anime_data_frame.to_csv(filename, index=False)
