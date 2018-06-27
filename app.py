import os
import sqlite3

from flask import Flask, g, request, redirect
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

DATABASE = './ha.db'

todos = {}


def getDB():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # print(db)
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


def queryDB(query, args=(), one=False):
    with app.app_context():
        print(query)
        cur = getDB().execute(query, args)
        # rv = cur.fetchall()
        rv = [dict((cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in cur.fetchall()]
        cur.close()
        return (rv[0] if rv else None) if one else rv

def updateDB(query):
    with app.app_context():
        db = getDB()
        cur = db.execute(query)
        cur.close()
        db.commit()



def backTagsAll():
    tags =  queryDB('select name from tags;')
    if not tags:
        return {"code":404}
    else:
        return {"code":200, "tags":tags}


def backTagsPosts(tag_id=1, name='default', use_id=True):
    if use_id:
        post_ids = queryDB('select post_id from post_tags where tag_id = %s;' % (str(tag_id)))
    else:
        tag_id = queryDB('select tag_id from tags where name ="%s";' % name, one=True)
        if not tag_id:
            return {"code": 404}
        tag_id = tag_id['tag_id']
        post_ids = queryDB('select post_id from post_tags where tag_id = %s;' % (str(tag_id)))
    if not post_ids:
        return {"code": 404}
    posts = [backPost(post_id['post_id'])[1] for post_id in post_ids]
    return {"code":200, "posts":posts}


def backPostsAll():
    posts = queryDB('select * from posts order by update_time desc;')
    for post in posts:
        post_id = post['post_id']
        tag_ids = [tag_id['tag_id'] for tag_id in
                   queryDB('select tag_id from post_tags where post_id = %s;' % str(post_id))]
        tags = [queryDB('select name from tags where tag_id=%s;' % (str(tag_id)), one=True)['name'] for tag_id in
                tag_ids]
        post['tags'] = tags
    return posts


def backPost(post_id):
    print(post_id)
    post = queryDB('select * from posts where post_id = %s;' % (str(post_id)), one=True)
    if not post:
        return 404, None
    post_id = post['post_id']
    tag_ids = [tag_id['tag_id'] for tag_id in queryDB('select tag_id from post_tags where post_id = %s;' % str(post_id))]
    tags = [queryDB('select name from tags where tag_id=%s;' % (str(tag_id)), one=True)['name'] for tag_id in tag_ids]
    post['tags'] = tags
    return 200,post


def createPost(title, content, descrption, tags):
    if not descrption:
        try:
            descrption = content[:50]
        except:
            descrption = content
    updateDB('insert into posts (title, descrption, content, create_time) values '
            '("%s", "%s", "%s", current_time);' % (title, content, descrption))
    post_id = queryDB('select post_id from posts order by post_id DESC;', one=True)

    addTags(post_id['post_id'], tags)

    return post_id['post_id']


def addTags(post_id, tags):
    print(post_id, " Post ID")
    for tag in tags:
        tag_id = getTagID(tag)
        var = queryDB('select * from post_tags where post_id = %s and tag_id=%s;' % (post_id, tag_id))
        print("Var is ", var)
        if not var:
            updateDB('insert into post_tags (post_id, tag_id) values (%s, %s) ;' % (post_id, tag_id))


def getTagID(name):
    tag = queryDB('select tag_id from tags where name = "%s";' % name)
    if len(tag) == 0:
        updateDB('insert into tags (name) values ("%s");' % name)
        tag = queryDB('select tag_id from tags where name = "%s";' % name)
    return tag[0]['tag_id']

def updatePost(post_id, title, content, descrption, tags):
    if not descrption:
        try:
            descrption = content[:50]
        except:
            descrption = content
    var = queryDB('select * from posts where post_id = %s' % str(post_id))
    if not var:
        return 404, None
    updateDB('update  posts set title = "%s", descrption = "%s", content ="%s", create_time = "%s", update_time=current_time '
             'where post_id = %s;' % (title, content, descrption, post_id))

    addTags(post_id, tags)

    return 200,post_id


class Post(Resource):
    def get(self, post_id):
        code, post = backPost(post_id)
        if code == 200:
            return {"code":200, "post": post}
        else:
            return {"code":code}
    def put(self, post_id):
        title = request.json['title']
        content = request.json['content']
        tags = request.json['tags']
        descrption = request.json['descrption']
        code, post_id = updatePost(post_id, title, content, descrption, tags)
        if code == 200:
            return {"code": 200, "post_id": post_id}
        else:
            return {"code":code}


class PostAdd(Resource):
    def post(self):
        title = request.json['title']
        content = request.json['content']
        tags = request.json['tags']
        descrption = request.json['descrption']
        print(request.json)
        post_id = createPost(title, content, descrption, tags)
        return {"code":200, "post_id":post_id}


class Tag(Resource):
    def get(self, name):
        return backTagsPosts(name=name, use_id=False)

class Tags(Resource):
    def get(self):
        return  backTagsAll()


api.add_resource(Post, '/posts/<string:post_id>')
api.add_resource(Tag, '/tags/<string:name>')
api.add_resource(PostAdd, '/posts','/posts/')
api.add_resource(Tags, '/tags','/tags/')

if __name__ == '__main__':
    initDB()
    app.run()
