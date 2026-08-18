from flask import Blueprint, render_template, request, redirect, flash
from models import Ingredient, Transaction, PurchaseRequest
from extension import db

store_bp = Blueprint("store", __name__)


# Store Dashboard
@store_bp.route("/store/dashboard")
def dashboard():
    return redirect("/store/receive")


# =========================
# Receive Stock
# =========================
@store_bp.route("/store/receive", methods=["GET", "POST"])
def receive_stock():
    ingredients = Ingredient.query.all()

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        received_quantity = float(request.form["received_quantity"])
        damaged_quantity = float(request.form["damaged_quantity"])
        unit = request.form["unit"]

        ingredient = Ingredient.query.get(ingredient_id)

        allowed_units = {
            "g": ["g", "kg"],
            "ml": ["ml", "litre"],
            "pieces": ["pieces"]
        }

        if unit not in allowed_units.get(ingredient.base_unit, []):
            flash(
                f"{ingredient.name} accepts only {allowed_units[ingredient.base_unit]}",
                "danger"
            )
            return redirect("/store/receive")

        # Unit conversion
        if unit == "kg":
            received_converted = received_quantity * 1000
            damaged_converted = damaged_quantity * 1000

        elif unit == "litre":
            received_converted = received_quantity * 1000
            damaged_converted = damaged_quantity * 1000

        else:
            received_converted = received_quantity
            damaged_converted = damaged_quantity

        # Validation
        if damaged_converted > received_converted:
            flash("Damaged quantity cannot exceed received quantity", "danger")
            return redirect("/store/receive")

        accepted_quantity = received_converted - damaged_converted

        # Save accepted stock
        receive_transaction = Transaction(
            ingredient_id=ingredient_id,
            property_id=1,
            transaction_type="RECEIVE",
            quantity=received_quantity - damaged_quantity,
            unit=unit,
            converted_quantity=accepted_quantity,
            created_by=1,
            notes="Stock received after damage deduction"
        )

        db.session.add(receive_transaction)

        # Save damaged stock separately
        if damaged_quantity > 0:
            damage_transaction = Transaction(
                ingredient_id=ingredient_id,
                property_id=1,
                transaction_type="RECEIVE_DAMAGE",
                quantity=damaged_quantity,
                unit=unit,
                converted_quantity=-damaged_converted,
                created_by=1,
                notes="Damaged during receiving"
            )

            db.session.add(damage_transaction)

        db.session.commit()

        flash("Stock received successfully!", "success")
        return redirect("/store/receive")

    return render_template(
        "store/receive.html",
        ingredients=ingredients
    )


# =========================
# View Current Store Stock
# =========================
@store_bp.route("/store/stock")
def stock_view():
    ingredients = Ingredient.query.all()
    stock_data = []

    for ingredient in ingredients:

        # Total received
        total_received = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "RECEIVE"
        ).scalar()

        total_received = total_received if total_received else 0

        # Total issued
        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0

        # Store wastage
        total_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "STORE_WASTAGE"
        ).scalar()

        total_wastage = abs(total_wastage) if total_wastage else 0

        # Final store stock
        total_stock = total_received - total_issued - total_wastage

        stock_data.append({
            "name": ingredient.name,
            "stock": total_stock if total_stock > 0 else 0,
            "unit": ingredient.base_unit
        })

    return render_template(
        "store/stock.html",
        stock_data=stock_data
    )


# =========================
# View Chef Requests
# =========================
@store_bp.route("/store/request")
def view_requests():
    requests = PurchaseRequest.query.filter_by(
        status="PENDING"
    ).all()

    return render_template(
        "store/request.html",
        requests=requests
    )


# =========================
# Issue Stock to Chef
# =========================
@store_bp.route("/store/issue-request/<int:request_id>")
def issue_request(request_id):
    stock_request = PurchaseRequest.query.get(request_id)

    if not stock_request:
        flash("Request not found", "danger")
        return redirect("/store/request")

    ingredient_id = stock_request.ingredient_id
    requested_qty = stock_request.requested_qty

    ingredient = Ingredient.query.get(ingredient_id)

    # Total received
    total_received = db.session.query(
        db.func.sum(Transaction.converted_quantity)
    ).filter(
        Transaction.ingredient_id == ingredient_id,
        Transaction.transaction_type == "RECEIVE"
    ).scalar()

    total_received = total_received if total_received else 0

    # Already issued
    total_issued = db.session.query(
        db.func.sum(Transaction.converted_quantity)
    ).filter(
        Transaction.ingredient_id == ingredient_id,
        Transaction.transaction_type == "ISSUE"
    ).scalar()

    total_issued = abs(total_issued) if total_issued else 0

    # Store wastage
    total_wastage = db.session.query(
        db.func.sum(Transaction.converted_quantity)
    ).filter(
        Transaction.ingredient_id == ingredient_id,
        Transaction.transaction_type == "STORE_WASTAGE"
    ).scalar()

    total_wastage = abs(total_wastage) if total_wastage else 0

    available_store_stock = (
        total_received - total_issued - total_wastage
    )

    if available_store_stock < requested_qty:
        flash("Not enough stock available to issue", "danger")
        return redirect("/store/request")

    transaction = Transaction(
        ingredient_id=ingredient_id,
        property_id=stock_request.property_id,
        transaction_type="ISSUE",
        quantity=requested_qty,
        unit=ingredient.base_unit,
        converted_quantity=-requested_qty,
        created_by=1,
        notes="Issued to Chef"
    )

    db.session.add(transaction)

    stock_request.status = "FULFILLED"

    db.session.commit()

    flash("Stock issued successfully!", "success")
    return redirect("/store/request")


# =========================
# Record Store Wastage
# =========================
@store_bp.route("/store/wastage", methods=["GET", "POST"])
def store_wastage():
    ingredients = Ingredient.query.all()
    stocked_ingredients = []

    for ingredient in ingredients:

        total_received = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "RECEIVE"
        ).scalar()

        total_received = total_received if total_received else 0

        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0

        total_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "STORE_WASTAGE"
        ).scalar()

        total_wastage = abs(total_wastage) if total_wastage else 0

        available_stock = total_received - total_issued - total_wastage

        if available_stock > 0:
            stocked_ingredients.append({
                "id": ingredient.id,
                "name": ingredient.name,
                "base_unit": ingredient.base_unit,
                "available_stock": available_stock
            })

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]

        if unit == "kg":
            converted_quantity = quantity * 1000
        elif unit == "litre":
            converted_quantity = quantity * 1000
        else:
            converted_quantity = quantity

        total_stock = next(
            (x["available_stock"] for x in stocked_ingredients
             if x["id"] == ingredient_id),
            0
        )

        if converted_quantity > total_stock:
            flash("Wastage quantity exceeds available stock", "danger")
            return redirect("/store/wastage")

        transaction = Transaction(
            ingredient_id=ingredient_id,
            property_id=1,
            transaction_type="STORE_WASTAGE",
            quantity=quantity,
            unit=unit,
            converted_quantity=-converted_quantity,
            created_by=1,
            notes="Stock wasted in store"
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Store wastage recorded successfully!", "success")
        return redirect("/store/wastage")

    return render_template(
        "store/wastage.html",
        ingredients=stocked_ingredients
    )