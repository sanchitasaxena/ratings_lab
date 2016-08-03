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

@app.route('/sign_in', methods=["GET"])
def register_form():
    """ Verifies if user is already in db, if not shows registration page."""
    # Get user input from form submission, send to db and query against it
    email = request.args.get('email')
    users = User.query.all()

    # If user's email exists in the db, send to homepage

    # Else redirect them to the registration page
    if email in users:
        #and email matches password <- for later
        # Add email to session
        session['email'] = email
        flash('You are successfully signed in')
        return redirect('/')
        
    else:
        flash('You are not in our system, please create an account.')
        return render_template('/register_form.html')

@app.route('/register_form', methods=["POST"])
def register_process():
    """ Allows user to register with email and password. """
    # get from previous page instead of making them enter new ones
    email = request.form.get('email')
    password = request.form.get('password')

    # Create a User object to give to db
    new_User = User(email,password)

    # Insert a new row into the user database with those attributes
    db.session.add(new_User)
    db.session.commit()

    # Sign in (store email in session)
    session['email'] = email
    flash('You have created an account and are signed in.')
    return redirect('/')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
