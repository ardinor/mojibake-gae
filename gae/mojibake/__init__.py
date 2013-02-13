from flask import Flask, request, url_for
from flask_login import LoginManager
from flask_assets import Environment, Bundle

app = Flask(__name__)
app.config.from_object('config')

lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'

assets = Environment(app)

css = Bundle('vendor/css/bootstrap.min.css',
    'vendor/css/bootstrap-responsive.css',
    'vendor/css/jquery.pnotify.default.css')
assets.register('css_all', css)

js = Bundle('vendor/js/bootstrap-scrollspy.js',
    'vendor/js/jquery-1.9.0.js',
    'vendor/js/jquery.pnotify.min.js',
    'vendor/js/bootstrap.min.js',
    'js/mojibake.js')
assets.register('js_all', js)


#http://flask.pocoo.org/snippets/44/
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

from mojibake import views
