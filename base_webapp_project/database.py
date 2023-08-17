import os

from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
from dotenv import load_dotenv
from typing import Optional

from db_models import (
    UserModel,
    Base
)

class DatabaseTool:
    """
    Class for interacting with the database. Does not require
    a flask app to be executed.
    """

    def __init__(self):
        self.engine = db.create_engine("sqlite:///instance/data.db")

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()

    # Managing Users Section
    def add_user(self, email: str, password: str, access_level: str) -> None:
        """Add current email (user) and password to database."""

        user = UserModel()
        user.email = email
        user.password = password
        user.access_level = access_level
        user.theme = "Light"
        
        self.session.add(user)
        self.session.commit()
    
    def get_user(self, email: str) -> Optional[UserModel]:
        return self.session.scalars(db.select(UserModel).where(UserModel.email==email)).first()

    def get_all_users(self) -> Optional[list[UserModel]]:
        return self.session.scalars(db.select(UserModel)).all()

    def change_user_password(self, email: str, password: str) -> None:
        user: UserModel = self.get_user(email)

        user.password = password

        self.session.add(user)
        self.session.commit()

    def change_user_access_level(self, email: str, access_level: str) -> None:
        user: UserModel = self.get_user(email)

        user.access_level = access_level

        self.session.add(user)
        self.session.commit()

    def change_user_theme(self, email: str, theme: str) -> None:
        user: UserModel = self.get_user(email)

        user.theme = theme

        self.session.add(user)
        self.session.commit()

    def remove_user(self, email: str) -> None:
        user_to_remove: UserModel = self.get_user(email)

        self.session.delete(user_to_remove)
        self.session.commit()

    # Context Manager Section
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()
        
        if exc_type != None or exc_value != None or exc_traceback != None:
            raise exc_type


if __name__ == "__main__":
    print("Nothing happens...")