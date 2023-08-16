from cs50 import SQL
import os
from flask import Flask, redirect, render_template, request, session, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
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
        for un in uns:
            if un["username"] == name:
                return render_template(
                    "register.html", message="Username is not available!"
                )
        if pw != cpw:
            return render_template(
                "register.html", message="Password and Confirmation do not match!"
            )
        h = generate_password_hash(pw)
        db.execute(
            "INSERT INTO users(username, hash, downloads) VALUES (?, ?, 0)", name, h
        )
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
    top = get_top()
    return render_template("index.html", top=top, enumerate=enumerate)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    if request.method == "POST":
        query = request.form.get("query")
        N = request.form.get("n")
        tracks = get_tracks(query=query, N=N)
        return render_template("search.html", tracks=tracks, enumerate=enumerate)


@app.route("/download", methods=["POST"])
@login_required
def download():
    if request.method == "POST":
        name = request.form.get("name")
        artists = request.form.get("artists")
        title = f"{name} - {artists}"
        image = request.form.get("image")
        url = get_url(f"{name} {artists} Lyrics")
        album = request.form.get("album")

        # Create a temporary directory to store downloaded files
        dir = "downloads"
        os.makedirs(dir, exist_ok=True)

        # Download the file using the download function
        download_audio(url=url, title=title, path=dir)

        # Get the downloaded file path
        path = os.path.join(dir, f"{title}.mp4")

        # Send the file to the user's browser for download
        response = send_file(path, as_attachment=True)

        # Delete the downloaded file from the server
        os.remove(path)
        print(
            f"name = {name}, artists={artists}, image={image}, album={album}, url={url}"
        )
        check = db.execute(
            "SELECT number FROM downloads WHERE user_id = ? AND image = ? AND title = ?",
            session["user_id"],
            image,
            name,
        )
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
    history = db.execute(
        "SELECT title, artists, image, album, number FROM downloads WHERE user_id = ?",
        session["user_id"],
    )
    total = db.execute("SELECT downloads FROM users WHERE id = ?", session["user_id"])[
        0
    ]["downloads"]
    return render_template(
        "history.html", history=history, total=total, reversed=reversed
    )
