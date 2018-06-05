from flask_restful import Resource, reqparse, marshal_with, fields, abort
from app.models import Post, User


parser = reqparse.RequestParser()
parser.add_argument('post_id', type=int, help='post_id please.')

parser2 = reqparse.RequestParser()
parser2.add_argument('user_id', type=int, help='user_id please.')

post_fields = {
    'title': fields.String,
    'outline': fields.String,
    'body': fields.String,
    'timestamp': fields.DateTime,
    'author_id': fields.Integer,
    'praise': fields.Integer,
    'kind_id': fields.Integer
}

user_fields = {
    'email': fields.String,
    'role_id': fields.Integer,
    'username': fields.String,
    'about_me': fields.String,
    'member_since': fields.DateTime,
    'last_seen': fields.DateTime,
    'likes': fields.Integer
}


class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self):
        args = parser.parse_args(strict=True)
        post = Post.query.filter_by(id=args['post_id']).first()
        print(args['post_id'], post)
        if post:
            return post
        abort(404)


class UserApi(Resource):
    @marshal_with(user_fields)
    def get(self):
        args = parser2.parse_args(strict=True)
        user = User.query.filter_by(id=args['user_id']).first()
        print(args['user_id'], user)
        if user:
            return user
        abort(404)
