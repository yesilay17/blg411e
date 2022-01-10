from flask import (
    current_app,
    render_template,
    redirect,
    request,
    url_for,
    session,
    jsonify,
)
from objects import *
from mail import send_email
import random
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename
import os
import uuid
import requests
import urllib.parse
import json
from utils import get_recommended_users


def home():
    return redirect(url_for("home_page", page=1))


def home_page(page):
    user = session.get("user")
    print(user)
    if user and user.get("logged_in"):
        db = current_app.config["db"]
        all_users = db.get_user()
        recommended_users = get_recommended_users(user, all_users, db)

        followings = db.get_follower(email=user.get("email"), type=1)

        trips = db.get_trip()
        n_trips_per_page = 10
        trips_range_begin = (page - 1) * n_trips_per_page
        trips_range_end = trips_range_begin + n_trips_per_page

        is_last_page = True
        if len(trips) > trips_range_end:
            is_last_page = False

        trips = trips[trips_range_begin:trips_range_end]

        for i in range(len(trips)):
            trips[i]["email"] = db.get_user(email=trips[i]["email"])
            if (
                trips[i]["email"]["email"] != user["email"]
                and trips[i]["email"]["private_account"]
                and not any(
                    trips[i]["email"]["email"] == following["followed"]
                    for following in followings
                )
            ):
                trips[i] = None
                continue

            trips[i]["comments"] = list(
                map(
                    lambda comment: {
                        **comment,
                        "email": db.get_user(email=comment["email"]),
                    },
                    trips[i]["comments"],
                )
            )

            trips[i]["is_liked"] = any(
                thumb["email"] == user["email"] for thumb in trips[i]["thumbs"]
            )

            route_json_str = trips[i]["route"]
            route_list = json.loads(route_json_str)
            route_str = ""
            route_coordinates = []
            for j, route in enumerate(route_list):
                route_str += route["place"]
                if j != len(route_list) - 1:
                    route_str += " → "
                route_coordinates.append([route["latt"], route["long"]])

            trips[i]["route"] = route_str
            trips[i]["route_coordinates"] = route_coordinates

        trips = list(filter(lambda trip: trip != None, trips))

        db.connect()
        db.mycursor.execute(
            """
            SELECT location, count(location) AS total FROM Blog
            GROUP BY location
            ORDER BY total DESC
            """
        )
        hot_places = db.mycursor.fetchall()
        db.disconnect()

        context = {
            "user": user,
            "Trips": trips,
            "hot_places": hot_places,
            "page": page,
            "is_last_page": is_last_page,
            "recommended_users": recommended_users,
        }

        return render_template("home.html", **context)

    return redirect(url_for("login_page"))


def profile_page(email):
    logged_in_user = session.get("user")
    print(logged_in_user)
    if logged_in_user and logged_in_user.get("logged_in"):
        if email:
            db = current_app.config["db"]
            profile_user = db.get_user(email=email)
            if profile_user:
                trips = db.get_trip(email=email)
                all_users = db.get_user()
                recommended_users = get_recommended_users(logged_in_user, all_users, db)

                for i in range(len(trips)):
                    trips[i]["comments"] = list(
                        map(
                            lambda comment: {
                                **comment,
                                "email": db.get_user(email=comment["email"]),
                            },
                            trips[i]["comments"],
                        )
                    )

                    trips[i]["email"] = db.get_user(email=trips[i]["email"])

                    trips[i]["is_liked"] = any(
                        thumb["email"] == logged_in_user["email"]
                        for thumb in trips[i]["thumbs"]
                    )

                    route_json_str = trips[i]["route"]
                    route_list = json.loads(route_json_str)
                    route_str = ""
                    route_coordinates = []
                    for j, route in enumerate(route_list):
                        route_str += route["place"]
                        if j != len(route_list) - 1:
                            route_str += " → "
                        route_coordinates.append([route["latt"], route["long"]])

                    trips[i]["route"] = route_str
                    trips[i]["route_coordinates"] = route_coordinates

                db.connect()
                db.mycursor.execute(
                    """
                    SELECT location, count(location) AS total FROM Blog
                    GROUP BY location
                    ORDER BY total DESC
                    """
                )
                hot_places = db.mycursor.fetchall()
                db.disconnect()

                followers = db.get_follower(email=profile_user.get("email"), type=0)
                followings = db.get_follower(email=profile_user.get("email"), type=1)

                accepted_followers = [
                    db.get_user(email=follower["email"])
                    for follower in followers
                    if follower["accepted"] == 1
                ]

                waiting_followers = [
                    db.get_user(email=follower["email"])
                    for follower in followers
                    if follower["accepted"] == 0
                ]

                accepted_followings = [
                    db.get_user(email=following["followed"])
                    for following in followings
                    if following["accepted"] == 1
                ]

                waiting_followings = [
                    db.get_user(email=following["followed"])
                    for following in followings
                    if following["accepted"] == 0
                ]

                follow_status = "not_following"
                for follower in followers:
                    if logged_in_user.get("email") == follower.get("email"):
                        if follower.get("accepted"):
                            follow_status = "following"
                        else:
                            follow_status = "waiting"

                context = {
                    "user": logged_in_user,
                    "profile_user": profile_user,
                    "Trips": trips,
                    "accepted_followers": accepted_followers,
                    "waiting_followers": waiting_followers,
                    "accepted_followings": accepted_followings,
                    "waiting_followings": waiting_followings,
                    "follow_status": follow_status,
                    "recommended_users": recommended_users,
                    "hot_places": hot_places,
                }

                return render_template("profile.html", **context)

            else:
                return redirect(url_for("home_page", page=1))
        else:
            return redirect(url_for("home_page", page=1))

    return redirect(url_for("login_page"))


def settings_page():
    user = session.get("user")
    db = current_app.config["db"]
    if user and user.get("logged_in"):
        if request.method == "GET":
            p_user = db.get_user(user["email"])
            all_users = db.get_user()
            recommended_users = get_recommended_users(user, all_users, db)

            db.connect()
            db.mycursor.execute(
                """
                SELECT location, count(location) AS total FROM blog
                GROUP BY location
                ORDER BY total DESC
                """
            )
            hot_places = db.mycursor.fetchall()
            hot_places = [place for (place, count) in hot_places]
            db.disconnect()
            return render_template(
                "settings.html",
                user=user,
                recommended_users=recommended_users,
                hot_places=hot_places,
            )
        else:
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            birth_date = request.form.get("birth_date", "").strip()
            delete_profile_image = request.form.get("delete_profile_image")
            if delete_profile_image and user.get("profile_image"):
                image_id = user["profile_image"]["image_id"]
                filename = user["profile_image"]["filename"]
                db.delete_image(image_id)
                os.remove(os.path.join(current_app.config["UPLOAD_DIR"], filename))

            private = None
            if request.form.get("private_account"):
                private = True
            else:
                private = False

            files = request.files.getlist("profile_image")
            for file in files:
                if file.mimetype.startswith("image/"):
                    if user.get("profile_image"):
                        file.save(
                            os.path.join(
                                current_app.config["UPLOAD_DIR"],
                                user["profile_image"]["filename"],
                            )
                        )
                    else:
                        filename = secure_filename(
                            uuid.uuid4().hex
                            + "."
                            + file.filename.rsplit(".", 1)[1].lower()
                        )
                        file.save(
                            os.path.join(current_app.config["UPLOAD_DIR"], filename)
                        )

                        db.add_image(
                            Image(
                                filename=filename,
                                email=user["email"],
                                tripid=-1,
                                blogid=-1,
                            )
                        )

            user = db.get_user(user["email"])
            user.pop("profile_image")
            user["first_name"] = first_name
            user["last_name"] = last_name
            user["birth_date"] = birth_date
            user["private_account"] = private
            db.update_user(User(**user))
            user = db.get_user(user["email"])

            user.pop("password")
            user["logged_in"] = True
            session["user"] = user
            return render_template("settings.html", user=user)
    else:
        return redirect(url_for("login_page"))


def verification_page():
    user = session.get("user")
    code = session.get("code")
    code_valid_until = session.get("code_valid_until")
    failure_caller = session.get("failure_caller")
    success_caller = session.get("success_caller")
    if user and user.get("logged_in"):
        return redirect(url_for("home_page", page=1))

    if not user:
        return redirect(url_for("login_page"))

    # User exists in session

    if not code:
        session["failure_caller"] = None
        session["success_caller"] = None
        session["warning"] = "Verificaition code expired"

        return redirect(url_for(failure_caller))

    # User exists, code exists
    now = datetime.now(timezone.utc)
    if (code_valid_until - now).total_seconds() < 0:
        session.pop("code")
        session.pop("code_valid_until")
        session.pop("user")
        session["warning"] = "Verification code expired"
        session["failure_caller"] = None
        session["success_caller"] = None

        return redirect(url_for(failure_caller))

    # Code valid
    if request.method == "GET":
        return render_template("verification.html", code_valid_until=code_valid_until)

    if request.method == "POST":
        number1 = str(request.form.get("number1", "").strip())
        number2 = str(request.form.get("number2", "").strip())
        number3 = str(request.form.get("number3", "").strip())
        number4 = str(request.form.get("number4", "").strip())
        code_from_user = int(number1 + number2 + number3 + number4)
        if code_from_user == int(code):
            if failure_caller == "register_page":
                db = current_app.config["db"]
                user.pop("logged_in")
                db.add_user(User(**user))
                session.pop("user")
            elif success_caller == "reset_password":
                user["password_reset"] = True
            session.pop("code")
            session.pop("code_valid_until")
            session["warning"] = None
            session["failure_caller"] = None
            session["success_caller"] = None

            return redirect(url_for(success_caller))

        else:
            return render_template(
                "verification.html",
                warning="Verification code does not match",
                code_valid_until=code_valid_until,
            )

    return "<h1>Method not allowed!</h1>", 405


def register_page():
    user = session.get("user")
    db = current_app.config["db"]
    if user and user.get("logged_in"):
        return redirect(url_for("home_page", page=1))

    # No user
    if request.method == "GET":
        # Display warning for incoming redirects
        warning = session.get("warning")
        # Only for once
        session["warning"] = None
        return render_template("register.html", warning=warning)

    if request.method == "POST":
        email = request.form.get("email").strip()
        # Empty email
        if email == "":
            return render_template("register.html", warning="Email cannot be empty")

        # Email exists
        if db.get_user(email):
            return (
                render_template(
                    "register.html",
                    warning="User already exists",
                ),
                409,
            )  # Conflict

        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        birth_date = request.form.get("birth_date", "").strip()
        password1 = request.form.get("password1", "").strip()
        password2 = request.form.get("password2", "").strip()
        print(birth_date)

        # Passwords did not match
        if password1 != password2:
            return render_template(
                "register.html",
                warning="Password does not match",
            )

        # Create user
        user = {
            "email": email,
            "password": hasher.hash(password1),
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "logged_in": False,
        }

        # Create random verification code
        verification_code = ""
        for i in range(4):
            verification_code += str(random.randint(0, 9))

        # Errors may raise from sendmail
        try:
            send_email(email, verification_code)
        except:
            return (
                render_template(
                    "register.html",
                    warning="Verification code could not be send",
                ),
                500,
            )

        session["user"] = user
        # Important: Need to store code
        session["code"] = verification_code
        code_valid_until = datetime.now(timezone.utc) + timedelta(seconds=120)
        session["code_valid_until"] = code_valid_until
        # Caller is register_page
        session["failure_caller"] = "register_page"
        session["success_caller"] = "login_page"

        return redirect(url_for("verification_page"))

    return "<h1>Method not allowed!</h1>", 405


def login_page():
    db = current_app.config["db"]
    user = session.get("user")
    if user and user.get("logged_in"):
        return redirect(url_for("home_page", page=1))

    if request.method == "GET":
        values = {"email": "", "password": ""}
        warning = session.get("warning")
        session["warning"] = None
        return render_template("login.html", values=values, warning=warning)
    else:
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = db.get_user(email)
        if user:
            if not hasher.verify(password, user["password"]):
                user = None
        values = {"email": email, "password": password}
        if user:
            user["logged_in"] = True
            print("LOGGEDIN", user)
            session["user"] = user
            return redirect(url_for("home_page", page=1))
        else:
            return render_template(
                "login.html", values=values, warning="Email and password did not match"
            )


def logout():
    user = session.get("user")
    if user and user.get("logged_in"):
        session.pop("user")
    return redirect(url_for("login_page"))


def forgot_password():
    user = session.get("user")
    code = session.get("code")
    if user and user.get("logged_in"):
        # Already logged in user
        return redirect(url_for("home_page", page=1))

    # No user in session
    if request.method == "POST":
        db = current_app.config["db"]
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = db.get_user(email)

        if user:
            # User exists in db
            user["logged_in"] = False

            # Create a random verification code
            verification_code = ""
            for i in range(4):
                verification_code += str(random.randint(0, 9))

            # send_mail may raise exception
            try:
                send_email(email, verification_code, forgot_password=True)
            except:
                return (
                    render_template(
                        "login.html",
                        warning="Verification code could not be send",
                    ),
                    500,
                )

            session["user"] = user
            # Important to store code
            session["code"] = verification_code
            code_valid_until = datetime.now(timezone.utc) + timedelta(seconds=120)
            session["code_valid_until"] = code_valid_until
            # If success, redirect to reset_password
            session["success_caller"] = "reset_password"
            # To login_page otherwise
            session["failure_caller"] = "login_page"

            return redirect(url_for("verification_page"))

        # User does not exist in db
        return render_template(
            "login.html",
            warning="No such email is found",
            values={"email": email, "password": password},
        )

    return "<h1>Method not allowed!</h1>", 405


def reset_password():
    user = session.get("user")

    if user and user.get("password_reset"):
        if request.method == "GET":
            return render_template("reset_password.html", warning=None)
        if request.method == "POST":
            password1 = request.form.get("password1", "").strip()
            password2 = request.form.get("password2", "").strip()
            if password1 != password2:
                return render_template(
                    "reset_password.html", warning="Passowords did not match"
                )

            db = current_app.config["db"]
            user.pop("logged_in")
            user.pop("password_reset")
            user.pop("profile_image")
            user["password"] = hasher.hash(password1)
            db.update_user(User(**user))
            session.pop("user")

            return redirect(url_for("login_page"))

        return "<h1>Method not allowed!</h1>", 405

    return redirect(url_for("login_page"))


def thumb(tripid, blogid, command):
    db = current_app.config["db"]
    user = session.get("user")
    if user:
        thumb = Thumb(user["email"], int(tripid), int(blogid))
        if command == "add":
            print("Thumb is added")
            db.add_thumb(thumb)
        elif command == "delete":
            print("Thumb is deleted")
            db.delete_thumb(thumb)
    return "Thumb"


def comment(tripid, blogid, text, date, command):
    db = current_app.config["db"]
    user = session.get("user")
    if user:
        if command == "add":
            print("Comment is inserted!")
            comment = Comment(
                email=user["email"],
                tripid=int(tripid),
                blogid=int(blogid),
                text=text,
                date=date,
            )
            db.add_comment(comment)
        elif command == "delete":
            db.delete_comment(tripid=tripid, blogid=blogid, date=date)
            print("Comment is deleted!")
    return "Comment"


def trip(url_param_trip_id):
    user = session.get("user")
    db = current_app.config["db"]
    if user and user.get("logged_in"):
        if request.method == "GET":
            if url_param_trip_id:
                trips = db.get_trip(tripid=url_param_trip_id)
                if trips:
                    trip = trips[0]
                    trip["email"] = db.get_user(email=trip["email"])
                    trip["is_liked"] = any(
                        thumb["email"] == user["email"] for thumb in trip["thumbs"]
                    )
                    followings = db.get_follower(email=user.get("email"), type=1)
                    if (
                        trip["email"]["email"] != user["email"]
                        and trip["email"]["private_account"]
                        and not any(
                            trip["email"]["email"] == following.get("followed")
                            and following.get("accepted")
                            for following in followings
                        )
                    ):
                        return f"<h1>You need to follow {trip.get('email')} to see this trip</h1>"

                    blogs = db.get_blog(tripid=url_param_trip_id)
                    for i in range(len(blogs)):
                        blogs[i]["email"] = trip["email"].copy()

                        blogs[i]["comments"] = list(
                            map(
                                lambda comment: {
                                    **comment,
                                    "email": db.get_user(email=comment["email"]),
                                },
                                blogs[i]["comments"],
                            )
                        )

                        blogs[i]["is_liked"] = any(
                            thumb["email"] == user["email"]
                            for thumb in blogs[i]["thumbs"]
                        )

                    trip["blogs"] = blogs
                    print(trips)
                    return render_template("blogs.html", user=user, Trip=trip)

                return "Not found", 404
            else:
                return render_template("add_trip.html", user=user)

        if request.method == "POST":
            email = user.get("email")
            title = request.form.get("title", "").strip()
            date = datetime.now()
            text = request.form.get("text", "").strip()
            route_list = []
            for key, value in request.form.items():
                if key.startswith("route"):
                    place = request.form.get(key, "").strip()
                    place_url = urllib.parse.quote(place)
                    url = f"https://api.opencagedata.com/geocode/v1/geojson?q={place_url}&key={current_app.config['API_KEY']}&limit=1"
                    response = requests.get(url).json()
                    status_code = response["status"]["code"]
                    if status_code == 200 and len(response["features"]) > 0:
                        long = response["features"][0]["geometry"]["coordinates"][0]
                        latt = response["features"][0]["geometry"]["coordinates"][1]
                        route_dict = {"place": place, "long": long, "latt": latt}
                    else:
                        route_dict = {"place": place, "long": -999, "latt": -999}
                    route_list.append(route_dict)
            route = json.dumps(route_list, ensure_ascii=False)
            trip = Trip(email=email, title=title, date=date, text=text, route=route)
            trip_id = db.add_trip(trip)

            files = request.files.getlist("file")
            for file in files:
                if file.mimetype.startswith("image/"):
                    filename = secure_filename(
                        uuid.uuid4().hex + "." + file.filename.rsplit(".", 1)[1].lower()
                    )
                    file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

                    db.add_image(
                        Image(
                            filename=filename,
                            email=user["email"],
                            tripid=trip_id,
                            blogid=-1,
                        )
                    )

            return redirect(url_for("home_page", page=1))

        return "<h1>Method not allowed!</h1>", 405

    return redirect(url_for("login_page"))


def blog():
    user = session.get("user")
    db = current_app.config["db"]
    if user and user.get("logged_in"):
        if request.method == "GET":
            trips = db.get_trip(email=user.get("email"))
            return render_template("add_blog.html", user=user, Trips=trips)

        if request.method == "POST":
            email = user.get("email")
            trip_id = request.form.get("tripid")
            date = datetime.now()
            text = request.form.get("text", "").strip()
            location = request.form.get("location", "").strip()
            blog = Blog(
                tripid=trip_id, email=email, date=date, text=text, location=location
            )
            blog_id = db.add_blog(blog)

            files = request.files.getlist("file")
            for file in files:
                if file.mimetype.startswith("image/"):
                    filename = secure_filename(
                        uuid.uuid4().hex + "." + file.filename.rsplit(".", 1)[1].lower()
                    )
                    file.save(os.path.join(current_app.config["UPLOAD_DIR"], filename))

                    db.add_image(
                        Image(
                            filename=filename,
                            email=user["email"],
                            tripid=-1,
                            blogid=blog_id,
                        )
                    )

            return redirect(url_for("home_page", page=1))

        return "<h1>Method not allowed!</h1>", 405

    return redirect(url_for("login_page"))


def follow_user(email, followed, command):
    db = current_app.config["db"]
    user = session.get("user")
    if user:
        if command == "follow":
            print("follow")
            f = Follower(email, followed, False)
            db.add_follower(f)
        elif command == "unfollow":
            f = Follower(email, followed, 1)
            db.delete_follower(f)
        elif command == "accept":
            db.accept_follower(email, followed)
        elif command == "reject":
            f = Follower(email, followed, 1)
            db.delete_follower(f)

    return "follower"


def delete_trip(tripid):
    db = current_app.config["db"]
    db.delete_trip(tripid)
    print("Trip is deleted with id:", tripid)
    return "Delete Trip"


def search():
    db = current_app.config["db"]
    user = session.get("user")
    if request.method == "POST":
        search = request.form.get("search", "").strip()
        recommended_users = get_recommended_users(user, None, db)
        db.connect()
        db.mycursor.execute(
            """
            SELECT location, count(location) AS total FROM Blog
            GROUP BY location
            ORDER BY total DESC
            """
        )
        hot_places = db.mycursor.fetchall()
        db.disconnect()

        if search.startswith("user:"):
            query = search.split("user:")[1].strip()
            query = "%" + query + "%"
            users = db.get_user_by_search(query)
            if not isinstance(users, list):
                users = [users]

            return render_template(
                "user_list.html",
                user=user,
                users=users,
                hot_places=hot_places,
                recommended_users=recommended_users,
            )

        if search.startswith("from:"):
            query = search.split("from:")[1].strip()
            query = "%" + query + "%"
            trips = db.get_trip_by_search(query, col="user")

        elif search.startswith("title:"):
            query = search.split("title:")[1].strip()
            query = "%" + query + "%"
            trips = db.get_trip_by_search(query, col="title")

        else:
            query = search.split().strip()
            trips = db.get_trip_by_search(query, col="title")

        followings = db.get_follower(email=user.get("email"), type=1)
        for i in range(len(trips)):
            trips[i]["email"] = db.get_user(email=trips[i]["email"])
            if (
                trips[i]["email"]["email"] != user["email"]
                and trips[i]["email"]["private_account"]
                and not any(
                    trips[i]["email"]["email"] == following["followed"]
                    for following in followings
                )
            ):
                trips[i] = None
                continue

            trips[i]["comments"] = list(
                map(
                    lambda comment: {
                        **comment,
                        "email": db.get_user(email=comment["email"]),
                    },
                    trips[i]["comments"],
                )
            )

            trips[i]["is_liked"] = any(
                thumb["email"] == user["email"] for thumb in trips[i]["thumbs"]
            )

            route_json_str = trips[i]["route"]
            route_list = json.loads(route_json_str)
            route_str = ""
            route_coordinates = []
            for j, route in enumerate(route_list):
                route_str += route["place"]
                if j != len(route_list) - 1:
                    route_str += " → "
                route_coordinates.append([route["latt"], route["long"]])

            trips[i]["route"] = route_str
            trips[i]["route_coordinates"] = route_coordinates

        trips = list(filter(lambda trip: trip != None, trips))

        context = {
            "user": user,
            "Trips": trips,
            "hot_places": hot_places,
            "recommended_users": recommended_users,
            "page": 1,
            "is_last_page": True,
        }

        return render_template("home.html", **context)

    return "<h1>Method not allowed!</h1>", 403
