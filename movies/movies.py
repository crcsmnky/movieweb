import os
import pymongo

from bson.json_util import dumps
from flask import Flask, request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://{host}:{port}/{database}'.format(
    host=os.environ.get('MONGODB_HOST', 'localhost'),
    port=os.environ.get('MONGODB_PORT', 27017),
    database=os.environ.get('MONGODB_DB', 'movieweb')
)

mongo = PyMongo(app)


@app.route('/movies/top', methods=['GET'])
def top_movies():
    movies = mongo.db.movies.find({}).sort([
        ('ratings', pymongo.DESCENDING),
        ('avg_rating', pymongo.DESCENDING)
    ]).limit(10)
    return dumps(movies), 200


@app.route('/movies/all', methods=['GET'])
def all_movies():
    skip = request.args.get('skip', 0)
    movies = mongo.db.movies.find({}).sort([
        ('ratings', pymongo.DESCENDING),
        ('avg_rating', pymongo.DESCENDING)
    ]).limit(20)
    return dumps(movies), 200


@app.route('/movies/<movieid>', methods=['GET'])
def movie(movieid):
    movie = mongo.db.movies.find_one({'movieid': int(movieid)})
    return dumps(movie), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)