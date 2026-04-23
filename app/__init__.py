import os
import sqlite3
from flask import Flask
from .routes.book_route import books_bp

def init_db(app):
    db_path = os.path.join(app.instance_path, 'database.db')
    schema_path = os.path.join(app.root_path, '..', 'database', 'schema.sql')
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # If the database doesn't exist, create it and initialize the schema
    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        print("Database initialized successfully.")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize DB (creates file and schema if it doesn't exist)
    init_db(app)

    # Register blueprints
    app.register_blueprint(books_bp)
    
    return app
