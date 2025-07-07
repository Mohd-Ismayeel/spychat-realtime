from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import encode_message, decode_message
from metadata import encrypt_metadata, identify_cipher_from_metadata
from functools import wraps
from flask_socketio import SocketIO, emit
import os
import sys

app = Flask(__name__)
app.secret_key = 'spychat-secret-key'
socketio = SocketIO(app)

users = {'spy1': 'pass', 'spy2': 'pass'}

# ---------- Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Routes ----------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash("Username already exists")
        else:
            users[username] = password
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=session['username'])

@app.route('/encode', methods=['POST'])
@login_required
def encode():
    message = request.form['message']
    method = request.form['method']
    encoded = encode_message(method, message)
    metadata_hash, display_code = encrypt_metadata(method)
    full_message = f"{metadata_hash}:: {encoded}"
    return render_template(
        'chat.html', 
        username=session['username'], 
        preview_message=full_message, 
        metadata_preview=metadata_hash, 
        preview_code=display_code
    )

@app.route('/send', methods=['POST'])
@login_required
def send():
    try:
        full_message = request.form['encoded']
        print("📨 Incoming encoded:", full_message, file=sys.stdout, flush=True)
        sender = session['username']

        if '::' not in full_message:
            print("❌ Invalid message format", file=sys.stdout, flush=True)
            return "Bad Format", 400

        metadata, encoded_msg = full_message.split('::', 1)
        cipher_method, display_code = identify_cipher_from_metadata(metadata.strip())
        print("🔍 Identified method:", cipher_method, file=sys.stdout, flush=True)

        msg_data = {
            'sender': sender,
            'encoded': encoded_msg.strip(),
            'metadata': metadata.strip(),
            'cipher_method': cipher_method,
            'display_code': display_code,
            'decoded': ''
        }

        socketio.emit('receive_message', msg_data, broadcast=True)
        return '', 204

    except Exception as e:
        print("🔥 ERROR in /send:", str(e), file=sys.stdout, flush=True)
        return "Internal Server Error", 500

@app.route('/decode', methods=['POST'])
@login_required
def decode():
    encoded_msg = request.form['encoded']
    method = request.form['method']
    try:
        decoded_msg = decode_message(method, encoded_msg)
    except Exception as e:
        decoded_msg = f"[Error: {str(e)}]"

    socketio.emit('decode_message', {
        'encoded': encoded_msg,
        'decoded': decoded_msg
    }, broadcast=True)
    return '', 204

@socketio.on('send_message')
def handle_send_message(data):
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
