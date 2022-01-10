from flask import Flask, session
from datetime import timedelta
import views
from database import Database

app = Flask(__name__, static_folder="static/", static_url_path="")
app.secret_key = "secret"


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=3)


app.add_url_rule("/login", view_func=views.login_page, methods=["GET", "POST"])
app.add_url_rule("/logout", view_func=views.logout, methods=["GET"])
app.add_url_rule("/forgot_password", view_func=views.forgot_password, methods=["POST"])
app.add_url_rule(
    "/reset_password", view_func=views.reset_password, methods=["GET", "POST"]
)
app.add_url_rule("/", view_func=views.home, methods=["GET"])
app.add_url_rule("/<int:page>", view_func=views.home_page, methods=["GET"])
app.add_url_rule("/settings", view_func=views.settings_page, methods=["GET", "POST"])
app.add_url_rule("/register", view_func=views.register_page, methods=["GET", "POST"])
app.add_url_rule(
    "/verification", view_func=views.verification_page, methods=["GET", "POST"]
)
app.add_url_rule(
    "/thumb/<tripid>/<blogid>/<command>", view_func=views.thumb, methods=["GET", "POST"]
)

app.add_url_rule(
    "/profile/<string:email>", view_func=views.profile_page, methods=["GET"]
)

app.add_url_rule(
    "/comment/<tripid>/<blogid>/<text>/<date>/<command>",
    view_func=views.comment,
    methods=["GET", "POST"],
)

app.add_url_rule(
    "/delete_trip/<tripid>",
    view_func=views.delete_trip,
    methods=["GET", "POST"],
)

app.add_url_rule(
    "/follower/<email>/<followed>/<command>",
    view_func=views.follow_user,
    methods=["GET", "POST"],
)

app.add_url_rule(
    "/search",
    view_func=views.search,
    methods=["POST"],
)

app.add_url_rule(
    "/trip/",
    defaults={"url_param_trip_id": None},
    view_func=views.trip,
    methods=["GET", "POST"],
)
app.add_url_rule("/trip/<int:url_param_trip_id>", view_func=views.trip, methods=["GET"])

app.add_url_rule("/blog", view_func=views.blog, methods=["GET", "POST"])


db = Database()
app.config["db"] = db
app.config["UPLOAD_DIR"] = "./static"
app.config["API_KEY"] = "9e486d4828864d0195b481286bde2ba2"

if __name__ == "__main__":
    app.run(port=3000, debug=True)
