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
    return render_template("user_list.html", users=users,
                            login=session.get('user'))

@app.route('/login')
def login():
    """Prompts user for login info"""
    return render_template('login_form.html',
                            login=session.get('user'))

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
    
    return render_template("user_info.html", user=user,
                            login=session.get('user'))

@app.route('/movies')
def movie_list():
    """Show list of movies"""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies,
                            login=session.get('user'))

@app.route("/movies/<int:movie_id>")
def show_movie_info(movie_id):
    """Shows movie info"""

    movie = Movie.query.get(movie_id)

    # gets logged-in user id from session cookie
    user_id = session.get('user')

    # gets rating from user for movie if it exists, otherwise binds the rating as None
    if user_id:    
        user_rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        
        if user:
            prediction = user.predict_rating(movie)

    # if user hasn't rated a movie, uses predicted rating
    if prediction:
        effective_rating = prediction
    # if user has rated, uses rating
    elif user_rating:
        effective_rating = user_rating.score
    # if user hasn't rated and unable to predict a rating, uses None
    else: 
        effective_rating = None
    
    # instantiates the Eye as a user
    the_eye = User.query.filter_by(email="the-eye@of-judgment.com").one()
    
    #Grabs eyes rating object if it exists
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    # predicts the eye's rating if it doesn't have a score of it's own
    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)
    else: 
        eye_rating = eye_rating.score

    # if there is both a rating by the eye and an effective rating, determines the difference
    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)
    else: 
        difference = None

    # Depending on how different we are from the Eye, choose a message

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has brought me" +
            " to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly failed you.",
        "That movie is great. For a clown to watch. Idiot.",
        "Words cannot express the awfulness of your taste."
    ]

    # since there is a max diff of 4, uses an index equal to the difference
    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    #if unable to predict, no beratement
    else:
        beratement = None

    return render_template("movie_info.html", 
                           movie=movie,
                           login=user_id,
                           average=avg_rating,
                           prediction=prediction,
                           user_rating=user_rating,
                           beratement=beratement)


@app.route('/rating-submit', methods=['POST'])
def sumbit_rating():
    """checks for existing review by user, if none, creates new."""

    user_id = session.get('user')

    rating = request.form.get("rating")

    movie_id = request.form.get('movie_id')

    review = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    # if rating already exists, checks updates review, if not, creates review
    # for password again
    if review:
        review.score = int(rating)
        flash("Your rating has been updated")
        db.session.commit()
        return redirect('/movies/' + str(review.movie_id))

    else:
        rating = Rating(user_id=user_id, movie_id=movie_id, score=rating)
        db.session.add(rating)
        db.session.commit()
        flash("Your rating has been created")
        return redirect('/movies/' + str(rating.movie_id))


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
