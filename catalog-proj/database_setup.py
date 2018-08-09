#!/usr/bin/env python2.7

import datetime

from sqlalchemy import (UniqueConstraint, Column, DateTime, ForeignKey,
                        Integer, String, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    items = relationship("Item", backref="category",
                         cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'Item': [i.serialize for i in self.items],
        }


class Item(Base):
    __tablename__ = 'item'

    cat_id = Column(Integer, ForeignKey('category.id'))
    description = Column(String(500))
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    UniqueConstraint('cat_id', 'title', name='unique_category_title')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'cat_id': self.cat_id,
            'description': self.description,
            'id': self.id,
            'title': self.title,
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
