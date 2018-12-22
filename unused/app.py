import os
from flask import Flask
from flask import request, render_template, redirect, url_for, flash, session
from flask.ext.pymongo import PyMongo
import pymongo
from datetime import datetime
from functools import wraps


app = Flask(__name__)

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'movielens'

app.secret_key = '34ef8d4064770c8f97f2b0e060bb91d0'

mongo = PyMongo(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'userid' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
def index():
    movies = mongo.db.movies.find({}).sort('ratings', pymongo.DESCENDING).limit(6)
    users = mongo.db.users.find({}).sort('ratings', pymongo.DESCENDING).limit(10)
    genres = mongo.db.genres.find({}).sort('count', pymongo.DESCENDING).limit(10)
    return render_template('index.html', movies=movies, users=users, genres=genres)


@app.route('/movies', methods=['GET'])
def movies():
    skip = int(request.args.get('skip', 0))
    movies = mongo.db.movies.find({}).sort('ratings', pymongo.DESCENDING).skip(skip).limit(20)
    return render_template('movies.html', movies=movies, count=movies.count(), skip=skip, page=20, step=5)


@app.route('/rate/<int:movieid>', methods=['POST'])
@login_required
def rate(movieid):
    userid = session['userid']
    query = {
        'userid': userid,
        'movieid': movieid
    }
    update = {'$set': {
        'rating': int(request.form['rating']),
        'ts': datetime.now()
    }}
    mongo.db.ratings.update(query, update, upsert=True)

    return redirect('/movies/{movieid}'.format(movieid=movieid))


@app.route('/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    movie = mongo.db.movies.find_one({'movieid': movieid})

    if 'userid' in session:
        userid = session['userid']
        rating = mongo.db.ratings.find_one({'movieid': movieid, 'userid': userid})
        recs = mongo.db.predictions.find({'userid': userid}).sort(
            'rating', pymongo.DESCENDING).limit(100)
        movieids = [r['movieid'] for r in recs]

        try:
            movieids.remove(movie['movieid'])
        except:
            pass

        movies = mongo.db.movies.find({'movieid': {'$in': movieids },
            'genres': {'$in': movie['genres']}}).limit(10)

    else:
        rating = None
        movies = None
        movieids = []

    return render_template('movie.html', movie=movie, rating=rating, movies=movies, page=10, step=5, count=len(movieids))


@app.route('/login', methods=['GET','POST'])
def login():
    if 'userid' in session:
        if 'next' in request.args:
            return redirect(request.args['next'])
        else:
            return redirect(url_for('index'))

    if request.method == 'POST':
        userid = int(request.form['userid'])
        user = mongo.db.users.find_one({'userid': userid})
        if user is None:
            flash('Error: User ID not found. Please try again.', 'danger')
            return render_template('login.html')

        session['userid'] = user['userid']

        if 'next' in request.args:
            return redirect(request.args['next'])
        else:
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid')
    return redirect(url_for('index'))


@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    skip = int(request.args.get('skip', 0))
    recs = mongo.db.predictions.find(
        {'userid': session['userid']}).sort(
            'rating', pymongo.DESCENDING).skip(skip).limit(10)
    count = recs.count()
    recs = {r['movieid']: r for r in recs}
    movies = mongo.db.movies.find({'movieid' : {'$in': recs.keys()}})

    ret = []
    for movie in movies:
        movie['rating'] = recs[movie['movieid']]['rating']
        ret.append(movie)

    return render_template('recommendations.html', movies=ret, count=count, skip=skip, step=5, page=10)


@app.route('/ratings', methods=['GET'])
@login_required
def ratings():
    skip = int(request.args.get('skip', 0))
    ratings = mongo.db.ratings.find(
        {'userid': session['userid']}).sort(
            'rating', pymongo.DESCENDING).skip(skip).limit(10)
    count = ratings.count()
    ratings = {rating['movieid']: rating for rating in ratings}
    movies = mongo.db.movies.find({'movieid' : {'$in': ratings.keys()}})

    ret = []
    for movie in movies:
        movie['rating'] = ratings[movie['movieid']]['rating']
        ret.append(movie)

    return render_template('ratings.html', movies=ret, count=count, skip=skip, step=5, page=10)


@app.route('/genres', methods=['GET'])
def genres():
    genres = mongo.db.genres.find({}).sort('count', pymongo.DESCENDING)
    return render_template('genres.html', genres=genres)


@app.route('/genre/<name>', methods=['GET'])
def genre(name):
    skip = int(request.args.get('skip', 0))
    movies = mongo.db.movies.find({'genres': name}).sort('ratings', pymongo.DESCENDING).skip(skip).limit(20)
    return render_template('genre.html', movies=movies, skip=skip, step=5, page=20, count=movies.count(), genre=name)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)