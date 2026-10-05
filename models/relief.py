"""
relief database model
"""
from db import db

class ReliefModel(db.Model):
    """
    relief table definition
    """
    __tablename__ = "relief"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payperiod = db.Column(db.Integer, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey("user_detail.id"), nullable=False)
    __table_args__ = (
            db.UniqueConstraint(
                "description",
                "payperiod",
                "userid",
                name="uq_relief_perperiod"
            ),
        )
    user_detail = db.relationship("UserModel", back_populates="relief")
