"""

usage: python movielens.py [movies] [ratings] [links]

"""

import sys
import re
import csv
import os
import tmdbsimple as tmdb

from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime
from time import sleep


def import_movies(db, mfile):
    count = 0
    movies = []
    mcsv = csv.DictReader(mfile)

    for row in mcsv:
        movie = {
            'movieid': int(row['movieId']),
            'title': row['title'].split(' (')[0],
            'year': row['title'].split(' (')[-1][:-1],
            'genres': row['genres'].split('|')
        }
        movies.append(movie)
        count += 1

        if (count % 1000) == 0:
            # print count, "movies inserted"
            db.command('insert', 'movies', documents=movies, ordered=False)
            movies = []
    
    if count > 0:
        db.command('insert', 'movies', documents=movies, ordered=False)


def import_ratings(db, rfile):
    count = 0
    ratings, movies, users = [], [], []
    rcsv = csv.DictReader(rfile)

    for row in rcsv:
        rating = {
            'movieid': int(row['movieId']),
            'userid': int(row['userId']),
            'rating': float(row['rating']),
            'ts': datetime.fromtimestamp(float(row['timestamp']))
        }
        ratings.append(rating)

        movie_update = {
            'q': { 'movieid': int(row['movieId']) },
            'u': { '$inc': {
                    'ratings' : 1,
                    'total_rating': float(row['rating'])
                }
            }
        }
        movies.append(movie_update)

        user_update = {
            'q': { 'userid' : int(row['userId']) },
            'u': { '$inc': { 'ratings': 1 } },
            'upsert': True
        }
        users.append(user_update)

        count += 1

        if (count % 1000) == 0:
            # print count, "ratings inserted, movies updated, users updated"
            db.command('insert', 'ratings', documents=ratings, ordered=False)
            db.command('update', 'movies', updates=movies, ordered=False)
            db.command('update', 'users', updates=users, ordered=False)
            ratings, movies, users = [], [], []

    if count > 0:
        db.command('insert', 'ratings', documents=ratings, ordered=False)
        db.command('update', 'movies', updates=movies, ordered=False)
        db.command('update', 'users', updates=users, ordered=False)


def import_links(db, lfile):
    count = 0
    movies = []
    lcsv = csv.DictReader(lfile)

    for row in lcsv:
        try:
            movies.append({
                'q': {'movieid': int(row['movieId'])},
                'u': { '$set': {
                        'imdb': row['imdbId'], 
                        'tmdb': row['tmdbId']
                }}
            })
            count += 1
        except:
            continue

        if (count % 1000) == 0:
            db.command('update', 'movies', updates=movies, ordered=False)
            movies = []

    if count > 0:
        db.command('update', 'movies', updates=movies, ordered=False)


def create_genres(db):
    docs = list(db.movies.aggregate([
        {'$unwind' : '$genres'},
        {'$group': {
            '_id': '$genres',
            'count': {'$sum': 1}
        }},
    ], cursor={}))

    genres = [
        {'_id': idx, 'name': doc['_id'], 'count': doc['count']}
        for idx, doc in enumerate(docs)
    ]

    db.command('insert', 'genres', documents=genres, ordered=False)


def update_avg_ratings(db):
    movies = db.movies.find()
    for m in movies:
        try:
            db.movies.update_one({'_id': m['_id']}, {'$set': {'avg_rating': float(m['total_rating'])/m['ratings']}})
        except:
            continue
    

def get_poster_links(db):
    tmdb.API_KEY='[YOUR API KEY HERE]'
    conf = tmdb.Configuration()
    imgurl = conf.info()['images']['base_url'] + 'w154' + '{path}'

    allmovies = db.movies.find()

    for i in xrange(0, allmovies.count(), 40):
        print i
        for j in xrange(i, i+40):
            try:
                movie = tmdb.Movies(int(allmovies[j]['tmdb'])).info()
                db.movies.update_one(
                    {'_id': allmovies[j]['_id']},
                    {'$set': {'poster': imgurl.format(path=movie['poster_path'])}}
                )
            except:
                continue
        sleep(10)


def ensure_indexes(db):
    db.movies.ensure_index("movieid")
    db.movies.ensure_index("ratings")
    db.movies.ensure_index("genres")
    db.ratings.ensure_index([("userid", ASCENDING),("movieid", ASCENDING)])
    db.users.ensure_index("userid")
    db.genres.ensure_index("name")


def main():
    host=os.environ.get('MONGODB_HOST', 'localhost')
    port=os.environ.get('MONGODB_PORT', 27017)
    database=os.environ.get('MONGODB_DB', 'movieweb')

    db = MongoClient(host, port)[database]

    with open(sys.argv[1]) as mfile:
        import_movies(db, mfile)

    with open(sys.argv[2]) as rfile:
        import_ratings(db, rfile)

    with open(sys.argv[3]) as lfile:
        import_links(db, lfile)

    create_genres(db)

    update_avg_ratings(db)

    get_poster_links(db)

    # ensure_indexes(db)


if __name__ == '__main__':
    main()
