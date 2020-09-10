from flask import Flask, jsonify, request
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config.from_object(Config)


client = app.test_client()

engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

jwt = JWTManager(app)

from models import *

Base.metadata.create_all(bind=engine)


@app.route("/tutorials", methods=["GET"])
@jwt_required
def get_list():
    user_id = get_jwt_identity()
    videos = Video.query.filter(Video.user_id == user_id).all()
    serialized = []
    for video in videos:
        serialized.append(
            {
                "id": video.id,
                "user_id": video.user_id,
                "name": video.name,
                "description": video.description,
            }
        )
    return jsonify(serialized)


@app.route("/tutorials", methods=["POST"])
@jwt_required
def update_list():
    user_id = get_jwt_identity()
    new_one = Video(user_id=user_id, **request.json)
    session.add(new_one)
    session.commit()
    serialized = {
        "id": new_one.id,
        "user_id": new_one.user_id,
        "name": new_one.name,
        "description": new_one.description,
    }
    return jsonify(serialized)


@app.route("/tutorials/<int:tutorial_id>", methods=["PUT"])
@jwt_required
def update_tutorial(tutorial_id):
    user_id = get_jwt_identity()
    item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
    params = request.json
    if not item:
        return {"message": "No tutorials with this id"}, 400
    for key, value in params.items():
        setattr(item, key, value)
    session.commit()
    serialized = {
        "id": item.id,
        "user_id": item.user_id,
        "name": item.name,
        "description": item.description,
    }
    return serialized


@app.route("/tutorials/<int:tutorial_id>", methods=["DELETE"])
@jwt_required
def delete_tutorial(tutorial_id):
    user_id = get_jwt_identity()
    item = Video.query.filter(Video.id == tutorial_id, Video.user_id == user_id).first()
    if not item:
        return {"message": "No tutorials with this id"}, 400
    session.delete(item)
    session.commit()
    return "", 204


@app.route("/register", methods=["POST"])
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    token = user.get_token()
    return {"access_token": token}


@app.route("/login", methods=["POST"])
def login():
    params = request.json
    user = User.authenticate(**params)
    token = user.get_token()
    return {"access_token": token}


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()


if __name__ == "__main__":
    app.run()
