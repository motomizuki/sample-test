__author__ = 'mizumoto'

from flask import Blueprint, jsonify, request, abort
from app.api.auth import get_user_from_token
from app.models import Events, Attends

module = Blueprint('companies', __name__, url_prefix='/api/companies')


'''
@param {string} token: required
@param {string} from: required
@param {number} offset: optional, min 0
@param {number} limit: optional, min 1
@return {number} code: status code
@return {object} events: event list
@description
login is required and company user only.
get own event list and number of event attendees.
'''
@module.route('/events', methods=['POST'])
def events():
    token = request.form['token']  # required
    events_from = request.form['from']  # required

    # check required parameter
    if token == 'null' or token is None:
        return jsonify({'code': 401})

    if events_from == 'null' or events_from is None:
        abort(400)

    user = get_user_from_token(token)
    if user and user.group_id == 2:
        q = Events.query \
            .filter(Events.start_date >= events_from, Events.user_id == user.id) \
            .order_by(Events.start_date)

        if 'offset' in request.form:
            try:
                offset = int(request.form['offset'])
                if offset >= 0:
                    q = q.offset(offset)
                else:
                    abort(400)
            except ValueError:
                abort(400)

        if 'limit' in request.form:
            try:
                limit = int(request.form['offset'])
                if limit > 0:
                    q = q.limit(limit)
                else:
                    abort(400)
            except ValueError:
                abort(400)

        json_results = []
        results = q.all()
        for result in results:
            attend = Attends.query.filter(Attends.event_id == result.id).count()
            d = {'id': result.id,
                 'name': result.name,
                 'start_date': result.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                 'number_of_attendees': attend
            }
            json_results.append(d)

        return jsonify({'code': 200, 'events': json_results})
    else:  # students or invalid token
        return jsonify({'code': 401})
