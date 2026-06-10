from flask import Flask

def create_app():
    # Initialize the core Flask framework application object
    app = Flask(__name__)
    
    # Secret key for security sessions
    app.config['SECRET_KEY'] = 'dev-school-library-key-12345'

    # Register our website routing files (where URLs are defined)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app