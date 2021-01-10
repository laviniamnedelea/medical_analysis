import MySQLdb
from MySQLdb import cursors
from flask import Flask, render_template, request, url_for, session, flash
from flask_mysqldb import MySQL
from requests import Session
from werkzeug.utils import redirect


with open("data.txt", "r") as f:
    for line in f:
        password=line

sess = Session()
app = Flask(__name__)
app.secret_key = 'super secret key'

app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'gestiune_analize_medicale'

mysql = MySQL(app)

@app.route('/', methods = ['GET','POST'])
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return render_template('start.html')

@app.route('/adminPanel', methods = ['GET','POST'])
def admin():
    if 'loggedin' in session and session['id'] == 1:
        return render_template('admin.html')
    else:
        return render_template('start.html')

@app.route('/utilizatori', methods=['GET', 'POST', 'SUBMIT'])
def users_admin():
    if 'loggedin' in session and session['id'] == 1:
        cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
        cur.execute('SELECT * FROM pacienti as P LEFT JOIN buletin_analiza as b ON P.id_pacient = b.id_pacient')
        data = cur.fetchall()
        if request.method == 'POST':
            res = request.form # will be None if form wasn't submitted
            query = res['search']
            session['msg'] = str(query)
            cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
            cur.execute(
                'SELECT * FROM pacienti as P LEFT JOIN buletin_analiza as B ON P.id_pacient = B.id_pacient'
                ' LEFT JOIN Analiza as A ON A.id_analiza = B.id_analiza WHERE P.CNP =' + session['msg'])
            # mai adauga un join cu alt tabel

            search_data = cur.fetchall()
            if not search_data:
                return render_template("utilizatori.html")
            session['search_data']=search_data
            session['msg'] = str(query)
            flash(session['msg'])
            return render_template('utilizatori.html', data=search_data)

        elif request.method == 'SUBMIT' and request.name == "delete_user":
                #flash(session['msg'])
                return redirect(url_for('delete'))

        return render_template('utilizatori.html', data = data)


@app.route('/delete', methods = ['GET','POST'])
def delete():
    cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
    cur.execute("DELETE p,a,pac FROM pacienti as p LEFT JOIN pacient_analiza_centru as pac on pac.id_pacient = p.id_pacient"
                " LEFT JOIN buletin_analiza as a on pac.id_pacient = a.id_pacient  WHERE p.CNP=" + session['msg'])
    mysql.connection.commit()
    return render_template('utilizatori.html')

@app.route('/analize', methods = ['GET','POST'])
def analize():
    cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor)) # aici gandeste te la un join ca sa afisezi si analizele existente
    if request.method == 'POST':
        dateUser = request.form
        cnp = dateUser['cnp']
        id_analiza = str(dateUser['analiza'])
        id_centru = str(dateUser['centru'])
        cur.execute('SELECT p.id_pacient from pacienti as p WHERE p.CNP = ' + cnp )
        id_pacient_form = str(cur.fetchall()[0]['id_pacient'])
        #return render_template("home.html", username = id_pacient_form[0]['id_pacient'])
        cur.execute(
            "INSERT INTO pacient_analiza_centru(id_pacient, id_analiza, id_centru) VALUES(" + id_pacient_form + ","
             + id_analiza + ', ' + id_centru + ")")
        mysql.connection.commit()
    cur.execute(
        'SELECT * FROM pacienti as P LEFT JOIN pacient_analiza_centru as pac ON P.id_pacient = pac.id_pacient'
        ' LEFT JOIN analiza as A ON A.id_analiza = pac.id_analiza LEFT JOIN centru  as c ON '
        'pac.id_centru = c.id_centru' )
    data = cur.fetchall()
    session['analize'] = data
    return render_template("analize.html", data = data)


@app.route('/update', methods = ['GET','POST'])
def update():
    cur = mysql.connection.cursor((MySQLdb.cursors.DictCursor))
    cur.execute(
        'SELECT * FROM pacienti as P LEFT JOIN buletin_analiza as B ON P.id_pacient = B.id_pacient'
        ' LEFT JOIN Analiza as A ON A.id_analiza = B.id_analiza WHERE P.CNP =' + session['msg'])
    search_data = cur.fetchall()
    if request.method == 'POST':
        dateUser = request.form #dar pot fi mai multe formulare
        nume = dateUser['nume']
        prenume = dateUser['prenume']
        numar_telefon = dateUser['numar_telefon']
        email = dateUser['email']
        data_nastere = dateUser['data']
        sex = dateUser['sex']
        istoric = dateUser['istoric']
        modalitate_plata = dateUser['modalitate_plata']
        cur = mysql.connection.cursor()
        if nume != '':
            cur.execute('UPDATE pacienti SET Nume = \'' + nume + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if prenume != '':
            cur.execute('UPDATE pacienti SET Prenume = \'' + prenume + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if numar_telefon != '':
            cur.execute('UPDATE pacienti SET Numar_telefon = \'' + numar_telefon + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if email != '':
            cur.execute('UPDATE pacienti SET Email = \'' + email + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if data_nastere != '':
            cur.execute('UPDATE pacienti SET Data_nastere = \'' + data_nastere + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if sex != '':
            cur.execute('UPDATE pacienti SET Sex = \'' + sex + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if istoric != '':
            cur.execute('UPDATE pacienti SET Istoric = \'' + istoric + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        if modalitate_plata != '':
            cur.execute('UPDATE pacienti SET Modalitate_plata = \'' + modalitate_plata + '\' WHERE CNP =' + session['msg'])
            mysql.connection.commit()
        return redirect(url_for('users_admin'))

    return render_template('update.html', data =search_data, cnp = session['msg'])


@app.route('/add_user', methods=['GET','POST'])
def add_users():
    if 'loggedin' in session and session['id'] == 1:
        if request.method == 'POST':
            dateUser = request.form  # dar pot fi mai multe formulare
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
                cur.execute(
                    "INSERT INTO pacienti(nume, prenume, cnp, numar_telefon, email, parola, data_nastere, istoric, sex, modalitate_plata) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (nume, prenume, cnp, numar_telefon, email, parola, data_nastere, istoric, sex, modalitate_plata))
                mysql.connection.commit()
                cur.close()
                msg = "Nou utilizator adaugat!"
                return users_admin()
            except Exception as e:
                print(e)
                if "Duplicate" in str(e):
                    return render_template('add_user.html', msg="Datele sunt deja inregistrate.")
        else:
            return render_template('add_user.html')
        return render_template('utilizatori.html')

@app.route('/rezultat', methods = ['GET','POST'])
def rezultat():
    if 'loggedin' in session and session['id'] == 1:
        cur = mysql.connection.cursor(
            (MySQLdb.cursors.DictCursor))
        if request.method == 'POST':
            dateUser = request.form
            cnp = dateUser['cnp']
            id_analiza = str(dateUser['analiza'])
            rezultat = str(dateUser['rezultat'])
            data_recoltare = dateUser['data_recoltare']
            ora = dateUser['ora']
            refacere = dateUser['refacere']
            specializare = dateUser['specializare']
            # cur.execute('SELECT p.id_pacient from pacienti as p WHERE p.CNP = ' + cnp)
            # id_pacient_form = str(cur.fetchall()[0]['id_pacient'])
            # # return render_template("home.html", username = id_pacient_form[0]['id_pacient'])
            # cur.execute(
            #     "INSERT INTO pacient_analiza_centru(id_pacient, id_analiza, id_centru) VALUES(" + id_pacient_form + ","
            #     + id_analiza + ', ' + id_centru + ")")
            # mysql.connection.commit()

    return render_template('rezultat.html')


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
                    session['id'] = account['id_pacient']
                    session['username'] = account['Nume'] + " " + account ['Prenume']
                    msg ='Logare efectuata cu succes!'
                    return render_template('home.html', username=session['username'])
                else:
                    msg = 'Email/parola incorecte!'
        return render_template('index.html', msg=msg)

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
            if "Duplicate" in str(e):
                return render_template('signin.html',  msg="Datele sunt deja inregistrate.")
    else:
        return render_template('signin.html')

@app.route('/login/profile')
def profile():
    if 'loggedin' in session:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM pacienti WHERE id_pacient = %s', (session['id'],))
        account = cur.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
