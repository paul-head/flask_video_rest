from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from schemas import VideoSchema, UserSchema, AuthSchema
from flask_apispec import use_kwargs, marshal_with

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config.from_object(Config)


client = app.test_client()

engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

docs = FlaskApiSpec()
docs.init_app(app)

app.config.update({
    "APISPEC_SPEC": APISpec(
        title='videoblog',
        version='v1',
        openapi_version='2.0',
        plugins=[MarshmallowPlugin()]
    ),
    'APISPEC_SWAGGER_URL': '/swagger/'
})

from models import *

Base.metadata.create_all(bind=engine)


@app.route("/tutorials", methods=["GET"])
@jwt_required
@marshal_with(VideoSchema(many=True))
def get_list():
    try:
        user_id = get_jwt_identity()
        videos = Video.query.filter(Video.user_id == user_id).all()
    except Exception as e:
        return {'message': str(e)}, 400
    return videos


@app.route("/tutorials", methods=["POST"])
@jwt_required
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update_list(**kwargs):
    try:
        user_id = get_jwt_identity()
        new_one = Video(user_id=user_id, **kwargs)
        session.add(new_one)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return new_one


@app.route("/tutorials/<int:tutorial_id>", methods=["PUT"])
@jwt_required
@use_kwargs(VideoSchema)
@marshal_with(VideoSchema)
def update_tutorial(tutorial_id, **kwargs):
    try:
        user_id = get_jwt_identity()
        item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
        if not item:
            return {"message": "No tutorials with this id"}, 400
        for key, value in kwargs.items():
            setattr(item, key, value)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return item


@app.route("/tutorials/<int:tutorial_id>", methods=["DELETE"])
@jwt_required
@marshal_with(VideoSchema)
def delete_tutorial(tutorial_id):
    try:
        user_id = get_jwt_identity()
        item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
        if not item:
            return {"message": "No tutorials with this id"}, 400
        session.delete(item)
        session.commit()
    except Exception as e:
        return {'message': str(e)}, 400
    return "", 204


@app.route("/register", methods=["POST"])
@use_kwargs(UserSchema)
@marshal_with(AuthSchema)
def register(**kwargs):
    try:
        user = User(**kwargs)
        session.add(user)
        session.commit()
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {"access_token": token}


@app.route("/login", methods=["POST"])
@use_kwargs(UserSchema(only=('email', 'password')))
@marshal_with(AuthSchema)
def login(**kwargs):
    try:
        user = User.authenticate(**kwargs)
        token = user.get_token()
    except Exception as e:
        return {'message': str(e)}, 400
    return {"access_token": token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


docs.register(get_list)
# docs.register(update_list)
# docs.register(update_tutorial)
docs.register(delete_tutorial)
#docs.register(register)
#docs.register(login)


if __name__ == "__main__":
    app.run()
