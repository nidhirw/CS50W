import os
import string
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def index():
    """Log in to an account"""
    state = signin()
    if state == 0:
        # return render_template("index.html", loggedin=session["loggedin"], username=session["username"], nav_bar=True)
        return render_template("index.html", loggedin=False, username=None, nav_bar=False)
    elif state == 1:
        return redirect(url_for('search'))
    elif state == 2:
        return render_template("error.html", message="Username or password incorrect.", login=True, nav_bar=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in to an account"""

    state = signin()
    if state == 0:
        # return render_template("login.html", loggedin=session["loggedin"], username=session["username"], nav_bar=False)
        return render_template("login.html", loggedin=False, username=None, nav_bar=False)
    elif state == 1:
        return redirect(url_for('search'))
    elif state == 2:
        return render_template("error.html", message="Username or password incorrect.", login=True, nav_bar=True)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register for an account"""

    username = None
    password = None

    username = request.form.get("username")
    password = request.form.get("password")

    # Making sure both fields are filled by a user
    if username != None and password != None:
        # Checking if a person already exists with the particular username
        stored_username = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        if len(stored_username) == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username":username, "password": password})
            db.commit()
            return render_template("success.html", title="Success!", message="You have successfully registered.")
        else:
            return render_template("error.html", message="User already exists with that username.", register=True)

    return render_template("register.html")

@app.route("/logout", methods=["POST"])
def logout():

    session["loggedin"] = False
    session["username"] = None
    return render_template("success.html", title="Logged Out", message="You have successfully logged out. ", logged_out=True, nav_bar=False)

@app.route("/search", methods=["GET", "POST"])
def search():
    
    search = None
    search_value = None
    search_results = None

    if session["loggedin"] == True:
        search = request.form.get("search")
        search_value = request.form.get("search_value")
        
        if search != None and search_value!= None:
            if search == "isbn":
                search_results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": f"%{search_value.upper()}%"}).fetchall()
            elif search == "title":
                search_results = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title": f"%{string.capwords(search_value)}%"}).fetchall()
            elif search == "author":   
                search_results = db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": f"%{string.capwords(search_value)}%"}).fetchall()
        return render_template("search.html", title="Search", search_results=search_results, loggedin=session["loggedin"], username=session["username"], nav_bar=True)
    return render_template("login.html", loggedin=session["loggedin"], username=session["username"], nav_bar=False)

@app.route("/search/<isbn>", methods=["GET", "POST"])
def book(isbn):
    """Show details for a specific book"""

    review_results = None
    
    if session["loggedin"] == True:

        book_details = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": isbn}).fetchone()
        if book_details == None:
            return render_template("error.html", message="No book with that ISBN")

        # checking if a user has submitted a review
        user_review = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": session["username"], "isbn": isbn}).fetchone()
        
        if user_review == None:

            # adding a review
            new_rating = None
            new_review = None

            new_rating = request.form.get("rating")
            new_review = request.form.get("review")

            if new_rating != None and new_review != None:
                db.execute("INSERT INTO reviews (review_id, review, rating, username, isbn) VALUES (:review_id, :review, :rating, :username, :isbn)",
                    {"review_id":isbn+session["username"], "review":new_review, "rating":new_rating, "username":session["username"], "isbn":isbn})
                db.commit()
                user_review = True

        # getting reviews
        review_results = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        no_ratings, avg_rating = get_response_Goodreads(isbn)

        return render_template("book.html", loggedin=session["loggedin"], username=session["username"], book=book_details, nav_bar=True, user_review=user_review, review_results=review_results, no_ratings=no_ratings, avg_rating=avg_rating)

    return render_template("login.html", loggedin=session["loggedin"], username=session["username"], nav_bar=False)


@app.route("/api/<isbn>", methods=["GET", "POST"])
def api_isbn(isbn):
    """Return details about a book"""

    # Make sure the book exists
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if len(book) == 0:
        return jsonify({"error": "No book found with that isbn"}), 404

    no_ratings, avg_rating = get_response_Goodreads(isbn)
    
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": isbn,
        "review_count": no_ratings,
        "average_score": avg_rating
    })


def signin():
    """Log in to an account"""
    state = 0

    username = None
    password = None

    username = request.form.get("username")
    password = request.form.get("password")

    # Making sure both fields are filled by a user
    if username != None and password != None:

        loggedin_username = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone()
        loggedin_password = db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone()

        if loggedin_username != None and loggedin_password != None and loggedin_username[0] == username and loggedin_password[0] == password:
            session["username"] = username
            session["loggedin"] = True
            state = 1
        else:
            state = 2
    
    return state

def get_response_Goodreads(isbn):

    # making a request to Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9m4IojSSVZAt4NA3V2wsw", "isbns": isbn})
    
    if res.status_code == 200:
        data = res.json()
        no_ratings = data["books"][0]["work_ratings_count"]
        avg_rating = data["books"][0]["average_rating"]
    else:
        no_ratings = None
        avg_rating = None
    
    return no_ratings, avg_rating