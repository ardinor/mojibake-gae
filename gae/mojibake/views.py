from flask import render_template, g, redirect, url_for, \
    flash, request, jsonify, abort, session
#from flask import session
from flask_login import login_required, login_user, \
    logout_user, current_user
from passlib.hash import pbkdf2_sha256
#from datetime import datetime
#from google.appengine.api import users
from math import ceil

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from mojibake import app, lm
from models import User, Post, Comment
from models import POST_VISIBLE, ROLE_ADMIN
from forms import LoginForm, CreateUserForm, PostForm, \
    CommentForm
from config import POSTS_PER_PAGE
from config import REGISTRATION, REGISTRATION_OPEN


#http://flask.pocoo.org/snippets/44/
class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


@app.route("/", defaults={'page': 1})
@app.route("/index", defaults={'page': 1})
@app.route("/<int:page>")
def index(page):
    #post_count = Post.query().fetch().count(100)  # limit=0
    p = Post.query(Post.visible == True).order(-Post.created_at)
    #if page > 1:
    #    page_offset = (page - 1) * POSTS_PER_PAGE
    #    posts = Post.query().filter("visible =", True).order("-created_at").run(offset=page_offset, limit=POSTS_PER_PAGE)
    #else:
        #posts = Post.query().filter("visible =", True).order("-created_at").run(limit=POSTS_PER_PAGE)
    #    posts = Post.query(Post.visible == True).order(-Post.created_at).fetch(limit=POSTS_PER_PAGE)
    #if not posts and page != 1:
    #    abort(404)
    #pagination = Pagination(page, POSTS_PER_PAGE, post_count)

    if page == 1:
        posts, cursor, more = p.fetch_page(POSTS_PER_PAGE)
        session['cursor'] = cursor.urlsafe()
    else:
        if 'cursor' in session:
            cursor = Cursor(urlsafe=session['cursor'])
            posts, cursor, more = p.fetch_page(POSTS_PER_PAGE, start_cursor=cursor)
            session['cursor'] = cursor


    #recent = Post.objects(visible=True).order_by('-created_at')[:5]
    return render_template("posts/list.html",
        posts=posts,
        more=more,
        pagination=''
        )  # recent=recent


@app.route('/post/<slug>', methods=['GET', 'POST'])
def get_post(slug):
    #post = Post.all().filter('slug =', slug).get()
    post = Post.query(Post.slug == slug).get()
    if not post:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
            author=form.author.data,
            email=form.email.data,
            post=post
            )
        comment.put()
        flash('Comment posted and awaiting administrator approval.', 'success')
        return redirect(url_for('get_post', slug=slug))
    return render_template('posts/detail.html',
        post=post,
        slug=slug,
        form=form,
        title=post.title)


@app.route('/post/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    #post = Post.all().filter('slug =', slug).get()
    post = Post.query(Post.slug == slug).get()
    if not post:
        abort(404)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        tags_list = []
        for i in form.tags.data.split(','):
            tags_list.append(i.strip())
        post.title = form.title.data
        post.slug = form.slug.data
        post.body = form.body.data
        post.visible = form.visible.data
        post.tags = tags_list
        post.put()
        flash('Post updated!', 'success')
        return redirect(url_for('get_post', slug=slug))
    return render_template('posts/edit.html',
        form=form,
        title='Edit Post')


@app.route('/post/<slug>/delete', methods=['GET'])
@login_required
def delete_post(slug):
    #post = Post.all().filter('slug =', slug).get()
    post = Post.query(Post.slug == slug).get()
    if not post:
        abort(404)
    user = g.user
    #check if it's the users post or if the user has admin?
    if User.get_by_id(int(user.key().id())) == post.author or User.get_by_id(int(user.key().id())).role == ROLE_ADMIN:
        post.delete()
        flash('Post deleted!', 'success')
        return redirect(url_for('index'))
    else:
        flash('You do not have permission to delete this post.', 'error')
    return redirect(url_for('get_post', slug=slug))


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    user = g.user
    if form.validate_on_submit():
        tags_list = []
        for i in form.tags.data.split(','):
            tags_list.append(i.strip())
        post = Post(title=form.title.data,
            slug=form.slug.data,
            body=form.body.data,
            visible=form.visible.data,
            author=User.get_by_id(int(user.key().id())),
            tags=tags_list)  # tags not right I think
        post.put()

        #user.posts.append(post)
        flash('Post created!', 'success')
        return redirect(url_for('get_post', slug=post.slug))
    return render_template('posts/edit.html',
        form=form,
        title='New Post')


@app.route('/tags')
@app.route('/tags/<tag>')
def tags(tag=None):
    if tag is None:
        tags = Post.objects(visible=True).distinct('tags')
        return render_template('posts/tags.html',
            tags=tags)
    else:
        posts = Post.objects(tags=tag, visible=POST_VISIBLE)
        return render_template('posts/tag_list.html',
            posts=posts,
            tag=tag,
            title=tag)


@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    if username is None:
        users = User.objects.all()
        return render_template('users/userlist.html',
            users=users)
    else:
        user = User.objects.get_or_404(username=username)
        return render_template('users/user.html',
            user=user)


@app.route('/panel')
@app.route('/panel/<int:page>')
@login_required
def panel(page=1):
    user = g.user
    #can't just use user as it is type <class 'werkzeug.local.LocalProxy'>
    #better way of doing this?
    awaiting_comments = {}
    post_awaiting_comments = []
    #paginate comments? what if there's 50 comments?
    #author = User.objects(id=user.id)[0] User.get_by_id(int(id))
    #author = User.get_by_id(int(user.key.id()))
    #Post.objects
    ##for i in Post.all().filter('author =', author).filter(comments__approved=False):
    ##    post_awaiting_comments = post_awaiting_comments + i.get_comments_awaiting()
    ##    awaiting_comments[i] = post_awaiting_comments
    ##    post_awaiting_comments = []
    #posts = Post.objects(author=author).paginate(page=page, per_page=POSTS_PER_PAGE)
    #posts = Post.all().filter('author =', author).order('-created_at').run(limit=POSTS_PER_PAGE)
    query = Post.query(Post.author == ndb.Key(User, int(user.key.id()))). \
        order(-Post.created_at)
    if page == 1:
        posts, cursor, more = query.fetch_page(POSTS_PER_PAGE)
        g.cursor = cursor
    else:
        if g.cursor:
            posts, cursor, more = query.fetch_page(POSTS_PER_PAGE, cursor)
    return render_template('users/panel.html',
        user=user,
        pagination=posts,
        comments=awaiting_comments)


@app.route('/panel/comment/approve')
def approve_comment():
    rqst_comment = request.args.get('comment')
    with open('C:/Git/testpast.txt', 'w') as f:
        f.write(rqst_comment.encode('utf-8'))
    return jsonify(comment=rqst_comment)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('panel'))
    form = LoginForm()
    if form.validate_on_submit():
        #logging_in_user = User.objects(username=form.username.data)
        #logging_in_user = User.all().filter('username =', form.username.data).get()
        logging_in_user = User.query(User.username == form.username.data).get()
        if logging_in_user:
            #logging_in_user = logging_in_user[0]
            if pbkdf2_sha256.verify(form.password.data, logging_in_user.password):
            #if True:
                remember_me = False
                if form.remember_me.data:
                    remember_me = True
                login_user(logging_in_user, remember=remember_me)
                return redirect(request.args.get('next') or url_for('panel'))
            else:
                flash('Invalid login. Please try again.', 'error')
                redirect(url_for('login'))
        else:
            flash('Invalid login. Please try again.', 'error')
            redirect(url_for('login'))
    return render_template('users/login.html',
        title='Sign In',
        form=form)


@app.route('/loginmodal')
def login_modal():
    form = LoginForm()
    return render_template('users/loginmodal.html',
        form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if REGISTRATION == REGISTRATION_OPEN:
        form = CreateUserForm()
        if form.validate_on_submit():
            new_user = User(username=form.username.data,
                email=form.email.data,
                password=pbkdf2_sha256.encrypt(form.password.data))
            new_user.put()
            return redirect(url_for('panel'))
            #else:
            #    flash('Invalid details. Please try again.')
            #    redirect(url_for('create'))
        return render_template('users/create.html',
            title='Create account',
            form=form)
    else:
        return render_template('users/closed.html',
            title='Registration closed.')



@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.before_request
def before_request():
    g.user = current_user
    #if g.user.is_authenticated():
    #    g.user.last_seen = datetime.utcnow()
    #    g.user.save()


@lm.user_loader
def load_user(id):
    #return User.objects.get(id)
    #the above returned MultipleObjectsReturned: 2 items returned, instead of 1
    #the below right or messy?
    #return User.objects(id=id)[0]
    #return User.all().filter('id =', id).get()
    return User.get_by_id(int(id))
