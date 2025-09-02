from flask import Flask, Response, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from models import User
from routes import bp_messanger, bp_user
from settings import DatabaseConfig

app = Flask(__name__)
app.config.from_object(DatabaseConfig)

login_manager = LoginManager()
login_manager.login_view = "login"  # type: ignore
login_manager.init_app(app)

csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    return user


@app.after_request
def add_security_headers(response: Response) -> Response:
    # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
    # response.set_cookie("session", value=session.get("csrf_token"), httponly=True, samesite="Strict") # type: ignore
    return response


@app.route("/")
def index():
    return render_template("base.html")


app.register_blueprint(bp_user, url_prefix="/user")
app.register_blueprint(bp_messanger, url_prefix="/chat")

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, port=5050)
