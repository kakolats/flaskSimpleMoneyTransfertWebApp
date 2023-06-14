
from datetime import datetime
from inspect import classify_class_attrs
from lib2to3.pytree import Base
import os
from re import match
from socket import if_nameindex
from weakref import ref
from flask import Flask, redirect, url_for, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config["SECRET_KEY"] = "zawarudo"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Migrate(app, db)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(50), nullable = False)
    prenom = db.Column(db.String(100), nullable = False)
    login = db.Column(db.String(50), nullable=True)
    password = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

    def __init__(self,nom,prenom,login,password):
        self.nom = nom
        self.prenom = prenom
        self.login = login
        self.password = password


class Client(User):
    __tablename__ = "client"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    telephone = db.Column(db.String(50),nullable = False)
    numero = db.Column(db.String(50),nullable = False)
    code = db.Column(db.String(50),nullable = False)
    solde = db.Column(db.Integer,nullable = False)
    etat = db.Column(db.Boolean, nullable=False)
    createur_id = db.Column(db.Integer,nullable = False)
    transactions = db.relationship('Recharge',backref='client',lazy=True)
    codes = db.relationship('Code',backref='client',lazy=True)
    envois = db.relationship('Envoi',backref='envoyeur',lazy=True)  
    receptions = db.relationship('Reception',backref='receveur',lazy=True)  
    __mapper_args__ = {
        'polymorphic_identity':'client',
    }

    def __init__(self, nom, prenom, telephone,createur_id):
        super().__init__(nom, prenom, telephone, "PASSER")
        self.telephone = telephone
        self.numero = generateNumero()
        self.code = "PASSER"
        self.solde = 0
        self.etat = True
        self.createur_id = createur_id

class Distributeur(User):
    __tablename__ = "distributeur"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String(50),nullable = False)
    transactions = db.relationship('Recharge',backref='distributeur',lazy=True)
    etat = db.Column(db.Boolean, nullable=False)
    createur_id = db.Column(db.Integer,nullable = False)
    codes = db.relationship('Code',backref='distributeur',lazy=True)
    __mapper_args__ = {
        'polymorphic_identity':'distributeur',
    }
    def __init__(self,nom,prenom,email,createur_id):
        super().__init__(nom, prenom, email,"DISTRIBUTEUR")
        self.createur_id= createur_id
        self.etat = True
        self.nom = nom
        self.prenom = prenom
        self.email = email

class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime,nullable = False)
    montant = db.Column(db.Integer,nullable = False)
    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity':'transaction',
        'polymorphic_on':type
    }
    def __init__(self,montant):
        self.montant=montant
        self.date=datetime.now()


class Recharge(Transaction):
    __tablename__ = "recharge"
    id = db.Column(db.Integer, db.ForeignKey('transaction.id'), primary_key=True)
    from_id = db.Column(db.Integer,db.ForeignKey('distributeur.id'),nullable = False)
    to_id = db.Column(db.Integer,db.ForeignKey('client.id'),nullable = False)
    __mapper_args__ = {
        'polymorphic_identity':'recharge'
    }
    def __init__(self, montant,distributeur,client):
        super().__init__(montant)
        self.distributeur = distributeur
        self.client = client

class Envoi(Transaction):
    __tablename__ = "envoi"
    id = db.Column(db.Integer, db.ForeignKey('transaction.id'), primary_key=True)
    from_id = db.Column(db.Integer,db.ForeignKey('client.id'),nullable = False)
    to_id = db.Column(db.Integer,nullable = False)
    __mapper_args__ = {
        'polymorphic_identity':'envoi'
    }
    def __init__(self, montant,envoyeur,to_id):
        super().__init__(montant)
        self.envoyeur = envoyeur
        self.to_id = to_id

class Reception(Transaction):
    __tablename__ = "reception"
    id = db.Column(db.Integer, db.ForeignKey('transaction.id'), primary_key=True)
    from_id = db.Column(db.Integer,nullable = False)
    to_id = db.Column(db.Integer,db.ForeignKey('client.id'),nullable = False)
    __mapper_args__ = {
        'polymorphic_identity':'reception'
    }
    def __init__(self, montant,receveur,from_id):
        super().__init__(montant)
        self.receveur = receveur
        self.from_id = from_id

class Admin(User):
    __tablename__ = "admin"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'admin',
    }

    def __init__(self, nom, prenom, login, password):
        super().__init__(nom, prenom, login, password)

class Code(db.Model):
    __tablename__ = "code"
    id = db.Column(db.Integer, primary_key = True)
    valeur = db.Column(db.String(50),nullable = False)
    montant = db.Column(db.Integer,nullable = False)
    from_id = db.Column(db.Integer,db.ForeignKey('distributeur.id'),nullable = False)
    to_id = db.Column(db.Integer,db.ForeignKey('client.id'),nullable = False)
    def __init__(self,montant,a,b):
        self.valeur=generateCode()
        self.montant=montant
        self.distributeur=a
        self.client=b

def generateNumero():
    now=datetime.now()
    return now.strftime("%Y")+now.strftime("%d")+now.strftime("%m")+now.strftime("%H")+now.strftime("%M")

def generateCode():
    now=datetime.now()
    return now.strftime("%M")+now.strftime("%H")+now.strftime("%m")+now.strftime("%d")+now.strftime("%Y")



#####################ROUTES#########################################
@app.route("/")
def index():
    return render_template("base.html")

@app.route("/test")
def test():
    return render_template("base.client.html")

from forms import LoginForm,SearchAccountForm,AddClientForm,AddAdminForm,ChangePasswordForm,TransfertForm,RechargeForm,AddDistributeurForm,AlimentationForm

            ################ CONNEXION DES UTILISATEURS ######################
@app.route("/connexion/client" , methods = ["GET","POST"],defaults={"route": None})
def connexionClient(route):
    form=LoginForm()
    if form.validate_on_submit():
        telephone=form.login.data
        password=form.password.data
        cl=Client.query.filter_by(telephone=telephone,password=password).first()
        if cl==None:
            flash("Login ou mot de passe incorrect")
        else:
            if not cl.etat:
                flash('votre compte est bloqué')
            else:
                session['id']=cl.id
                session['nom']=cl.nom
                session['prenom']=cl.prenom
                session['numero']=cl.numero
                session['code']=cl.code,
                session['telephone']=cl.telephone
                session['solde']=cl.solde
                session['createur']=Admin.query.get(cl.createur_id).nom+" "+Admin.query.get(cl.createur_id).prenom
                if(route=="admin"):
                    return redirect(url_for('addAdmin'))
                elif(route=="client"):
                    return redirect(url_for('addClient'))
                else:
                    return redirect(url_for('clientProfil',id=cl.id))
            
    return render_template("connexionClient.html",form=form)

@app.route("/connexion/admin",methods = ["GET","POST"])
def connexionAdmin():
    form=LoginForm()
    if form.validate_on_submit():
        login=form.login.data
        password=form.password.data
        admin=Admin.query.filter_by(login=login,password=password).first()
        if admin!=None: 
            session['utilisateur']={'id':admin.id,'nom':admin.nom,'prenom':admin.prenom,'login':admin.login,'password':admin.password}
            return redirect(url_for('gestionComptes'))
        else:
            flash("Login ou mot de passe incorrect")
    return render_template("connexionAdmin.html",form=form)
                ############ FIN CONNEXION DES UTILISATEURS #############

@app.route('/connexion/distributeur',methods = ["GET","POST"])
def connexionDistributeur():
    form = LoginForm()
    if form.validate_on_submit():
        login=form.login.data
        password=form.password.data
        dis=Distributeur.query.filter_by(email=login,password=password).first()
        if dis!=None:
            if not dis.etat:
                flash('Votre compte est bloqué')
            else:
                session["id"]=dis.id
                session["nom"]=dis.nom
                session["prenom"]=dis.prenom
                session["email"]=dis.email
                session["password"]=dis.password
                session['createur']=Admin.query.get(dis.createur_id).nom+" "+Admin.query.get(dis.createur_id).prenom
                return redirect(url_for('distributeurProfil',id=dis.id))
        else:
            flash('email ou mot de passe incorrect')
    return render_template("connexionDistributeur.html",form=form)



        ####### GESTION DES COMPTES CLIENTS ET DISTRIBUTEUR ###########
    # LIEN VERS LA PAGE DE GESTION DES COMPTES ET GESTION DE LA RECHERCHE PAR NUMERO DE COMPTE

@app.route('/admin/gestion/compte',methods = ["GET","POST"])
def gestionComptes():
    listUsers= Client.query.all()
    form = SearchAccountForm()
    if form.validate_on_submit():
        num=form.numero.data
        cl=Client.query.filter_by(numero=num).first()
        if cl!=None:
            listUsers=[cl]
        else:
            listUsers=[]
    return render_template("admin.gestion.client.html",form=form,users=listUsers)

@app.route('/admin/gestion/distributeurs')
def gestionDistributeurs():
    users= Distributeur.query.all()
    return render_template("admin.gestion.distributeur.html",users=users)

            ############# CREATION DES UTILISATEURS ##############
    # AJOUT D'UN CLIENT
@app.route('/admin/create/client',methods = ["GET","POST"])
def addClient():
    form=AddClientForm()
    if form.validate_on_submit():
        nom=form.nom.data
        prenom=form.prenom.data
        telephone=form.telephone.data
        us=Client.query.filter_by(telephone=telephone).first()
        if(us!=None):
            flash('Ce numero de telephone est deja utilisé')
        else:
            user = Client(nom,prenom,telephone,session.get('utilisateur')["id"])
            db.session.add(user)
            db.session.commit()
            flash('Utilisateur ajouté avec succès')
            return redirect(url_for('gestionComptes'))

    return render_template("admin.add.client.html",form=form)

    # AJOUT D'UN ADMIN
@app.route('/admin/create/admin',methods = ["GET","POST"])
def addAdmin():
    form=AddAdminForm()
    if form.validate_on_submit():
        nom=form.nom.data
        prenom=form.prenom.data
        login=form.login.data
        password=form.password.data
        passwordConf=form.passwordConfirm.data
        if password !=passwordConf:
            flash('veuillez confirmer correctement le mot de passe')
        else:
            us=Admin.query.filter_by(login=login).first()
            if(us!=None):
                flash('Ce login est deja utilisé')
            else:
                user = Admin(nom,prenom,login,password)
                db.session.add(user)
                db.session.commit()
                flash('Admin ajouté avec succès')
                return redirect(url_for('gestionComptes'))
    return render_template("admin.add.admin.html",form=form)
            ######## FIN ##################

    # AJOUT D'UN DISTRIBUTEUR
@app.route('/admin/create/distributeur',methods = ["GET","POST"])
def addDistributeur():
    form = AddDistributeurForm()
    if form.validate_on_submit():
        nom = form.nom.data
        prenom = form.prenom.data
        email = form.email.data
        dis = Distributeur.query.filter_by(email=email).first()
        if(dis!=None):
            flash('ce email est deja utilise')
        else:
            dist = Distributeur(nom,prenom,email,session.get('utilisateur')["id"])
            db.session.add(dist)
            db.session.commit()
            flash('Compte cree avec succes')
            return redirect(url_for('gestionDistributeurs'))
    return render_template('admin.add.distributeur.html',form=form)

    ######## BLOQUAGE ET DEBLOQUAGE D'UN COMPTE ##########        
@app.route('/change/state/<int:id>')
def changeAccountState(id):
    client=Client.query.get(id)
    client.etat= not client.etat
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('gestionComptes'))

@app.route('/change/distributeur/<int:id>')
def changeDistributeurState(id):
    dis=Distributeur.query.get(id)
    dis.etat = not dis.etat
    db.session.add(dis)
    db.session.commit()
    return redirect(url_for('gestionDistributeurs'))

        ############# FONCTIONNALITES DU CLIENT ###############

    #VOIR SON PROFIL ET MODIFIER SON MOT DE PASSE
@app.route('/client/profil/<int:id>',methods = ["GET","POST"])
def clientProfil(id):
    form = ChangePasswordForm()
    if form.validate_on_submit:
        oldPass=form.oldPassword.data
        newPass=form.newPassword.data
        confPass=form.confirmNewPassword.data
        if(oldPass!=Client.query.get(id).code):
            flash('mot de passe incorrect')
        else:
            if(newPass!=confPass):
                flash('veuillez confirmer correctement le mot de passe')
            else:
                cl=Client.query.get(id)
                cl.code=cl.password=newPass
                session["code"]=newPass
                db.session.add(cl)
                db.session.commit()
    return render_template("client.profil.html",form=form)

    #RECHARGE
@app.route('/recharge/<int:id>',methods = ["GET","POST"])
def recharge(id):
    form = RechargeForm()
    if form.validate_on_submit():
        code = form.code.data
        token = Code.query.filter_by(valeur=code,to_id=session["id"]).first()
        if(token==None):
            flash('code invalide')
        else:
            client=Client.query.get(id)
            client.solde+=token.montant
            session["solde"]=client.solde
            trans = Recharge(token.montant,token.distributeur,client)
            db.session.add(client)
            db.session.delete(token)
            db.session.add(trans)
            db.session.commit()
            return redirect(url_for('clientProfil',id=client.id))
    return render_template('client.recharge.html',form=form)

    #TRANSFERER VERS UN AUTRE COMPTE CLIENT
@app.route('/transfert/<int:id>',methods = ["GET","POST"])
def transfert(id):
    form = TransfertForm()
    if form.validate_on_submit():
        compte = form.numeroCompte.data
        montant = form.montant.data
        cl = Client.query.get(id)
        if(montant<500 or montant>5000):
            flash('Le montant doit etre entre 500 et 5000')
        else:
            if(cl.solde-montant<1000):
                flash('Votre solde est insuffisant pour ce transfert')
            else:
                us=Client.query.filter_by(numero=compte).first()
                if(us==None):
                    flash('Le numero de compte ne correspond à aucun compte')
                else:
                    if not us.etat:
                        flash('compte bloque')
                    else:
                        cl.solde-=montant
                        us.solde+=montant
                        session["solde"]=cl.solde
                        envoi=Envoi(montant,cl,us.id)
                        reception= Reception(montant,us,cl.id)
                        db.session.add(cl)
                        db.session.add(us)
                        db.session.add(envoi)
                        db.session.add(reception)
                        db.session.commit()
                        return redirect(url_for('clientProfil',id=cl.id))
    return render_template('client.transfert.html',form=form)

@app.route('/client/transactions')
def listeTransactionsClient():
    envois = Envoi.query.filter_by(from_id=session['id'])
    receptions = Reception.query.filter_by(to_id=session['id'])
    env=[]
    rec=[]
    for i in envois:
        env.append({'expediteur':session['nom'],'receveur':Client.query.get(i.to_id).numero,'item':i})
    for i in receptions:
        rec.append({'expediteur':Client.query.get(i.from_id).numero,'receveur':session['nom'],'item':i})
    return render_template("client.transactions.html",envois=env,receptions=rec)

@app.route('/client/recharges')
def listeRechargesClient():
    recharges = Recharge.query.filter_by(to_id=session['id'])
    rech=[]
    for i in recharges:
        rech.append({'expediteur':i.distributeur.email,'receveur':session['nom'],'item':i})
    return render_template("client.recharges.html",recharges=rech)

            ################ FONCTIONNALITES DISTRIBUTEUR CONNECTE #####################
@app.route('/distributeur/transactions')
def listeTransactions():
    transactions = Recharge.query.filter_by(from_id=session['id'])
    trans=[]
    for i in transactions:
        trans.append({'expediteur':session['nom'],'receveur':i.client.numero,'item':i})
    return render_template("distributeur.transactions.html",transactions=trans)

@app.route('/distributeur/depot',methods=['GET','POST'])
def depotCompte():
    form = AlimentationForm()
    if form.validate_on_submit():
        numero = form.numeroCompte.data
        montant = form.montant.data
        client = Client.query.filter_by(numero=numero).first()
        if client==None:
            flash('numero de compte inexistant')
        else:
            if not client.etat:
                flash('compte bloqué. Impossible de faire la transaction')
            else:
                if(montant<1000 or montant>500000):
                    flash('Veuillez rester entre 1 000 et 500 000')
                else:
                    dis=Distributeur.query.get(session.get('id'))
                    code = Code(montant,dis,client)
                    db.session.add(code)
                    db.session.commit()
                    return redirect(url_for('codes'))
    return render_template("distribution.depot.html",form=form)

@app.route('/distributeur/profil/<int:id>',methods=['GET','POST'])
def distributeurProfil(id):
    form = ChangePasswordForm()
    if form.validate_on_submit:
        oldPass=form.oldPassword.data
        newPass=form.newPassword.data
        confPass=form.confirmNewPassword.data
        if(oldPass!=Distributeur.query.get(id).password):
            flash('mot de passe incorrect')
        else:
            if(newPass!=confPass):
                flash('veuillez confirmer correctement le mot de passe')
            else:
                cl=Distributeur.query.get(id)
                cl.password=newPass
                session["password"]=newPass
                db.session.add(cl)
                db.session.commit()
    return render_template("distribution.profil.html",form=form)

@app.route('/distributeur/codes')
def codes():
    dis = Distributeur.query.get(session.get('id'))
    codes = dis.codes
    return render_template("distribution.codes.html",codes=codes)

@app.route('/distributeur/listeComptes')
def listeComptes():
    users = Client.query.all()
    return render_template("distribution.liste.html",users=users)

@app.route('/distributeur/code/supprimer/<int:id>')
def annulerDepot(id):
    code = Code.query.get(id)
    db.session.delete(code)
    db.session.commit()
    return redirect(url_for('codes'))


    #DECONNEXION
@app.route('/logout')
def logout():
    session.clear()
    return render_template("base.html")

if __name__ == '__main__':
    app.run(debug=True)