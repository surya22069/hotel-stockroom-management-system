from flask import Flask, render_template
from config import Config
from extension import db
from flask_migrate import Migrate   # add this


def create_app():
    app = Flask(__name__)
    app.secret_key = "stockroom_secret"
    app.config.from_object(Config)

    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    import models

    from routes.auth import auth_bp
    from routes.store import store_bp
    from routes.chef import chef_bp
    from routes.manager import manager_bp
    from routes.purchase import purchase_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(chef_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(purchase_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)