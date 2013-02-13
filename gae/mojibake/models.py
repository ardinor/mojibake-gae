import datetime
from flask import url_for
#from mojibake import db
from google.appengine.ext import db

ROLE_USER = 0
ROLE_STAFF = 1
ROLE_ADMIN = 2

STATUS_ACTIVE = 0
STATUS_INACTIVE = 1
STATUS_BANNED = 2

POST_VISIBLE = True
POST_INVISIBLE = False

COMMENT_AWAITING = False
COMMENT_APPROVED = True


class User(db.Model):
    username = db.StringProperty(required=True)  # , unique=True
    email = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    role = db.IntegerProperty(default=ROLE_USER)
    status = db.IntegerProperty(default=STATUS_ACTIVE)
    last_seen = db.DateTimeProperty()
    #posts = db.ListField(db.ReferenceField('Post', dbref=True))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.key().id())

    #def __unicode__(self):
    #    return self.username

    def __repr__(self):
        return '<User %r>' % (self.username)

    #meta = {
    #    #'allow_inheritance': True,
    #    'indexes': ['username'],
    #    'ordering': ['username']
    #}


class Post(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True, required=True)
    #overreplication of data? But I want to query uniques values of these....
    #created_year = db.IntegerProperty(default=datetime.datetime.now().year, required=True)
    #created_month = db.IntegerProperty(default=datetime.datetime.now().month, required=True)
    #created_day = db.IntegerProperty(default=datetime.datetime.now().day, required=True)
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    body = db.StringProperty(required=True)
    visible = db.BooleanProperty(default=POST_VISIBLE)
    #author = db.ReferenceField(User, dbref=True, reverse_delete_rule=db.CASCADE)
    author = db.ReferenceProperty(User)
    #edited at?
    #tags = db.ListField(db.EmbeddedDocumentField('Tag'))
    #tags = db.ListField(db.StringProperty())  # tags later - many to many http://blog.notdot.net/2010/10/Modeling-relationships-in-App-Engine
    #comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post', kwargs={'slug': self.slug})

    # def get_visible_comments(self):
    #     visible_comments = []
    #     for i in self.comments:
    #         if i.approved == True:
    #             visible_comments.append(i)
    #     return visible_comments

    # def get_comments_awaiting(self):
    #     awaiting_comments = []
    #     for i in self.comments:
    #         if i.approved == False:
    #             awaiting_comments.append(i)
    #     return awaiting_comments

    # @db.queryset_manager
    # def visible_posts(self, queryset):
    #     return queryset.filter(visible=POST_VISIBLE)

    #Post.objects.filter(comments__approved=False)  # returns all posts with comments awaiting approval

    #def __unicode__(self):
    #    return self.title

    def __repr__(self):
        return '<Post %r>' % (self.title)

    # meta = {
    #     'allow_inheritance': True,
    #     'indexes': ['-created_at', 'slug'],
    #     'ordering': ['-created_at'],
    #     'cascade': True
    # }


class Comment(db.Model):
    created_at = db.DateTimeProperty(auto_now_add=True, required=True)
    body = db.StringProperty(verbose_name='Comment', required=True)
    author = db.StringProperty(verbose_name='Name', required=True)
    email = db.StringProperty(verbose_name='E-mail', required=True)
    approved = db.BooleanProperty(default=COMMENT_AWAITING)
    post = db.ReferenceProperty(Post)

    def __repr__(self):
        return '<Comment %r>' % (self.author)

#class Tag(db.Document):
    #maybe change this to a Document not EmbeddedDocument?
#    tag = db.StringProperty()
#    posts = db.ListField(db.ReferenceField(Post, dbref=True))
    #tag = db.ReferenceField(User, dbref=True, reverse_delete_rule=db.CASCADE)

#    def __unicode__(self):
#        return self.tag
