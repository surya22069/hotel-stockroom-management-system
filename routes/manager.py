from flask import Blueprint, render_template, redirect, flash
from models import PurchaseOrder, Ingredient, Transaction
from extension import db

manager_bp = Blueprint("manager", __name__)


# =========================
# Manager Dashboard
# =========================
@manager_bp.route("/manager/dashboard")
def dashboard():
    return render_template("manager/dashboard.html")


# =========================
# View Pending Purchase Orders
# =========================
@manager_bp.route("/manager/purchase-orders")
def view_purchase_orders():
    orders = PurchaseOrder.query.filter_by(
        status="PENDING_APPROVAL"
    ).all()

    return render_template(
        "manager/purchase_orders.html",
        orders=orders
    )


# =========================
# Approve Purchase Order
# =========================
@manager_bp.route("/manager/approve-po/<int:po_id>")
def approve_purchase_order(po_id):
    purchase_order = PurchaseOrder.query.get(po_id)

    if not purchase_order:
        flash("Purchase Order not found!", "danger")
        return redirect("/manager/purchase-orders")

    purchase_order.status = "APPROVED"
    db.session.commit()

    flash("Purchase Order approved successfully!", "success")
    return redirect("/manager/purchase-orders")


# =========================
# Reject Purchase Order
# =========================
@manager_bp.route("/manager/reject-po/<int:po_id>")
def reject_purchase_order(po_id):
    purchase_order = PurchaseOrder.query.get(po_id)

    if not purchase_order:
        flash("Purchase Order not found!", "danger")
        return redirect("/manager/purchase-orders")

    purchase_order.status = "REJECTED"
    db.session.commit()

    flash("Purchase Order rejected successfully!", "danger")
    return redirect("/manager/purchase-orders")


# =========================
# Variance Report
# =========================
@manager_bp.route("/manager/variance")
def variance_report():
    ingredients = Ingredient.query.all()
    report = []

    for ingredient in ingredients:
        received = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "RECEIVE"
        ).scalar() or 0

        store_wastage = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "STORE_WASTAGE"
            ).scalar() or 0
        )

        issued = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "ISSUE"
            ).scalar() or 0
        )

        consumed = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "CONSUME"
            ).scalar() or 0
        )

        kitchen_wastage = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "KITCHEN_WASTAGE"
            ).scalar() or 0
        )

        store_balance = received - issued - store_wastage
        kitchen_balance = issued - consumed - kitchen_wastage

        report.append({
            "name": ingredient.name,
            "received": received,
            "store_wastage": store_wastage,
            "issued": issued,
            "consumed": consumed,
            "kitchen_wastage": kitchen_wastage,
            "store_balance": store_balance,
            "kitchen_balance": kitchen_balance
        })

    return render_template(
        "manager/variance.html",
        report=report
    )


# =========================
# Wastage Report
# =========================
@manager_bp.route("/manager/wastage-report")
def wastage_report():
    ingredients = Ingredient.query.all()
    wastage = []

    for ingredient in ingredients:
        store = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "STORE_WASTAGE"
            ).scalar() or 0
        )

        kitchen = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "KITCHEN_WASTAGE"
            ).scalar() or 0
        )

        wastage.append({
            "name": ingredient.name,
            "store": store,
            "kitchen": kitchen,
            "total": store + kitchen
        })

    return render_template(
        "manager/wastage_report.html",
        wastage=wastage
    )


# =========================
# Consumption Report
# =========================
@manager_bp.route("/manager/consumption-report")
def consumption_report():
    ingredients = Ingredient.query.all()
    consumption = []

    for ingredient in ingredients:
        total = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "CONSUME"
            ).scalar() or 0
        )

        consumption.append({
            "name": ingredient.name,
            "total": total
        })

    return render_template(
        "manager/consumption_report.html",
        consumption=consumption
    )


# =========================
# Low Stock Alerts
# =========================
@manager_bp.route("/manager/low-stock")
def low_stock():
    ingredients = Ingredient.query.all()
    low_stock_data = []

    for ingredient in ingredients:
        received = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "RECEIVE"
        ).scalar() or 0

        issued = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "ISSUE"
            ).scalar() or 0
        )

        store_wastage = abs(
            db.session.query(
                db.func.sum(Transaction.converted_quantity)
            ).filter(
                Transaction.ingredient_id == ingredient.id,
                Transaction.transaction_type == "STORE_WASTAGE"
            ).scalar() or 0
        )

        current_stock = received - issued - store_wastage

        if current_stock < ingredient.par_level:
            low_stock_data.append({
                "name": ingredient.name,
                "stock": current_stock,
                "par_level": ingredient.par_level
            })

    return render_template(
        "manager/low_stock.html",
        low_stock=low_stock_data
    )


# =========================
# Purchase Order History
# =========================
@manager_bp.route("/manager/purchase-history")
def purchase_history():
    orders = PurchaseOrder.query.order_by(
        PurchaseOrder.created_at.desc()
    ).all()

    return render_template(
        "manager/purchase_history.html",
        orders=orders
    )