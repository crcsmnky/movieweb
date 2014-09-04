from tmdbsimple import TMDB
import requests
from pymongo import MongoClient
from time import sleep
from PIL import Image
from StringIO import StringIO
import sys


def main():
    tmdb = TMDB('YOUR TMDB API KEY HERE')
    movies = MongoClient()['movielens']['movies']

    conf = tmdb.Configuration()
    img_url = conf.info()['images']['base_url']

    search = tmdb.Search()
    allmovies = movies.find()

    for i in xrange(0, allmovies.count(), 30):
        print i
        for j in xrange(i, i+30):
            resp = search.movie({'query': allmovies[j]['title']})
            if len(search.results) > 0:
                if search.results[0]['poster_path'] is not None:
                    poster_url = img_url + u'w185' + search.results[0]['poster_path']
                    # r = requests.get(poster_url)
                    # poster_data =
                    movies.update({'_id': allmovies[j]['_id']}, {'$set': {'poster': poster_url}})
        sleep(10)


if __name__ == '__main__':
    main()