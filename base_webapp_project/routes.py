import functools
import os

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from forms import (
    ChangePasswordForm,
    DeleteAccountForm,
    GenericAppStartForm,
    GenericAppBackForm,
    LoginForm,
    RegisterForm,
    UserManagerForm,
    UserSettingsForm
)
from database import DatabaseTool, UserModel

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


def advanced_login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None or session.get("access_level") != "advanced":
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper

@pages.route("/")
def index():
    return render_template(
        "index.html",
        title="Red Book",
    )

@pages.route("/apps")
@login_required
def apps():
    return render_template(
        "apps.html",
        title="Applications",
        access_level=session["access_level"]
    )

@pages.route("/user-manager", methods=["POST", "GET"])
@advanced_login_required
def user_manager():
    form = UserManagerForm()
    users = list()
    
    with DatabaseTool() as db:
        if form.validate_on_submit():
            if form.update_submit.data:
                have_user: UserModel = db.get_user(form.user_email.data)
                if form.new_password.data and have_user != None:
                    new_password: str = pbkdf2_sha256.hash(form.new_password.data)
                    db.change_user_password(form.user_email.data, new_password)
                if form.new_access_level.data != "No Change" and have_user != None:
                    db.change_user_access_level(form.user_email.data, form.new_access_level.data)
            elif form.remove_submit.data:
                db.remove_user(form.user_email.data)
        
        users: list[UserModel] = db.get_all_users()

    if len(users) == 0:
        users = None

    return render_template(
        "user_manager.html",
        title="User Manager",
        users=users,
        form=form
    )

@pages.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if session.get("email") == None:
        return redirect(url_for(".login"))

    form = UserSettingsForm()

    with DatabaseTool() as db:
        user: UserModel = db.get_user(session.get("email"))

        if form.validate_on_submit():
            if not user:
                flash("You are not logged in.", category="danger")
                return redirect(url_for(".login"))

            if form.change_theme_submit.data:
                if user.theme == "Light":
                    db.change_user_theme(user.email, "Dark")
                    session["theme"] = "Dark"
                else:
                    db.change_user_theme(user.email, "Light")
                    session["theme"] = "Light"
                return redirect(url_for(".settings"))
            elif form.change_password_submit.data:
                return redirect(url_for(".change_password"))
            elif form.delete_account_submit.data:
                return redirect(url_for(".delete_account"))

            flash("Settings Updated")

    return render_template(
        "settings.html",
        title="Settings",
        user=user,
        form=form
    )


@pages.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        with DatabaseTool() as db:
            user: UserModel = db.get_user(session["email"])
            if user and pbkdf2_sha256.verify(form.old_password.data, user.password):
                new_password: str = pbkdf2_sha256.hash(form.new_password.data)
                db.change_user_password(session["email"], new_password)
                return redirect(url_for(".settings"))
            
            flash("Password did not change. Check to see if your old password is correct.", "danger")

    return render_template("change_password.html", title="Change Password", form=form)


@pages.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        with DatabaseTool() as db:
            user: UserModel = db.get_user(session["email"])
            if user and pbkdf2_sha256.verify(form.password.data, user.password):
                db.remove_user(session["email"])
                return redirect(url_for(".logout"))
            
            flash("Account was not deleted.", "danger")

    return render_template("delete_account.html", title="Delete Account", form=form)


@pages.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()
    if form.validate_on_submit():
        access_level = ""
        if form.registration_key.data == os.environ.get("BASIC_REGISTRATION_KEY"):
            email = form.email.data
            password = pbkdf2_sha256.hash(form.password.data)
            access_level = "basic"
        elif form.registration_key.data == os.environ.get("ADVANCED_REGISTRATION_KEY"):
            email = form.email.data
            password = pbkdf2_sha256.hash(form.password.data)
            access_level = "advanced"

        if access_level != "":
            with DatabaseTool() as db:
                try:
                    db.add_user(email, password, access_level)
                    flash("User registered successfully", "success")
                except SQLAlchemyError:
                    flash("User was not registered", "failure")

            return redirect(url_for(".login"))

    return render_template(
        "register.html", title="CSforAR Webtool - Register", form=form
    )


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".apps"))

    form = LoginForm()

    if form.validate_on_submit():
        with DatabaseTool() as db:
            user: UserModel = db.get_user(form.email.data)

        if not user:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["email"] = user.email
            session["access_level"] = user.access_level
            session["theme"] = user.theme

            return redirect(url_for(".apps"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="CSforAR Webtool - Login", form=form)


@pages.route("/logout")
def logout():
    session.clear()

    return redirect(url_for(".login"))