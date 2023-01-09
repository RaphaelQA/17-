# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    rating = fields.Int()
    genre_id = fields.Str()
    director_id = fields.Str()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()
class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

Director_schema = DirectorSchema()
Directors_schema = DirectorSchema(many=True)

Genre_schema = GenreSchema()
Genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


# +++++++ m ++++++
@movie_ns.route("/")
class MovieView(Resource):
    def get(self):
        movies_query = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            movies_query = movies_query.query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.query.filter(Movie.director_id == director_id)

        return movies_schema.dump(movies_query.all()), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)
        return "Movie created", 201

@movie_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "User not found"
        return movie_schema.dump(movie), 200

    def put(self, mid: int):
        updated_movie = db.session.query(Movie).filter(Movie.id == mid).update(request.json)
        if updated_movie != 1:
            return "Not updated"

        db.session.commit()
        return "", 204
    def delete(self, mid: int):
        delete_movie = db.session.query(Movie).get(mid)
        if not delete_movie:
            return "Movie not found", 404

        db.session.delete(delete_movie)
        db.session.commit()
        return "", 204

# +++++++ d ++++++
@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_derectors = db.session.query(Director)
        return Directors_schema.dump(all_derectors), 201

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)
        db.session.add(new_director)
        db.session.commit()
        return "Director created", 201

@director_ns.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did: int):
        try:
            director = db.session.query(Director).get(did)
            return Director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404

    def put(self, did: int):
        director = Director.query.get(did)
        request_json = request.json
        if "name" in request_json:
            director.name = request_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "director updated", 204

    def delete(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "director not found", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204

# ++++++ g +++++
@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre)
        return Genres_schema.dump(all_genres), 201

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)
        db.session.add(new_genre)
        db.session.commit()
        return "Genres created", 201

@genre_ns.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid: int):
        try:
            genre = db.session.query(Genre).get(gid)
            return Genre_schema.dump(genre), 200
        except Exception:
            return str(Exception), 404

    def put(self, gid: int):
        genre = Genre.query.get(gid)
        request_json = request.json
        if "name" in request_json:
            Genre.name = request_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "genre updated", 204

    def delete(self, did: int):
        genre = db.session.query(Genre).get(did)
        if not genre:
            return "genre not found", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
