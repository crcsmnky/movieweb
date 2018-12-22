import os
import pymongo

from bson.json_util import dumps
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://{host}:{port}/{database}'.format(
    host=os.environ.get('MONGODB_HOST', 'localhost'),
    port=os.environ.get('MONGODB_PORT', 27017),
    database=os.environ.get('MONGODB_DB', 'movieweb')
)

mongo = PyMongo(app)


@app.route('/ratings/<int:movieid>', methods=['POST'])
def update_movie_rating(movieid):
    user = request.headers.get('user', None)
    if not user:
        return dumps('unauthorized'), 401
    
    query = {
        'userid': user,
        'movieid': movieid
    }
    update = {'$set': {
        'rating': int(request.form['rating']),
        'ts': datetime.now()
    }}
    mongo.db.ratings.update(query, update, upsert=True)

    return dumps(''), 204


@app.route('/ratings/<int:movieid>', methods=['GET'])
def get_movie_ratings(movieid):
    skip = request.args.get('skip', 0)
    ratings = mongo.db.ratings.find({
        'movieid': movieid
    }).sort('ts', pymongo.DESCENDING).skip(skip).limit(10)
    
    return dumps(ratings), 200


@app.route('/ratings', methods=['GET'])
def get_user_ratings():
    user = request.headers.get('user', None)
    if not user:
        return dumps('unauthorized'), 401

    skip = request.args.get('skip', 0)
    ratings = mongo.db.ratings.find({
        'userid': user
    }).sort('ts', pymongo.DESCENDING).skip(skip).limit(20)

    return dumps(ratings), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)