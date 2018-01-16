# -*- coding: utf-8 -*-
from mal_profile import MALProfile
from mal_parser import MALParser
from feature_constructor import FeatureConstructor


if __name__ == '__main__':
    profile_url = 'https://myanimelist.net/animelist/CrematorWii?status=2'
    profile = MALProfile(profile_url)
    parser = MALParser(profile)
    parser.parse_modern_anime_list()
    parser.create_anime_list()
    constructor = FeatureConstructor(parser)
    constructor.preprocess()



