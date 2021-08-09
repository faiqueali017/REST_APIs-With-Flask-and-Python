from flask import request, url_for
from requests import Response

from db import db
from libs.mailgun import Mailgun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    # To Tell SQLAlchemy tablename and col_name
    __tablename__ = "users"

    # nullable=False ;will check whether req or not when loading data into ma
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # lazy="dynamic" ;when new usermodel created, the ConfirmationModel not retrieved from the db when access confir. property then it access
    # cascade="all, delete-orphan" ;when we delete a user, it going to confirmation and delete all his belongings
    # overlaps="user" ;to hide warning in debug
    confirmation = db.relationship(
        "ConfirmationModel",
        lazy="dynamic",
        cascade="all, delete-orphan",
        overlaps="user",
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(
            db.desc(ConfirmationModel.expire_at)
        ).first()  # expire_at(col) in desc order, then its desc_first() => newest

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self) -> Response:
        subject = "Registration confirmation"

        # http://127.0.0.1:5000/ ;excluding last '/' + /confirmation/confirmation_id
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        text = f"Please click the link to confirm your registeration: {link}"
        html = f'<html>Please click the link to confirm your registeration: <a href="{link}">{link}</a></html>'

        return Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()