import mysql.connector

from objects import Comment, Follower, Image, Thumb, User, Blog, Trip
from datetime import datetime

sql = """
CREATE DATABASE IF NOT EXISTS heroku_e3cf3818d1518b5;
USE heroku_e3cf3818d1518b5;
CREATE TABLE IF NOT EXISTS user(
    email VARCHAR(128) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    private_account BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (email)
);

CREATE TABLE IF NOT EXISTS Trip(
    trip_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    email VARCHAR(128) NOT NULL,
    title VARCHAR(50) NOT NULL,
    date DATETIME NOT NULL,
    text LONGTEXT,
    route TEXT NOT NULL,
    PRIMARY KEY (trip_id),
    FOREIGN KEY (email) 
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Blog(
    blog_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    trip_id INT NOT NULL,
    date DATE NOT NULL,
    email VARCHAR(128) NOT NULL,
    text LONGTEXT,
    location VARCHAR(150) NOT NULL,
    PRIMARY KEY (blog_id),
    FOREIGN KEY (email) 
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (trip_id)
        REFERENCES Trip(trip_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS Comment(
    date DATETIME NOT NULL,
    email VARCHAR(128) NOT NULL,
    trip_id INT NOT NULL,
    blog_id INT NOT NULL DEFAULT -1,
    PRIMARY KEY (email, date, trip_id, blog_id),
    text TEXT NOT NULL,
    FOREIGN KEY (email) 
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (trip_id) 
        REFERENCES Trip(trip_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (blog_id)
        REFERENCES Blog(blog_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS Thumb(
    email VARCHAR(128) NOT NULL,
    trip_id INT NOT NULL,
    blog_id INT NOT NULL DEFAULT -1,
    PRIMARY KEY (email, trip_id, blog_id),
    FOREIGN KEY (email) 
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (trip_id) 
        REFERENCES Trip(trip_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (blog_id) 
        REFERENCES Blog(blog_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS Image(
    image_id INT AUTO_INCREMENT NOT NULL UNIQUE,
    filename VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(128) NOT NULL,
    trip_id INT NOT NULL,
    blog_id INT NOT NULL DEFAULT -1,
    PRIMARY KEY (email, image_id, trip_id, blog_id),
    FOREIGN KEY (email) 
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (trip_id) 
        REFERENCES Trip(trip_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (blog_id) 
        REFERENCES Blog(blog_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

Create TABLE IF NOT EXISTS Follower_list(
    email VARCHAR(128) NOT NULL,
    followed VARCHAR(128) NOT NULL,
    accepted boolean default False,
    PRIMARY KEY (email, followed),
    FOREIGN KEY (email)
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (followed)
        REFERENCES user(email)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
"""


class Database:
    def __init__(self):
        self.mc = None
        self.connect()
        self.mycursor.execute(sql, multi=True)
        self.mc.commit()
        self.disconnect()

    def connect(self):
        if self.mc and self.mc.is_connected():
            print("Database is already connected!")
        else:
            self.mc = mysql.connector.connect(
                host="eu-cdbr-west-02.cleardb.net",
                user="b281f1c79c8512",
                password="bd3764c7",
                database="heroku_e3cf3818d1518b5",
            )
            self.mycursor = self.mc.cursor(dictionary=True)

    def disconnect(self):
        self.mycursor.close()
        self.mc.close()
        self.mc = None
        self.mycursor = None

    def add_user(self, user):
        # registration
        self.connect()
        self.mycursor.execute(
            "INSERT INTO user(email, password, first_name, last_name, birth_date) VALUES('%s','%s','%s', '%s', '%s');"
            % (
                user.email,
                user.password,
                user.first_name,
                user.last_name,
                user.birth_date,
            )
        )
        self.mc.commit()
        self.disconnect()

    def get_all_users(self):
        self.connect()
        self.mycursor.execute("SELECT * FROM user")
        data = self.mycursor.fetchall()
        self.disconnect()

        return data

    def get_user_by_search(self, query):
        self.connect()
        self.mycursor.execute(
            "SELECT * FROM user WHERE email LIKE %s OR first_name LIKE %s OR last_name LIKE %s",
            (query, query, query),
        )

        data = self.mycursor.fetchall()

        if data:
            for d in range(len(data)):
                data[d]["birth_date"] = str(data[d]["birth_date"])
                self.mycursor.execute(
                    "SELECT * FROM image WHERE email = '%s' AND trip_id = %d AND blog_id = %d;"
                    % (data[d]["email"], int(-1), int(-1))
                )
                images = self.mycursor.fetchall()
                print(images)

                if images:
                    data[d]["profile_image"] = images[0]
                else:
                    data[d]["profile_image"] = None

            self.disconnect()
            if len(data) == 1:
                return data[0]
            else:
                return data

        self.disconnect()
        return None

    def get_user(self, email=None, first_name=None, last_name=None):
        self.connect()
        if email:
            self.mycursor.execute("SELECT * FROM user Where email='%s'" % (email))
        else:
            self.mycursor.execute("SELECT * FROM user")

        data = self.mycursor.fetchall()

        if data:
            for d in range(len(data)):
                data[d]["birth_date"] = str(data[d]["birth_date"])
                self.mycursor.execute(
                    "SELECT * FROM image WHERE email = '%s' AND trip_id = %d AND blog_id = %d;"
                    % (data[d]["email"], int(-1), int(-1))
                )
                images = self.mycursor.fetchall()
                print(images)

                if images:
                    data[d]["profile_image"] = images[0]
                else:
                    data[d]["profile_image"] = None

            self.disconnect()
            if len(data) == 1:
                return data[0]
            else:
                return data

        self.disconnect()
        return None

    def delete_user(self, email):
        self.connect()
        self.mycursor.execute("DELETE FROM user WHERE email = '%s';" % (email))
        self.mc.commit()
        self.disconnect()

    def update_user(self, user):
        self.connect()
        self.mycursor.execute(
            "UPDATE user SET first_name = '%s', last_name = '%s', password = '%s', birth_date = '%s', private_account = %r WHERE email = '%s';"
            % (
                user.first_name,
                user.last_name,
                user.password,
                user.birth_date,
                bool(user.private_account),
                user.email,
            )
        )
        self.mc.commit()
        self.disconnect()

    def add_blog(self, blog):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO blog(trip_id, date, email, text, location) VALUES(%d, '%s', '%s', '%s', '%s');"
            % (
                int(blog.tripid),
                blog.date,
                blog.email,
                blog.text,
                blog.location,
            )
        )
        self.mc.commit()
        blog_id = self.mycursor.lastrowid
        self.disconnect()

        return blog_id

    def get_blog(
        self, blogid=None, email=None, tripid=None, order_by="date", order_mode="DESC"
    ):
        self.connect()
        if blogid is not None:
            self.mycursor.execute(
                "SELECT * FROM blog WHERE blog_id = %d;" % (int(blogid))
            )
        elif email is not None:
            self.mycursor.execute("SELECT * FROM blog WHERE email = '%s';" % (email))
        elif tripid is not None:
            self.mycursor.execute(
                "SELECT * FROM blog WHERE trip_id = %d ORDER BY %s %s;"
                % (int(tripid), order_by, order_mode)
            )
        else:
            self.mycursor.execute(
                "SELECT * FROM blog ORDER BY %s %s;" % (order_by, order_mode)
            )

        data = self.mycursor.fetchall()

        Blogs = []
        for row in data:
            blog_id = row["blog_id"]
            if int(blog_id) == -1:
                continue
            self.mycursor.execute(
                "SELECT * FROM image WHERE blog_id = %d;" % (int(blog_id))
            )
            images = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT email FROM thumb WHERE blog_id = %d;" % (int(blog_id))
            )
            thumbs = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT * FROM comment WHERE blog_id = %d;" % (int(blog_id))
            )
            comments = self.mycursor.fetchall()

            Blogs.append(
                {**row, "images": images, "thumbs": thumbs, "comments": comments}
            )
        self.disconnect()
        return Blogs

    def delete_blog(self, blogid, email):
        self.connect()

        if blogid is not None:
            self.mycursor.execute(
                "DELETE FROM blog WHERE blog_id = %d;" % (int(blogid))
            )
            self.mc.commit()

        if email is not None:
            self.mycursor.execute("DELETE FROM blog WHERE email = '%s';" % (email))
            self.mc.commit()

        self.disconnect()

    def update_blog(self, blog):
        self.connect()
        self.mycursor.execute(
            "UPDATE blog SET blog_id = %d, trip_id = %d, date = '%s', email = '%s', text = '%s', location = '%s' WHERE blog_id = %d;"
            % (
                int(blog.blogid),
                int(blog.tripid),
                blog.date,
                blog.email,
                blog.text,
                blog.location,
                int(blog.blogid),
            )
        )
        self.mc.commit()
        self.disconnect()

    def add_comment(self, comment):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO comment(date, email, trip_id, blog_id, text) VALUES('%s', '%s', %d, %d, '%s');"
            % (
                comment.date,
                comment.email,
                int(comment.tripid),
                int(comment.blogid),
                comment.text,
            )
        )
        self.mc.commit()
        self.disconnect()

    def get_comment(self, blogid=None, tripid=None):
        self.connect()
        if blogid is not None:
            self.mycursor.execute(
                "SELECT * FROM comment WHERE blog_id = %d;" % (int(blogid))
            )
            data = self.mycursor.fetchall()
        if tripid is not None:
            self.mycursor.execute(
                "SELECT * FROM comment WHERE trip_id = %d;" % (int(tripid))
            )
            data = self.mycursor.fetchall()
        Comments = []
        for row in data:
            date = row[0]
            email = row[1]
            trip_id = row[2]
            blog_id = row[3]
            text = row[4]
            comment = Comment(email, date, trip_id, blog_id, text)
            Comments.append(comment)
        self.disconnect()
        return Comments

    def delete_comment(self, tripid, blogid, date):
        self.connect()

        """if blogid is not None:  # deletes all comment of blog
            self.mycursor.execute(
                "DELETE FROM comment WHERE blog_id = %d AND trip_id = %d;" % (int(blogid), int(tripid))
            )
            self.mc.commit()"""

        if date is not None:  # deletes spesific one comment
            self.mycursor.execute(
                "DELETE FROM comment WHERE date = '%s' and blog_id = %d and trip_id = %d;"
                % (date, int(blogid), int(tripid))
            )
            self.mc.commit()

        self.disconnect()

    def update_comment(self, comment):
        self.connect()
        self.mycursor.execute(
            "UPDATE comment SET date = '%s', email = '%s', trip_id = %d, blog_id = %d, text = '%s' WHERE date = '%s', blog_id = %d;"
            % (
                comment.date,
                comment.email,
                int(comment.tripid),
                int(comment.blogid),
                comment.date,
                int(comment.blogid),
            )
        )
        self.mc.commit()
        self.disconnect()

    def add_thumb(self, thumb):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO thumb(email, trip_id, blog_id) VALUES('%s', %d, %d);"
            % (thumb.email, int(thumb.tripid), int(thumb.blogid))
        )
        self.mc.commit()
        self.disconnect()

    def get_thumb(self, blogid=None, tripid=None):
        self.connect()
        if blogid is not None:
            self.mycursor.execute(
                "SELECT * FROM thumb WHERE blog_id = %d;" % (int(blogid))
            )
            data = self.mycursor.fetchall()
        if tripid is not None:
            self.mycursor.execute(
                "SELECT * FROM thumb WHERE trip_id = %d;" % (int(tripid))
            )
            data = self.mycursor.fetchall()

        Thumbs = []
        for row in data:
            email = row[0]
            trip_id = row[1]
            blog_id = row[2]
            thumb = Thumb(email, trip_id, blog_id)
            Thumbs.append(thumb)
        self.disconnect()
        return Thumbs

    def delete_thumb(self, thumb):
        self.connect()
        self.mycursor.execute(
            "DELETE FROM thumb WHERE blog_id = %d AND trip_id = %d;"
            % (int(thumb.blogid), int(thumb.tripid))
        )
        self.mc.commit()
        self.disconnect()

    def add_image(self, image):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO image(filename, email, trip_id, blog_id) VALUES('%s', '%s', %d, %d);"
            % (
                image.filename,
                image.email,
                int(image.tripid),
                int(image.blogid),
            )
        )
        self.mc.commit()
        self.disconnect()

    def delete_image(self, imageid):
        self.connect()
        self.mycursor.execute("DELETE FROM image WHERE image_id = %d;" % (int(imageid)))
        self.mc.commit()
        self.disconnect()

    def get_image(self, imageid=None, blogid=None, tripid=None):
        self.connect()
        if imageid is not None:
            self.mycursor.execute(
                "SELECT * FROM image WHERE image_id = %d;" % (int(imageid))
            )

        if blogid is not None:
            self.mycursor.execute(
                "SELECT * FROM image WHERE blog_id = %d;" % (int(blogid))
            )

        if tripid is not None:
            self.mycursor.execute(
                "SELECT * FROM image WHERE trip_id = %d AND blogid = %d;"
                % (int(tripid), int(-1))
            )

        data = self.mycursor.fetchall()
        self.disconnect()

        return data

    def add_trip(self, trip):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO trip(email, title, date, text, route) VALUES('%s', '%s', '%s', '%s', '%s');"
            % (
                trip.email,
                trip.title,
                trip.date,
                trip.text,
                trip.route,
            ),
        )
        self.mc.commit()
        trip_id = self.mycursor.lastrowid
        self.disconnect()

        return trip_id

    def update_trip(self, trip):
        self.connect()
        self.mycursor.execute(
            "UPDATE trip SET trip_id = %d, email = '%s', title = '%s', date = '%s', text = '%s', route = '%s' WHERE trip_id = %d;"
            % (
                int(trip.tripid),
                trip.email,
                trip.title,
                trip.date,
                trip.text,
                trip.route,
                int(trip.tripid),
            )
        )
        self.mc.commit()
        self.disconnect()

    def delete_trip(self, tripid):
        self.connect()
        self.mycursor.execute("DELETE FROM trip WHERE trip_id = %d;" % (int(tripid)))
        self.mc.commit()
        self.disconnect()

    def get_trip_by_search(self, query, col, orderby="date", ordermode="DESC"):
        self.connect()
        if col == "user":
            self.mycursor.execute(
                "SELECT trip_id, trip.email, title, date, text, route FROM Trip INNER JOIN User ON User.email=Trip.email WHERE User.first_name LIKE %s OR User.last_name LIKE %s OR User.email LIKE %s ORDER BY %s %s",
                (query, query, query, orderby, ordermode),
            )
        elif col == "title":
            self.mycursor.execute(
                "SELECT * FROM Trip WHERE title LIKE %s ORDER BY %s %s",
                (query, orderby, ordermode),
            )
        data = self.mycursor.fetchall()

        Trips = []
        for row in data:
            trip_id = row["trip_id"]
            if int(trip_id) == -1:
                continue
            self.mycursor.execute(
                "SELECT * FROM image WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            images = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT email FROM thumb WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            thumbs = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT *, text FROM comment WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            comments = self.mycursor.fetchall()

            self.mycursor.execute(
                "SELECT * FROM blog WHERE trip_id = %d;" % (int(trip_id))
            )
            blogs = self.mycursor.fetchall()

            Trips.append(
                {
                    **row,
                    "images": images,
                    "thumbs": thumbs,
                    "comments": comments,
                    "blogs": blogs,
                }
            )
        self.disconnect()
        return Trips

    def get_trip(
        self, tripid=None, email=None, title=None, orderby="date", ordermode="DESC"
    ):
        self.connect()

        if tripid is not None:
            self.mycursor.execute(
                "SELECT * FROM trip WHERE trip_id = %d;" % (int(tripid))
            )
        elif email is not None:
            self.mycursor.execute(
                "SELECT * FROM trip WHERE email = '%s' ORDER BY %s %s;"
                % (email, orderby, ordermode)
            )
        elif title is not None:
            self.mycursor.execute(
                "SELECT * FROM trip WHERE title LIKE %s;", ("%" + title + "%",)
            )
        else:
            self.mycursor.execute(
                "SELECT * FROM trip ORDER BY %s %s;" % (orderby, ordermode)
            )

        data = self.mycursor.fetchall()

        Trips = []
        for row in data:
            trip_id = row["trip_id"]
            if int(trip_id) == -1:
                continue
            self.mycursor.execute(
                "SELECT * FROM image WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            images = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT email FROM thumb WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            thumbs = self.mycursor.fetchall()
            self.mycursor.execute(
                "SELECT *, text FROM comment WHERE trip_id = %d AND blog_id = %d;"
                % (int(trip_id), int(-1))
            )
            comments = self.mycursor.fetchall()

            self.mycursor.execute(
                "SELECT * FROM blog WHERE trip_id = %d;" % (int(trip_id))
            )
            blogs = self.mycursor.fetchall()

            Trips.append(
                {
                    **row,
                    "images": images,
                    "thumbs": thumbs,
                    "comments": comments,
                    "blogs": blogs,
                }
            )
        self.disconnect()
        return Trips

    def add_follower(self, follower):
        self.connect()
        self.mycursor.execute(
            "INSERT INTO Follower_list(email, followed, accepted) VALUES('%s', '%s', %d);"
            % (follower.email, follower.followed, int(follower.accepted))
        )
        self.mc.commit()
        self.disconnect()

    def get_follower(self, email, type):
        # if type is 0, function returns followers and accepted followers amount
        # if type is 1, function returns followings and accepted following amount
        self.connect()
        if type == 0:
            self.mycursor.execute(
                "SELECT * FROM Follower_list WHERE followed = '%s';" % (email)
            )
        elif type == 1:
            self.mycursor.execute(
                "SELECT * FROM Follower_list WHERE email = '%s';" % (email)
            )
        data = self.mycursor.fetchall()
        self.disconnect()

        return data

    def delete_follower(self, follower):
        self.connect()
        self.mycursor.execute(
            "DELETE FROM Follower_list WHERE email = '%s' AND followed = '%s';"
            % (follower.email, follower.followed)
        )
        self.mc.commit()
        self.disconnect()

    def accept_follower(self, email, followed):
        self.connect()
        self.mycursor.execute(
            "UPDATE Follower_list SET accepted = %d WHERE email = '%s' AND followed = '%s';"
            % (1, email, followed)
        )
        self.mc.commit()
        self.disconnect()
