#!/usr/bin/python

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM

db = SQLAlchemy()

class Assets(db.Model):
    """The model for the assets database table.
    """

    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(ENUM("active", "pending", name="status_type"), nullable=False)