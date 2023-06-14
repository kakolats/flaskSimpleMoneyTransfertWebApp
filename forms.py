from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField ("Password", validators=[DataRequired("Mot de passe obligatoire")])
    submit = SubmitField("Connexion")

class SearchAccountForm(FlaskForm):
    numero= StringField("Numero", validators=[DataRequired()])
    submit = SubmitField("Rechercher")

class AddClientForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prenom", validators=[DataRequired()])
    telephone = StringField("Telephone", validators=[DataRequired()])
    submit = SubmitField("Ajouter")

class AddAdminForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prenom", validators=[DataRequired()])
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    passwordConfirm = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Ajouter")

class AddDistributeurForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired()])
    prenom = StringField("Prenom", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    submit = SubmitField("Ajouter")

class DesactivateUserForm(FlaskForm):
    id = IntegerField("User Id", validators=[DataRequired()])
    submit = SubmitField("Desactiver")

class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField("Old Password", validators=[DataRequired()])
    newPassword = PasswordField("New Password", validators=[DataRequired()]) 
    confirmNewPassword = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Changer")


class RechargeForm(FlaskForm):
    code = StringField("Code de recharge",validators=[DataRequired()])
    submit = SubmitField("Recharger")

class TransfertForm(FlaskForm):
    numeroCompte = StringField("Numero de compte",validators=[DataRequired()])
    montant = IntegerField("Montant de transfert",validators=[DataRequired()])
    submit = SubmitField("Transferer")

class AlimentationForm(FlaskForm):
    numeroCompte = StringField("Numero de compte",validators=[DataRequired()])
    montant = IntegerField("Montant de transfert",validators=[DataRequired()])
    submit = SubmitField("Transferer")
