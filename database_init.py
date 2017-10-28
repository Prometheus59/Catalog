from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()

## Delete all previous entries
session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()

# Fake Users
User1 = User(id=1, name="Frank", email="frank@gmail.com",
             picture="http://www.pieglobal.com/wp-content/uploads/2015/10/placeholder-user.png")
session.add(User1)
session.commit()

User2 = User(id=2, name="James", email="james@gmail.com",
             picture="http://www.pieglobal.com/wp-content/uploads/2015/10/placeholder-user.png")
session.add(User2)
session.commit()

# Fake Categories

Category1 = Category(id=1, name="Tops")
session.add(Category1)
session.commit()

Category2 = Category(id=2, name="Bottoms")
session.add(Category2)
session.commit()

# Fake Items

Item1 = Item(id = 1, name="T-shirt", category_id = 1, user_id=1, description="Plain white T-shirt")
session.add(Item1)
session.commit()

Item2 = Item(id=2, name="Jeans", category_id=2, user_id=2, description="Long black Jeans")
session.add(Item2)
session.commit()

print "Database successfully populated"