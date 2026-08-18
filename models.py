from extension import db
from datetime import datetime


# 1. Properties Table
class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Property {self.name}>"


# 2. Users Table
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)

    property = db.relationship("Property", backref="users")

    def __repr__(self):
        return f"<User {self.name} - {self.role}>"


# 3. Ingredients Table
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    base_unit = db.Column(db.String(20), nullable=False)
    par_level = db.Column(db.Float, nullable=False)
    vendor_name = db.Column(db.String(100))
    lead_time = db.Column(db.Integer)
    price_per_unit = db.Column(db.Float)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)

    property = db.relationship("Property", backref="ingredients")

    def __repr__(self):
        return f"<Ingredient {self.name}>"


# 4. Unit Conversion Table
class UnitConversion(db.Model):
    __tablename__ = "unit_conversions"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    purchase_unit = db.Column(db.String(20), nullable=False)
    base_unit = db.Column(db.String(20), nullable=False)
    conversion_factor = db.Column(db.Float, nullable=False)

    ingredient = db.relationship("Ingredient", backref="unit_conversions")

    def __repr__(self):
        return f"<UnitConversion {self.purchase_unit} -> {self.base_unit}>"


# 5. Transactions Table (CORE LEDGER)
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    converted_quantity = db.Column(db.Float, nullable=False)
    reference_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ingredient = db.relationship("Ingredient", backref="transactions")
    property = db.relationship("Property", backref="transactions")
    user = db.relationship("User", backref="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_type} - {self.quantity}>"


# 6. Recipes Table
class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(100), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)

    property = db.relationship("Property", backref="recipes")

    def __repr__(self):
        return f"<Recipe {self.dish_name}>"


# 7. Recipe Ingredients Table
class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    quantity_needed = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    recipe = db.relationship("Recipe", backref="recipe_items")
    ingredient = db.relationship("Ingredient", backref="recipe_usage")

    def __repr__(self):
        return f"<RecipeIngredient Recipe:{self.recipe_id} Ingredient:{self.ingredient_id}>"


# 8. Purchase Requests Table
class PurchaseRequest(db.Model):
    __tablename__ = "purchase_requests"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    requested_qty = db.Column(db.Float, nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(50), default="PENDING")
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ingredient = db.relationship("Ingredient", backref="purchase_requests")
    property = db.relationship("Property", backref="purchase_requests")

    def __repr__(self):
        return f"<PurchaseRequest {self.status}>"


# 9. Purchase Orders Table
class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id"),
        nullable=False
    )

    vendor_name = db.Column(
        db.String(100),
        nullable=False
    )

    ordered_qty = db.Column(
        db.Float,
        nullable=False
    )

    expected_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="PENDING_APPROVAL"
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    ingredient = db.relationship(
        "Ingredient",
        backref="purchase_orders"
    )

    property = db.relationship(
        "Property",
        backref="purchase_orders"
    )

    user = db.relationship(
        "User",
        backref="purchase_orders"
    )

    def __repr__(self):
        return f"<PurchaseOrder {self.id} - {self.status}>"