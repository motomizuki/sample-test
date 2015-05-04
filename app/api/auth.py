__author__ = 'mizumoto'

from flask import Blueprint, jsonify, request
import hashlib
from app.models import Users
from app.jwtutils import encode_token, decode_token
from logging import getLogger,StreamHandler,DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

module = Blueprint('auth', __name__, url_prefix='/api/auth')

'''
@param {string} email: required
@param {string} password: required
@return {number} code: status code
@return {string} token: jwt
@return {object} user: user info
@description
user login and get token, user data.
'''
@module.route('/login', methods=['POST'])
def login():
    response = {'code': 500}
    email = request.form['email']
    password = request.form['password']

    if email and password:
        user = existed_user(email, hashlib.sha1(password.encode()).hexdigest())
        if user:
            response['code'] = 200
            response['token'] = create_token(user)
            response['user'] = {'id': user.id,
                                'name': user.name,
                                'group_id': user.group_id}
    return jsonify(response)


'''
@param {string} email: required
@param {string} password: required, hashed strings
@return {object} user: user data
@description
check existed user? and collect password?
if invalid return False.
'''
def existed_user(email, password):
    user = Users.query.filter_by(email=email).first()
    if user:
        if user.password == password:
            return user

    return False


def create_token(user):
    token = encode_token({u'email': user.email,
                          u'password': user.password})
    return token


def get_user_from_token(token):
    if token is None:
        return False

    claim = decode_token(token)
    #if invalid email, password, existed_user return False
    user = existed_user(claim['email'], claim['password'])
    return user
