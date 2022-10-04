from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, url_for_security
from flask import redirect, url_for
from selfie import app
from .util_views import log_access 

al_db = SQLAlchemy(app)

roles_users = al_db.Table(
   'roles_users',
   al_db.Column('user_id', al_db.Integer(), al_db.ForeignKey('user.id')),
   al_db.Column('role_id', al_db.Integer(), al_db.ForeignKey('role.id'))
)

class Role(al_db.Model, RoleMixin):
   id = al_db.Column(al_db.Integer(), primary_key=True)
   name = al_db.Column(al_db.String(80), unique=True)
   description = al_db.Column(al_db.String(255))

   def __str__(self):
      return self.name

   def __hash__(self):
      return hash(self.name)

class User(al_db.Model, UserMixin):
   id = al_db.Column(al_db.Integer, primary_key=True)
   email = al_db.Column(al_db.String(255), unique=True)
   password = al_db.Column(al_db.String(255))
   name = al_db.Column(al_db.String(255))
   active = al_db.Column(al_db.Boolean())
   #
   last_login_at = al_db.Column(al_db.DateTime())
   current_login_at = al_db.Column(al_db.DateTime())
   last_login_ip = al_db.Column(al_db.String(45))
   current_login_ip = al_db.Column(al_db.String(45))
   login_count = al_db.Column(al_db.Integer)
   failed_login_count = al_db.Column(al_db.Integer)

user_datastore = SQLAlchemyUserDatastore(al_db, User, Role)
security = Security(app, user_datastore)

@app.route('/', methods=['GET', 'POST'])
def login():
    return redirect(url_for_security('login'))
