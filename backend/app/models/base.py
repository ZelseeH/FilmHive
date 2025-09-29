from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Float,
    Boolean,
    Enum,
    Text,
)
from sqlalchemy.orm import validates
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app.services.database import db

from app.extensions import Base


class CustomBase(Base):
    __abstract__ = True
