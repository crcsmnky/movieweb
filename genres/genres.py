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


@app.route('/genres/top', methods=['GET'])
def top_genres():
    genres = mongo.db.genres.find({}).sort('count', pymongo.DESCENDING).limit(10)
    return dumps(genres), 200


@app.route('/genres/<name>', methods=['GET'])
def genre(name):
    skip = int(request.args.get('skip', 0))
    movies = mongo.db.movies.find(
        {'genres': name}
    ).sort('ratings', pymongo.DESCENDING).skip(skip).limit(20)
    return dumps(movies), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 7000))
    app.run(host='0.0.0.0', port=port, debug=True)