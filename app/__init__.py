from flask_cors import CORS
from flask import Flask
# from flask_session import Session
from .routes import blueprint
def create_app():
    app = Flask(__name__)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SECURE'] = True  # Use True if running over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SECRET_KEY'] = 'pclinfo'
    app.config['SESSION_FILE_DIR']=r'flask_session'

    # Session(app)

    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["https://ecom-admin-liard.vercel.app", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
            "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
            "methods": ["OPTIONS", "GET", "POST", "PUT", "DELETE"]
        }
    })
    with app.app_context():
        app.register_blueprint(blueprint)

    return app


