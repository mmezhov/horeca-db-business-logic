"""
Data Base Model

"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Criteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True))
    employee_id = db.Column(db.Integer, nullable=False)
    criteria_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)
