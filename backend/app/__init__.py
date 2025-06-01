from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure CORS to allow all origins during development
    CORS(app)
    
    # Register blueprints
    from app.routes import auth, questionnaires, responses, analytics
    app.register_blueprint(auth.bp)
    app.register_blueprint(questionnaires.bp)
    app.register_blueprint(responses.bp)
    app.register_blueprint(analytics.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
