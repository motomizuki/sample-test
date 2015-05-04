__author__ = 'mizumoto'

from flask import Blueprint, jsonify, request, abort
from app.models import Events, Users

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

