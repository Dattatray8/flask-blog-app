from flask import Flask
from datetime import timedelta
from utils.auth import init_extensions
from routes.users import users_bp
from routes.blogs import blogs_bp
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_COOKIE_SECURE"] = False 
app.config["JWT_COOKIE_SAMESITE"] = "None"  
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

init_extensions(app)

app.register_blueprint(users_bp)
app.register_blueprint(blogs_bp)


@app.route("/")
def home():
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run(debug=True)
