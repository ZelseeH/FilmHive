from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import validates
from datetime import datetime


class Base(DeclarativeBase):
    pass