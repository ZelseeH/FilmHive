from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from sqlalchemy.ext.declarative import declarative_base

# Create SQLAlchemy instance
db = SQLAlchemy()

# Create declarative base model using the db instance
Base = db.Model

# Initialize other extensions
migrate = Migrate()
jwt = JWTManager()
