from datetime import datetime
from app import db,User,Client,Distributeur,Transaction,Admin
from flask import session

db.create_all()
""" but= Distributeur("nom","prenom","akolatse1@gmail.com")
cl= Client("de","dfd","787df")

all=[but,cl]
db.session.add_all(all)
db.session.commit()

but1=Distributeur.query.get(1)
cl1=Client.query.get(2)
trans = Transaction(datetime.now(),but1,cl1)
db.session.add(trans)
db.session.commit() """
admin = Admin("one","two","admin","1234")
db.session.add(admin)
db.session.commit()

# one=Client("akol","two","773473107")
# two=Client("loka","three","773473108")
# users=[one,two]

# db.session.add_all(users)
# db.session.commit()

#obj=Client.query.get(1)
#cl=Client.query.filter_by(numero="202214040626").first()
#cl=session.query(Client).filter(Client.numero.like('202214040626'))
#print(cl.login)