from flask import Flask, g, request, jsonify
from flask_restful import  Resource, Api

import  os
import sqlite3

app = Flask(__name__)
api = Api(app)

DATABASE = './blog.db'


todos = {}

def getDB():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def initDB():
    if os.path.exists(DATABASE):
        return
    else:
        with app.app_context():
            db = getDB()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


@app.route('/todo')
def todo():
    return jsonify(todos)



api.add_resource(HelloWorld, '/ping')
api.add_resource(TodoSimple, '/todo/<string:todo_id>')

if __name__ == '__main__':
    app.run()
