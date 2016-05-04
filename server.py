"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from model import User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template('homepage.html',
                            login=session.get('user'))

@app.route('/users')
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/login')
def login():
    """Prompts user for login info"""
    return render_template('login_form.html')

@app.route('/login-submit', methods=['POST'])
def sumbit_login():
    """checks for login info to log in and if not present, creates user"""

    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(email=username).first()
    # if user already exists, checks password and logs them in if correct. If not, prompts
    # for password again
    if user:
        if user.password == password:
            session['user'] = user.user_id
            flash("You are now logged in")
            return redirect('/users/' + str(user.user_id))
        else:
            flash("Password incorrect")
            return redirect('/login')
    else:
        #instantiates new user and passes user_id to session
        user = User(email=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.user_id
        flash("Your account has been created")
        return redirect('/')

@app.route('/logout')
def logout():
    """logs out user"""
    session['user'] = None
    flash ("You are now logged out")
    return redirect('/')

@app.route("/users/<int:user_id>")
def show_user_profile(user_id):
    """Shows user info"""

    user = User.query.get(user_id)
    
    return render_template("user_info.html", user=user)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
