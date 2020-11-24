import MySQLdb
from MySQLdb import cursors
from flask import Flask, render_template, request, url_for, flash, session
from flask_mysqldb import MySQL
from requests import Session
from werkzeug.utils import redirect
import yaml

sess = Session()
app = Flask(__name__)
app.secret_key = 'super secret key'

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='lolacola'
app.config['MYSQL_DB'] = 'gestiune_analize_medicale'

mysql = MySQL(app)

@app.route('/', methods = ['GET','POST'])
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return render_template('start.html')

@app.route('/login', methods = ['GET','POST'])
def index():
    if 'loggedin' in session:
        return profile()
    else:
        msg = ''
        if request.method=='POST':
            if request.form['submit_button'] == 'Sign In':
                return redirect(url_for("signin"))
            elif request.form['submit_button'] == 'Log In' and 'email' in request.form and 'parola' in request.form:
                email = request.form['email']
                parola = request.form['parola']
                cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
                cur.execute('SELECT * FROM pacienti WHERE email = %s AND parola = %s', (email, parola))
                account = cur.fetchone()
                #return account
                if account:
                    session['loggedin'] = True
                    session['id'] = account['idpacienti']
                    session['username'] = account['Nume'] #+ account ['prenume']
                    msg ='Logare efectuata cu succes!'
                    return render_template('home.html', username=session['username'])
                else:
                    msg = 'Email/parola incorecte!'
        return render_template('index.html')

@app.route('/login/logout', methods = ['GET','POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        dateUser = request.form #dar pot fi mai multe formulare
        nume = dateUser['nume']
        prenume = dateUser['prenume']
        cnp = dateUser['cnp']
        numar_telefon = dateUser['numar_telefon']
        email = dateUser['email']
        parola = dateUser['parola']
        data_nastere = dateUser['data']
        sex = dateUser['sex']
        istoric = dateUser['istoric']
        modalitate_plata = dateUser['modalitate_plata']
        cur = mysql.connection.cursor()

        try:
            cur.execute("INSERT INTO pacienti(nume, prenume, cnp, numar_telefon, email, parola, data_nastere, istoric, sex, modalitate_plata) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (nume, prenume, cnp, numar_telefon, email, parola, data_nastere ,istoric,sex, modalitate_plata))
            mysql.connection.commit()
            cur.close()
            msg = "Nou utilizator adaugat!"
            return render_template('index.html', msg=msg)

        except Exception as e:
            print(e)
            flash("Noul utilizator nu a putut fi adaugat!")
            return render_template('signin.html')
    else:
        return render_template('signin.html')

@app.route('/login/profile')
def profile():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM pacienti WHERE idpacienti = %s', (session['id'],))
        account = cur.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
