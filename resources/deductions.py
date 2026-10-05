"""
Deduction module contains apis for creating, updating, deleting, 
and retrieving the deduction for a user
"""
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

from db import db
from models import DeductionModel

from schemas import DefaultAllowDeductSchema, AllowDeductCreationSchema, UpdateAllowDeductSchema



blp = Blueprint("deductions", __name__, description="Operations on deductions")

@blp.route("/getdeduction")
class GetAllDeduction(MethodView):
    """
    get all deductions
    """
    @blp.response(200, DefaultAllowDeductSchema(many=True))
    def get(self):
        return DeductionModel.query.all()

@blp.route("/deduction/<int:userid>")
class Deduction(MethodView):
    """
    get specified deduction
    """
    @jwt_required()
    @blp.response(200, DefaultAllowDeductSchema(many=True))
    def get(self,userid):
        try:
            deduction = (
                db.session.execute(db.select(DeductionModel)
                                   .filter_by(userid=userid)).scalars().all()
            )
            if not deduction:
                abort (404, message= "No deduction for the user")
        except SQLAlchemyError as error:
            abort(500, message=str(error))
        return deduction

@blp.route("/deduction/<int:deduct_id>")
class DeleteDeduction(MethodView):
    """
    delete specified deduction
    """
    @jwt_required()
    def delete(self,deduct_id):
        try:
            deduction = (
                db.session.execute(db.select(DeductionModel)
                                   .filter_by(id=deduct_id)).scalar_one()
            )
            db.session.delete(deduction)
            db.session.commit()
        except NoResultFound:
            abort(404, message="The deduction does not exist")
        return {"message": "The deduction has been deleted"}, 200

   
@blp.route("/creatededuction")
class CreateDeduction(MethodView):
    """
    create deduction
    """
    @jwt_required()
    @blp.arguments(AllowDeductCreationSchema)
    def post(self,deductiondata):
        deductions = DeductionModel(**deductiondata)
        try:
            db.session.add(deductions)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )

            if constraint_name == "uq_deduction_perperiod":
                abort(409, message="The deduction already exists for the pay period.")

            abort(500, message="Unable to create deduction.")
        except SQLAlchemyError as e:
            abort(500, message=f"{e}")

        return {"message":"deduction created successfully"}

    # add an update endpoint using put
@blp.route("/deduction/<int:deduct_id>")
class UpdateDeduction(MethodView):
    """
    update specified deduction
    """
    @jwt_required()
    @blp.arguments(UpdateAllowDeductSchema)
    @blp.response(200, UpdateAllowDeductSchema)
    def put(self,deductiondata,deduct_id):
        #deduction = DeductionModel.query.get(deduct_id)
        deduction = (
            db.session.execute(db.select(DeductionModel)
                               .filter_by(id=deduct_id)).scalar_one()
        )
        try:
            if deduction:
                if "description" in deductiondata:
                    deduction.description = deductiondata["description"]
                elif "amount" in deductiondata:
                    deduction.amount = deductiondata["amount"]
                elif "payperiod" in deductiondata:
                    deduction.payperiod = deductiondata["payperiod"]
                elif "taxable" in deductiondata:
                    deduction.taxable = deductiondata["taxable"]
                    
                db.session.commit()
            else:
                deduction = DeductionModel(**deductiondata)
                db.session.add(deduction)
                db.session.commit()
        except IntegrityError as e:
            db.session.rollback()

            constraint_name = getattr(
                getattr(e.orig, "diag", None),
                "constraint_name",
                None
            )

            if constraint_name == "uq_deduction_perperiod":
                abort(409, message="The deduction already exists for the pay period.")

            abort(500, message="Unable to create deduction.")

        return deduction
    