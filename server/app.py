#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

from flask import jsonify
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError
from models import User, Recipe


class Signup(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('image_url', type=str)
        parser.add_argument('bio', type=str)
        args = parser.parse_args()

        username = args['username']
        password = args['password']
        image_url = args.get('image_url')
        bio = args.get('bio')

        new_user = User(username=username, password=password, image_url=image_url, bio=bio)
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Username already exists'}), 422

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            return jsonify({'user_id': user.id, 'username': user.username, 'image_url': user.image_url, 'bio': user.bio}), 200
        else:
            return jsonify({'error': 'Unauthorized'}), 401

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        username = args['username']
        password = args['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return jsonify({'user_id': user.id, 'username': user.username, 'image_url': user.image_url, 'bio': user.bio}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return '', 204
        else:
            return jsonify({'error': 'Unauthorized'}), 401

class RecipeIndex(Resource):
    def get(self):
        if 'user_id' in session:
            recipes = Recipe.query.all()
            serialized_recipes = []
            for recipe in recipes:
                serialized_recipe = {
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'author': {
                        'user_id': recipe.author.id,
                        'username': recipe.author.username,
                        'image_url': recipe.author.image_url,
                        'bio': recipe.author.bio
                    }
                }
                serialized_recipes.append(serialized_recipe)
            return jsonify(serialized_recipes), 200
        else:
            return jsonify({'error': 'Unauthorized'}), 401



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)