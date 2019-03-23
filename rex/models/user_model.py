import datetime
from mongokit import Document
from rex import app, db
import validators
from bson.objectid import ObjectId
__author__ = 'taijoe'


class User(Document):
    __collection__ = 'users'

    structure = {

        'customer_id' : unicode,
        'username': unicode,
        'password': unicode,
        'password_transaction' : unicode,
        'email': unicode,
        'fullname' : unicode,
        'telephone' : unicode,
        'p_node': unicode,
        'p_binary': unicode,
        'left': unicode,
        'right': unicode,
        'level': int,
        'level_dh': int,
        'creation': datetime.datetime,
        'total_pd_left' : float,
        'total_pd_right' : float,
        'max_out' : float,
        'total_earn' : float,
        'total_invest': float,
        'total_node' : float,
        'status' : int,
        'code_active' : unicode,
        'total_max_out': float,
        'investment' : float,
        'active_email' : int,
        'birthday' : datetime.datetime,
        'balance_wallet' : float,
        'total_receive' : float,
        'total_pd_lefts' : float,
        'total_pd_rights' : float,
        'th_wallet' : float,
        'dh_wallet' : float,
        'n_wallet' : float,
        'ch_wallet' :float,
        'address' : unicode,
        'cmnd' : unicode,
        'account_horder' : unicode,
        'account_number' : unicode,
        'bankname' : unicode,
        'brandname' : unicode
    }
    validators = {
        'email': validators.max_length(120)
    }
    default_values = {
        'creation': datetime.datetime.utcnow(),
        'level' : 0,
        'status' : 0,
        'total_pd_left' : 0,
        'total_pd_right' : 0,
        'total_receive' : 0,
        'total_pd_lefts' : 0,
        'total_pd_rights' : 0,
        'th_wallet' : 0,
        'dh_wallet' : 0,
        'n_wallet' : 0,
        'ch_wallet' :0,
        'balance_wallet' : 0
        }
    use_dot_notation = True

    def __repr__(self):
        return '<User %r>' % self.email

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def get_role(self):
        return self.role

    def get_user_home(self):
        role = db['roles'].find_one({'_id': self.get_role()})
        return role['home_page']


db.register([User])