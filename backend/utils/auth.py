from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

bcrypt = Bcrypt()
jwt = JWTManager()


def init_extensions(app):
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )
    bcrypt.init_app(app)
    jwt.init_app(app)
