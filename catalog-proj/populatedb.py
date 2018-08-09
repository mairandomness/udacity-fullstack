#!/usr/bin/env python2.7

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Soccer category
category1 = Category(name="Soccer")
Item1 = Item(title="Soccer Cleats",
             description="Shoes for playing field soccer.")
category1.items.append(Item1)
Item2 = Item(title="Jersey", description="A shirt with shiny numbers on it.")
category1.items.append(Item2)
session.add(category1)
session.add(Item1)
session.add(Item2)
session.commit()

category2 = Category(name="Basketball")
session.add(category2)
session.commit()

category3 = Category(name="Baseball")
Item1 = Item(title="Baseball Cleats",
             description="Shoes for playing baseball.")
category3.items.append(Item1)
Item2 = Item(title="Bat",
             description=("A bat for playing baseball, can also be used for "
                          "self defense, apparently."))
category3.items.append(Item2)
session.add(category3)
session.add(Item1)
session.add(Item2)
session.commit()

category4 = Category(name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(name="Snowboarding")
Item1 = Item(title="Snowboard",
             description=("You know, the board that you use for snowboarding. "
                          "Shoes not included."))
category5.items.append(Item1)
Item2 = Item(title="Snow Goggles",
             description=("For you to be able to keep your eyes open and maybe"
                          " warm. Mirror finish."))
category5.items.append(Item2)
Item3 = Item(title="Snow Gloves",
             description="It's cold!! You could lose a finger out there.")
category5.items.append(Item3)
session.add(category3)
session.add(Item1)
session.add(Item2)
session.add(Item3)
session.commit()

print "added catalog items!"
