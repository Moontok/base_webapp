from sqlalchemy.orm import DeclarativeBase, relationship, backref
import sqlalchemy as db


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    """
    ORM-Model for users table and items.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=True, nullable=False)
    access_level = db.Column(db.String(40), nullable=False)
    theme = db.Column(db.String(40), nullable=False)
