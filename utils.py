def get_recommended_users(user, all_users, db):
    # Get followers and followings of user
    followers = db.get_follower(email=user.get("email"), type=0)
    followings = db.get_follower(email=user.get("email"), type=1)

    followers = set([follower["email"] for follower in followers])
    followings = set([following["followed"] for following in followings])
    results = followers.copy()

    # Go over followings
    for following in followings:
        # Get followers and followings of following
        followers2 = db.get_follower(email=following, type=0)
        followings2 = db.get_follower(email=following, type=1)

        followers2 = set([follower["email"] for follower in followers2])
        followings2 = set([following["followed"] for following in followings2])

        results = results.union(followers2)
        results = results.union(followings2)

    # Go over followers
    for follower in followers:
        # Get followers and followings of following
        followers2 = db.get_follower(email=follower, type=0)
        followings2 = db.get_follower(email=follower, type=1)

        followers2 = set([follower["email"] for follower in followers2])
        followings2 = set([following["followed"] for following in followings2])

        results = results.union(followers2)
        results = results.union(followings2)

    results = results.difference(followings)
    results = results.difference({user["email"]})
    results = [db.get_user(email=email) for email in results]

    return results
