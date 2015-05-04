__author__ = 'mizumoto'

from flask import Blueprint, jsonify, request, abort
from app.models import Events, Users, Attends
from app.api.auth import get_user_from_token
from app.models import db
from datetime import datetime

module = Blueprint('users', __name__, url_prefix='/api/users')

'''
@param {string} from: required
@param {number} offset: optional, min 0
@param {number} limit: optional, min 1
@return {number} code: status code
@return {object} events: event list
@description
login is not required
get events list.
'''
@module.route('/events')
def events():
    events_from = request.args.get("from")
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    if events_from is None:
        abort(400)

    q = Events.query.join(Users, Events.user_id == Users.id) \
        .filter(Events.start_date >= events_from).order_by(Events.start_date)
    if offset is not None:
        try:
            offset = int(offset)
            if offset >= 0:
                q = q.offset(offset)
            else:
                abort(400)
        except ValueError:
            abort(400)

    if limit is not None:
        try:
            limit = int(limit)
            if limit > 0:
                q = q.limit(limit)
            else:
                abort(400)
        except ValueError:
            abort(400)

    results = q.all()
    json_results = []
    for result in results:
        d = {'id': result.id,
             'name': result.name,
             'start_date': result.start_date.strftime('%Y-%m-%d %H:%M:%S'),
             'company': {
                 'id': result.users.id,
                 'name': result.users.name
             }
        }
        json_results.append(d)

    return jsonify({'code': 200, 'events': json_results})


'''
@param {string} token: required
@param {number} event_id: required
@param {string} reserve: required, true is 'reserve', false is 'cancel'
@return {number} code: status code
@return {string} message: error messages if code is not 200.
@description
login is required and student only.
reserve/cancel events.
'''
@module.route('/reserve', methods=['POST'])
def reserve():
    token = request.form['token']
    event_id = int(request.form['event_id'])
    is_reserve = request.form['reserve']

    if token == 'null' or token is None:
        return jsonify({'code': 401, 'message': 'can not call with out login'})

    user = get_user_from_token(token)
    if user and user.group_id == 1:
        if is_reserve == 'true':
            response = reserved(user.id, event_id)
        elif is_reserve == 'false':
            response = cancel(user.id, event_id)
        else:
            response = {'code': 401, 'message': 'invalid parameters'}
        return jsonify(response)
    else:
        return jsonify({'code': 401, 'message': 'can not reserve event.'})


def reserved(user_id, event_id):
    # check if already reserved
    attend = Attends.query \
        .filter(Attends.user_id == user_id, Attends.event_id == event_id) \
        .first()
    if attend is None:
        try:
            db.session.add(Attends(user_id, event_id))
            db.session.commit()
            return {'code': 200}
        except:
            return {'code': 500, 'message': 'database error.'}

    else:
        return {'code': 501, 'message': 'can not reserve already reaserved event.'}


def cancel(user_id, event_id):
    attend = Attends.query \
        .filter(Attends.user_id == user_id, Attends.event_id == event_id) \
        .first()
    if attend:
        try:
            db.session.delete(attend)
            db.session.commit()
            return {'code': 200}
        except:
            return {'code': 500, 'message': 'database error.'}
    else:
        return {'code': 502, 'message': 'can not unreserve not reaserved event.'}

