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

@app.route('/login_form')
def show_login_form():
    """Displays login form to user."""
    return render_template('login_form.html')


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

@app.route('/users/<user_id>')
def show_user_profile():
    """Shows the user profile page."""

    return render_template('user_profile.html')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
