# from flask.ext.wtf import Form, TextField, BooleanField, PasswordField, \
#     TextAreaField
# from flask.ext.wtf.html5 import EmailField
# from flask.ext.wtf import Required, Length, EqualTo
from models import Post
from flask_wtf import Form, TextField, BooleanField, PasswordField, \
    TextAreaField
from flask_wtf.html5 import EmailField
from flask_wtf import Required, Length, EqualTo


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class CreateUserForm(Form):
    username = TextField('Username', validators=[Required(), Length(max=50)])
    email = EmailField('E-mail', validators=[Required(), Length(max=255)])
    password = PasswordField('Password', validators=[Required()])
    password_verify = PasswordField('Password Again', validators=[Required(), EqualTo('password', message='Passwords must match')])


class PostForm(Form):
    title = TextField('Title', validators=[Required(), Length(max=255)])
    slug = TextField('Slug', validators=[Required(), Length(max=255)])
    body = TextAreaField('Body', validators=[Required()])
    visible = BooleanField('Visible')
    tags = TextField('Tags')

    #def __init__(self, *args, **kwargs):
    #    Form.__init__(self, *args, **kwargs)
    #    self.slug = None

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        slug = Post.all().filter('slug =', self.slug.data).get()
        if slug:
            self.slug.errors.append('The slug needs to be unique')
            return False

        return True


class CommentForm(Form):
    author = TextField('Author', validators=[Required(), Length(max=50)])
    email = EmailField('E-mail', validators=[Required(), Length(max=255)])
    body = TextAreaField('Comment', validators=[Required()])
