from flask_admin.contrib.sqla import ModelView
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import admin, app, db
from app.forms import MovieForm, SignupForm, LoginForm
from app.forms import EditProfileForm, DeleteAccountForm
from app.models import Movie, User, Like
from werkzeug.security import generate_password_hash, check_password_hash # noqa
from flask_login import login_user, logout_user, current_user, login_required
import requests

# Flask-Admin views
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(Like, db.session))

# Constants for TMDb API
TMDB_API_KEY = 'bcfe172528284610ed6f37ec96a49fff'
TMDB_API_URL = 'https://api.themoviedb.org/3'

# Landing page for when the user is not logged in
@app.route('/')
def landing_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('landing_page.html')


# Route for the home page displaying all movies
@app.route('/home')
@login_required
def home():
    sort_option = request.args.get('sort', 'default')  # Default sorting option

    # Sorting logic for movies based on the selected option
    if sort_option == 'earliest':
        movies = Movie.query.order_by(Movie.watch_date.asc()).all()
    elif sort_option == 'latest':
        movies = Movie.query.order_by(Movie.watch_date.desc()).all()
    elif sort_option == 'rating_desc':
        movies = Movie.query.order_by(Movie.rating.desc()).all()
    elif sort_option == 'rating_asc':
        movies = Movie.query.order_by(Movie.rating.asc()).all()
    elif sort_option == 'title':
        movies = Movie.query.order_by(Movie.title.asc()).all()
    elif sort_option == 'title_desc':
        movies = Movie.query.order_by(Movie.title.desc()).all()
    elif sort_option == 'None':
        movies = Movie.query.all()
    else:
        movies = Movie.query.all()

    return render_template('home.html', movies=movies)


# Route for adding a new movie
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    form = MovieForm()
    prompt_tmdb = False  # Default value for the prompt variable
    error_message = None  # Initialize error message

    if form.validate_on_submit():
        movie_title = form.title.data  # Get the title from the form

        # Search TMDb for the movie title
        search_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}'
        response = requests.get(search_url)

        if response.status_code == 200:
            movie_data = response.json()

            # If movie is found
            if 'results' in movie_data and movie_data['results']:
                for movie in movie_data['results']:
                    if movie['original_title'].lower() == movie_title.lower():
                        tmdb_id = movie['id']

                        # Check if this movie already exists for this user
                        existing_movie = Movie.query.filter_by(user_id=current_user.id, tmdb_id=tmdb_id).first()
                        if existing_movie:
                            flash("This movie already exists in your collection.", "danger")
                            return render_template('add_movie.html', form=form, prompt_tmdb=prompt_tmdb, error_message=error_message)

                        poster_url = f'https://image.tmdb.org/t/p/w500{movie["poster_path"]}' if movie.get('poster_path') else None

                        new_movie = Movie(
                            title=movie_title,
                            tmdb_id=tmdb_id,
                            poster_url=poster_url,
                            genre=form.genre.data,
                            watch_date=form.watch_date.data,
                            rating=int(form.rating.data) if form.rating.data else 0,
                            review=form.review.data,
                            reflections=form.reflections.data,
                            watched=form.watched.data,
                            user_id=current_user.id
                        )
                        db.session.add(new_movie)
                        db.session.commit()

                        # After adding, redirect to the home page
                        return redirect(url_for('home'))
            else:
                flash("No results found for the movie title. Try finding its exact TMDb name (the movie's name may be in its local language).", "danger")
                prompt_tmdb = True
        else:
            flash(f"Failed to retrieve movie data from TMDb. Status Code: {response.status_code}", "danger")
            prompt_tmdb = True

        # If movie is not found, proceed without poster URL
        new_movie = Movie(
            title=movie_title,
            tmdb_id=None,  # TMDb ID is not available
            poster_url=None,  # No poster URL if movie is not found
            genre=form.genre.data,
            watch_date=form.watch_date.data,
            rating=int(form.rating.data) if form.rating.data else 0,
            review=form.review.data,
            reflections=form.reflections.data,
            watched=form.watched.data,
            user_id=current_user.id
        )
        db.session.add(new_movie)
        db.session.commit()

        # After adding, redirect to the home page
        return redirect(url_for('home'))

    return render_template('add_movie.html', form=form, prompt_tmdb=prompt_tmdb, error_message=error_message)


# Route for viewing unwatched movies
@app.route('/unwatched')
@login_required
def view_unwatched():
    unwatched_movies = Movie.query.filter_by(watched=False, user_id=current_user.id).all()
    return render_template('home.html', movies=unwatched_movies)


# Route for viewing watched movies
@app.route('/watched')
@login_required
def view_watched():
    watched_movies = Movie.query.filter_by(watched=True, user_id=current_user.id).all()
    return render_template('home.html', movies=watched_movies)


# Route for marking a movie as watched
@app.route('/watched/<int:movie_id>')
@login_required
def mark_watched(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash("You don't have permission to update this movie.", 'danger')
        return redirect(url_for('home'))
    movie.watched = True
    db.session.commit()
    flash('Movie marked as watched!', 'success')
    return redirect(url_for('home'))


# Route for marking a movie as unwatched
@app.route('/unwatched/<int:movie_id>')
@login_required
def mark_unwatched(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash("You don't have permission to update this movie.", 'danger')
        return redirect(url_for('home'))
    movie.watched = False
    db.session.commit()
    flash('Movie marked as unwatched!', 'success')
    return redirect(url_for('home'))


# Route for editing a movie
@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash("You don't have permission to edit this movie.", 'danger')
        return redirect(url_for('home'))

    form = MovieForm(obj=movie)
    if form.validate_on_submit():
        new_title = form.title.data

        # Check if another movie with the same title exists for this user
        existing_movie = Movie.query.filter(
            Movie.user_id == current_user.id,
            Movie.title.ilike(new_title),
            Movie.id != movie.id
        ).first()

        if existing_movie:
            flash("This movie already exists in your collection.", "danger")
            return render_template('edit_movie.html', form=form, movie=movie)

        # If the title is changed, search TMDb for the new title
        if new_title.lower() != movie.title.lower():
            search_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={new_title}'
            response = requests.get(search_url)

            if response.status_code == 200:
                movie_data = response.json()

                if 'results' in movie_data and movie_data['results']:
                    for tmdb_movie in movie_data['results']:
                        if tmdb_movie['original_title'].lower() == new_title.lower():
                            # Update movie details with TMDb data
                            movie.tmdb_id = tmdb_movie['id']
                            movie.poster_url = f'https://image.tmdb.org/t/p/w500{tmdb_movie["poster_path"]}' if tmdb_movie.get('poster_path') else None
                            break
                    else:
                        flash("No exact match found on TMDb. Updating details without changing poster.", "warning")
                        movie.poster_url = None
                else:
                    flash("No results found on TMDb. Updating details without changing poster.", "warning")
                    movie.poster_url = None
            else:
                flash(f"Failed to retrieve movie data from TMDb. Status Code: {response.status_code}", "danger")
                movie.poster_url = None

        # Update other fields from the form
        movie.title = new_title
        movie.genre = form.genre.data
        movie.watch_date = form.watch_date.data
        movie.rating = int(form.rating.data) if form.rating.data else 0
        movie.review = form.review.data
        movie.reflections = form.reflections.data
        movie.watched = form.watched.data

        db.session.commit()
        flash('Movie updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_movie.html', form=form, movie=movie)


# Route for deleting a movie
@app.route('/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash("You don't have permission to delete this movie.", 'danger')
        return redirect(url_for('home'))
    db.session.delete(movie)
    db.session.commit()
    flash('Movie deleted successfully!', 'success')
    return redirect(url_for('home'))


# Route for signing up a new user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


# Route for logging in an existing user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        # Log the user in
        remember_me = form.remember.data  # Capture "Remember Me" checkbox
        login_user(user, remember=remember_me)

        # Flash success message
        flash('Login successful!', 'success')
        return redirect(url_for('home'))

    return render_template('login.html', form=form)


# Route for logging out the user
@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('login'))


# Route for viewing account details
@app.route('/account')
@login_required
def account():
    movies = Movie.query.filter_by(user_id=current_user.id).all()
    return render_template('account.html', movies=movies)


# Route for editing user profile
@app.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    delete_form = DeleteAccountForm()

    if form.validate_on_submit():
        # Validate password confirmation
        if form.password.data and form.password.data != form.confirm_password.data:
            flash('Passwords do not match!', 'danger')
            return render_template('edit_profile.html', form=form, delete_form=delete_form)

        # Update profile details
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('account'))

    # Render the form on GET request or failed validation
    return render_template('edit_profile.html', form=form, delete_form=delete_form)


# Route for deleting an account
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)

    if user:
        # Delete all movies associated with the user
        Movie.query.filter_by(user_id=user.id).delete()

        # Delete the user account
        db.session.delete(user)
        db.session.commit()

        flash("Your account and all associated movies have been deleted.", "success")
        logout_user()
        return redirect(url_for('signup'))
    else:
        flash("Error: Account not found.", "danger")
        return redirect(url_for('edit_profile'))


# Route for filtering and sorting movies
@app.route('/filter', methods=['GET', 'POST'])
@login_required
def filter_movies():
    # Only handle the sorting parameter
    sort_by = request.args.get('sort_by', 'title')

    # Start with a query filtered by the current user
    query = Movie.query.filter_by(user_id=current_user.id)

    # Apply sorting based on the `sort_by` parameter
    if sort_by == 'date':
        query = query.order_by(Movie.watch_date.desc())
    elif sort_by == 'rating':
        query = query.order_by(Movie.rating.desc())
    elif sort_by == 'title':
        query = query.order_by(Movie.title)

    # Execute the query and fetch results
    movies = query.all()

    # Return the sorted movies to the template
    return render_template('home.html', movies=movies)


# Route for user profiles
@app.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    movies = Movie.query.filter_by(user_id=user_id).all()
    return render_template('user_profile.html', user=user, movies=movies)


# Route for liking movies
@app.route('/toggle_like/<int:movie_id>', methods=['POST'])
@login_required
def toggle_like(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # Check if the user has already liked the movie
    existing_like = Like.query.filter_by(movie_id=movie_id, user_id=current_user.id).first()

    if existing_like:
        # If the user has liked the movie, remove the like
        db.session.delete(existing_like)
        db.session.commit()
        liked = False
    else:
        # If the user has not liked the movie, add a like
        new_like = Like(movie_id=movie_id, user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()
        liked = True

    # Return the updated like status and count
    like_count = movie.like_count()
    return jsonify({'liked': liked, 'like_count': like_count})
