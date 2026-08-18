from app import app
from extension import db
from models import (
    Property,
    User,
    Ingredient,
    UnitConversion
)
from werkzeug.security import generate_password_hash


with app.app_context():

    # Properties
    p1 = Property(name="Hotel A", location="nellore")
    p2 = Property(name="Hotel B", location="Chennai")

    db.session.add_all([p1, p2])
    db.session.commit()

    # Users
    users = [
        User(
            name="Kavitha",
            email="store@hotel.com",
            password=generate_password_hash("1234"),
            role="STORE_KEEPER",
            property_id=1
        ),
        User(
            name="Ramesh",
            email="chef@hotel.com",
            password=generate_password_hash("1234"),
            role="CHEF",
            property_id=1
        ),
        User(
            name="Arjun",
            email="manager@hotel.com",
            password=generate_password_hash("1234"),
            role="FB_MANAGER",
            property_id=1
        ),
        User(
            name="Meena",
            email="purchase@hotel.com",
            password=generate_password_hash("1234"),
            role="PURCHASE_MANAGER",
            property_id=1
        )
    ]

    db.session.add_all(users)
    db.session.commit()

    ingredients = [
    Ingredient(
        name="Chicken",
        category="Meat",
        base_unit="g",
        par_level=5000,
        vendor_name="Fresh Farms",
        lead_time=2,
        price_per_unit=0.25,
        property_id=1
    ),

    Ingredient(
        name="Rice",
        category="Grains",
        base_unit="g",
        par_level=10000,
        vendor_name="Rice Traders",
        lead_time=3,
        price_per_unit=0.05,
        property_id=1
    ),

    Ingredient(
        name="Butter",
        category="Dairy",
        base_unit="g",
        par_level=2000,
        vendor_name="Dairy Fresh",
        lead_time=1,
        price_per_unit=0.15,
        property_id=1
    ),

    Ingredient(
        name="Oil",
        category="Liquid",
        base_unit="ml",
        par_level=5000,
        vendor_name="Oil Traders",
        lead_time=2,
        price_per_unit=0.12,
        property_id=1
    ),

    Ingredient(
        name="Egg",
        category="Poultry",
        base_unit="pieces",
        par_level=50,
        vendor_name="Egg Farm",
        lead_time=1,
        price_per_unit=5,
        property_id=1
    ),

    Ingredient(
        name="Tomatoes",
        category="Vegetable",
        base_unit="g",
        par_level=3000,
        vendor_name="Veg Suppliers",
        lead_time=1,
        price_per_unit=0.08,
        property_id=1
    ),

    Ingredient(
        name="Onions",
        category="Vegetable",
        base_unit="g",
        par_level=4000,
        vendor_name="Veg Suppliers",
        lead_time=1,
        price_per_unit=0.06,
        property_id=1
    ),

    Ingredient(
        name="Milk",
        category="Dairy",
        base_unit="ml",
        par_level=5000,
        vendor_name="Dairy Fresh",
        lead_time=1,
        price_per_unit=0.09,
        property_id=1
    )
]

    db.session.add_all(ingredients)
    db.session.commit()

    conversions = [
    UnitConversion(ingredient_id=1, purchase_unit="kg", base_unit="g", conversion_factor=1000),
    UnitConversion(ingredient_id=2, purchase_unit="kg", base_unit="g", conversion_factor=1000),
    UnitConversion(ingredient_id=3, purchase_unit="kg", base_unit="g", conversion_factor=1000),
    UnitConversion(ingredient_id=4, purchase_unit="L", base_unit="ml", conversion_factor=1000),
    UnitConversion(ingredient_id=5, purchase_unit="pieces", base_unit="pieces", conversion_factor=1),
    UnitConversion(ingredient_id=6, purchase_unit="kg", base_unit="g", conversion_factor=1000),
    UnitConversion(ingredient_id=7, purchase_unit="kg", base_unit="g", conversion_factor=1000),
    UnitConversion(ingredient_id=8, purchase_unit="L", base_unit="ml", conversion_factor=1000)
]

    db.session.add_all(conversions)
    db.session.commit()

    print("Seed data inserted successfully.")