import os
import requests

from flask import Flask
from flask import request, redirect, url_for, session, jsonify
from functools import wraps

app = Flask(__name__)

app.secret_key = '34ef8d4064770c8f97f2b0e060bb91d0'

# app.config['MONGO_URI'] = 'mongodb://{host}:{port}/{database}'.format(
#     host=os.environ.get('MONGODB_HOST', 'localhost'),
#     port=os.environ.get('MONGODB_PORT', 27017),
#     database=os.environ.get('MONGODB_DB', 'movieweb')
# )

# mongo = PyMongo(app)

services = {
    "movies": {
        "host": "http://movies:5000", "endpoint": "movies"
    },
    "genres": {
        "host": "http://genres:5000", "endpoint": "genres"
    },
    "ratings": {
        "host": "http://ratings:5000", "endpoint": "ratings"
    },
    "users": {
        "host": "http://users:5000", "endpoint": "users"
    }
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def request_resource(service, slug, user=None, data=None):
    try:
        url = '{host}/{endpoint}{slug}'.format(
            host=services[service]['host'],
            endpoint=services[service]['endpoint'],
            slug=slug
        )
        headers = {'user': user} if user else {}
        if data:
            res = requests.post(url, headers=headers, data=data)
        else:
            res = requests.get(url, headers=headers)

        status = res.status_code
        body = res.json()
    except ValueError:
        body = res.text
    except:
        status = 500
        body = {'error': 'sorry, this resource is not available at this time'}
    finally:
        return jsonify(body), status


# Movies API Methods
@app.route('/api/v1/movies/top', methods=['GET'])
def top_movies():
    return request_resource(service='movies', slug='/top')


@app.route('/api/v1/movies', methods=['GET'])
def all_movies():
    skip = request.args.get('skip', 0)
    return request_resource(
        service='movies', 
        slug='/all?skip={}'.format(skip)
    )


@app.route('/api/v1/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    return request_resource(
        service='movies', 
        slug='/{}'.format(movieid)
    )


# Recommendations API Methods
# @app.route('/api/v1/recommendations/<int:movieid>', methods=['GET'])
# @login_required
# def recommendations(movieid):
#     status, content = request_resource(
#         service='recommendations', slug='/{}'.format(movieid), 
#         user=session['user'])
#     return json.dumps(content), status, {'Content-Type': 'application/json'}


# Ratings API Methods
@app.route('/api/v1/ratings/<int:movieid>', methods=['POST'])
@login_required
def update_movie_rating(movieid):
    return request_resource(
        service='ratings', 
        slug='/{}'.format(movieid), 
        user=session['user'], 
        data=request.data
    )


@app.route('/api/v1/ratings/<int:movieid>', methods=['GET'])
def get_movie_ratings(movieid):
    skip = request.args.get('skip', 0)
    return request_resource(
        service='ratings', 
        slug='/{}?skip={}'.format(movieid, skip), 
        user=session['user']
    )


@app.route('/api/v1/ratings', methods=['GET'])
@login_required
def get_user_ratings():
    skip = request.args.get('skip', 0)
    return request_resource(
        service='ratings',
        slug='?skip={}'.format(skip),
        user=session['user']
    )


# Genres API Methods
@app.route('/api/v1/genres/top', methods=['GET'])
def top_genres():
    return request_resource(service='genres', slug='/top')


@app.route('/api/v1/genres/<name>', methods=['GET'])
def genre(genreid):
    skip = request.args.get('skip', 0)
    return request_resource(
        service='genres', 
        slug='/{}?skip={}'.format(name, skip)
    )


# Users API Methods
@app.route('/api/v1/users/top', methods=['GET'])
def top_users():
    return request_resource(service='users', slug='/top')


@app.route('/api/v1/users/ratings', methods=['GET'])
@login_required
def user_ratings():
    skip = request.args.get('skip', 0)
    return request_resource(
        service='ratings', 
        slug='?skip={}'.format(skip), 
        user=session['user']
    )


@app.route('/api/v1/users/login', methods=['POST'])
def login():
    content, status = request_resource(
        service='users', 
        slug='/login', 
        data=request.form
    )

    if status is 200:
        session['user'] = request.form['user']
        if 'next' in request.args:
            return redirect(request.args['next'])
        else:
            return redirect('/')
    
    return content, status, {'Content-Type': 'application/json'}


@app.route('/api/v1/users/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)