__author__ = 'mizumoto'
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'adfS3WbDE580-+k64vKielnfEg23+'

'''
@params: user = {'email': email, 'password': password}
@desc: encode user's email and password to jwt.
       jwt exp is i day.
@return: jwt string
'''
def encode_token(user):
    user['exp'] = datetime.utcnow() + timedelta(days=1)
    return jwt.encode(user, SECRET_KEY, algorithm='HS256').decode()


'''
@params token = jwt string
@desc decode jtw to user's.
      if token is time over return None
@return dict = {'email': email, 'password': password}
'''
def decode_token(token):
    try:
        options = {'verify_exp': True}
        ret = jwt.decode(token.encode(), SECRET_KEY, options=options, algorithms=['HS256'])
        return ret
    except jwt.ExpiredSignatureError:
        return None
