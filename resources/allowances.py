"""
Allowance module contains apis for creating, updating, deleting, 
and retrieving the allowance for a user
"""
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from db import db
from models import AllowanceModel

from schemas import DefaultAllowDeductSchema, AllowDeductCreationSchema, UpdateAllowDeductSchema



blp = Blueprint("allowances", __name__, description="Operations on allowances")

# get all allowances that belongs to a user
@blp.route("/getallowance")
class GetAllAllowance(MethodView):
    """
    obtain all allowances on the db
    """
    @blp.response(200, DefaultAllowDeductSchema(many=True))
    def get(self):
        return AllowanceModel.query.all()

@blp.route("/allowance/<int:userid>")
class Allowance(MethodView):
    """
    get all allowance that belong to a particular user
    """
    @jwt_required()
    # if user not found redirect to login page
    @blp.response(200, DefaultAllowDeductSchema(many=True))
    def get(self,userid):
        # allowance = db.get_or_404(AllowanceModel, userid)
        try:
            allowance = (
                db.session.execute(db.select(AllowanceModel)
                                   .filter_by(userid=userid)).scalars().all()
            )
            if not allowance:
                abort (404, message= "User has no allowance")
        except SQLAlchemyError as error:
            abort(500, message=str(error))

        return allowance
           
@blp.route("/allowance/<int:allow_id>")
class DeleteAllowance(MethodView):
    """
    delete a sepcified allowance 
    """
    @jwt_required()
    def delete(self,allow_id):
        # allowance = AllowanceModel.query.get_or_404(allow_id)
        try:
            allowance = db.session.execute(db.select(AllowanceModel)
                                           .filter_by(id=allow_id)).scalar_one()
            db.session.delete(allowance)
            db.session.commit()
        except NoResultFound:
            abort(404, message="The allowance does not exist")
        return {"message": "The allowance has been deleted"}, 200

@blp.route("/createallowance")
class CreateAllowance(MethodView):
    """
    create user allowance
    """
    @jwt_required()
    @blp.arguments(AllowDeductCreationSchema)
    def post(self,allowancedata):
        allowances = AllowanceModel(**allowancedata)
        try:
            db.session.add(allowances)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )
            if constraint_name == "uq_allowance_perperiod":
                abort(409, message="The allowance already exists for the pay period.")

            abort(500, message="Unable to create allowance.")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"{e}")

        return {"message":"allowance created successfully"}

    # add an update endpoint using put
@blp.route("/allowance/<int:allow_id>")
class UpdateAllowance(MethodView):
    """
    update specified user allowance
    """
    @jwt_required()
    @blp.arguments(UpdateAllowDeductSchema)
    @blp.response(200, DefaultAllowDeductSchema)
    def put(self,allowancedata,allow_id):
        # allowance = AllowanceModel.query.get(allow_id)
        allowance = (
            db.session.execute(db.select(AllowanceModel)
                               .filter_by(id=allow_id)).scalar_one()
        )
        try:
            if allowance:
                if "description" in allowancedata: 
                    allowance.description = allowancedata["description"]
                elif "amount" in allowancedata:
                    allowance.amount = allowancedata["amount"]
                elif "payperiod" in allowancedata:
                    allowance.payperiod = allowancedata["payperiod"]
                elif "taxable" in allowancedata:
                    allowance.taxable = allowancedata["taxable"]

                db.session.commit()
            else:
                allowance = AllowanceModel(**allowancedata)
                db.session.add(allowance)
                db.session.commit()
        except IntegrityError as e:
            db.session.rollback() 
            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )

            if constraint_name == "uq_allowance_perperiod":
                abort(409, message="The allowance already exists for the pay period.")

            abort(500, message="Unable to create allowance.")

        return allowance
    