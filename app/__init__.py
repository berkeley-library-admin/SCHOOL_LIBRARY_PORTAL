from flask import Flask
from app.routes import main_bp

def create_app():
    """Application factory engine responsible for initializing services, secret configurations, and routing maps."""
    app = Flask(__name__)
    
    # 🔒 STEP 2: SECURE APPLICATION SECRET KEY FOR COOKIE SIGNING
    # This prevents users from altering their session status manually.
    app.secret_key = 'super-secret-library-token-key-change-this-later'
    
    # Register your blueprints
    app.register_blueprint(main_bp)
    
    return app
