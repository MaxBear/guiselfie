from flask import render_template, flash
from flask_login import current_user
from selfie import app
from .util_views import view_wrapper

@app.context_processor
def inject_version():
   major = app.config['MAJOR_RELEASE']
   minor = app.config['MINOR_RELEASE']
   build = app.config['BUILD']
   version = "%s.%s.%s" % (major, minor, build)
   return dict(version=version)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404 

@app.route('/', methods=['GET'])
@view_wrapper()
def home():
    flash('Welcome, %s!' % current_user.name, '')
    return render_template('selfie/index.html')
