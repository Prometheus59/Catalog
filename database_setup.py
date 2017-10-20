from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, LargeBinary, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base

class User(Base):
    __tablename__: "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=false)
    email = Column(String(50), nullable=false)
    picture = Column(String(50), nullable=false)
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
    }

class Category(Base):
    __tablename__: "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Item(Base):
    __tablename__: "items"
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey(categories.id), nullable=false)
    item_category = relationship("Category", back_populates="Item")
    user_id = Column(Integer, ForeignKey(user.id), nullable=false)
    item_creator = relationship("User", back_populates="Item")
    description = Column(String, nullable=true)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
            'category': self.item_category.name
        }

engine = create_engine('postgresql://item_catalog.db')
base.metadata.create_all(engine)
