from flask import Flask
from flask_cors import CORS
from app.routes.itinerary_routes import itinerary_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for Angular frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(itinerary_bp, url_prefix='/api')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
