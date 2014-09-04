# MovieWeb Demo App

## Setup

    $ pip install -r requirements.txt

## Data

- Download [MovieLens 10M](http://grouplens.org/datasets/movielens/) archive and unzip
- Load the dataset by running the following:

    $ python dataset/movielens.py [/path/to/movies.dat] [/path/to/ratings.dat]

The script will import the data set and create the following collections (with indexes):

- movies
- users
- ratings
- genres

## Running

    $ python app.py

## Notes

The script assumes that MongoDB is running on `localhost` and the database name `movielens`

