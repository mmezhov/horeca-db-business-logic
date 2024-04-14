"""
Data Base Model

"""
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Criteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
