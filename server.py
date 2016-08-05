"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User,Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html')

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template('movie_list.html', movies=movies)


@app.route('/login_form')
def show_login_form():
    """Displays login form to user."""
    return render_template('login_form.html')

@app.route('/movies/<int:movie_id>')
def show_movie_profile(movie_id):
    """Shows the movie profile page."""

    movies = Movie.query.filter_by(movie_id=movie_id).all()

    # Pass variables to Jinja in order to dispaly on the internet
    return render_template('movie_profile.html', movies=movies)



@app.route('/login', methods=["POST"])
def login_process():
    """ Verifies if user is already in db, if not shows registration page."""
    # Get user input from form submission, send to db and query against it
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter(User.email == email).first() 

    if not user:
        flash('You are not in our system, please create an account.')
        return render_template('/register_form.html') 

    # If user's email exists in the db, send to homepage
    if user.password == password:
        # Add email to session and send to user profile page
        session['email'] = email
        flash('You are successfully signed in')
        return redirect('/users/%d', user.user_id)

    # If user is in system and password doesn't match, take back to login page
    else:
        flash('Incorrect password, try again')
        return redirect('/login_form')

@app.route('/logout')
def logout_process():
    """Logs user out, returns user to homepage."""
    session.pop('email')
    return redirect('/')
        
@app.route('/register_form')
def show_register_form():
    """Displays register form to user."""

    return render_template('/register_form.html')


@app.route('/register', methods=["POST"])
def register_process():
    """ Allows user to register with email and password. """

    # get from previous page instead of making them enter new ones
    email = request.form['email']
    password = request.form['password']
    zipcode = request.form['zipcode']
    age = int(request.form['age'])

    # Create a User object to give to db
    new_user = User(email=email, password=password,zipcode=zipcode, age=age)

    # Insert a new row into the user database with those attributes
    db.session.add(new_user)
    db.session.commit()
    
    user = User.query.filter_by(email=email).first()
    user_id = str(user.user_id)

    # Sign in (store email in session)
    session['email'] = email
    flash('You have created an account and are signed in.')
    response = redirect('/users/%s' % user_id)

    return response

@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Shows the user profile page."""

    user = User.query.filter_by(user_id=user_id).first()
    # query list of ratings for each movie rated by user
    ratings = Rating.query.filter_by(user_id=user_id).all()

    # Takes user id, finds all movies user has rated
    # Returns list of dictionaries containing movie title, movie score, movie id
    user_ratings = []
    for rating in ratings:
        movie_title = Movie.query.filter_by(movie_id=rating.movie_id).one().title
        movie_score = rating.score
        movie = {}
        movie['title'] = movie_title
        movie['score'] = movie_score
        movie['id'] = rating.movie_id
        user_ratings.append(movie)

    # Pass variables to Jinja in order to dispaly on the internet
    return render_template('user_profile.html', user=user, user_ratings=user_ratings)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
