#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""
from gevent.pywsgi import WSGIServer # Imports the WSGIServer
from gevent import monkey; monkey.patch_all()
from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
import requests
import json

end_point = "http://192.168.15.240:9394/checks"
headers = {'Content-type':'application/json'}

app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'InPro':
        return 'Karvy@123'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

tasks = [
    {
        'id':1,
        'Panno': u'NA',
        'Invname': u'salih muhammad',
        'DOB': u'28/09/1973',
        'City': u'qatar',
        'Citizenship': u'qatar',
        'Year_Original': u'1973',
        'Day_Original': u'28',
        'Month_Original': u'9',
        'Key_Words': u'NA',
        'External_Sources':u'NA',
        'UIDs':u'2754303',
        'No_of_Matches': u'1',
        'Profile': 'Profile 2',
        'done':True
    }
]

task_fields = {
    'Panno': fields.String,
    'Invname': fields.String,
    'DOB': fields.String,
    'City': fields.String,
    'Citizenship': fields.String,
    'Year_Original': fields.String,
    'Day_Original': fields.String,
    'Month_Original': fields.String,
    'Key_Words': fields.String,
    'UIDs':fields.String,
    'No_of_Matches': fields.String,
    'External_Sources':fields.String,
    'Profile': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('Panno', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('Invname', type=str, default="",
                                   location='json')
        self.reqparse.add_argument('DOB', type=str, default="",
                                   location='json')
        self.reqparse.add_argument('City', type=str, default="",
                                   location='json')
        self.reqparse.add_argument('Citizenship', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        # print("Entered")
        return {'tasks': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'Panno':args['Panno'],
            'Invname': args['Invname'],
            'DOB': args['DOB'],
            'City': args['City'],
            'Citizenship': args['Citizenship'],
        }
        data = json.dumps(task)
        r = requests.post(url = end_point, data = data,headers = headers)
        task = json.loads(r.text)
        {kk: str(vv) for kk, vv in task.items()}
        if 'Profile 0' in task['Profile']:
            task['done'] = False
        else:
            task['done'] = True
        task['id'] = (tasks[-1]['id'] + 1 if len(tasks) > 0 else 1)
        # print(task['External_Sources'])
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('Panno', type=str, location='json')
        self.reqparse.add_argument('Invname', type=str, location='json')
        self.reqparse.add_argument('DOB', type=str, location='json')
        self.reqparse.add_argument('City', type=str, location='json')
        self.reqparse.add_argument('Citizenship', type=str, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}


api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')


if __name__ == '__main__':
    # app.run(host = '0.0.0.0',debug=True)
    LISTEN = ('0.0.0.0',5008)   

    http_server = WSGIServer( LISTEN, app )
    http_server.serve_forever()
