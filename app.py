from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class Movie():
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    rating = db.Column(db.String, nullable=False)
    img = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    def __init__(self, title, rating, img, description):
        self.title = title
        self.rating = rating
        self.img = img
        self.description = description


class MovieSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'rating', 'img', 'description')


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@app.route('/movie/add', methods=["POST"])
def add_movie():
    if request.content_type != 'application/json':
        return jsonify('data must be json')
    post_data = request.get_json()
    title = post_data.get('title')
    rating = post_data.get('rating')
    img = post_data.get('img')
    description = post_data.get('description')

    new_movie = Movie(title, rating, img, description)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify(movie_schema.dump(new_movie))


@app.route('/movies/add', methods=["POST"])
def add_movies():
    if request.content_type != 'application/json':
        return jsonify('content must be json')
    post_data = request.get_json()
    movies = post_data.get('movies')

    new_movies = []

    for movie in movies:
        title = movie.get('title')
        rating = movie.get('rating')
        img = movie.get('img')
        description = movie.get('description')

        new_movie = Movie(title, rating, img, description)
        db.session.add(new_movie)
        db.session.commit()
        new_movies.append(new_movie)

    return jsonify(movies_schema.dump(new_movies))


@app.route('/movies/get', methods=["GET"])
def get_movies():
    movies = db.session.query(Movie).all()
    return jsonify(movies_schema.dump(movies))


@app.route('/movie/get/<id>', methods=["GET"])
def get_movie(id):
    movie = db.session.query(Movie).filter(Movie.id == id).first()
    return jsonify(movie_schema.dump(movie))


@app.route('/movie/delete/<id>', methods=["DELETE"])
def delete_movie(id):
    movie = db.session.query(Movie).filter(Movie.id == id).first()
    db.session.delete(movie)
    db.session.commit()
    return jsonify('that movie was deleted')


@app.route('/movie/update/<id>')
def update_movie(id):
    if request.content_type != 'application/json':
        return jsonify('data must be json')

    update_data = request.get_json()
    title = update_data.get('title')
    rating = update_data.get('rating')
    img = update_data.get('img')
    description = update_data.get('description')

    movie_to_update = db.session.query(Movie).filter(Movie.id == id).first()

    if title != None:
        movie_to_update.title = title
    if rating != None:
        movie_to_update.rating = rating
    if img != None:
        movie_to_update.img = img
    if description != None:
        movie_to_update.description = description

    db.session.commit()
    return jsonify(movie_schema.dump(movie_to_update))


if __name__ == '__main__':
    app.run(debug=True)
