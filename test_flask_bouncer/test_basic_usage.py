from flask import Flask, abort
from flask_bouncer import Bouncer, ensure, can, requires
from bouncer.constants import *
from nose.tools import *
from .models import Article, TopSecretFile, User
from .helpers import user_set

app = Flask("basic")
app.debug = True
bouncer = Bouncer(app)


@bouncer.authorization_method
def define_authorization(user, they):

    if user.is_admin:
        # self.can_manage(ALL)
        they.can(MANAGE, ALL)
    else:
        they.can(READ, Article)
        they.can(EDIT, Article, author_id=user.id)


@app.route("/")
def hello():
    return "Hello World"


@app.route("/articles")
@requires(READ, Article)
def articles_index():
    return "A bunch of articles"


@app.route("/topsecret")
@requires(READ, TopSecretFile)
def topsecret_index():
    return "A bunch of top secret stuff that only admins should see"


@app.route("/article_ensure/<int:post_id>", methods=['POST'])
def edit_post_with_ensure(post_id):

    # Find an article form a db -- faking for testing
    mary = User(name='mary', admin=False)
    article = Article(author_id=mary.id)

    # bounce them out if they do not have access
    ensure(EDIT, article)
    # edit the post
    return "successfully edited post"


@app.route("/article_can/<int:post_id>", methods=['POST'])
def edit_post_with_can(post_id):

    # Find an article form a db -- faking for testing
    mary = User(name='mary', admin=False)
    article = Article(author_id=mary.id)

    # bounce them out if they do not have access
    if not can(EDIT, article):
        return abort(401)

    # edit the post
    return "successfully edited post"

client = app.test_client()


def test_default():
    jonathan = User(name='jonathan', admin=False)
    with user_set(app, jonathan):
        resp = client.get('/')
        eq_(b"Hello World", resp.data)


def test_allowed_index():
    jonathan = User(name='jonathan', admin=False)
    with user_set(app, jonathan):
        resp = client.get('/articles')
        eq_(b"A bunch of articles", resp.data)


def test_not_allowed_index():
    doug = User(name='doug', admin=False)
    with user_set(app, doug):
        resp = client.get('/topsecret')
        eq_(resp.status_code, 401)


def test_securing_specific_object_with_ensure():
    doug = User(name='doug', admin=False)
    with user_set(app, doug):
        resp = client.post('/article_ensure/1')
        eq_(resp.status_code, 401)


def test_securing_specific_object_with_can():
    doug = User(name='doug', admin=False)
    with user_set(app, doug):
        resp = client.post('/article_can/1')
        eq_(resp.status_code, 401)
