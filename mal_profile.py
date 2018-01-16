class MALProfile(object):
    def __init__(self, url):
        self.url = url
        self.anime_scores, self.anime_titles, self.anime_urls = [], [], []
        self.anime_list = {}