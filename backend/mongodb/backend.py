import os
import pymongo

from bson.json_util import dumps
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'f8b800fdbdabda83018ed4ffb8088b9e'
app.config['MONGO_URI'] = 'mongodb://{host}:{port}/{database}'.format(
    host=os.environ.get('MONGODB_HOST', 'localhost'),
    port=os.environ.get('MONGODB_PORT', 27017),
    database=os.environ.get('MONGODB_DB', 'movielens')
)

mongo = PyMongo(app)


@app.route('/api/movies/top', methods=['GET'])
def top_movies():
    movies = mongo.db.movies.find({}).sort([
        ('ratings', pymongo.DESCENDING),
        ('avg_rating', pymongo.DESCENDING)
    ]).limit(8)
    return dumps(movies), 200


@app.route('/api/movies/all', methods=['GET'])
def all_movies():
    skip = int(request.args.get('skip', 0))
    movies = mongo.db.movies.find({}).sort([
        ('ratings', pymongo.DESCENDING),
        ('avg_rating', pymongo.DESCENDING)
    ]).skip(skip).limit(20)
    return dumps(movies), 200


@app.route('/api/movies/count', methods=['GET'])
def all_movies_count():
    count = mongo.db.movies.count_documents({})
    return dumps({'count': count}), 200


@app.route('/api/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    movie = mongo.db.movies.find_one_or_404({'movieid': movieid})
    return dumps(movie), 200


@app.route('/api/genres/top', methods=['GET'])
def top_genres():
    genres = mongo.db.genres.find({}).sort('count', pymongo.DESCENDING).limit(10)
    return dumps(genres), 200


@app.route('/api/genres/all', methods=['GET'])
def all_genres():
    genres = mongo.db.genres.find({}).sort('count', pymongo.DESCENDING)
    return dumps(genres), 200


@app.route('/api/genres/<name>', methods=['GET'])
def genre(name):
    skip = int(request.args.get('skip', 0))
    movies = mongo.db.movies.find(
        {'genres': name}
    ).sort('ratings', pymongo.DESCENDING).skip(skip).limit(20)
    return dumps(movies), 200


@app.route('/api/genres/count/<name>', methods=['GET'])
def genre_count(name):
    count = mongo.db.movies.count_documents({'genres': name})
    return dumps({'count': count}), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)