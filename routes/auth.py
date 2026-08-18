from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from models import User

auth_bp = Blueprint("auth", __name__)


# Login Page
@auth_bp.route("/login")
def login():
    return render_template("login.html")


# Handle Login
@auth_bp.route("/login", methods=["POST"])
def handle_login():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["role"] = user.role
        session["property_id"] = user.property_id

        if user.role == "STORE_KEEPER":
            return redirect("/store/dashboard")

        elif user.role == "CHEF":
            return redirect("/chef/dashboard")

        elif user.role == "FB_MANAGER":
            return redirect("/manager/dashboard")

        elif user.role == "PURCHASE_MANAGER":
            return redirect("/purchase/dashboard")

    return "Invalid credentials"


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")