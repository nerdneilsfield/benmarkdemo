from flask import Flask, g, request, jsonify
from flask_restful import  Resource, Api
import sqlite3

app = Flask(__name__)
api = Api(app)

DATABASE = './blog.db'


todos = {}

class HelloWorld(Resource):
    def get(self):
        return {"Ping":"Pong"}

class TodoSimple(Resource):
    def get(self, todo_id):
        return {todo_id: todos[todo_id]}
    def post(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}
    def put(self, todo_id):
        todos[todo_id] = request.form['data']
        return {todo_id: todos[todo_id]}
    def delte(selfs, todo_id):
        if todo_id in todos.keys():
            ha = todos[todo_id]
            del todos[todo_id]
            return {todo_id:ha}
        else:
            return {todo_id: "not exist"}


@app.route('/todo')
def todo():
    return jsonify(todos)



api.add_resource(HelloWorld, '/ping')
api.add_resource(TodoSimple, '/todo/<string:todo_id>')

if __name__ == '__main__':
    app.run()
