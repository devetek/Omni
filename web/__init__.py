from config import Config
from flask import Flask, session
from flask_session import Session
from models import db, migrate
from models.user import User
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from .helpers.session_handler import validate_session, validate_session_header, unauthorized_session
from .helpers.jwt_handler import jwt_unauthorized_response, jwt_revoked_token_response, jwt_check_if_token_is_revoked


# ===== Modular Routes =====
from web.modules.account import bp as account_bp, routes
from web.modules.oauth import bp as oauth_bp, routes
from web.modules.payment import bp as payment_bp, routes
from web.modules.errors import bp as errors_bp, handlers


sess = Session()
login = LoginManager()


def bootstrap_web(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Plugin Initialization
    sess.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # JWT: Session Centralized
    jwt = JWTManager(app)
    jwt.expired_token_loader(jwt_unauthorized_response)
    jwt.unauthorized_loader(jwt_unauthorized_response)
    jwt.invalid_token_loader(jwt_unauthorized_response)
    jwt.revoked_token_loader(jwt_revoked_token_response)
    jwt.token_in_blacklist_loader(jwt_check_if_token_is_revoked)

    # Flask Session
    login.init_app(app)
    login.unauthorized_handler(unauthorized_session)
    login.user_loader(validate_session)
    login.request_loader(validate_session_header)

    """[routes handler for http, ws or polling]
    Descriptions: define your routes method, using Flask Blueprint or traditional routes
    Author: Prakasa <prakasa@devetek.com>
    """
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(errors_bp)

    return app
