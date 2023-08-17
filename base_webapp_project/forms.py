from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, SelectField
from wtforms.validators import Email, EqualTo, InputRequired, Length


class GenericAppStartForm(FlaskForm):
    submit = SubmitField("Start")


class GenericAppBackForm(FlaskForm):
    submit = SubmitField("Back")


class UserManagerForm(FlaskForm):
    user_email = StringField("User Email", validators=[InputRequired()])
    new_password = StringField("New Password")
    new_access_level = SelectField("Access Level", choices=["No Change", "advanced", "basic"])
    update_submit = SubmitField("Update")
    remove_submit = SubmitField("Remove")


class UserSettingsForm(FlaskForm):
    change_theme_submit = SubmitField("Toggle Theme")
    change_password_submit = SubmitField("Change Password")
    delete_account_submit = SubmitField("Delete Account")


class RegisterForm(FlaskForm):
    registration_key = StringField("Registration Key", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(
                min=8,
                message="Your password must be at least 8 characters long.",
            )
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password did not match the one in the password field.",
            )
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class DeleteAccountForm(FlaskForm):
    password = PasswordField("Enter Password", validators=[InputRequired()])
    submit = SubmitField("Delete")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old Password", validators=[InputRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            InputRequired(),
            Length(
                min=8,
                message="Your password must be at least 8 characters long.",
            )
        ]
    )
    submit = SubmitField("Change")
