from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, LargeBinary, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    picture = Column(String(50), nullable=False)
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
    }

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    item_category = relationship("Category", backref="items")
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    item_creator = relationship("User", backref="items")
    description = Column(String, nullable=True)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.item_category.name
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
