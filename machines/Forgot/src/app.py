import uuid
import base64
import random
import hashlib
import urllib.parse
import mysql.connector
from flask import *
from flask_session import Session
import netifaces as ni
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def reset_db_records():
    conn.reconnect()
    c = conn.cursor()
    c.execute('update users set password="dCvf34@3#8(6" where username like "robert-dev%"')
    conn.commit()


def remove_escalate_records():
    conn.reconnect()
    c = conn.cursor()
    c.execute("delete from escalate")
    conn.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_db_records, trigger="interval", seconds=600)
scheduler.add_job(func=remove_escalate_records, trigger="interval", seconds=240)
scheduler.start()


def login_required(f):
    @wraps(f)
    def session_validation(*args, **kwargs):
        try:
            if session['user']:
                return f(*args, **kwargs)
            else:
                return redirect('/home?err=ACCESS_DENIED')
        except Exception as _:
            return redirect('/')

    return session_validation


def host_check(f):
    @wraps(f)
    def validation(*args, **kwargs):
        h = request.headers.get('Host')
        tun_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        if h != tun_ip and h != "forgot.htb":
            return redirect(f'http://{h}', code=302)
        else:
            return f(*args, **kwargs)

    return validation


@app.route('/home', defaults={'path': ''})
@app.route('/home/<path:path>')
@host_check
@login_required
def home(path):
    return render_template('home.html', user='Robert')


@app.route('/')
@host_check
def index():
    conn.reconnect()
    c = conn.cursor()
    c.execute('select username from users')
    user = c.fetchall()
    return render_template('index.html', user=random.choice(user[1:])[0])


@app.route('/login', methods=["GET", "POST"])
@host_check
def login():
    conn.reconnect()
    c = conn.cursor()
    username = request.form.get('username')
    password = request.form.get('password')
    c.execute('select username,password from users where username=%s and password=%s', (username, password,))
    if c.fetchone():
        session['user'] = username
        return '<script>window.location.href="/home";</script>';
    else:
        return render_template('index.html', err='Invalid Credentials')


@app.route('/forgot')
def forgot():
    conn.reconnect()
    c = conn.cursor()
    c.execute('select * from users')
    u = c.fetchall()
    users = {}
    for i in u:
        users[i[0]] = generate_password_hash(i[1])
    if request.args.get('username'):
        username = request.args.get('username')
        if username == 'admin':
            return 'Admin password can\'t be reset'
        elif username in users:
            c = conn.cursor()
            u = uuid.uuid4().hex
            token = base64.b64encode(
                hashlib.sha512((username + 'dcFd034sd@$(%*!Jcve85#2)4$@*^' + u).encode('utf-8')).digest())
            link = 'http://' + request.headers.get('host') + '/reset?token=' + urllib.parse.quote_plus(
                token.decode('utf-8'))
            c.execute("insert into forgot values(%s,%s,%s,%s)", (token.decode('utf-8'), link, u, username,))
            conn.commit()
            return 'Password reset link has been sent to user inbox. Please use the link to reset your password'
        else:
            return 'Invalid Username'

    return render_template('forgot.html')


@app.route('/reset', methods=["GET", "POST"])
def reset():
    if request.method == 'GET':
        return render_template('reset.html')
    else:
        token = request.args.get('token')
        password = request.form.get('password')
        conn.reconnect()
        c = conn.cursor()
        c.execute('select username,reset_code from forgot where reset_token=%s', (token,))
        rows = c.fetchone()
        if rows:
            v_token = base64.b64encode(
                hashlib.sha512((rows[0] + 'dcFd034sd@$(%*!Jcve85#2)4$@*^' + rows[1]).encode('utf-8')).digest())
            if token == v_token.decode('utf-8'):
                c.execute('update users set password=%s where username=%s', (password, rows[0]))
                conn.commit()
                c.execute('delete from forgot where reset_token=%s', (token,))
                conn.commit()
                return 'Success'
            else:
                return 'Invalid token'
        else:
            return 'Invalid token'


@app.route('/tickets', defaults={'path': ''})
@app.route('/tickets/<path:path>')
@login_required
def tickets(path):
    conn.reconnect()
    c = conn.cursor()
    c.execute('select * from tickets')
    r = c.fetchall()
    return render_template('tickets.html', tickets=r)


@app.route('/escalate', methods=['GET', 'POST'])
@login_required
def escalate():
    if request.method == 'GET':
        conn.reconnect()
        c = conn.cursor()
        c.execute('select * from tickets')
        r = c.fetchall()
        return render_template('escalate.html', tickets=r)
    else:
        to = request.form.get('to')
        link = request.form.get('link')
        issue = request.form.get('issue')
        reason = request.form.get('reason')
        if 'http' in link.lower():
            ip = link.split('/')[2]
            tun_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
            if ip != tun_ip:
                return 'This request can\'t be reviewed since the issue link is flagged'
        conn.reconnect()
        c = conn.cursor()
        c.execute('insert into escalate values(%s,%s,%s,%s)', (to, issue, link, reason,))
        conn.commit()
        return 'Escalation form submitted to Admin and will be reviewed soon!'


@app.route('/admin_tickets', defaults={'path': ''})
@app.route('/admin_tickets/<path:path>')
@login_required
def admin(path):
    conn.reconnect()
    c = conn.cursor()
    c.execute('select username from users where username=%s', (session['user'],))
    if 'admin' not in c.fetchone():
        return redirect('/home?err=ACCESS_DENIED')
    else:
        c.execute('select * from admin_tickets');
        r = c.fetchall()
        return render_template('admin.html', tickets=r)


if __name__ == "__main__":
    conn = mysql.connector.connect(host='localhost', database='app', user='diego', password='dCb#1!x0%gjq')
    app.run(host='127.0.0.1', port=8080)
