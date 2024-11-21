from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # Relationship to associate users with their movies
    movies = db.relationship('Movie', backref='user', lazy=True, cascade='all, delete-orphan')

    # Relationship for the liked movies (many-to-many)
    liked_movies = db.relationship('Movie', secondary='like', backref='likers', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Movie model for storing movie details
class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    watch_date = db.Column(db.Date)
    genre = db.Column(db.String(50))
    review = db.Column(db.String(500))
    reflections = db.Column(db.String(500))
    watched = db.Column(db.Boolean, default=False)

    # TMDb data: We only need poster_url for now
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)
    poster_url = db.Column(db.String(255), nullable=True)

    # Foreign key to associate each movie with a user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship for the likes
    likes = db.relationship('Like', backref='liked_movie', lazy='dynamic')

    @property
    def tmdb_link(self):
        """Generate the TMDb link for the movie."""
        if self.tmdb_id:
            return f'https://www.themoviedb.org/movie/{self.tmdb_id}'
        return None

    def is_liked_by(self, user):
        """Check if the movie is liked by the current user."""
        return self.likes.filter_by(user_id=user.id).count() > 0

    def like_count(self):
        """Count the number of likes for the movie."""
        return self.likes.count()

    def __repr__(self):
        return f'<Movie {self.title}>'


class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=True)

    user = db.relationship('User', backref='likes', lazy='select')
    movie = db.relationship('Movie', backref='liked_by', lazy='select')

    def __repr__(self):
        return f'<Like {self.user_id} likes movie {self.movie_id}>'
