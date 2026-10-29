from datetime import UTC, datetime

from flask_login import UserMixin

from . import db


def _now() -> datetime:
    return datetime.now(UTC)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    type = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=_now)
    donations = db.relationship("Donation")


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    description = db.Column(db.String)
    organisation = db.Column(db.String(250))
    date_donated = db.Column(db.Date)
    date_created = db.Column(db.DateTime(timezone=True), default=_now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
