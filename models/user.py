"""
user database model
"""
from db import db

class UserModel (db.Model):
    """
    user table definition
    """
    __tablename__ = "user_detail"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=False, nullable=False)

    allowance = (
        db.relationship("AllowanceModel", back_populates="user_detail",
                        lazy="dynamic", cascade="all, delete")
    )
    deduction = (
        db.relationship("DeductionModel", back_populates="user_detail",
                        lazy="dynamic", cascade="all, delete")
    )
    relief = (
        db.relationship("ReliefModel", back_populates="user_detail",
                        lazy="dynamic", cascade="all, delete")
    )
