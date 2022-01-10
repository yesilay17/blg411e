class User:
    def __init__(
        self,
        email,
        password,
        first_name,
        last_name,
        birth_date,
        private_account=False,
        profile_image=None,
    ):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.birth_date = birth_date
        self.private_account = private_account

    def get_as_dict(self):
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date,
            "private_account": self.private_account,
        }

    def __repr__(self):
        return f"""
        email = {self.email}
        first_name = {self.first_name}
        last_name = {self.last_name}
        password = {self.password}
        birth_date = {self.birth_date}
        private_account = {self.private_account}\n\n"""

    def __str__(self):
        return f"""
        email = {self.email}
        first_name = {self.first_name}
        last_name = {self.last_name}
        password = {self.password}
        birth_date = {self.birth_date}
        private_account = {self.private_account}\n\n"""


class Follower:
    def __init__(self, email, followed, accepted):
        self.email = email
        self.followed = followed
        self.accepted = accepted

    def __repr__(self):
        return f"""
        email = {self.email}
        follower = {self.followed}
        accepted = {self.accepted}\n\n"""

    def __str__(self):
        return f"""
        email = {self.email}
        followed = {self.followed}
        accepted = {self.accepted}\n\n"""


class Trip:
    def __init__(
        self,
        email,
        title,
        date,
        route,
        tripid=None,
        text=None,
        images=None,
        comments=None,
        thumbs=None,
        blogs=None,
    ):
        self.tripid = tripid
        self.email = email
        self.title = title
        self.date = date
        self.text = text
        self.route = route
        self.images = images
        self.comments = comments
        self.thumbs = thumbs
        self.blogs = blogs

    def __repr__(self):
        return f"""
        trip_id: {self.tripid}
        email: {self.email}
        title: {self.title}
        date: {self.date}
        text: {self.text}
        route: {self.route}\n\n"""

    def __str__(self):
        return f"""
        trip_id: {self.tripid}
        email: {self.email}
        title: {self.title}
        date: {self.date}
        text: {self.text}
        route: {self.route}\n\n"""


class Blog:
    def __init__(
        self,
        tripid,
        date,
        email,
        location,
        blogid=None,
        text=None,
        images=None,
        comments=None,
        thumbs=None,
    ):
        self.blogid = blogid
        self.tripid = tripid
        self.date = date
        self.email = email
        self.text = text
        self.location = location
        self.comments = comments
        self.thumbs = thumbs


class Comment:
    def __init__(self, email, date, tripid, blogid, text):
        # if blogid is -1, "Comment" belongs to corresponding Trip
        self.email = email
        self.date = date
        self.tripid = tripid
        self.blogid = blogid
        self.text = text

    def __repr__(self):
        return f"""
        email = {self.email}
        date = {self.date}
        tripid = {self.tripid}
        blogid = {self.blogid}
        text = {self.text}\n\n"""

    def __str__(self):
        return f"""
        email = {self.email}
        date = {self.date}
        tripid = {self.tripid}
        blogid = {self.blogid}
        text = {self.text}\n\n"""


class Thumb:
    # if blogid is -1, "Thumb" belongs to corresponding Trip
    def __init__(self, email, tripid, blogid):
        self.email = email
        self.tripid = tripid
        self.blogid = blogid


class Image:
    # if blogid is -1, "Image" belongs to corresponding Trip
    def __init__(self, filename, email, tripid, blogid, imageid=None):
        self.imageid = imageid
        self.filename = filename
        self.email = email
        self.tripid = tripid
        self.blogid = blogid
