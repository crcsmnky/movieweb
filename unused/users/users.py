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


@app.route('/users/top', methods=['GET'])
def top_users():
    users = mongo.db.users.find({}).sort('ratings', pymongo.DESCENDING).limit(10)
    return dumps(users), 200


@app.route('/users/login', methods=['POST'])
def login_user():
    userid = int(request.form['user'])
    user = mongo.db.users.find_one({'userid': userid})
    if not user:
        return dumps('user not found'), 404
    
    return dumps(''), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)