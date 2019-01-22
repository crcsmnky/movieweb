import os

from flask import Flask, request, jsonify
from google.cloud import firestore

app = Flask(__name__)
app.secret_key = 'f8b800fdbdabda83018ed4ffb8088b9e'
db = firestore.Client()


@app.route('/api/movies/top', methods=['GET'])
def top_movies():
    movies_ref = db.collection('movies')

    movies = movies_ref.order_by(
        'ratings', direction=firestore.Query.DESCENDING
    ).order_by(
        'avg_rating', direction=firestore.Query.DESCENDING
    ).limit(8).get()

    ret = [m.to_dict() for m in movies]

    return jsonify(ret), 200


@app.route('/api/movies/all', methods=['GET'])
def all_movies():
    skip = int(request.args.get('skip', 0))
    movies_ref = db.collection('movies')

    movies = movies_ref.order_by(
        'ratings', direction=firestore.Query.DESCENDING
    ).order_by(
        'avg_rating', direction=firestore.Query.DESCENDING
    )

    if skip > 0:
        last_movies = movies_ref.order_by(
            'ratings', direction=firestore.Query.DESCENDING
        ).order_by(
            'avg_rating', direction=firestore.Query.DESCENDING
        ).limit(skip).get()
        last_movie = list(last_movies)[-1]

        movies = movies.start_after(last_movie)

    movies = movies.limit(20).get()
    ret = [m.to_dict() for m in movies]

    return jsonify(ret), 200


@app.route('/api/movies/count', methods=['GET'])
def all_movies_count():
    count_ref = db.collection('counts').document('movies').get()
    count = count_ref.to_dict()['count']
    return jsonify({'count': count}), 200


@app.route('/api/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    movie = db.collection('movies').document(str(movieid)).get()
    return jsonify(movie.to_dict()), 200


@app.route('/api/genres/top', methods=['GET'])
def top_genres():
    genres = db.collection('genres').order_by(
        'count', direction=firestore.Query.DESCENDING
    ).limit(10).get()
    ret = [g.to_dict() for g in genres]
    return jsonify(ret), 200


@app.route('/api/genres/all', methods=['GET'])
def all_genres():
    genres = db.collection('genres').order_by(
        'count', direction=firestore.Query.DESCENDING
    ).get()
    ret = [g.to_dict() for g in genres]
    return jsonify(ret), 200


@app.route('/api/genres/<name>', methods=['GET'])
def genre(name):
    skip = int(request.args.get('skip', 0))
    movies_ref = db.collection('movies')

    movies = movies_ref.where(
        'genres', 'array_contains', name
    ).order_by(
        'ratings', direction=firestore.Query.DESCENDING
    ).order_by(
        'avg_rating', direction=firestore.Query.DESCENDING
    )

    if skip > 0:
        last_movies = movies_ref.where(
            'genres', 'array_contains', name
        ).order_by(
            'ratings', direction=firestore.Query.DESCENDING
        ).order_by(
            'avg_rating', direction=firestore.Query.DESCENDING
        ).limit(skip).get()
        last_movie = list(last_movies)[-1]

        movies = movies.start_after(last_movie)
    
    movies = movies.limit(20).get()
    ret = [m.to_dict() for m in movies]

    return jsonify(ret), 200


@app.route('/api/genres/count/<name>', methods=['GET'])
def genre_count(name):
    count_ref = db.collection('genres').document(name).get()
    count = count_ref.to_dict()['count']
    return jsonify({'count': count}), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)