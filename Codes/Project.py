import email_validator
from flask import Flask, render_template, flash, url_for, redirect, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Register Form
class RegisterForm(Form):
    Name = StringField("İsim",validators=[validators.Length(min=2, max=40)])
    SurName = StringField("Soyisim",validators=[
                          validators.Length(min=2, max=40)])
    Password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen Parola Belirleyin"),
        validators.EqualTo(fieldname="Confirm", message="Parola Uyuşmuyor")
    ])
    Confirm = PasswordField("Parola Doğrula")
    Email = StringField("Email",validators=[validators.Email(
        message="Lütfen geçerli bir e-mail adresi giriniz")])

    Phone = StringField("Telefon",validators=[validators.Length(max = 13,min = 10)])
    Adress = TextAreaField("Adres",validators=[validators.Length(max = 250,min = 0)])

class LoginForm(Form):
    e_mail = StringField("Email",validators=[validators.Email(message="Geçerli bir email adresi giriniz")])
    Password = PasswordField("Parola")

app = Flask(__name__)


app.config["MYSQL_HOST"] = "localhost" 
app.config["MYSQL_USER"] = "root"  
app.config["MYSQL_PASSWORD"] = "projesifre123"
app.config["MYSQL_DB"] = "e_manav"   
app.config["MYSQL_CURSORCLASS"] = "DictCursor"  
app.secret_key = "E_MANAV"                                     
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("homepage.html")

@app.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        e_mail = request.form["e_mail"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()
        query = f"select * from users where email = '{e_mail}'"

        result = cursor.execute(query)

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]

            if sha256_crypt.verify(password,real_password):
                flash("Başarı İle Giriş Yaptınız" , category="success")
                session["logged_in"] = True
                session["name"] = data["name"].title()
                session["email"] = data["email"]
                cursor.close()
                return redirect(url_for("index"))
            else:
                flash("Şifre Yanlış" , category="danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle Bir Kullanıcı Bulunmuyor" , category="danger")
            return redirect(url_for("login"))        
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():

        Name = form.Name.data
        SurName = form.SurName.data
        Password = sha256_crypt.encrypt(form.Password.data)
        Email = form.Email.data
        Number = form.Phone.data
        Adress = form.Adress.data

        cursor = mysql.connection.cursor()
        query = f"Insert into users(name,surname,password,email,number,adress) VALUES('{Name}','{SurName}','{Password}','{Email}','{Number}','{Adress}')"

        cursor.execute(query)
        mysql.connection.commit()
        cursor.close()

        flash("Başarı İle Kayıt Oldunuz" , category="success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

@app.route("/basket",methods = ["GET" , "POST"])
def basket():
    return render_template("basket.html") 

if __name__ == "__main__":
    app.run(debug=True)