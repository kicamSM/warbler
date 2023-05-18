import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
   #add_user_to_g is a function which is adding the current user to the Flask global if that user is logged in. This is going to allow us to show the correct and allowed user pages by grabbing the g.user (of the logged in individudal) and displaying the correct information. 
   
    # @app.before_request means that this function is running before each request. This allows us to continuakky have the currect g.user in the session 
    
    #Flask g object is the data that is being saved globally in flask in this case the g.user 

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        # this is so that you can reference the global object which will be the logged in user. 

    else:
        g.user = None
        #if no longed in user than there will  ot be  a global object and I believe that there will be restrictions to what you can access. 

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id
    # adding user.id in the session 
    #  the flask g object is the global object which is data being stored in flask globtally 

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    # user = User.query.get(session[CURR_USER_KEY])
    do_logout()
    flash("You have been logged out!", 'success')
    return redirect('/login')
    # IMPLEMENT THIS


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)

@app.route('/users/add_like/<int:msg_id>', methods=["POST"])
def add_like(msg_id):
    """Add a like to specific message"""
    # msg_list = []
    # msg = Message.query.get_or_404(msg_id)
    
    # msg_list.append(msg)
    user = g.user
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    liked_msg = Message.query.get_or_404(msg_id)
    # raise ValueError(liked_msg)
    
    # raise ValueError(liked_msg.id)
    # g.user.following.append(followed_user)
    g.user.likes.append(liked_msg)
    # raise ValueError(g.user.likes)
    # g.user.likes has messages in it so there is a disconnect between the two functions 
    db.session.commit()
    
    return render_template('users/show.html', liked_msg=liked_msg, user=user)
# if you do the above return instead you have to be able to pass in the user as well 

    # return redirect(f"/users/{g.user.id}")
    
# msg_list needs to be passed in to the html which means either you need to simply return the html or you need to return route and then somehow add the msg_List to that route 

@app.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    # user = g.user
    # message = Message.query.all()
    # raise ValueError(g.user.likes)
    liked_ids = [l.id for l in g.user.likes]
# ********************************************************
    # this is not updating the two value for some reason wheen we are redirecting to this route from the remove like 
    # currently liked_ids are have 3 values in list
#************************************************************
    # raise ValueError(liked_ids)
    # raise ValueError(l.id)
    
    messages = (Message
                        .query
                        .order_by(Message.timestamp.desc())
                        .filter(Message.id.in_(liked_ids))
                        .limit(100)
                        .all())
    # raise ValueError(messages)
    #note that this all seems to be working accept that the messages currently have nothing inside of them 
    return render_template('users/likes.html', user=user, messages=messages)

@app.route('/users/remove_like/<int:msg_id>', methods=["POST"])
def remove_like(msg_id):
    """remove the like from message"""
    # liked_ids = [l.id for l in g.user.likes]
    # also 3 values in liked_ids here 
    # raise ValueError(g.user.likes)
    # for index, item in enumerate(liked_ids):
    #     if item.id == msg_id: 
    #         break 
    #     else: 
    #         index -1 
    # msg_index  = liked_ids.index(msg_id)
    # raise ValueError(msg_index)
    # msg_index = liked_ids.where(msg_id)
    # raise ValueError(msg_index)
    # liked_ids.pop(msg_index)
    # liked ids only have two values here which is also correct 
    # raise ValueError(liked_ids)
    message = Message.query.get(msg_id)
    g.user.likes.remove(message)
    db.session.commit()
    # raise ValueError(liked_ids)
    return redirect(f"/users/{g.user.id}")

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    #Step Three is going to have to do wtih details.html check that 
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    # raise ValueError(g.user.following)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    
    # IMPLEMENT THIS
    form = UserEditForm()
    g.user = User.authenticate(form.username.data,
                             form.password.data)
    if form.validate_on_submit():
       if not g.user:
        flash("You entered the incorrect password.", "danger")
        return redirect("/")
       else: 
        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.image_url = form.image_url.data
        g.user.header_image_url = form.header_image_url.data
        g.user.bio = form.bio.data 
    
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(f"/users/{g.user.id}")
    return render_template('/users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""
    import pdb
    pdb.set_trace()
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    # g.user.following.append(followed_user)
    # this is how the previous routes are adding the followings 

    if g.user:
        # if g.user.following == True:
        # messages = g.user.following(Message 
        # this is returning Instrumented list which is not callable 
        #in models there is a function which is is_following that is probably what you need in order to return the messages of only followed users
        
        # raise ValueError(User.is_following(g.user))
        # raise ValueError(g.user.following.messages)
        # following = list(g.user.following)
        following_ids = [f.id for f in g.user.following] + [g.user.id]
        # raise ValueError(following_ids)

        messages = (Message
                        .query
                        .order_by(Message.timestamp.desc())
                        .filter(Message.user_id.in_(following_ids))
                        .limit(100)
                        .all())
        # raise ValueError(messages)
        # raise ValueError(g.user.following.messages)
        # raise ValueError(g.user.following.messages)
                    # change this from all to just the users that the user is following and the logged in user 

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
