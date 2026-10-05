"""
Tax module for calculating Nigeria tax  
"""
from decimal import Decimal

from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db import db
from models import AllowanceModel
from models import DeductionModel
from models import ReliefModel


blp = Blueprint("Tax", __name__, description="user tax")

class TaxableIncome(MethodView):
    """
    obtain taxable income
    """

    def relief_total (self,userid):
        """
        get total relief
        """
        relief = (
            db.session.execute(db.select(ReliefModel)
                               .filter_by(userid=userid)).scalars().all()
        )
        deduction = (
            db.session.execute(db.select(DeductionModel)
                               .filter_by(userid=userid)).scalars().all()
        )
        rentrelief = 0
        otherrelief = 0
        dedutionrelief = 0
        for item in relief:
            if item.description.lower() == "annual rent":
                rentrelief = min(Decimal(0.2) * item.amount, 500000) / 12
            else:
                otherrelief += item.amount
        for item in deduction:
                    if item.description.lower() == "nhf":
                        dedutionrelief = item.amount
        totalrelief = rentrelief + otherrelief + dedutionrelief
        return totalrelief

    def taxable_deduction (self,userid):
        """
        get total deduction
        """
        deduction = (
             db.session.execute(db.select(DeductionModel)
                                .filter_by(userid=userid)).scalars().all()
        )
        total_deduction_taxable = 0
        for item in deduction:
            if (item.description.lower()
                not in  ("loan", "pension","nhf", "nsitf")
                or item.taxable.upper() == 'Y'
            ):
                total_deduction_taxable += item.amount
        return total_deduction_taxable

    def taxable_allowance (self,userid):
        """
        get total allowance
        """
        allowance = (
             db.session.execute(db.select(AllowanceModel)
                                .filter_by(userid=userid)).scalars().all()
        )
        total_allowance_taxable = 0
        for item in allowance:
            if item.taxable.upper() == 'Y':
                total_allowance_taxable += item.amount
        return total_allowance_taxable

    def gross(self,userid):
        """
        get gross for a user
        """
        allowance = (
             db.session.execute(db.select(AllowanceModel)
                                .filter_by(userid=userid)).scalars().all()
        )
        total_gross = 0
        for item in allowance:
            total_gross += item.amount
        return total_gross

    def taxable_income (self, userid):
        """
        get net taxable
        """
        total_taxable = self.taxable_deduction(userid) + self.taxable_allowance(userid)
        net_taxable = total_taxable - self.relief_total(userid)
        return net_taxable


@blp.route("/tax/<int:userid>")
class Tax(MethodView):
    """
    Tax Calculator
    """

    def __init__(self):
        self.taxable = TaxableIncome()

    @jwt_required()
    def get(self, userid):
        """
        obtain the Nigeria tax using the new tax law.
        """
        relief = round(self.taxable.relief_total(userid), 2)
        deduction = round(self.taxable.taxable_deduction(userid),2)
        allowance = round(self.taxable.taxable_allowance(userid),2)
        gross = round(self.taxable.gross(userid),2)
        taxable_amount = float(round(self.taxable.taxable_income(userid),2))

        if taxable_amount <= 66666.67:
            tax_amount = 0
        elif taxable_amount <= 250000:
            amount = taxable_amount - 66666.67
            tax_amount = round((0.15 * amount), 2)
        elif taxable_amount <=  1000000:
            amount = taxable_amount - 66666.67 - 183333.33
            tax_amount = round((0.15 * 183333.33) + (0.18 * amount), 2)
        elif taxable_amount <=  2083333.33:
            amount = taxable_amount - 66666.67 - 183333.33 - 750000
            tax_amount = round((0.15 * 183333.33) + (0.18 * 750000) + (0.21 *  amount), 2)
        elif taxable_amount <=  4166666.67:
            amount = taxable_amount - 66666.67 - 183333.33 - 750000 - 1083333.33
            tax_amount = (
                round((0.15 * 183333.33) + (0.18 * 750000) +
                      (0.21 *  amount) + (0.23 * amount), 2)
            )
        else:
            amount = taxable_amount - 66666.67 - 183333.33 - 750000 - 1083333.33 -  2083333.33
            tax_amount = (
                round((0.15 * 183333.33) + (0.18 * 750000)
                      + (0.21 *  amount) + (0.23 * amount) + (0.24 * amount),2)
            )

        return (
            {
            "Gross amount":f"{gross}",
            "Taxable Allowance":f"{allowance}", 
            "Taxable Deduction":f"{deduction}",
            "Total Relief": f"{relief}",
            "Net Taxable": f"{taxable_amount}",
            "Tax":f"{tax_amount}"
                 }
        )
