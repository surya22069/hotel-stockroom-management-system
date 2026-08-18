from flask import Blueprint, render_template, request, redirect, flash
from models import (
    Ingredient,
    Transaction,
    PurchaseRequest,
    UnitConversion,
    Recipe,
    RecipeIngredient
)
from extension import db

chef_bp = Blueprint("chef", __name__)


# =========================
# Chef Dashboard
# =========================
@chef_bp.route("/chef/dashboard")
def dashboard():
    return render_template("chef/dashboard.html")


# =========================
# View Available Store Stock
# =========================
@chef_bp.route("/chef/stock")
def chef_stock():
    ingredients = Ingredient.query.all()
    stock_data = []

    for ingredient in ingredients:

        # Total stock received in store
        total_received = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "RECEIVE"
        ).scalar()

        total_received = total_received if total_received else 0


        # Total stock issued from store to chef
        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0


        # Store wastage
        total_store_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "STORE_WASTAGE"
        ).scalar()

        total_store_wastage = (
            abs(total_store_wastage)
            if total_store_wastage else 0
        )


        # Remaining stock in store
        available_stock = (
            total_received
            - total_issued
            - total_store_wastage
        )

        stock_data.append({
            "name": ingredient.name,
            "stock": available_stock if available_stock > 0 else 0,
            "unit": ingredient.base_unit
        })

    return render_template(
        "chef/stock.html",
        stock_data=stock_data
    )


# =========================
# Request Stock
# =========================
@chef_bp.route("/chef/request", methods=["GET", "POST"])
def request_stock():
    ingredients = Ingredient.query.all()

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        quantity = float(request.form["quantity"])
        unit = request.form["unit"]

        conversion = UnitConversion.query.filter_by(
            ingredient_id=ingredient_id,
            purchase_unit=unit
        ).first()

        converted_quantity = (
            quantity * conversion.conversion_factor
            if conversion else quantity
        )

        stock_request = PurchaseRequest(
            ingredient_id=ingredient_id,
            requested_qty=converted_quantity,
            requested_by=2,
            property_id=1,
            status="PENDING"
        )

        db.session.add(stock_request)
        db.session.commit()

        flash("Stock request sent successfully!", "success")
        return redirect("/chef/request")

    return render_template(
        "chef/request.html",
        ingredients=ingredients
    )


# =========================
# Recipe Master
# =========================
@chef_bp.route("/chef/recipes", methods=["GET", "POST"])
def recipes():
    if request.method == "POST":
        recipe_name = request.form["recipe_name"]

        recipe = Recipe(
            dish_name=recipe_name,
            property_id=1
        )

        db.session.add(recipe)
        db.session.commit()

        flash("Recipe created successfully!", "success")
        return redirect(f"/chef/recipe/{recipe.id}")

    all_recipes = Recipe.query.all()

    return render_template(
        "chef/recipes.html",
        recipes=all_recipes
    )


# =========================
# Edit Recipe
# =========================
@chef_bp.route("/chef/recipe/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        flash("Recipe not found!", "danger")
        return redirect("/chef/recipes")

    if request.method == "POST":
        recipe.dish_name = request.form["recipe_name"]
        db.session.commit()

        flash("Recipe updated successfully!", "success")
        return redirect("/chef/recipes")

    return render_template(
        "chef/edit_recipe.html",
        recipe=recipe
    )


# =========================
# Delete Recipe
# =========================
@chef_bp.route("/chef/recipe/delete/<int:recipe_id>")
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        flash("Recipe not found!", "danger")
        return redirect("/chef/recipes")

    RecipeIngredient.query.filter_by(
        recipe_id=recipe.id
    ).delete()

    db.session.delete(recipe)
    db.session.commit()

    flash("Recipe deleted successfully!", "success")
    return redirect("/chef/recipes")


# =========================
# Recipe Details
# =========================
@chef_bp.route("/chef/recipe/<int:recipe_id>", methods=["GET", "POST"])
def recipe_detail(recipe_id):
    recipe = Recipe.query.get(recipe_id)

    if not recipe:
        flash("Recipe not found!", "danger")
        return redirect("/chef/recipes")

    ingredients = Ingredient.query.all()

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        quantity = float(request.form["quantity"])

        ingredient = Ingredient.query.get(ingredient_id)

        existing_item = RecipeIngredient.query.filter_by(
            recipe_id=recipe.id,
            ingredient_id=ingredient_id
        ).first()

        if existing_item:
            flash("Ingredient already added!", "danger")
            return redirect(f"/chef/recipe/{recipe.id}")

        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ingredient_id,
            quantity_needed=quantity,
            unit=ingredient.base_unit
        )

        db.session.add(recipe_ingredient)
        db.session.commit()

        flash("Ingredient added successfully!", "success")
        return redirect(f"/chef/recipe/{recipe.id}")

    mapped_ingredients = RecipeIngredient.query.filter_by(
        recipe_id=recipe.id
    ).all()

    return render_template(
        "chef/recipe_detail.html",
        recipe=recipe,
        ingredients=ingredients,
        mapped_ingredients=mapped_ingredients
    )


# =========================
# Edit Recipe Ingredient
# =========================
@chef_bp.route("/chef/recipe-item/edit/<int:item_id>", methods=["GET", "POST"])
def edit_recipe_item(item_id):
    recipe_item = RecipeIngredient.query.get(item_id)

    if not recipe_item:
        flash("Recipe ingredient not found!", "danger")
        return redirect("/chef/recipes")

    if request.method == "POST":
        quantity = float(request.form["quantity"])

        if quantity <= 0:
            flash("Quantity must be greater than zero!", "danger")
            return redirect(f"/chef/recipe-item/edit/{item_id}")

        recipe_item.quantity_needed = quantity
        db.session.commit()

        flash("Ingredient updated successfully!", "success")

        return redirect(
            f"/chef/recipe/{recipe_item.recipe_id}"
        )

    return render_template(
        "chef/edit_recipe_item.html",
        recipe_item=recipe_item
    )


# =========================
# Delete Recipe Ingredient
# =========================
@chef_bp.route("/chef/recipe-item/delete/<int:item_id>")
def delete_recipe_item(item_id):
    recipe_item = RecipeIngredient.query.get(item_id)

    if not recipe_item:
        flash("Recipe ingredient not found!", "danger")
        return redirect("/chef/recipes")

    recipe_id = recipe_item.recipe_id

    db.session.delete(recipe_item)
    db.session.commit()

    flash("Ingredient deleted successfully!", "success")
    return redirect(f"/chef/recipe/{recipe_id}")


# =========================
# Kitchen Production Page
# =========================
@chef_bp.route("/chef/production")
def production():
    recipes = Recipe.query.all()
    ingredients = Ingredient.query.all()

    kitchen_stock = []

    for ingredient in ingredients:

        # Total issued
        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0


        # Total consumed
        total_consumed = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "CONSUME"
        ).scalar()

        total_consumed = abs(total_consumed) if total_consumed else 0


        # Total kitchen wastage
        total_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "KITCHEN_WASTAGE"
        ).scalar()

        total_wastage = abs(total_wastage) if total_wastage else 0


        # Remaining stock in kitchen
        available = total_issued - total_consumed - total_wastage

        if available > 0:
            kitchen_stock.append({
                "name": ingredient.name,
                "stock": available,
                "unit": ingredient.base_unit
            })

    return render_template(
        "chef/production.html",
        recipes=recipes,
        kitchen_stock=kitchen_stock
    )


# =========================
# Start Production
# =========================
@chef_bp.route("/chef/start-production", methods=["POST"])
def start_production():
    recipe_id = int(request.form["recipe_id"])
    plates = int(request.form["plates"])

    recipe_items = RecipeIngredient.query.filter_by(
        recipe_id=recipe_id
    ).all()

    if not recipe_items:
        flash("No ingredients found for this recipe!", "danger")
        return redirect("/chef/production")

    # Validate stock before consuming
    for item in recipe_items:
        required_qty = item.quantity_needed * plates


        # Total issued
        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == item.ingredient_id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0


        # Total consumed
        total_consumed = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == item.ingredient_id,
            Transaction.transaction_type == "CONSUME"
        ).scalar()

        total_consumed = abs(total_consumed) if total_consumed else 0


        # Total kitchen wastage
        total_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == item.ingredient_id,
            Transaction.transaction_type == "KITCHEN_WASTAGE"
        ).scalar()

        total_wastage = abs(total_wastage) if total_wastage else 0


        # Available kitchen stock
        kitchen_available = (
            total_issued - total_consumed - total_wastage
        )

        if kitchen_available < required_qty:
            flash(
                f"Low stock! {item.ingredient.name} available: "
                f"{kitchen_available} {item.unit}, required: "
                f"{required_qty} {item.unit}",
                "danger"
            )
            return redirect("/chef/production")

    # Consume stock
    for item in recipe_items:
        required_qty = item.quantity_needed * plates

        transaction = Transaction(
            ingredient_id=item.ingredient_id,
            property_id=1,
            transaction_type="CONSUME",
            quantity=required_qty,
            unit=item.unit,
            converted_quantity=-required_qty,
            created_by=2,
            notes=f"Consumed for {plates} plate(s)"
        )

        db.session.add(transaction)

    db.session.commit()

    flash("Dishes are getting ready!", "success")
    return redirect("/chef/production")


# =========================
# Kitchen Wastage
# =========================
@chef_bp.route("/chef/wastage", methods=["GET", "POST"])
def kitchen_wastage():
    ingredients = Ingredient.query.all()
    kitchen_stock = []

    for ingredient in ingredients:

        total_issued = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "ISSUE"
        ).scalar()

        total_issued = abs(total_issued) if total_issued else 0

        total_consumed = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "CONSUME"
        ).scalar()

        total_consumed = abs(total_consumed) if total_consumed else 0

        total_wastage = db.session.query(
            db.func.sum(Transaction.converted_quantity)
        ).filter(
            Transaction.ingredient_id == ingredient.id,
            Transaction.transaction_type == "KITCHEN_WASTAGE"
        ).scalar()

        total_wastage = abs(total_wastage) if total_wastage else 0

        available_stock = (
            total_issued - total_consumed - total_wastage
        )

        if available_stock > 0:
            kitchen_stock.append({
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

        selected = next(
            (x for x in kitchen_stock if x["id"] == ingredient_id),
            None
        )

        if not selected:
            flash("Ingredient not found!", "danger")
            return redirect("/chef/wastage")

        if converted_quantity > selected["available_stock"]:
            flash("Wastage exceeds available kitchen stock!", "danger")
            return redirect("/chef/wastage")

        transaction = Transaction(
            ingredient_id=ingredient_id,
            property_id=1,
            transaction_type="KITCHEN_WASTAGE",
            quantity=quantity,
            unit=unit,
            converted_quantity=-converted_quantity,
            created_by=2,
            notes="Kitchen stock wastage"
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Kitchen wastage recorded!", "success")
        return redirect("/chef/wastage")

    return render_template(
        "chef/wastage.html",
        ingredients=kitchen_stock
    )