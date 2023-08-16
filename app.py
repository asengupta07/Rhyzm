from cs50 import SQL
import os
from flask import Flask, redirect, render_template, request, session, send_file
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from mutagen.mp4 import MP4, MP4Cover
from project import login_required, get_top, get_tracks, download_audio, get_url

app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///rhyzm.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template(
                "login.html", message="Invalid username and/or password!"
            )

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        name = request.form.get("username")
        pw = request.form.get("password")
        cpw = request.form.get("confirmation")
        uns = db.execute("SELECT username FROM users")

        # Check if username is available
        for un in uns:
            if un["username"] == name:
                return render_template(
                    "register.html", message="Username is not available!"
                )

        # Check if password matches confirmation
        if pw != cpw:
            return render_template(
                "register.html", message="Password and Confirmation do not match!"
            )

        # Generate password hash
        h = generate_password_hash(pw)

        # Insert new user data into database
        db.execute(
            "INSERT INTO users(username, hash, downloads) VALUES (?, ?, 0)", name, h
        )

        # Redirect to login screen
        return redirect("/login")

    if request.method == "GET":
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def index():
    # Get global top tracks in a list of dicts
    top = get_top()

    # Render index template
    return render_template("index.html", top=top, enumerate=enumerate)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")

    else:
        # Get query and required number of results from form
        query = request.form.get("query")
        N = request.form.get("n")

        # Get search results
        tracks = get_tracks(query=query, N=N)

        # Render search results
        return render_template("search.html", tracks=tracks, enumerate=enumerate)


@app.route("/download", methods=["POST"])
@login_required
def download():
    if request.method == "POST":
        # Get download information from form
        name = request.form.get("name")
        artists = request.form.get("artists")
        title = f"{name} - {artists}"
        image = request.form.get("image")
        album = request.form.get("album")

        # Get youtube url
        url = get_url(f"{name} {artists} Lyrics")

        # Create a temporary directory to store downloaded files
        dir = "downloads"
        os.makedirs(dir, exist_ok=True)

        # Download the file using the download_audio function
        download_audio(url=url, title=title, path=dir)

        # Get the downloaded file path
        path = os.path.join(dir, f"{title}.mp4")

        # Open the MP4 file
        mp4 = MP4(path)

        # Add metadata
        mp4["\xa9nam"] = name  # Title of the song
        mp4["\xa9ART"] = artists  # Artist name
        mp4["\xa9alb"] = album  # Album name

        response = requests.get(image)
        cover_data = response.content

        # Set the downloaded cover image as the cover art
        mp4["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

        # Save the changes
        mp4.save()

        # Send the file to the user's browser for download
        response = send_file(path, as_attachment=True)

        # Delete the downloaded file from the server
        os.remove(path)

        # Check if user has downloaded the song before
        check = db.execute(
            "SELECT number FROM downloads WHERE user_id = ? AND image = ? AND title = ?",
            session["user_id"],
            image,
            name,
        )

        # Modify downloads table in database accordingly
        if len(check) != 1:
            db.execute(
                "INSERT INTO downloads(user_id, title, artists, image, album, number) VALUES (?,?,?,?,?,?)",
                session["user_id"],
                name,
                artists,
                image,
                album,
                1,
            )
        else:
            db.execute(
                "UPDATE downloads SET number = ? WHERE image = ? AND user_id = ?",
                (check[0]["number"] + 1),
                image,
                session["user_id"],
            )

        # Modify users table in database
        n = db.execute("SELECT downloads FROM users WHERE id = ?", session["user_id"])
        db.execute(
            "UPDATE users SET downloads = ? WHERE id = ?",
            (n[0]["downloads"] + 1),
            session["user_id"],
        )

        return response


@app.route("/history")
@login_required
def history():
    # Get history
    history = db.execute(
        "SELECT title, artists, image, album, number FROM downloads WHERE user_id = ?",
        session["user_id"],
    )

    # Get total number of downloads for the user
    total = db.execute("SELECT downloads FROM users WHERE id = ?", session["user_id"])[
        0
    ]["downloads"]

    # Render history
    return render_template(
        "history.html", history=history, total=total, reversed=reversed
    )
