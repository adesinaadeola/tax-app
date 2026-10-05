"""
User module for creating, deleting, and user log in 
"""
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token

from db import db
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", __name__, description="user details")

@blp.route("/register")
class UserRegister(MethodView):
    """
    create a user
    """
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
    """
    login user
    """
    @blp.arguments(UserSchema)
    def post(self, userdata):
        """
        A secure login function 
        """
        user = UserModel.query.filter(
            UserModel.email == userdata["email"]
        ).first()

        if user and pbkdf2_sha256.verify(userdata["password"], user.password):
            access_token = create_access_token(identity=str(user.id))
            return {"access_token": access_token, "userid":f"{user.id}"}, 200

        abort(401, message="Invalid email or password.")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    A method for getting all users and deleting user
    """
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """
        This is solely for the developer use. Get user by id
        """
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        """ 
        delete user by id. This clear all the user data
        """
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
