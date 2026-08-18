from flask import Blueprint, render_template, request, redirect, flash
from models import Ingredient, PurchaseOrder
from extension import db
from datetime import datetime

purchase_bp = Blueprint("purchase", __name__)


# =========================
# Purchase Dashboard
# =========================
@purchase_bp.route("/purchase/dashboard")
def dashboard():
    return render_template("purchase/dashboard.html")


# =========================
# Create Purchase Order
# =========================
@purchase_bp.route("/purchase/create", methods=["GET", "POST"])
def create_purchase_order():
    ingredients = Ingredient.query.all()

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        quantity = float(request.form["quantity"])
        vendor_name = request.form["vendor_name"]
        expected_date = datetime.strptime(
            request.form["expected_date"],
            "%Y-%m-%d"
        ).date()

        purchase_order = PurchaseOrder(
            ingredient_id=ingredient_id,
            vendor_name=vendor_name,
            ordered_qty=quantity,
            expected_date=expected_date,
            status="PENDING_APPROVAL",
            property_id=1,
            created_by=3
        )

        db.session.add(purchase_order)
        db.session.commit()

        flash("Purchase Order created successfully!", "success")
        return redirect("/purchase/create")

    return render_template(
        "purchase/create_po.html",
        ingredients=ingredients
    )


# =========================
# View Purchase Orders
# =========================
@purchase_bp.route("/purchase/orders")
def view_purchase_orders():
    orders = PurchaseOrder.query.order_by(
        PurchaseOrder.created_at.desc()
    ).all()

    return render_template(
        "purchase/orders.html",
        orders=orders
    )