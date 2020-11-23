from flask import Flask, render_template, request, url_for, flash
from flask_mysqldb import MySQL
from requests import Session
from werkzeug.utils import redirect

sess = Session()
app = Flask(__name__)


app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] ='lolacola'
app.config['MYSQL_DB'] = 'gestiune_analize_medicale'

mysql = MySQL(app)

@app.route('/', methods = ['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/cont', methods = ['GET','POST'])
def index():
    if request.method=='POST':
        if request.form['submit_button'] == 'Sign In':
            return redirect(url_for("signin"))
        elif request.form['submit_button'] == 'Log In':
            return render_template('index.html')
    return render_template('index.html')


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
            flash("Nou utilizator adaugat!")
            return render_template('signin.html')
        except Exception as e:
            print(e)
            flash("Noul utilizator nu a putut fi adaugat!")
            return render_template('signin.html')
    else:
        return render_template('signin.html')
#
# @app.route('/users')
# def users():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute("SELECT * FROM pacienti")
#     if resultValue > 0:
#         userDetails = cur.fetchall()
#         return render_template('users.html',userDetails=userDetails)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
