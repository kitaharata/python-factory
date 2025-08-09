import datetime
import secrets

from flask import Flask, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder=".")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Generate a secure password, and store it for printing to the console.
admin_password = secrets.token_urlsafe(16)
users = {"admin": generate_password_hash(admin_password)}


@auth.verify_password
def verify_password(username, password):
    """Callback function to verify passwords."""
    if username in users and check_password_hash(users.get(username), password):
        return username


class Post(db.Model):
    """Model for a blog post."""

    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


def create_tables():
    """Create database tables."""
    with app.app_context():
        db.create_all()
    print("Database tables created.")


@app.route("/")
@auth.login_required(optional=True)
def index():
    """Homepage. Anyone can view posts."""
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template("1754665230.html", posts=posts, user=auth.current_user())


@app.route("/post", methods=["GET", "POST"])
@auth.login_required
def post_article():
    """New post page. Only authenticated users can post."""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = auth.current_user()

        new_post = Post(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("1754665231.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@auth.login_required
def edit_post(post_id):
    """Edit a post. Only authenticated users can edit."""
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("1754665231.html", post=post)


@app.route("/delete/<int:post_id>", methods=["POST"])
@auth.login_required
def delete_post(post_id):
    """Delete a post. Only authenticated users can delete."""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    from waitress import serve

    create_tables()
    print("---User Information---")
    print("Username: admin")
    print(f"Password: {admin_password}")
    print("----------------------")
    serve(app, host="127.0.0.1", port=8080)
