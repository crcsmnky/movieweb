import os
import requests
import json

from flask import Flask
from flask import request, render_template, abort

app = Flask(__name__)
app.secret_key = 'f845dec4583082b8bd27d4614cb5b858'

API = {
    'host': 'localhost',
    'port': 6000,
    'endpoint': 'api'
}

BASE_URL = 'http://{host}:{port}/{endpoint}'.format(
    host=API['host'], port=API['port'], endpoint=API['endpoint'])


@app.route('/', methods=['GET'])
def index():
    tops = {}
    for res in ['movies', 'genres']:
        resp = requests.get(BASE_URL + '/{res}/top'.format(res=res))
        tops[res] = resp.json()

    return render_template('index.html', movies=tops['movies'], genres=tops['genres'])


@app.route('/movies', methods=['GET'])
def movies():
    skip = int(request.args.get('skip', 0))
    mresp = requests.get(BASE_URL + '/movies/all?skip={skip}'.format(skip=skip))
    movies = mresp.json()
    
    cresp = requests.get(BASE_URL + '/movies/count')
    count = cresp.json()['count']

    return render_template('movies.html', movies=movies, skip=skip, page=20, count=count)


@app.route('/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    resp = requests.get(BASE_URL + '/movies/{movieid}'.format(movieid=movieid))
    if resp.status_code == 404:
        abort(resp.status_code)
    movie = resp.json()
    return render_template('movie.html', movie=movie)


@app.route('/genres', methods=['GET'])
def genres():
    resp = requests.get(BASE_URL + '/genres/all')
    genres = resp.json()
    return render_template('genres.html', genres=genres)


@app.route('/genres/<name>', methods=['GET'])
def genre(name):
    skip = int(request.args.get('skip', 0))
    resp = requests.get(
        BASE_URL + '/genres/{name}?skip={skip}'.format(
            name=name, 
            skip=skip
        )
    )
    if resp.status_code == 404:
        abort(resp.status_code)

    movies = resp.json()

    cresp = requests.get(
        BASE_URL + '/genres/count/{name}'.format(
            name=name
        )
    )
    count = cresp.json()['count']

    return render_template('genre.html', genre=name, movies=movies, skip=skip, page=20, count=count)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    