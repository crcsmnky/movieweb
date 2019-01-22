import os
import records

from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = 'f8b800fdbdabda83018ed4ffb8088b9e'

db = records.Database(
    'mysql://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
        dbuser = os.environ.get('DB_USER', 'movielens'),
        dbpass = os.environ.get('DB_PASS', 'movielens'),
        dbhost = os.environ.get('DB_HOST', '127.0.0.1'),
        dbname = os.environ.get('DB_NAME', 'movielens')
    )
)


@app.route('/api/movies/top', methods=['GET'])
def top_movies():
    top_movies_sql = """
    SELECT COUNT(*) as ratings, AVG(r.rating) as avg_rating, m.title, m.year, m.movieid, m.poster
    FROM movies m
    LEFT JOIN ratings r on r.movieid = m.movieid
    GROUP BY m.movieid
    ORDER BY ratings DESC, avg_rating DESC
    LIMIT 8
    """
    movies = db.query(top_movies_sql)

    return jsonify(movies.as_dict()), 200


@app.route('/api/movies/all', methods=['GET'])
def all_movies():
    all_movies_sql = """
    SELECT COUNT(*) as ratings, AVG(r.rating) as avg_rating, m.title, m.year, m.movieid, m.poster
    FROM movies m
    LEFT JOIN ratings r on r.movieid = m.movieid
    GROUP BY m.movieid
    ORDER BY ratings DESC, avg_rating DESC
    LIMIT 20 OFFSET {offset}    
    """
    skip = int(request.args.get('skip', 0))
    rows = db.query(all_movies_sql.format(offset=skip))

    movies = rows.as_dict()
    for m in movies:
        m['title'] = m['title'].decode('unicode_escape').encode('utf-8')

    return jsonify(movies), 200


@app.route('/api/movies/count', methods=['GET'])
def all_movies_count():
    all_movies_count_sql = """
    SELECT COUNT(*) as count FROM movies
    """
    count = db.query(all_movies_count_sql)
    return jsonify(count[0].as_dict()), 200


@app.route('/api/movies/<int:movieid>', methods=['GET'])
def movie(movieid):
    movie_sql = """
    SELECT COUNT(*) as ratings, SUM(r.rating) as total_rating, m.title, m.year, m.movieid, m.poster
    FROM movies m
    LEFT JOIN ratings r on r.movieid = m.movieid
    WHERE m.movieid = {movieid}
    GROUP BY m.movieid
    """
    row = db.query(movie_sql.format(movieid=movieid))
    movie = row[0].as_dict()
    movie['title'] = movie['title'].decode('unicode_escape').encode('utf-8')

    return jsonify(movie), 200


@app.route('/api/genres/top', methods=['GET'])
def top_genres():
    top_genres_sql = """
    SELECT * FROM genres ORDER BY count DESC LIMIT 10
    """
    genres = db.query(top_genres_sql)

    return jsonify(genres.as_dict()), 200


@app.route('/api/genres/all', methods=['GET'])
def all_genres():
    all_genres_sql = """
    SELECT * FROM genres ORDER BY count DESC
    """
    genres = db.query(all_genres_sql)

    return jsonify(genres.as_dict()), 200


@app.route('/api/genres/<name>', methods=['GET'])
def genre(name):
    genre_id_sql = """
    SELECT genreid FROM genres WHERE name='{name}'
    """
    row = db.query(genre_id_sql.format(name=name))
    genreid = row[0].genreid

    genre_movies_sql = """
    SELECT m.movieid, m.title, m.year, m.poster
    FROM movies m
    LEFT JOIN genres_movies gm ON gm.movieid=m.movieid
    WHERE gm.genreid = {genreid}
    ORDER BY m.movieid
    LIMIT 20 OFFSET {offset}
    """
    skip = int(request.args.get('skip', 0))
    rows = db.query(genre_movies_sql.format(genreid=genreid, offset=skip))

    movies = rows.as_dict()
    for m in movies:
        m['title'] = m['title'].decode('unicode_escape').encode('utf-8')

    return jsonify(movies), 200


@app.route('/api/genres/count/<name>', methods=['GET'])
def genre_count(name):
    genre_count_sql = """
    SELECT count FROM genres WHERE name='{name}'
    """

    count = db.query(genre_count_sql.format(name=name))

    return jsonify(count[0].as_dict()), 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, debug=True)