"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect, url_for
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined


app = Flask(__name__)
app.secret_key = "dev"
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/movies")
def all_movies():

    movies = crud.get_movies()
    return render_template("all_movies.html", movies=movies)

@app.route("/movies/<movie_id>")
def show_movie(movie_id):
    movie = crud.get_movie_by_id(movie_id)
    return render_template("movie_details.html", movie=movie)

@app.route("/users")
def all_users():
    
    users = crud.get_users()
    return render_template("all_users.html", users=users)

@app.route("/users/<user_id>")
def show_user(user_id):
    user = crud.get_user_by_id(user_id)
    return render_template("user_details.html", user=user)

@app.route("/users", methods=["POST"])
def create_user():
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("An account with that email already exists")
    else:
        user= crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("Account creation successful")
    return redirect("/")

@app.route("/login", methods=["POST"])
def login_user():

    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("Login attempt failed - Username or Password incorrect")
    else:
        session["user_email"] = user.email
        flash(f"Login successful")
    return redirect("/")

@app.route("/movies/<movie_id>/ratings", methods=["POST"])
def create_rating(movie_id):

    current_user = session.get("user_email")
    rating_score = request.form.get("rating")

    if current_user is None:
        flash("Please log in to be able to rate movies")
    else:
        user = crud.get_user_by_email(current_user)
        movie = crud.get_movie_by_id(movie_id)
        rating = crud.create_rating(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()

        flash(f"Your rating of {rating_score} has been assigned")
    
    return redirect(f"/movies/{movie_id}")

@app.route("/update_Rating", methods=["POST"])
def update_rating():
    rating_id = request.json["rating_id"]
    updated_score = request.json["updated_score"]
    crud.update_rating(rating_id, updated_score)
    db.session.commit

    return "Rating has been updated"


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
