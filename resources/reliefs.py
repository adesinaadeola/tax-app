"""
Relief module contains apis for creating, updating, deleting, 
and retrieving the relief for a user
"""
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from db import db
from models import ReliefModel

from schemas import DefaultReliefSchema, ReliefCreationSchema



blp = Blueprint("relief", __name__, description="Operations on relief")

@blp.route("/getrelief")
class GetAllRelief(MethodView):
    """
    get all relief
    """
    @blp.response(200, DefaultReliefSchema(many=True))
    def get(self):
        return ReliefModel.query.all()

@blp.route("/relief/<int:userid>")
class Relief(MethodView):
    """
    get all relief for the user
    """
    @jwt_required()
    @blp.response(200, DefaultReliefSchema(many=True))
    def get(self,userid):
        try:
            relief = (
                db.session.execute(db.select(ReliefModel)
                                   .filter_by(userid=userid)).scalars().all()
            )
            if not relief:
                abort(404, message = "The user has no relief")
        except SQLAlchemyError as error:
            abort(500, message = str(error))
        return relief

@blp.route("/relief/<int:relief_id>")
class DeleteRelief(MethodView):
    """
    delete specified relief
    """
    @jwt_required()
    def delete(self,relief_id):
        try:
            relief = (
                db.session.execute(db.select(ReliefModel)
                                   .filter_by(id=relief_id)).scalar_one()
            )
            db.session.delete(relief)
            db.session.commit()
        except NoResultFound:
            abort(404, message="The relief does not exist")
        return {"message": "The relief has been deleted"}, 200

@blp.route("/createrelief")
class CreateRelief(MethodView):
    """
    create a relief
    """
    @jwt_required()
    @blp.arguments(ReliefCreationSchema)
    def post(self,reliefdata):
        relief = ReliefModel(**reliefdata)
        try:
            db.session.add(relief)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )

            if constraint_name == "uq_relief_perperiod":
                abort(409, message="The relief already exists for the pay period.")

            abort(500, message="Unable to create relief.")
        except SQLAlchemyError as e:
            abort(500, message=f"{e}")

        return {"message":"relief created successfully"}

@blp.route("/relief/<string:relief_id>")
class UpdateRelief(MethodView):
    """
    update relief
    """
    @jwt_required()
    @blp.arguments(DefaultReliefSchema)
    @blp.response(200, DefaultReliefSchema)
    def put(self,reliefdata,relief_id):
        relief = (
            db.session.execute(db.select(ReliefModel)
                               .filter_by(id=relief_id)).scalar_one()
        )
        try:
            if relief:
                if "description" in reliefdata:
                    relief.description = reliefdata["description"]
                if "amount" in reliefdata:
                    relief.amount = reliefdata["amount"]
                if "payperiod" in reliefdata:
                    relief.payperiod = reliefdata["payperiod"]
                db.session.commit()
            else:
                relief = ReliefModel(**reliefdata)
                db.session.add(relief)
                db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )
            if constraint_name == "uq_relief_perperiod":
                abort(409, message="The relief already exists for the pay period.")

            abort(500, message="Unable to create relief.")

        return relief
    