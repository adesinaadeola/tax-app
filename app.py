"""
This is the flask app for the tax rest apis project.
"""
import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv


from db import db


from resources.user import blp as UserBlueprint
from resources.allowances import blp as AllowanceBlueprint
from resources.deductions import blp as DeductionBlueprint
from resources.reliefs import blp as ReliefBlueprint
from resources.tax import blp as TaxBlueprint

def create_app(db_url=None):
    """
    This function runs the flask app, incorporate jwt for security, and the db.
    For the database, it uses the db_url  or the database_url if provided, 
    and default to sqllite when both are missing
    """
    app = Flask(__name__)
    load_dotenv()



    with open(os.environ["DB_PASSWORD_FILE"], encoding="utf-8") as f:
        db_password = f.read().strip()

    db_user = os.environ["DB_USER"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]

    DATABASE_URL = (
        f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
    )

    with open("./secrets/jwt_secret.txt", "r", encoding="utf-8") as file:
        jwt_secret = file.read().strip()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Tax REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.0"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = jwt_secret

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )



    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(AllowanceBlueprint)
    api.register_blueprint(DeductionBlueprint)
    api.register_blueprint(ReliefBlueprint)
    api.register_blueprint(TaxBlueprint)

    return app
