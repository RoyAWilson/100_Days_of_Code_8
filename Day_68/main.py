from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create user_loader callback as per documentation:


def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE TABLE IN DB - add MixIn functionality


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


# TODO fix the routing to index.html that has stopped working since adding user authentication.

@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hash_and_salted_password = generate_password_hash(request.form.get('password'),
                                                          method='pbkdf2:sha256',
                                                          salt_length=8
                                                          )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('secrets'))
    return render_template("register.html")


@ app.route('/login')
def login():
    if request.method == 'POST':
        email = request.form.get(email)
        password = request.form.get(password)
        # Get user by email
        result = db.session.execute(
            db.select(User).where(User.email) == email)
        user = result.scalar()
        # Authenticate User:
        if check_password_hash(user.password, password):
            login_user(user)
            return url_for('secrets')
    return render_template("login.html")


@ app.route('/secrets')
@ login_required
def secrets():
    return render_template("secrets.html")


@ app.route('/logout')
def logout():
    pass


@ app.route('/download')
@login_required
def download():
    return send_from_directory('static', path='files/cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
